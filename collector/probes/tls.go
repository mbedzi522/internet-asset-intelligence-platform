
package probes

import (
	"crypto/ecdsa"
	"crypto/rsa"
	"crypto/tls"
	"encoding/base64"
	"fmt"
	"net"
	"time"
)

// TLSProbeResult holds the result of a TLS probe.
type TLSProbeResult struct {
	SubjectCN     string   `json:"subject_cn,omitempty"`
	SubjectSANs   []string `json:"subject_sans,omitempty"`
	IssuerCN      string   `json:"issuer_cn,omitempty"`
	ValidFrom     time.Time `json:"valid_from,omitempty"`
	ValidTo       time.Time `json:"valid_to,omitempty"`
	KeyAlgo       string   `json:"key_algo,omitempty"`
	KeySize       int      `json:"key_size,omitempty"`
	SelfSigned    bool     `json:"self_signed,omitempty"`
	CertDERB64    string   `json:"cert_der_b64,omitempty"`
	Error         string   `json:"error,omitempty"`
}

// TLSProbe performs a TLS handshake and extracts certificate information.
func TLSProbe(ip string, port int, timeout time.Duration, sni string) TLSProbeResult {
	addr := net.JoinHostPort(ip, fmt.Sprintf("%d", port))

	config := &tls.Config{
		InsecureSkipVerify: true, // We collect cert info regardless of validity
		ServerName:         sni,
	}

	conn, err := tls.DialWithDialer(&net.Dialer{Timeout: timeout}, "tcp", addr, config)
	if err != nil {
		return TLSProbeResult{Error: err.Error()}
	}
	defer conn.Close()

	certState := conn.ConnectionState()
	if len(certState.PeerCertificates) == 0 {
		return TLSProbeResult{Error: "no peer certificates found"}
	}

	cert := certState.PeerCertificates[0] // Get the first certificate in the chain

	result := TLSProbeResult{
		SubjectCN:  cert.Subject.CommonName,
		IssuerCN:   cert.Issuer.CommonName,
		ValidFrom:  cert.NotBefore,
		ValidTo:    cert.NotAfter,
		SelfSigned: cert.CheckSignatureFrom(cert) == nil,
		CertDERB64: base64.StdEncoding.EncodeToString(cert.Raw),
	}

	// Extract SANs
	result.SubjectSANs = append(cert.DNSNames, cert.EmailAddresses...)
	for _, ip := range cert.IPAddresses {
		result.SubjectSANs = append(result.SubjectSANs, ip.String())
	}

	// Extract Key Algorithm and Size
	if pubKey, ok := cert.PublicKey.(*rsa.PublicKey); ok {
		result.KeyAlgo = "RSA"
		result.KeySize = pubKey.N.BitLen()
	} else if pubKey, ok := cert.PublicKey.(*ecdsa.PublicKey); ok {
		result.KeyAlgo = "ECDSA"
		result.KeySize = pubKey.Curve.Params().BitSize
	}

	return result
}

