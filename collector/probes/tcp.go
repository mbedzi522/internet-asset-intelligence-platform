
package probes

import (
	"fmt"
	"net"
	"time"
)

// TCPConnectResult holds the result of a TCP connect probe.
type TCPConnectResult struct {
	Success bool  `json:"success"`
	Duration int64 `json:"duration_ms"`
	Error   string `json:"error,omitempty"`
}

// TCPConnect performs a simple TCP connection probe.
func TCPConnect(ip string, port int, timeout time.Duration) TCPConnectResult {
	addr := net.JoinHostPort(ip, fmt.Sprintf("%d", port))
	start := time.Now()
	conn, err := net.DialTimeout("tcp", addr, timeout)
	if err != nil {
		return TCPConnectResult{Success: false, Error: err.Error()}
	}
	defer conn.Close()
	return TCPConnectResult{Success: true, Duration: time.Since(start).Milliseconds()}
}

