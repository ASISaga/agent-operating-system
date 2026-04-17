"""Retrieve AZURE_CLIENT_ID from Key Vault.

Environment variables (required):
  KV_URL        – Key Vault URL, e.g. https://kv-name.vault.azure.net
  SECRET_NAME   – Secret name, e.g. clientid-mcp-subconscious-dev

Outputs:
  Prints the secret value to stdout on success.
  Prints nothing to stdout (warning to stderr) when the secret is not found.
  Exits with code 0 in both cases so the caller can fall back gracefully.
  Exits with code 1 only for unrecoverable configuration errors.
"""

from __future__ import annotations

import os
import sys


def main() -> None:
    kv_url = os.environ.get("KV_URL", "").strip()
    secret_name = os.environ.get("SECRET_NAME", "").strip()

    if not kv_url:
        print("::error::KV_URL environment variable is not set", file=sys.stderr)
        sys.exit(1)
    if not secret_name:
        print("::error::SECRET_NAME environment variable is not set", file=sys.stderr)
        sys.exit(1)

    # Log only the vault hostname (not the full URL) to avoid leaking path details.
    try:
        from urllib.parse import urlparse
        vault_host = urlparse(kv_url).netloc or kv_url
    except Exception:
        vault_host = "(Key Vault)"
    print(f"Connecting to Key Vault host: {vault_host}", file=sys.stderr)
    print(f"Retrieving secret: {secret_name}", file=sys.stderr)

    try:
        from azure.identity import DefaultAzureCredential
        from azure.keyvault.secrets import SecretClient

        cred = DefaultAzureCredential()
        client = SecretClient(vault_url=kv_url, credential=cred)
        secret = client.get_secret(secret_name)
        print("Secret retrieved successfully", file=sys.stderr)
        # Print the secret value to stdout so the caller can capture it.
        # This is intentional — the value is subsequently stored in GITHUB_OUTPUT
        # (masked by GitHub Actions) and never written to the workflow log.
        sys.stdout.write(secret.value)
    except Exception as exc:
        # Log only the exception type, not the message, to avoid leaking any
        # credential details that may appear in the Azure SDK error response.
        print(
            f"Warning: could not retrieve secret '{secret_name}' from Key Vault"
            f" ({type(exc).__name__}) — caller will fall back to GitHub secret",
            file=sys.stderr,
        )
        # Exit 0 so the caller falls back to the GitHub environment secret.
        sys.exit(0)


if __name__ == "__main__":
    main()
