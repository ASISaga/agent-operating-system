"""Resolve the Azure Function App name by scanning the resource group.

Environment variables (required):
  AZURE_SUBSCRIPTION_ID   – Azure subscription ID
  RESOURCE_GROUP          – Azure resource group name
  PREFIX                  – Function App name prefix to match

Outputs:
  Prints the matching Function App name to stdout on success.
  Exits with code 1 when no matching app is found.
  Exits with code 2 on unexpected Azure API errors.
"""

from __future__ import annotations

import os
import sys


def main() -> None:
    sub_id = os.environ.get("AZURE_SUBSCRIPTION_ID", "").strip()
    rg = os.environ.get("RESOURCE_GROUP", "").strip()
    prefix = os.environ.get("PREFIX", "").strip()

    # Collect all missing variables before exiting for better debugging.
    missing = [name for value, name in [(sub_id, "AZURE_SUBSCRIPTION_ID"), (rg, "RESOURCE_GROUP"), (prefix, "PREFIX")] if not value]
    if missing:
        for name in missing:
            print(f"::error::{name} environment variable is not set", file=sys.stderr)
        sys.exit(2)

    print(f"Listing Function Apps in resource group '{rg}'...", file=sys.stderr)
    print(f"Looking for apps with prefix '{prefix}'", file=sys.stderr)

    try:
        from azure.identity import DefaultAzureCredential
        from azure.mgmt.web import WebSiteManagementClient

        cred = DefaultAzureCredential()
        client = WebSiteManagementClient(cred, sub_id)
        apps = list(client.web_apps.list_by_resource_group(rg))

        print(f"Found {len(apps)} app(s) in resource group:", file=sys.stderr)
        for app in apps:
            app_name = app.name or ""
            print(f"  {app_name}", file=sys.stderr)
            if app_name.startswith(prefix):
                print(f"Matched: {app_name}", file=sys.stderr)
                print(app_name)
                sys.exit(0)

        print(
            f"::error::No Function App with prefix '{prefix}' found in '{rg}'",
            file=sys.stderr,
        )
        sys.exit(1)

    except Exception as exc:
        print(
            f"::error::Error listing Function Apps in '{rg}': {exc}",
            file=sys.stderr,
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
