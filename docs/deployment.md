# Deployment Guide - Zava Airlines FoundryIQ Demo

## Prerequisites

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Azure Subscription | - | Owner or Contributor + User Access Administrator |
| Azure CLI | 2.60+ | `az` commands |
| Azure Developer CLI | 1.5+ | `azd` orchestration |
| Python | 3.11+ | Backend and agents |
| Node.js | 18+ | Frontend build |

## Step-by-Step Deployment

### Step 1: Authenticate

```bash
az login
azd auth login
```

### Step 2: Copy Environment File

```bash
cp .env.sample .env
# Edit .env with your preferred location and resource name prefix
```

### Step 3: Deploy Infrastructure

**Option A: Full automated deployment**

```bash
chmod +x scripts/*.sh
./scripts/deploy.sh
```

This runs all steps: infrastructure → RBAC → indexes → sample data → knowledge sources → knowledge bases.

**Option B: Manual step-by-step**

```bash
# 1. Deploy Azure resources
azd up

# 2. Setup RBAC
./scripts/setup_rbac.sh

# 3. Create search indexes
./scripts/setup_indexes.sh

# 4. Upload sample documents
./scripts/upload_sample_data.sh

# 5. Create knowledge sources
./scripts/setup_knowledge_sources.sh

# 6. Create knowledge bases
./scripts/setup_knowledge_bases.sh
```

### Step 4: Enable Search API Keys (Portal)

After deployment, go to Azure Portal:
1. Navigate to your Azure AI Search service (`srch-zava-airlines`)
2. Settings → Keys
3. Change from "RBAC only" to **"Both"** (API keys + RBAC)

> This is required for the FoundryIQ knowledge sources to authenticate with Azure AI Search.

### Step 5: Verify Deployment

```bash
# Test health
curl http://localhost:8000/health

# Test orchestrator CLI
python app/backend/agents/orchestrator.py
```

## Infrastructure Resources

| Resource | SKU/Tier | Purpose |
|----------|----------|---------|
| Azure AI Search | Basic | Vector search indexes |
| Azure OpenAI (AIServices) | S0 | gpt-4.1 + embeddings |
| Storage Account | Standard LRS | Document storage |
| Container App | Consumption | Web application hosting |
| Container App Environment | Consumption | Container hosting |
| User-Assigned Managed Identity | - | RBAC authentication |

## RBAC Roles

| Role | Scope | Assigned To |
|------|-------|-------------|
| Search Index Data Contributor | Search Service | Current user, UAMI |
| Search Service Contributor | Search Service | Current user, UAMI |
| Cognitive Services OpenAI User | AIServices | Current user, UAMI |
| Storage Blob Data Contributor | Storage Account | Current user, UAMI |
| Azure AI Developer | AIServices | Current user, UAMI |
| Azure AI Inference Deployment Operator | AIServices | Current user, UAMI |

## Common Issues

### 403 on Knowledge Source Creation
**Solution:** Enable "Both" (API keys + RBAC) on the Search service.

### azd up Fails on OpenAI Quota
**Solution:** Change `location` in `infra/main.bicep` to a region with gpt-4.1 availability (e.g., `eastus2`, `swedencentral`).

### Bing Search Not Returning Results
**Solution:** Ensure the `ks-geopolitical-bing` knowledge source is correctly created and attached to `kb2-operations`.

### Container App 502 Error
**Solution:** Check Container App logs: `az containerapp logs show -n ca-zava-airlines -g rg-zava-airlines`
