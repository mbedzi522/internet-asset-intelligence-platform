package probes

import (
	"fmt"
	"net"
	"time"
)

// SSHBannerResult holds the result of an SSH banner probe.
type SSHBannerResult struct {
	Banner string `json:"banner,omitempty"`
	Error  string `json:"error,omitempty"`
}

// SSHBannerProbe connects to an SSH port and reads the banner.
func SSHBannerProbe(ip string, port int, timeout time.Duration) SSHBannerResult {
	addr := net.JoinHostPort(ip, fmt.Sprintf("%d", port))
	conn, err := net.DialTimeout("tcp", addr, timeout)
	if err != nil {
		return SSHBannerResult{Error: err.Error()}
	}
	defer conn.Close()

	// Set a read deadline for the banner
	conn.SetReadDeadline(time.Now().Add(timeout))

	buf := make([]byte, 256) // Read up to 256 bytes for the banner
	n, err := conn.Read(buf)
	if err != nil {
		return SSHBannerResult{Error: err.Error()}
	}

	return SSHBannerResult{Banner: string(buf[:n])}
}

