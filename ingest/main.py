
import os
import json
import base64
import time
import logging
from datetime import datetime, timezone

from minio import Minio
from minio.error import S3Error
from nacl.signing import VerifyKey
from nacl.exceptions import BadSignatureError
from opensearchpy import OpenSearch, helpers

from enrichment import geoip, tls_parser, cve_rules
from scoring import risk_scorer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class Config:
    def __init__(self):
        self.object_store_endpoint = os.getenv("OBJECT_STORE_ENDPOINT", "localhost:9000")
        self.object_store_access_key = os.getenv("OBJECT_STORE_ACCESS_KEY", "minioadmin")
        self.object_store_secret_key = os.getenv("OBJECT_STORE_SECRET_KEY", "minioadmin")
        self.object_store_bucket = os.getenv("OBJECT_STORE_BUCKET", "asset-events")
        self.public_keys_path = os.getenv("PUBLIC_KEYS_PATH", "./public_keys.json")
        self.opensearch_host = os.getenv("OPENSEARCH_HOST", "localhost")
        self.opensearch_port = int(os.getenv("OPENSEARCH_PORT", "9200"))
        self.opensearch_user = os.getenv("OPENSEARCH_USER", "admin")
        self.opensearch_password = os.getenv("OPENSEARCH_PASSWORD", "admin")
        self.opensearch_index_prefix = os.getenv("OPENSEARCH_INDEX_PREFIX", "asset-intelligence-")
        self.geoip_db_path = os.getenv("GEOIP_DB_PATH", "./GeoLite2-City.mmdb")
        self.cve_rules_path = os.getenv("CVE_RULES_PATH", "./cve_rules.yaml")
        self.archive_path = os.getenv("ARCHIVE_PATH", "./archive") # Local archive for canonical JSON

