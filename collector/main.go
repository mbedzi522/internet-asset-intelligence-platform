
package main

import (
	"crypto/rand"
	"encoding/json"
	"fmt"
	"log"
	"net"
	"os"
	"time"

	"github.com/google/uuid"
	"golang.org/x/crypto/ed25519"
	"gopkg.in/yaml.v2"

	"internet-asset-platform/collector/probes"
)

const ( 
	ScannerVersion = "0.1.0"
	CollectorID    = "collector-001" // This should be dynamically set in production
)

type Config struct {
	AllowedCIDRs        []string `yaml:"allowed_cidrs"`
	AllowPublicTargets  bool     `yaml:"allow_public_targets"`
	PublicScanConsent   string   `yaml:"public_scan_consent"`
	RequirePOAForPublic bool     `yaml:"require_poa_for_public"`
	Ports               []int    `yaml:"ports"`
	ProbeTypes          []string `yaml:"probe_types"`
	SignerKeyVaultPath  string   `yaml:"signer_key_vault_path"`
	DevSignerKeyPath    string   `yaml:"dev_signer_key_path"`
	ObjectStore         struct {
		Endpoint  string `yaml:"endpoint"`
		Bucket    string `yaml:"bucket"`
		AccessKey string `yaml:"access_key"`
		SecretKey string `yaml:"secret_key"`
	} `yaml:"object_store"`
	Kafka struct {
		Brokers []string `yaml:"brokers"`
		Topic   string   `yaml:"topic"`
	} `yaml:"kafka"`
	Concurrency       int `yaml:"concurrency"`
	RateLimitPerTarget int `yaml:"rate_limit_per_target"`
	GlobalRateLimit    int `yaml:"global_rate_limit"`
}

type Event struct {
	ID           uuid.UUID            `json:"id"`
	Timestamp    time.Time            `json:"timestamp"`
	ScannerVersion string             `json:"scanner_version"`
	CollectorID  string               `json:"collector_id"`
	Target       TargetInfo           `json:"target"`
	Probes       map[string]interface{} `json:"probes"`
	Meta         EventMeta            `json:"meta"`
}

type TargetInfo struct {
	IP       string `json:"ip"`
	Port     int    `json:"port"`
	Protocol string `json:"protocol"`
}

type EventMeta struct {
	ConfigHash string `json:"config_hash"`
	Policy     string `json:"policy"`
}

var ( 
	privateKey ed25519.PrivateKey
	publicKeys map[string]ed25519.PublicKey // In a real scenario, this would store trusted public keys
)

