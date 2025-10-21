
package probes

import (
	"crypto/tls"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"
	"regexp"
	"io"
)

// HTTPProbeResult holds the result of an HTTP probe.
type HTTPProbeResult struct {
	StatusCode int               `json:"status_code,omitempty"`
	Headers    map[string]string `json:"headers,omitempty"`
	Title      string            `json:"title,omitempty"`
	Error      string            `json:"error,omitempty"`
}

// HTTPProbe performs an HTTP GET request and extracts relevant information.
func HTTPProbe(ip string, port int, timeout time.Duration, useTLS bool) HTTPProbeResult {
	protocol := "http"
	if useTLS {
		protocol = "https"
	}
	url := fmt.Sprintf("%s://%s:%d", protocol, ip, port)

	// Create a custom HTTP client with a timeout and to handle TLS (e.g., skip cert verification for initial probe)
	tr := &http.Transport{
		TLSClientConfig: &tls.Config{InsecureSkipVerify: true},
	}
	client := &http.Client{Timeout: timeout, Transport: tr}

	req, err := http.NewRequest("GET", url, nil)
	if err != nil {
		return HTTPProbeResult{Error: err.Error()}
	}

	res, err := client.Do(req)
	if err != nil {
		return HTTPProbeResult{Error: err.Error()}
	}
	defer res.Body.Close()

	result := HTTPProbeResult{
		StatusCode: res.StatusCode,
		Headers:    make(map[string]string),
	}

	for k, v := range res.Header {
		// Only take the first value for simplicity, or join them
		if len(v) > 0 {
			result.Headers[k] = v[0]
		}
	}

	// Attempt to extract title from body (read a limited amount)
	bodyBytes, err := ioutil.ReadAll(io.LimitReader(res.Body, 1024*10)) // Read up to 10KB
	if err == nil {
		title := extractTitle(string(bodyBytes))
		if title != "" {
			result.Title = title
		}
	}

	return result
}

// extractTitle parses HTML to find the <title> tag.
func extractTitle(htmlContent string) string {
	// Very basic regex-based title extraction. A full HTML parser would be more robust.
	// For production, consider using a library like `golang.org/x/net/html`.
	re := regexp.MustCompile(`(?i)<title>(.*?)</title>`)
	matches := re.FindStringSubmatch(htmlContent)
	if len(matches) > 1 {
		return matches[1]
	}
	return ""
}

