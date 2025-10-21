
#!/bin/bash

set -euo pipefail

DEV_KEY_PATH="./collector/dev_signer.key"
PUBLIC_KEYS_JSON="./ingest/public_keys.json"
COLLECTOR_ID="collector-001"

# Check if private key exists
if [ ! -f "$DEV_KEY_PATH" ]; then
  echo "Error: Private key not found at $DEV_KEY_PATH. Please run the collector once to generate it."
  exit 1
fi

# Extract public key from private key (Ed25519 private key contains public key)
# The first 32 bytes of an Ed25519 private key are the public key.
PUBLIC_KEY_BYTES=$(head -c 32 "$DEV_KEY_PATH" | base64)

# Create public_keys.json for the ingest service
cat << EOF > "$PUBLIC_KEYS_JSON"
{
  "$COLLECTOR_ID": "$PUBLIC_KEY_BYTES"
}
EOF

echo "Generated public key for $COLLECTOR_ID and saved to $PUBLIC_KEYS_JSON"

