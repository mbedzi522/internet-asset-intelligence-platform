
import base64
import logging
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa, ec

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def parse_certificate(cert_der_b64: str) -> dict:
    try:
        cert_der = base64.b64decode(cert_der_b64)
        cert = x509.load_der_x509_certificate(cert_der, default_backend())

        subject_cn = cert.subject.get_attributes_for_oid(x509.OID_COMMON_NAME)[0].value if cert.subject.get_attributes_for_oid(x509.OID_COMMON_NAME) else None
        issuer_cn = cert.issuer.get_attributes_for_oid(x509.OID_COMMON_NAME)[0].value if cert.issuer.get_attributes_for_oid(x509.OID_COMMON_NAME) else None

        sans = []
        try:
            alt_names = cert.extensions.get_extension_for_class(x509.SubjectAlternativeName)
            for name in alt_names.value:
                if isinstance(name, x509.DNSName):
                    sans.append(name.value)
                elif isinstance(name, x509.IPAddress):
                    sans.append(str(name.value))
        except x509.ExtensionNotFound:
            pass # No Subject Alternative Name extension

        key_algo = "Unknown"
        key_size = 0
        public_key = cert.public_key()
        if isinstance(public_key, rsa.RSAPublicKey):
            key_algo = "RSA"
            key_size = public_key.key_size
        elif isinstance(public_key, ec.EllipticCurvePublicKey):
            key_algo = "ECDSA"
            key_size = public_key.curve.key_size

        self_signed = (cert.issuer == cert.subject)

        return {
            "subject_cn": subject_cn,
            "subject_sans": sans,
            "issuer_cn": issuer_cn,
            "valid_from": cert.not_valid_before_utc.isoformat(),
            "valid_to": cert.not_valid_after_utc.isoformat(),
            "key_algo": key_algo,
            "key_size": key_size,
            "self_signed": self_signed,
            "cert_der_b64": cert_der_b64, # Keep original DER for archiving
        }
    except Exception as e:
        logging.error(f"Error parsing TLS certificate: {e}")
        return {"error": str(e)}

