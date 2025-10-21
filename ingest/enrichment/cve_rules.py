"""
CVE Rule Engine: Matches banner or server header regex against known CVEs.
"""
import yaml
import re
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_cve_rules(rules_path: str) -> list:
    """Loads CVE rules from a YAML file."""
    try:
        with open(rules_path, 'r') as f:
            rules = yaml.safe_load(f)
        logging.info(f"Loaded {len(rules)} CVE rules from {rules_path}")
        return rules
    except FileNotFoundError:
        logging.warning(f"CVE rules file not found at {rules_path}. CVE enrichment will be limited.")
        return []
    except Exception as e:
        logging.error(f"Error loading CVE rules from {rules_path}: {e}")
        return []

def match_cves(cve_rules: list, probes: dict) -> list:
    """Matches probe outputs against loaded CVE rules.

    Args:
        cve_rules: List of CVE rules.
        probes: Dictionary of probe results (e.g., from collector).

    Returns:
        A list of matched CVEs with their details.
    """
    matched_cves = []

    # Example: Match against HTTP server headers
    if 'http' in probes and 'headers' in probes['http']:
        server_header = probes['http'].get('headers', {}).get('Server', '')
        if server_header:
            for rule in cve_rules:
                if 'server_regex' in rule:
                    try:
                        if re.search(rule['server_regex'], server_header, re.IGNORECASE):
                            matched_cves.append({
                                'cve_id': rule.get('cve_id', 'UNKNOWN'),
                                'severity': rule.get('severity', 'UNKNOWN'),
                                'description': rule.get('description', 'No description provided.'),
                                'matched_on': 'http_server_header',
                                'matched_value': server_header
                            })
                    except re.error as e:
                        logging.warning(f"Invalid regex in CVE rule '{rule.get('cve_id', 'N/A')}': {e}")

    # Example: Match against SSH banner
    if 'ssh_banner' in probes and 'Banner' in probes['ssh_banner']:
        ssh_banner = probes['ssh_banner'].get('Banner', '')
        if ssh_banner:
            for rule in cve_rules:
                if 'ssh_banner_regex' in rule:
                    try:
                        if re.search(rule['ssh_banner_regex'], ssh_banner, re.IGNORECASE):
                            matched_cves.append({
                                'cve_id': rule.get('cve_id', 'UNKNOWN'),
                                'severity': rule.get('severity', 'UNKNOWN'),
                                'description': rule.get('description', 'No description provided.'),
                                'matched_on': 'ssh_banner',
                                'matched_value': ssh_banner
                            })
                    except re.error as e:
                        logging.warning(f"Invalid regex in CVE rule '{rule.get('cve_id', 'N/A')}': {e}")

    # Add more matching logic for other probe types as needed

    return matched_cves