func main() {
	configPath := os.Getenv("COLLECTOR_CONFIG_PATH")
	if configPath == "" {
		configPath = "config.yaml"
	}
	cfg, err := loadConfig(configPath)
	if err != nil {
		log.Fatalf("Failed to load config: %v", err)
	}

	// Load signing key (for dev purposes, generate one if not found)
	if cfg.DevSignerKeyPath != "" {
		privateKey, err = loadOrCreateDevKey(cfg.DevSignerKeyPath)
		if err != nil {
			log.Fatalf("Failed to load or create dev key: %v", err)
		}
		log.Printf("Loaded dev signing key from %s\n", cfg.DevSignerKeyPath)
	} else if cfg.SignerKeyVaultPath != "" {
		// In a real scenario, integrate with Vault here
		log.Fatalf("Vault integration not implemented. Please provide a dev key path or implement Vault client.")
	} else {
		log.Fatalf("No signing key path provided. Please set dev_signer_key_path or signer_key_vault_path.")
	}

	log.Printf("Loaded Configuration: %+v\n", cfg)

	// Example scan target (e.g., localhost)
	targets := []string{"127.0.0.1"}

	for _, ipStr := range targets {
		ip := net.ParseIP(ipStr)
		if ip == nil {
			log.Printf("Invalid IP address: %s\n", ipStr)
			continue
		}

		if !isValidTarget(ip, cfg) {
			log.Printf("Target IP %s is not allowed by configuration. Skipping.\n", ip)
			continue
		}

		log.Printf("Scanning target: %s\n", ip)
		for _, port := range cfg.Ports {
			log.Printf(" Probing port: %d\n", port)
			probeResults := make(map[string]interface{})
			for _, probeType := range cfg.ProbeTypes {
				switch probeType {
				case "tcp":
					result := probes.TCPConnect(ip.String(), port, 5*time.Second)
					probeResults["tcp_connect"] = result
				case "http":
					result := probes.HTTPProbe(ip.String(), port, 10*time.Second, false)
					probeResults["http"] = result
				case "tls":
					result := probes.TLSProbe(ip.String(), port, 10*time.Second, ip.String()) // Use IP as SNI for now
					probeResults["tls"] = result
				case "ssh-banner":
					result := probes.SSHBannerProbe(ip.String(), port, 5*time.Second)
					probeResults["ssh_banner"] = result
				default:
					log.Printf("Unknown probe type: %s\n", probeType)
				}
			}

			event := Event{
				ID:           uuid.New(),
				Timestamp:    time.Now().UTC(),
				ScannerVersion: ScannerVersion,
				CollectorID:  CollectorID,
				Target:       TargetInfo{IP: ip.String(), Port: port, Protocol: "tcp"}, // Protocol might be more specific based on probe
				Probes:       probeResults,
				Meta:         EventMeta{ConfigHash: "TODO_CONFIG_HASH", Policy: "default-private"},
			}

			// Canonicalize and sign event
			canonicalEvent, err := json.Marshal(event) // This is not truly canonical JSON yet (sorted keys)
			if err != nil {
				log.Printf("Error marshaling event: %v\n", err)
				continue
			}

			signedEvent, err := signEvent(canonicalEvent, privateKey)
			if err != nil {
				log.Printf("Error signing event: %v\n", err)
				continue
			}

			// Upload event and signature
			err = uploadEvent(canonicalEvent, signedEvent, cfg)
			if err != nil {
				log.Printf("Error uploading event: %v\n", err)
				continue
			}
			log.Printf("Successfully processed and uploaded event for %s:%d\n", ip, port)
		}
	}

	fmt.Println("Collector agent finished scanning.")
}

func loadConfig(path string) (*Config, error) {
	data, err := os.ReadFile(path)
	if err != nil {
		return nil, fmt.Errorf("reading config file: %w", err)
	}

	var cfg Config
	// Set default values
	cfg.AllowedCIDRs = []string{"127.0.0.0/8", "10.0.0.0/8", "172.16.0.0/12", "192.168.0.0/16"}
	cfg.Ports = []int{80, 443}
	cfg.ProbeTypes = []string{"tcp", "http", "tls"}
	cfg.Concurrency = 100
	cfg.RequirePOAForPublic = true

	err = yaml.Unmarshal(data, &cfg)
	if err != nil {
		return nil, fmt.Errorf("unmarshaling config: %w", err)
	}

	return &cfg, nil
}

func isValidTarget(ip net.IP, cfg *Config) bool {
	// Check against allowed CIDRs
	for _, cidr := range cfg.AllowedCIDRs {
		_, ipNet, err := net.ParseCIDR(cidr)
		if err != nil {
			log.Printf("Invalid CIDR in config: %s - %v\n", cidr, err)
			continue
		}
		if ipNet.Contains(ip) {
			return true
		}
	}

	// If not in allowed CIDRs, check public target rules
	if !isPrivateIP(ip) {
		if !cfg.AllowPublicTargets {
			return false
		}
		// Further checks for public targets (consent, POA) would go here.
		// For now, if AllowPublicTargets is true, and it's not a private IP, we allow it.
		// The full logic for public_scan_consent and require_poa_for_public needs to be implemented.
		// This is a placeholder for actual consent/POA validation.
		if cfg.RequirePOAForPublic && cfg.PublicScanConsent == "" {
			log.Printf("Public scan requires POA and consent token, but public_scan_consent is empty.\n")
			return false
		}
		log.Printf("Public IP %s allowed due to AllowPublicTargets=true and consent token present (placeholder logic).\n", ip)
		return true
	}

	return true
}