class Ingester:
    def __init__(self, config: Config):
        self.config = config
        self.minio_client = Minio(
            self.config.object_store_endpoint,
            access_key=self.config.object_store_access_key,
            secret_key=self.config.object_store_secret_key,
            secure=False # Use secure=True for production with TLS
        )
        self.opensearch_client = OpenSearch(
            hosts=[{'host': self.config.opensearch_host, 'port': self.config.opensearch_port}],
            http_auth=(self.config.opensearch_user, self.config.opensearch_password),
            use_ssl=True,
            verify_certs=False, # Set to True in production with proper CA certs
            ssl_assert_hostname=False,
            ssl_show_warn=False
        )
        self.public_keys = self._load_public_keys()
        self.geoip_reader = geoip.load_geoip_db(self.config.geoip_db_path)
        self.cve_engine = cve_rules.load_cve_rules(self.config.cve_rules_path)

        if not os.path.exists(self.config.archive_path):
            os.makedirs(self.config.archive_path)

    def _load_public_keys(self):
        # In a real scenario, this would load keys from Vault or a secure store
        # For now, a simple JSON file mapping collector_id to base64 encoded public key
        try:
            with open(self.config.public_keys_path, 'r') as f:
                keys_data = json.load(f)
                return {cid: VerifyKey(base64.b64decode(pk)) for cid, pk in keys_data.items()}
        except FileNotFoundError:
            logging.warning(f"Public keys file not found at {self.config.public_keys_path}. Signature verification will fail.")
            return {}
        except Exception as e:
            logging.error(f"Error loading public keys: {e}")
            return {}

    def _verify_signature(self, event_data: bytes, signature_b64: str, collector_id: str) -> bool:
        if collector_id not in self.public_keys:
            logging.error(f"No public key found for collector_id: {collector_id}")
            return False
        verify_key = self.public_keys[collector_id]
        signature = base64.b64decode(signature_b64)
        try:
            verify_key.verify(event_data, signature)
            return True
        except BadSignatureError:
            logging.error(f"Bad signature for event from collector_id: {collector_id}")
            return False
        except Exception as e:
            logging.error(f"Error during signature verification: {e}")
            return False

    def _enrich_event(self, event: dict) -> dict:
        # GeoIP Enrichment
        event["enrichment"] = {}
        if "target" in event and "ip" in event["target"]:
            event["enrichment"]["geoip"] = geoip.enrich_ip(self.geoip_reader, event["target"]["ip"])

        # TLS Certificate Parsing
        if "probes" in event and "tls" in event["probes"] and "cert_der_b64" in event["probes"]["tls"]:
            cert_der_b64 = event["probes"]["tls"]["cert_der_b64"]
            if cert_der_b64:
                try:
                    event["enrichment"]["tls_cert"] = tls_parser.parse_certificate(cert_der_b64)
                except Exception as e:
                    logging.warning(f"Failed to parse TLS certificate: {e}")

        # CVE Rule Engine
        if "probes" in event:
            event["enrichment"]["cve_matches"] = cve_rules.match_cves(self.cve_engine, event["probes"])

        return event

    def _compute_risk_score(self, event: dict) -> dict:
        # Placeholder for actual risk scoring logic
        # This would use the `risk_scorer` module
        event["risk_score"] = risk_scorer.calculate_risk(event)
        event["risk_breakdown"] = risk_scorer.get_risk_breakdown(event)
        return event

    def _deduplicate(self, event: dict) -> bool:
        # Simple deduplication placeholder: check if event with same ID already processed
        # In a real system, this would involve checking OpenSearch or a dedicated cache
        return False # For now, always process

    def _write_to_opensearch(self, doc: dict):
        # OpenSearch index name based on timestamp or a fixed prefix
        index_name = self.config.opensearch_index_prefix + datetime.now(timezone.utc).strftime("%Y-%m")
        try:
            # Create index with ILM policy if it doesn't exist (simplified)
            if not self.opensearch_client.indices.exists(index=index_name):
                logging.info(f"Creating index {index_name}")
                self.opensearch_client.indices.create(index=index_name, body=self._get_index_mapping())

            self.opensearch_client.index(index=index_name, id=doc["id"], body=doc, refresh=True)
            logging.info(f"Indexed document {doc['id']} to OpenSearch index {index_name}")
        except Exception as e:
            logging.error(f"Failed to write to OpenSearch: {e}")

    def _get_index_mapping(self):
        # This should be loaded from a file (e.g., opensearch_mapping.json) in a real setup
        return {
            "settings": {
                "index": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                }
            },
            "mappings": {
                "properties": {
                    "id": {"type": "keyword"},
                    "timestamp": {"type": "date"},
                    "scanner_version": {"type": "keyword"},
                    "collector_id": {"type": "keyword"},
                    "target": {
                        "properties": {
                            "ip": {"type": "ip"},
                            "port": {"type": "integer"},
                            "protocol": {"type": "keyword"}
                        }
                    },
                    "enrichment": {
                        "properties": {
                            "geoip": {
                                "properties": {
                                    "country_name": {"type": "keyword"},
                                    "city_name": {"type": "keyword"},
                                    "location": {"type": "geo_point"}
                                }
                            },
                            "tls_cert": {"type": "object"},
                            "cve_matches": {"type": "nested"}
                        }
                    },
                    "risk_score": {"type": "integer"},
                    "risk_breakdown": {"type": "object"}
                }
            }
        }

    def _archive_canonical_json(self, event_id: str, canonical_json: bytes):
        file_path = os.path.join(self.config.archive_path, f"{event_id}.json")
        with open(file_path, "wb") as f:
            f.write(canonical_json)
        logging.info(f"Archived canonical JSON for {event_id} to {file_path}")

    def process_event_file(self, bucket_name: str, object_name: str):
        try:
            response = self.minio_client.get_object(bucket_name, object_name)
            event_payload = response.read()
            response.close()
            response.release_conn()

            # Assuming object_name is like 'event_UUID.json' or 'event_UUID.signed.json'
            # For now, let's assume we get event.json and event.json.sig separately
            # In a real system, we'd need a robust way to link them or have a single signed object.
            
            # For demonstration, let's assume object_name is the event JSON, and we need to fetch the .sig file
            if object_name.endswith('.json'):
                sig_object_name = object_name + '.sig'
                try:
                    sig_response = self.minio_client.get_object(bucket_name, sig_object_name)
                    signature_b64 = base64.b64encode(sig_response.read()).decode('utf-8')
                    sig_response.close()
                    sig_response.release_conn()
                except S3Error as e:
                    logging.error(f"Signature file {sig_object_name} not found for event {object_name}: {e}")
                    return
            else:
                logging.warning(f"Unexpected object name format: {object_name}. Skipping.")
                return

            event = json.loads(event_payload)
            event_id = event.get("id")
            collector_id = event.get("collector_id")

            if not event_id or not collector_id:
                logging.error(f"Event {object_name} missing 'id' or 'collector_id'. Skipping.")
                return

            if not self._verify_signature(event_payload, signature_b64, collector_id):
                logging.error(f"Signature verification failed for event {event_id}. Skipping.")
                return

            if self._deduplicate(event):
                logging.info(f"Event {event_id} already processed. Skipping.")
                return

            enriched_event = self._enrich_event(event)
            final_doc = self._compute_risk_score(enriched_event)

            self._write_to_opensearch(final_doc)
            self._archive_canonical_json(event_id, json.dumps(final_doc, sort_keys=True).encode('utf-8'))

            # After successful processing, you might want to delete the raw event and signature from MinIO
            # self.minio_client.remove_object(bucket_name, object_name)
            # self.minio_client.remove_object(bucket_name, sig_object_name)

        except S3Error as e:
            logging.error(f"S3 error processing {object_name}: {e}")
        except json.JSONDecodeError as e:
            logging.error(f"Invalid JSON in {object_name}: {e}")
        except Exception as e:
            logging.error(f"Unexpected error processing {object_name}: {e}", exc_info=True)

    def run_ingestion_loop(self):
        logging.info("Starting ingestion loop...")
        # This is a simplified polling loop. In production, use MinIO notifications or Kafka consumer.
        while True:
            try:
                objects = self.minio_client.list_objects(self.config.object_store_bucket, recursive=True)
                for obj in objects:
                    if obj.object_name.endswith(".json") and not obj.object_name.endswith(".json.sig"):
                        event_id = obj.object_name.replace("event_", "").replace(".json", "")
                        # Check if already archived (simple deduplication)
                        archived_file_path = os.path.join(self.config.archive_path, f"{event_id}.json")
                        if not os.path.exists(archived_file_path):
                            logging.info(f"Found new event object: {obj.object_name}")
                            self.process_event_file(self.config.object_store_bucket, obj.object_name)
                        else:
                            logging.info(f"Event {event_id} already archived. Skipping.")


            except S3Error as e:
                logging.error(f"MinIO connection error: {e}")
            except Exception as e:
                logging.error(f"Error in ingestion loop: {e}", exc_info=True)

            time.sleep(10) # Poll every 10 seconds

if __name__ == "__main__":
    config = Config()
    ingester = Ingester(config)
    ingester.run_ingestion_loop()

