
import logging
from datetime import datetime, timezone

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def calculate_risk(event: dict) -> int:
    """Calculates a deterministic risk score (0-100) for an event."""
    score = 0
    breakdown = get_risk_breakdown(event)

    # Sum up component scores, potentially with weights
    for component, s in breakdown.items():
        score += s

    # Ensure score is within 0-100
    return min(100, max(0, score))

def get_risk_breakdown(event: dict) -> dict:
    """Computes explainable risk score components."""
    breakdown = {
        "port_score": 0,
        "service_score": 0,
        "vuln_score": 0,
        "cert_score": 0,
        "exposure_score": 0,
        "freshness_score": 0,
    }

    # Example scoring logic (to be expanded based on actual rules)

    # Port Score: Higher risk for commonly exploited ports
    target_port = event.get("target", {}).get("port")
    if target_port in [21, 22, 23, 80, 443, 3389]: # FTP, SSH, Telnet, HTTP, HTTPS, RDP
        breakdown["port_score"] += 5
    if target_port in [23]: # Telnet
        breakdown["port_score"] += 10

    # Service Score: Based on identified service banners/HTTP headers
    if "probes" in event:
        if "http" in event["probes"]:
            http_headers = event["probes"]["http"].get("headers", {})
            server_header = http_headers.get("Server", "").lower()
            if "nginx" in server_header or "apache" in server_header:
                breakdown["service_score"] += 2 # Common web servers

        if "ssh_banner" in event["probes"]:
            ssh_banner = event["probes"]["ssh_banner"].get("Banner", "").lower()
            if "openssh" not in ssh_banner:
                breakdown["service_score"] += 5 # Non-standard SSH

    # Vulnerability Score: Based on CVE matches
    if "enrichment" in event and "cve_matches" in event["enrichment"]:
        for cve in event["enrichment"]["cve_matches"]:
            severity = cve.get("severity", "UNKNOWN").upper()
            if severity == "CRITICAL":
                breakdown["vuln_score"] += 30
            elif severity == "HIGH":
                breakdown["vuln_score"] += 20
            elif severity == "MEDIUM":
                breakdown["vuln_score"] += 10
            elif severity == "LOW":
                breakdown["vuln_score"] += 5

    # Certificate Score: For TLS-enabled services
    if "enrichment" in event and "tls_cert" in event["enrichment"]:
        tls_cert = event["enrichment"]["tls_cert"]
        if tls_cert.get("self_signed"):
            breakdown["cert_score"] += 10
        if tls_cert.get("valid_to"):
            valid_to_dt = datetime.fromisoformat(tls_cert["valid_to"])
            if valid_to_dt < datetime.now(timezone.utc):
                breakdown["cert_score"] += 15 # Expired certificate

    # Exposure Score: Based on GeoIP (e.g., public vs. private IPs)
    if "enrichment" in event and "geoip" in event["enrichment"]:
        country = event["enrichment"]["geoip"].get("country_name")
        if country not in ["PRIVATE", "LOCALHOST", "UNKNOWN"]:
            breakdown["exposure_score"] += 5 # Publicly exposed

    # Freshness Score: How recently the data was collected (not yet implemented in collector)
    # For now, assume fresh data has no penalty

    return breakdown

