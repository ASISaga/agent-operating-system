# Deploy Workflow — agent-operating-system

Deploys the [`ASISaga/agent-operating-system`](https://github.com/ASISaga/agent-operating-system)
Python Azure Function App to Azure using OIDC (passwordless) authentication.

**Deployment target:** Azure Function App `func-agent-operating-system-{env}-*`
(Flex Consumption plan, `FC1`)

---

## Quick Start

```bash
# Copy this workflow to the target repository
cp deploy.yml /path/to/agent-operating-system/.github/workflows/deploy.yml
```

Then complete the [one-time setup](#one-time-setup) below and push to `main`.

---

## How It Works

This is a thin caller (~30 lines) that delegates all deployment logic to the reusable
workflow in `ASISaga/aos-infrastructure`:

```
agent-operating-system  →  ASISaga/aos-infrastructure
.github/workflows/          .github/workflows/
deploy.yml (caller)         deploy-function-app.yml (reusable)
                            • Install Python deps
                            • OIDC login
                            • Discover func app name (prefix match)
                            • azure/functions-action@v1 deploy
```

A fix in `deploy-function-app.yml` automatically propagates to this repository on the
next run — no changes needed here.

---

## Prerequisites

Infrastructure must be provisioned first via `ASISaga/aos-infrastructure`
(`infrastructure-deploy.yml` workflow). The Bicep templates (Phases 1, 3, 4) create:

- The `func-agent-operating-system-{env}-*` Function App
- A User-Assigned Managed Identity for OIDC
- The OIDC Workload Identity Federation federated credential
- The Key Vault secret `clientid-agent-operating-system-{env}` (auto-stored after Phase 4)

---

## One-Time Setup

### 1. Retrieve `AZURE_CLIENT_ID`

After infrastructure provisioning, retrieve each environment's client ID from Key Vault:

```python
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

cred = DefaultAzureCredential()
client = SecretClient(vault_url="https://<kv-name>.vault.azure.net", credential=cred)
# Replace <env> with dev, staging, or prod
print(client.get_secret("clientid-agent-operating-system-<env>").value)
```

> **First run:** The `infra_provisioned` `repository_dispatch` event triggers this
> workflow automatically after Phase 4 succeeds and supplies the Key Vault URL in the
> payload — no manual retrieval needed on the initial deploy.

### 2. Create GitHub Environments

Go to **Settings → Environments** and create three environments:
`dev`, `staging`, `prod`.

For each environment, add these **secrets**:

| Secret | Value |
|---|---|
| `AZURE_CLIENT_ID` | Managed Identity client ID (from Key Vault above) |
| `AZURE_TENANT_ID` | Azure AD tenant ID |
| `AZURE_SUBSCRIPTION_ID` | Azure subscription ID |

Optionally add this **variable** (not sensitive):

| Variable | Default if omitted |
|---|---|
| `AZURE_RESOURCE_GROUP` | `rg-aos-{env}` |

### 3. Copy the workflow file

```bash
cp deploy.yml /path/to/agent-operating-system/.github/workflows/deploy.yml
```

---

## Triggers

| Event | Target Environment |
|---|---|
| Push to `main` | `dev` |
| GitHub Release published | `prod` |
| `workflow_dispatch` | Selected by user (`dev` / `staging` / `prod`) |
| `repository_dispatch` (`infra_provisioned`) | From infrastructure payload |

---

## Required Permissions

```yaml
permissions:
  id-token: write   # OIDC token exchange with Azure
  contents: read    # Repository checkout
```

---

## Function App Name Discovery

The Azure Function App name includes a unique 6-character suffix generated at provision
time (e.g. `func-agent-operating-system-dev-a1b2c3`). The reusable workflow discovers
the exact name at runtime using prefix matching — no hardcoded name needed.

---

## Full Setup Guide

For the complete setup guide, architecture diagrams, monitoring, and troubleshooting,
see [`deployment/workflow-templates/README.md`](https://github.com/ASISaga/aos-infrastructure/blob/main/deployment/workflow-templates/README.md)
in `ASISaga/aos-infrastructure`.