func isPrivateIP(ip net.IP) bool {
	// This function should ideally use the allowed_cidrs from config if they represent private ranges.
	// For now, hardcoding standard private IP blocks and loopback.
	var privateIPBlocks []*net.IPNet
	for _, cidr := range []string{
		"127.0.0.0/8",    // Loopback
		"10.0.0.0/8",     // Private
		"172.16.0.0/12",  // Private
		"192.168.0.0/16", // Private
	} {
		_, block, _ := net.ParseCIDR(cidr)
		privateIPBlocks = append(privateIPBlocks, block)
	}

	for _, block := range privateIPBlocks {
		if block.Contains(ip) {
			return true
		}
	}
	return false
}

// loadOrCreateDevKey loads an Ed25519 private key from path or creates a new one if it doesn't exist.
func loadOrCreateDevKey(path string) (ed25519.PrivateKey, error) {
	var privKey ed25519.PrivateKey

	if _, err := os.Stat(path); os.IsNotExist(err) {
		log.Printf("Dev key not found at %s, generating new key pair.\n", path)
		pub, priv, err := ed25519.GenerateKey(rand.Reader)
		if err != nil {
			return nil, fmt.Errorf("failed to generate Ed25519 key: %w", err)
		}
		privKey = priv

		// Save private key to file
		err = os.WriteFile(path, privKey, 0600)
		if err != nil {
			return nil, fmt.Errorf("failed to save private key: %w", err)
		}
		log.Printf("Generated and saved new dev private key to %s\n", path)
		// In a real scenario, public key would also be saved/registered
		_ = pub // Avoid unused variable error
	} else if err != nil {
		return nil, fmt.Errorf("error stating dev key file: %w", err)
	} else {
		// Load existing private key
		keyBytes, err := os.ReadFile(path)
		if err != nil {
			return nil, fmt.Errorf("failed to read dev private key: %w", err)
		}
		privKey = ed25519.PrivateKey(keyBytes)
		if len(privKey) != ed25519.PrivateKeySize {
			return nil, fmt.Errorf("invalid private key size in %s", path)
		}
	}
	return privKey, nil
}

// signEvent canonicalizes JSON, signs it with Ed25519 private key, and returns the signature.
func signEvent(eventBytes []byte, privateKey ed25519.PrivateKey) ([]byte, error) {
	// Re-marshal to ensure canonical JSON (sorted keys, no extra whitespace)
	// This is a simplified approach. A proper canonicalization would involve
	// sorting keys recursively. For now, assuming `json.Marshal` with default
	// struct tags will produce consistent output for our Event struct.
	var generic map[string]interface{}
	err := json.Unmarshal(eventBytes, &generic)
	if err != nil {
		return nil, fmt.Errorf("failed to unmarshal event for canonicalization: %w", err)
	}
	// A more robust canonicalization would sort keys here
	canonicalBytes, err := json.Marshal(generic) // Re-marshal to ensure consistent formatting
	if err != nil {
		return nil, fmt.Errorf("failed to re-marshal for canonicalization: %w", err)
	}

	signature := ed25519.Sign(privateKey, canonicalBytes)
	return signature, nil
}

// uploadEvent uploads the canonical JSON event and its signature.
// This implementation uses a simple file-based approach for demonstration.
// In production, this would interact with S3-compatible object storage or Kafka.
func uploadEvent(eventBytes []byte, signature []byte, cfg *Config) error {
	// For now, simulate upload by saving to a local file.
	// In a real scenario, this would use cfg.ObjectStore or cfg.Kafka.
	fileName := fmt.Sprintf("event_%s.json", uuid.New().String())
	sigFileName := fmt.Sprintf("%s.sig", fileName)

	// Create a dummy 'outbox' directory if it doesn't exist
	if _, err := os.Stat("outbox"); os.IsNotExist(err) {
		err = os.Mkdir("outbox", 0755)
		if err != nil {
			return fmt.Errorf("failed to create outbox directory: %w", err)
		}
	}

	err := os.WriteFile(fmt.Sprintf("outbox/%s", fileName), eventBytes, 0644)
	if err != nil {
		return fmt.Errorf("failed to write event file: %w", err)
	}

	err = os.WriteFile(fmt.Sprintf("outbox/%s", sigFileName), signature, 0644)
	if err != nil {
		return fmt.Errorf("failed to write signature file: %w", err)
	}

	log.Printf("Simulated upload: Saved event to outbox/%s and signature to outbox/%s\n", fileName, sigFileName)
	return nil
}

