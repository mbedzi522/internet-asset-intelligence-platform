
import geoip2.database
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_geoip_db(db_path: str):
    try:
        return geoip2.database.Reader(db_path)
    except geoip2.errors.AddressNotFoundError:
        logging.warning(f"GeoIP database not found at {db_path}. GeoIP enrichment will be limited.")
        return None
    except Exception as e:
        logging.error(f"Error loading GeoIP database from {db_path}: {e}")
        return None

def enrich_ip(reader, ip_address: str) -> dict:
    if ip_address.startswith("127.") or ip_address.startswith("10.") or \
       ip_address.startswith("172.16.") or ip_address.startswith("192.168."):
        return {"country_name": "PRIVATE", "city_name": "PRIVATE", "location": None}

    if reader is None:
        return {"country_name": "UNKNOWN", "city_name": "UNKNOWN", "location": None}

    try:
        response = reader.city(ip_address)
        return {
            "country_name": response.country.name,
            "city_name": response.city.name,
            "location": {"lat": response.location.latitude, "lon": response.location.longitude}
        }
    except geoip2.errors.AddressNotFoundError:
        return {"country_name": "UNKNOWN", "city_name": "UNKNOWN", "location": None}
    except Exception as e:
        logging.error(f"Error enriching IP {ip_address}: {e}")
        return {"country_name": "ERROR", "city_name": "ERROR", "location": None}

