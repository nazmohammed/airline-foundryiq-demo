# Zava Airlines - FoundryIQ and Agent Framework Demo

A multi-agent orchestration demo for the airline industry using **Microsoft Agent Framework SDK** and **Azure AI Foundry** with **FoundryIQ Knowledge Bases** for grounded retrieval, including real-time geo-political intelligence via **Bing Search**.

## Features

- **Multi-Agent Orchestration**: Intelligent routing of passenger queries to specialized agents (Customer Service, Operations, Loyalty)
- **Microsoft Agent Framework SDK**: Built on the official `agent-framework` Python SDK
- **FoundryIQ Knowledge Bases**: Agentic retrieval mode with gpt-4.1 for grounded responses
- **Bing Search Geo-Political Intel**: Real-time geo-political situation awareness for flight operations (airspace closures, conflict zones, travel bans)
- **RBAC-Only Authentication**: No API keys - uses `DefaultAzureCredential` for all services
- **Fully Automated Deployment**: Infrastructure as Code with Bicep + setup scripts

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Passenger Query                                     │
│          "I need to rebook my London-Dubai flight due to a travel advisory"   │
└─────────────────────────────────┬────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         ORCHESTRATOR AGENT                                    │
│                                                                               │
│   • Analyzes passenger intent                                                 │
│   • Routes to appropriate specialist agent                                    │
│   • Returns grounded response with citations                                  │
└───────────┬─────────────────────┬─────────────────────┬──────────────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│ CUSTOMER SERVICE  │  │  OPERATIONS       │  │  LOYALTY          │
│ AGENT             │  │  AGENT            │  │  AGENT            │
│                   │  │                   │  │                   │
│ kb1-customer-     │  │ kb2-operations    │  │ kb3-loyalty       │
│ service           │  │                   │  │                   │
│ • Rebooking       │  │ • Flight ops      │  │ • SkyRewards      │
│ • Refunds         │  │ • Disruptions     │  │ • Miles/Tiers     │
│ • Baggage         │  │ • Geo-political   │  │ • Lounge access   │
│ • Complaints      │  │ • Crew mgmt       │  │ • Partner rewards │
└─────────┬─────────┘  └─────────┬─────────┘  └─────────┬─────────┘
          │                      │                      │
          ▼                      ▼                      ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                         MICROSOFT FOUNDRY                                     │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                    FOUNDRYIQ KNOWLEDGE BASES                            │  │
│  │  ┌──────────────────┐  ┌──────────────┐  ┌──────────────┐             │  │
│  │  │ kb1-customer-    │  │kb2-operations│  │ kb3-loyalty  │             │  │
│  │  │ service (gpt-4.1)│  │  (gpt-4.1)   │  │  (gpt-4.1)  │             │  │
│  │  └────────┬─────────┘  └──────┬───────┘  └──────┬───────┘             │  │
│  │           ▼                   ▼                  ▼                     │  │
│  │  ┌───────────────────────────────────────────────────────────────┐     │  │
│  │  │                    KNOWLEDGE SOURCES                           │     │  │
│  │  │  Customer Svc: ks-cs-aisearch, ks-cs-web, ks-cs-sharepoint   │     │  │
│  │  │  Operations:   ks-ops-aisearch, ks-ops-web,                   │     │  │
│  │  │                ks-geopolitical-bing (Bing Search)              │     │  │
│  │  │  Loyalty:      ks-loyalty-aisearch, ks-loyalty-web            │     │  │
│  │  └───────────────────────────────────────────────────────────────┘     │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

## Prerequisites

- Azure subscription with Owner or Contributor + User Access Administrator
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli)
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [Python 3.11+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/) (for frontend)

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/nazmohammed/airline-foundryiq-demo.git
cd airline-foundryiq-demo

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements-dev.txt
```

### 2. Deploy Infrastructure

```bash
az login && azd auth login
azd up
```

### 3. Setup FoundryIQ Resources

```bash
./scripts/setup_indexes.sh
./scripts/upload_sample_data.sh
./scripts/setup_knowledge_sources.sh
./scripts/setup_knowledge_bases.sh
```

### 4. Configure Search RBAC (Manual)

In Azure Portal: Search service → Keys → Set to **"Both"** (API keys + RBAC)

### 5. Test the Orchestrator

```bash
python app/backend/agents/orchestrator.py
```

Try these queries:
- "I need to rebook my London to Dubai flight due to a travel advisory"
- "What is the current geo-political impact on our Eastern European routes?"
- "How many miles do I need to upgrade to Gold tier?"

### 6. Run the Web App

```bash
# Backend
cd app/backend && uvicorn main:app --reload

# Frontend (separate terminal)
cd app/frontend && npm install && npm run dev
```

## Project Structure

```
├── app/backend/agents/
│   ├── orchestrator.py              # Routes queries to specialists
│   ├── customer_service_agent.py    # Customer Service → kb1-customer-service
│   ├── operations_agent.py          # Operations → kb2-operations
│   └── loyalty_agent.py             # Loyalty → kb3-loyalty
├── app/backend/main.py              # FastAPI application
├── app/frontend/                    # React TypeScript frontend
├── infra/                           # Bicep IaC templates
├── scripts/                         # Setup and deployment scripts
├── data/                            # Sample airline documents
├── tests/                           # Test suite
└── docs/                            # Documentation
```

## Knowledge Base Mapping

| Agent | Knowledge Base | Content | Geo-Political |
|-------|----------------|---------|---------------|
| Customer Service | kb1-customer-service | Rebooking, refunds, baggage, complaints | Via Operations escalation |
| Operations | kb2-operations | Flight ops, disruptions, crew, NOTAMs | **Bing Search real-time intel** |
| Loyalty | kb3-loyalty | SkyRewards, miles, tiers, lounge access | N/A |

## Geo-Political Intelligence

The Operations agent is augmented with **Bing Search** via the `ks-geopolitical-bing` knowledge source, providing real-time awareness of:

- ✈️ Airspace closures and NOTAM alerts
- 🌍 Conflict zone routing restrictions
- 🚫 Government sanctions affecting flight operations
- ⚠️ Travel ban advisories
- 🌋 Natural disasters and volcanic activity
- 📡 Breaking geo-political developments

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_SEARCH_ENDPOINT` | `https://srch-zava-airlines.search.windows.net` | Search service |
| `AZURE_AI_PROJECT_ENDPOINT` | `https://foundry-zava-airlines.services.ai.azure.com/...` | Foundry project |
| `AZURE_OPENAI_DEPLOYMENT` | `gpt-4.1` | Model deployment |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| 403 Forbidden | Portal → Search → Keys → "Both" |
| Generic responses | Ensure context_provider passed to ChatAgent |
| KB errors | Run `./scripts/setup_rbac.sh` |
| Geo-political data stale | Verify ks-geopolitical-bing knowledge source is active |

## License

MIT License
