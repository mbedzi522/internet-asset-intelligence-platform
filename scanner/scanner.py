#!/usr/bin/env python3
"""
Automated Internet Scanner - Continuous IP scanning service
Scans the entire IPv4 space, detects services, and submits events directly to OpenSearch
"""

import asyncio
import socket
import random
import ipaddress
import json
import struct
import time
import os
from datetime import datetime
from typing import List, Dict, Optional
import logging
import aiohttp

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class InternetScanner:
    """Automated scanner that continuously scans the internet like Shodan"""

    # Common ports to scan (Shodan scans these frequently)
    COMMON_PORTS = [
        21,    # FTP
        22,    # SSH
        23,    # Telnet
        25,    # SMTP
        80,    # HTTP
        110,   # POP3
        143,   # IMAP
        443,   # HTTPS
        445,   # SMB
        3306,  # MySQL
        3389,  # RDP
        5432,  # PostgreSQL
        5900,  # VNC
        6379,  # Redis
        8080,  # HTTP Alt
        8443,  # HTTPS Alt
        27017, # MongoDB
        9200,  # Elasticsearch
        9300,  # Elasticsearch
    ]

    # Private IP ranges to skip
    PRIVATE_RANGES = [
        ipaddress.ip_network('10.0.0.0/8'),
        ipaddress.ip_network('172.16.0.0/12'),
        ipaddress.ip_network('192.168.0.0/16'),
        ipaddress.ip_network('127.0.0.0/8'),
        ipaddress.ip_network('169.254.0.0/16'),
    ]

    def __init__(self, scan_rate: int = 1000, timeout: float = 2.0, opensearch_url: str = None):
        """
        Initialize the scanner

        Args:
            scan_rate: Number of IPs to scan per second
            timeout: Socket connection timeout in seconds
            opensearch_url: OpenSearch endpoint URL
        """
        self.scan_rate = scan_rate
        self.timeout = timeout
        self.opensearch_url = opensearch_url or 'http://opensearch:9200'
        self.session = None
        self.stats = {
            'scanned': 0,
            'open_ports': 0,
            'services_detected': 0,
            'start_time': time.time()
        }

    def is_private_ip(self, ip: str) -> bool:
        """Check if IP is in private range"""
        try:
            ip_obj = ipaddress.ip_address(ip)
            return any(ip_obj in network for network in self.PRIVATE_RANGES)
        except ValueError:
            return True

    def generate_random_ip(self) -> str:
        """Generate a random public IPv4 address"""
        while True:
            # Generate random IP
            ip = socket.inet_ntoa(struct.pack('>I', random.randint(1, 0xffffffff)))

            # Skip private IPs
            if not self.is_private_ip(ip):
                return ip

    async def scan_port(self, ip: str, port: int) -> Optional[Dict]:
        """
        Scan a single port on an IP

        Returns:
            Dict with scan results if port is open, None otherwise
        """
        try:
            # Create socket with timeout
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)

            # Try to connect
            result = sock.connect_ex((ip, port))

            if result == 0:
                # Port is open, try to grab banner
                banner = await self.grab_banner(sock, port)
                sock.close()

                self.stats['open_ports'] += 1

                return {
                    'ip': ip,
                    'port': port,
                    'state': 'open',
                    'banner': banner,
                    'timestamp': datetime.utcnow().isoformat() + 'Z'
                }
            else:
                sock.close()
                return None

        except (socket.timeout, socket.error, OSError):
            return None

    async def grab_banner(self, sock: socket.socket, port: int) -> Optional[str]:
        """
        Attempt to grab service banner

        Args:
            sock: Connected socket
            port: Port number

        Returns:
            Banner string or None
        """
        try:
            # Set socket to non-blocking for banner grab
            sock.setblocking(False)

            # Send appropriate probe based on port
            if port == 80 or port == 8080:
                sock.send(b'GET / HTTP/1.0\r\n\r\n')
            elif port == 22:
                pass  # SSH sends banner automatically
            elif port == 21:
                pass  # FTP sends banner automatically
            elif port == 25:
                pass  # SMTP sends banner automatically

            # Try to receive banner (non-blocking)
            await asyncio.sleep(0.5)  # Wait a bit for response
            banner = sock.recv(1024)

            if banner:
                self.stats['services_detected'] += 1
                return banner.decode('utf-8', errors='ignore').strip()[:500]

        except (socket.timeout, socket.error, BlockingIOError, OSError):
            pass

        return None

    def create_asset_event(self, scan_result: Dict) -> Dict:
        """
        Create an asset event in the format expected by the collector/ingest pipeline

        Args:
            scan_result: Scan result dictionary

        Returns:
            Asset event dictionary
        """
        event = {
            'event_type': 'asset_discovered',
            'timestamp': scan_result['timestamp'],
            'collector_id': 'internet_scanner_001',
            'asset': {
                'ip_address': scan_result['ip'],
                'ports': [
                    {
                        'port': scan_result['port'],
                        'protocol': 'tcp',
                        'state': 'open',
                        'service': self.detect_service(scan_result['port'], scan_result.get('banner')),
                        'banner': scan_result.get('banner', '')
                    }
                ],
                'first_seen': scan_result['timestamp'],
                'last_seen': scan_result['timestamp']
            },
            'metadata': {
                'scanner_version': '1.0.0',
                'scan_type': 'internet_wide'
            }
        }

        return event

    def detect_service(self, port: int, banner: Optional[str]) -> str:
        """
        Detect service name from port and banner

        Args:
            port: Port number
            banner: Service banner (if available)

        Returns:
            Service name
        """
        # Port-based detection
        port_services = {
            21: 'ftp',
            22: 'ssh',
            23: 'telnet',
            25: 'smtp',
            80: 'http',
            110: 'pop3',
            143: 'imap',
            443: 'https',
            445: 'smb',
            3306: 'mysql',
            3389: 'rdp',
            5432: 'postgresql',
            5900: 'vnc',
            6379: 'redis',
            8080: 'http-proxy',
            8443: 'https-alt',
            27017: 'mongodb',
            9200: 'elasticsearch',
            9300: 'elasticsearch',
        }

        service = port_services.get(port, f'unknown-{port}')

        # Banner-based refinement
        if banner:
            banner_lower = banner.lower()
            if 'apache' in banner_lower:
                service = 'apache-httpd'
            elif 'nginx' in banner_lower:
                service = 'nginx'
            elif 'openssh' in banner_lower:
                service = 'openssh'
            elif 'mysql' in banner_lower:
                service = 'mysql'
            elif 'postgresql' in banner_lower:
                service = 'postgresql'
            elif 'redis' in banner_lower:
                service = 'redis'
            elif 'mongodb' in banner_lower:
                service = 'mongodb'
            elif 'elasticsearch' in banner_lower:
                service = 'elasticsearch'

        return service

    async def save_event(self, event: Dict):
        """
        Save event directly to OpenSearch

        Args:
            event: Asset event dictionary
        """
        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            # Index name with date for easier management
            date_str = datetime.utcnow().strftime('%Y.%m.%d')
            index_name = f'assets-{date_str}'

            # Create document for OpenSearch
            doc = {
                'timestamp': event['timestamp'],
                'ip_address': event['asset']['ip_address'],
                'ports': event['asset']['ports'],
                'first_seen': event['asset']['first_seen'],
                'last_seen': event['asset']['last_seen'],
                'scanner_id': event['collector_id'],
                'event_type': event['event_type'],
                'metadata': event.get('metadata', {})
            }

            # Post to OpenSearch
            url = f"{self.opensearch_url}/{index_name}/_doc"
            async with self.session.post(url, json=doc, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status in [200, 201]:
                    logger.debug(f"Saved to OpenSearch: {event['asset']['ip_address']}")
                else:
                    text = await resp.text()
                    logger.error(f"Failed to save to OpenSearch: {resp.status} - {text}")

        except Exception as e:
            logger.error(f"Failed to save event: {e}")

    async def scan_ip(self, ip: str):
        """
        Scan all common ports on a single IP

        Args:
            ip: IP address to scan
        """
        self.stats['scanned'] += 1

        # Scan all common ports concurrently
        tasks = [self.scan_port(ip, port) for port in self.COMMON_PORTS]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        for result in results:
            if result and isinstance(result, dict):
                # Create and save asset event
                event = self.create_asset_event(result)
                await self.save_event(event)

                logger.info(f"Found open port: {result['ip']}:{result['port']} - {self.detect_service(result['port'], result.get('banner'))}")

    async def print_stats(self):
        """Periodically print scanning statistics"""
        while True:
            await asyncio.sleep(60)  # Print stats every minute

            elapsed = time.time() - self.stats['start_time']
            rate = self.stats['scanned'] / elapsed if elapsed > 0 else 0

            logger.info(
                f"Stats - Scanned: {self.stats['scanned']} IPs | "
                f"Open Ports: {self.stats['open_ports']} | "
                f"Services: {self.stats['services_detected']} | "
                f"Rate: {rate:.2f} IPs/sec"
            )

    async def run(self):
        """
        Main scanning loop - continuously scans random IPs
        """
        logger.info("Starting Internet Scanner...")
        logger.info(f"Scan rate: {self.scan_rate} IPs/second")
        logger.info(f"Timeout: {self.timeout} seconds")
        logger.info(f"Scanning ports: {self.COMMON_PORTS}")

        # Start stats printer
        asyncio.create_task(self.print_stats())

        # Calculate delay between scans to achieve target rate
        delay = 1.0 / self.scan_rate

        while True:
            try:
                # Generate random IP
                ip = self.generate_random_ip()

                # Scan the IP
                asyncio.create_task(self.scan_ip(ip))

                # Rate limiting
                await asyncio.sleep(delay)

            except KeyboardInterrupt:
                logger.info("Shutting down scanner...")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(1)


async def main():
    """Main entry point"""
    # Configuration from environment variables
    scan_rate = int(os.getenv('SCAN_RATE', '100'))  # IPs per second
    timeout = float(os.getenv('SCAN_TIMEOUT', '2.0'))  # Connection timeout
    opensearch_host = os.getenv('OPENSEARCH_HOST', 'opensearch')
    opensearch_port = os.getenv('OPENSEARCH_PORT', '9200')
    opensearch_url = f'http://{opensearch_host}:{opensearch_port}'

    # Create and run scanner
    scanner = InternetScanner(scan_rate=scan_rate, timeout=timeout, opensearch_url=opensearch_url)

    try:
        await scanner.run()
    finally:
        # Cleanup
        if scanner.session:
            await scanner.session.close()


if __name__ == '__main__':
    asyncio.run(main())
