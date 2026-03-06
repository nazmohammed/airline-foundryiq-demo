# Zava Airlines - FoundryIQ and Agent Framework Demo

A multi-agent orchestration demo for the airline industry using **Microsoft Agent Framework SDK** (`agent-framework 1.0.0rc3`) and **Azure AI Foundry** with **FoundryIQ Knowledge Bases** for grounded retrieval, including real-time geo-political intelligence via **Bing Search**.

## Features

- **Multi-Agent Orchestration**: Intelligent routing of passenger queries to specialized agents (Customer Service, Operations, Loyalty)
- **Microsoft Agent Framework SDK**: Built on `agent-framework` 1.0.0rc3 (`Agent`, `Message`, `AzureAIAgentClient`, `AzureOpenAIChatClient`)
- **FoundryIQ Knowledge Bases**: Agentic retrieval mode with gpt-4.1 for grounded responses via `AzureAISearchContextProvider`
- **Bing Search Geo-Political Intel**: Real-time geo-political situation awareness for flight operations (airspace closures, conflict zones, travel bans)
- **RBAC-Only Authentication**: No API keys in code — uses `DefaultAzureCredential` for all Azure services
- **Stateless Router / Stateful Specialists**: Router uses `AzureOpenAIChatClient` (stateless) to avoid server-side state contamination; specialists use `AzureAIAgentClient` (stateful, KB-grounded)
- **Fully Automated Deployment**: Infrastructure as Code with Bicep + setup scripts

## Demo

<p align="center">
  <video src="https://github.com/nazmohammed/airline-foundryiq-demo/raw/main/docs/demo-screenshot.mp4" controls autoplay muted loop width="100%">
    Your browser does not support the video tag. <a href="docs/demo-screenshot.mp4">Download the demo video</a>.
  </video>
</p>

> **Live test run**: A passenger asks to rebook a London–Dubai flight due to a travel advisory. The orchestrator routes to the **Customer Service** agent (rebooking policy) and the **Operations** agent (geo-political situation with Iran), each grounded by their respective FoundryIQ Knowledge Base with citations.

## Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                           Passenger Query                                     │
│          "I need to rebook my London-Dubai flight due to a travel advisory"   │
└─────────────────────────────────┬────────────────────────────────────────────┘
                                  │
                                  ▼
┌──────────────────────────────────────────────────────────────────────────────┐
│                    ORCHESTRATOR (Router Agent)                                 │
│                    AzureOpenAIChatClient (stateless)                           │
│                                                                               │
│   • Analyzes passenger intent                                                 │
│   • Routes to: customer_service | operations | loyalty                        │
│   • Returns grounded response with citations                                  │
└───────────┬─────────────────────┬─────────────────────┬──────────────────────┘
            │                     │                     │
            ▼                     ▼                     ▼
┌───────────────────┐  ┌───────────────────┐  ┌───────────────────┐
│ CUSTOMER SERVICE  │  │  OPERATIONS       │  │  LOYALTY          │
│ AGENT             │  │  AGENT            │  │  AGENT            │
│ AzureAIAgentClient│  │ AzureAIAgentClient│  │ AzureAIAgentClient│
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
│                 AZURE AI FOUNDRY + FOUNDRYIQ                                  │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                    FOUNDRYIQ KNOWLEDGE BASES                            │  │
│  │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐     │  │
│  │  │ kb1-customer-    │  │ kb2-operations   │  │ kb3-loyalty      │     │  │
│  │  │ service (gpt-4.1)│  │   (gpt-4.1)     │  │   (gpt-4.1)     │     │  │
│  │  └────────┬─────────┘  └──────┬───────────┘  └──────┬───────────┘     │  │
│  │           ▼                   ▼                     ▼                  │  │
│  │  ┌───────────────────────────────────────────────────────────────┐     │  │
│  │  │                    KNOWLEDGE SOURCES                           │     │  │
│  │  │  Customer Svc: ks-cs-aisearch (Azure AI Search)               │     │  │
│  │  │  Operations:   ks-ops-aisearch, ks-geopolitical-bing (Bing)   │     │  │
│  │  │  Loyalty:      ks-loyalty-aisearch (Azure AI Search)          │     │  │
│  │  └───────────────────────────────────────────────────────────────┘     │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  ┌────────────────────────────────────────────────────────────────────────┐  │
│  │                    AZURE AI SEARCH INDEXES                              │  │
│  │  index-customer-service │ index-operations │ index-loyalty              │  │
│  │  (HNSW vector, 3072 dims, text-embedding-3-large, semantic config)     │  │
│  └────────────────────────────────────────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────────────────────┘
```

---

## Prerequisites

- Azure subscription with **Owner** or **Contributor + User Access Administrator**
- [Azure CLI](https://learn.microsoft.com/cli/azure/install-azure-cli) (v2.60+)
- [Azure Developer CLI (azd)](https://learn.microsoft.com/azure/developer/azure-developer-cli/install-azd)
- [Python 3.11+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/) (for frontend)
- Azure AI Foundry project with **gpt-4.1** model deployed
- Azure AI Search service

---

## Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/nazmohammed/airline-foundryiq-demo.git
cd airline-foundryiq-demo

# Create virtual environment
python -m venv .venv
source .venv/bin/activate        # Linux/Mac
# .venv\Scripts\Activate.ps1     # Windows PowerShell

# Install dependencies (--pre required for agent-framework rc)
pip install --pre -r requirements-dev.txt
```

### 2. Assign RBAC Roles

The app uses `DefaultAzureCredential` (RBAC) — no API keys in code. Assign these roles to your user or service principal:

```bash
az login

# Get your user object ID
USER_OBJECT_ID=$(az ad signed-in-user show --query id -o tsv)
SUBSCRIPTION_ID="<your-subscription-id>"

# Required roles
az role assignment create --assignee $USER_OBJECT_ID \
  --role "Cognitive Services OpenAI User" \
  --scope /subscriptions/$SUBSCRIPTION_ID

az role assignment create --assignee $USER_OBJECT_ID \
  --role "Cognitive Services User" \
  --scope /subscriptions/$SUBSCRIPTION_ID

az role assignment create --assignee $USER_OBJECT_ID \
  --role "Search Index Data Reader" \
  --scope /subscriptions/$SUBSCRIPTION_ID
```

### 3. Load Sample Data into Azure AI Search

The `scripts/setup_all.py` script creates 3 search indexes with vector search (HNSW, 3072 dimensions for `text-embedding-3-large`) and semantic configuration, then uploads 15 sample airline policy documents (5 per index).

```bash
# You need your Azure AI Search admin key for index creation
# Find it in Azure Portal → Search service → Keys

python scripts/setup_all.py
```

When prompted, enter your **Azure AI Search admin API key**. The script will:

1. **Create 3 indexes** with vector search + semantic config:
   - `index-customer-service` — Rebooking, refund, baggage, complaint, and assistance policies
   - `index-operations` — Route network, airspace restrictions, geo-political disruptions, crew scheduling
   - `index-loyalty` — SkyRewards tiers, miles earning/redemption, lounge access, award chart

2. **Upload 15 sample documents** (5 per index) with categories, metadata, and vector-ready fields

3. **Verify** document counts per index

> **Note**: The script uses the Search REST API (`2024-11-01-preview`). Vector search profiles use the `algorithm` property (not `algorithmConfigurationName`) in this API version.

### 4. Create FoundryIQ Knowledge Bases (Portal)

Create 3 knowledge bases in the **Azure AI Foundry portal** → FoundryIQ section. See [Knowledge Base Configuration](#foundryiq-knowledge-base-configuration) below for complete settings.

### 5. Test the Orchestrator (CLI)

```bash
cd app/backend
python -m agents.orchestrator
```

Try these queries:
- "I need to rebook my London to Dubai flight due to a travel advisory"
- "What is the current geo-political impact on our Eastern European routes?"
- "How many miles do I need to upgrade from Silver to Gold tier?"

### 6. Run the Web App

```bash
# Backend (terminal 1)
cd app/backend
python -m uvicorn main:app --reload --port 8000

# Frontend (terminal 2)
cd app/frontend
npm install
npm run dev
```

Open **http://localhost:5173** to use the web UI.

---

## Project Structure

```
├── app/
│   ├── backend/
│   │   ├── main.py                          # FastAPI app (/health, /chat, /agents, /knowledge-bases)
│   │   └── agents/
│   │       ├── orchestrator.py              # Multi-agent router + specialist dispatch
│   │       ├── customer_service_agent.py    # Customer Service → kb1-customer-service
│   │       ├── operations_agent.py          # Operations → kb2-operations
│   │       └── loyalty_agent.py             # Loyalty → kb3-loyalty
│   └── frontend/                            # React + TypeScript + Vite
├── scripts/
│   └── setup_all.py                         # Creates indexes + uploads sample data
├── infra/                                   # Bicep IaC templates
├── data/                                    # Sample airline documents (reference)
├── tests/                                   # Test suite
└── docs/                                    # Documentation
```

---

## FoundryIQ Knowledge Base Configuration

All 3 knowledge bases are created in the **Azure AI Foundry portal** under the FoundryIQ section. Each KB connects to its corresponding Azure AI Search index via a knowledge source.

### KB1: Customer Service (`kb1-customer-service`)

| Setting | Value |
|---------|-------|
| **Name** | `kb1-customer-service` |
| **Description** | Customer service knowledge base for Zava Airlines — rebooking, refunds, complaints, baggage, and passenger assistance |
| **Model** | `gpt-4.1` |
| **Knowledge Source** | Azure AI Search → `index-customer-service` |
| **Retrieval Reasoning Effort** | `medium` |
| **Retrieval Instructions** | Search for airline customer service policies, rebooking procedures, refund guidelines, baggage rules, EU261/DOT compensation, seat upgrade policies, and special assistance requirements. |
| **Output Mode** | `answer_synthesis` |
| **Answer Instructions** | You are the Zava Airlines customer service assistant. Provide empathetic, policy-grounded answers. Always cite the specific Zava Airlines policy. Include rebooking options, refund timelines, compensation amounts, and next steps. If a geo-political disruption is mentioned, explain the free rebooking and refund options available under the Geo-Political Disruption Policy. |

### KB2: Operations (`kb2-operations`)

| Setting | Value |
|---------|-------|
| **Name** | `kb2-operations` |
| **Description** | Flight operations knowledge base for Zava Airlines — route network, airspace restrictions, geo-political disruptions, crew scheduling, and operational procedures |
| **Model** | `gpt-4.1` |
| **Knowledge Source** | Azure AI Search → `index-operations` + Bing Search → `ks-geopolitical-bing` |
| **Retrieval Reasoning Effort** | `medium` |
| **Retrieval Instructions** | Search for flight operations data including route networks, airspace restrictions, NOTAM alerts, geo-political conflict zones, crew scheduling rules, disruption management procedures, and alternate routing options. For geo-political queries, search for current airspace closures, sanctions, travel bans, and conflict zone overfly restrictions. |
| **Output Mode** | `answer_synthesis` |
| **Answer Instructions** | You are the Zava Airlines operations intelligence assistant. Provide factual, safety-first operational analysis. Use IATA airport codes. For geo-political queries, list affected airspace (with ICAO FIR codes if available), current restrictions, alternate routing options, and estimated impact on flight times and costs. Always prioritize safety and regulatory compliance. |

### KB3: Loyalty (`kb3-loyalty`)

| Setting | Value |
|---------|-------|
| **Name** | `kb3-loyalty` |
| **Description** | Loyalty program knowledge base for Zava Airlines SkyRewards — tier status, miles earning/redemption, lounge access, partner benefits, and elite member perks |
| **Model** | `gpt-4.1` |
| **Knowledge Source** | Azure AI Search → `index-loyalty` |
| **Retrieval Reasoning Effort** | `low` |
| **Retrieval Instructions** | Search for SkyRewards loyalty program details including tier qualification requirements (Blue, Silver, Gold, Platinum, Diamond), miles earning rates, redemption charts, lounge access rules, partner airline benefits, credit card partnerships, and elite member perks. |
| **Output Mode** | `answer_synthesis` |
| **Answer Instructions** | You are the Zava Airlines SkyRewards loyalty expert. Provide enthusiastic, precise answers about the loyalty program. Always cite exact mile amounts, tier thresholds, and qualification criteria. Include tier comparison details when relevant. Suggest strategies to maximize miles and achieve tier upgrades. |

---

## Agent Framework SDK Migration Notes

This project uses `agent-framework` **1.0.0rc3** (pre-release). If you're coming from an earlier version, the following breaking changes apply:

### API Changes (pre-rc → 1.0.0rc3)

| Before (old API) | After (1.0.0rc3) | Notes |
|---|---|---|
| `from agent_framework import ChatAgent` | `from agent_framework import Agent` | Class renamed |
| `from agent_framework import ChatMessage, Role` | `from agent_framework import Message` | Simplified message type |
| `ChatMessage(role=Role.USER, text=query)` | `Message("user", [query])` or pass `str` to `agent.run()` | Can pass string directly |
| `ChatAgent(chat_client=client, ...)` | `Agent(client=client, ...)` | Parameter renamed |
| `ChatAgent(context_provider=kb)` | `Agent(context_providers=[kb])` | Now a list |
| `response = await agent.run(messages)` | `response = await agent.run(query_string)` | Accepts string directly |

### Client Types

| Client | Class | Use Case |
|--------|-------|----------|
| **Stateful** (server-side agent) | `AzureAIAgentClient` | KB-grounded specialists — maintains conversation state on the server |
| **Stateless** (OpenAI-compatible) | `AzureOpenAIChatClient` | Router agent — no server-side state, avoids state contamination |

### State-Sharing Bug & Fix

> **Critical**: `AzureAIAgentClient` shares server-side conversation state between `Agent` instances created from the same client. If the router agent runs first and returns `"customer_service"`, the specialist agent receives that token in its context and echoes it back instead of querying the KB.

**Fix**: Use `AzureOpenAIChatClient` (stateless) for the router and `AzureAIAgentClient` only for KB-grounded specialists:

```python
from agent_framework import Agent
from agent_framework.azure import AzureAIAgentClient, AzureOpenAIChatClient, AzureAISearchContextProvider

# Stateless router — no KB, no server-side state leakage
router_client = AzureOpenAIChatClient(
    endpoint=OPENAI_ENDPOINT,       # e.g. https://<resource>.services.ai.azure.com/
    deployment_name=MODEL,           # e.g. gpt-4.1
    credential=credential,
)

# Stateful specialists — KB-grounded via AzureAISearchContextProvider
async with AzureAIAgentClient(
    project_endpoint=PROJECT_ENDPOINT,   # e.g. https://<resource>.services.ai.azure.com/api/projects/<project>
    model_deployment_name=MODEL,
    credential=credential,
) as specialist_client:

    router = Agent(client=router_client, instructions=ROUTER_INSTRUCTIONS)

    customer_svc = Agent(
        client=specialist_client,
        context_providers=[customer_service_kb],
        instructions=CUSTOMER_SERVICE_INSTRUCTIONS,
    )
```

### Required RBAC Roles

These Azure RBAC roles must be assigned to the identity running the app (user or managed identity):

| Role | Why |
|------|-----|
| **Cognitive Services OpenAI User** | Call gpt-4.1 model via Azure OpenAI / AI Foundry |
| **Cognitive Services User** | Access FoundryIQ knowledge bases and AI services |
| **Search Index Data Reader** | Query Azure AI Search indexes via context providers |

```bash
USER_OID=$(az ad signed-in-user show --query id -o tsv)
SUB="/subscriptions/<your-subscription-id>"

az role assignment create --assignee $USER_OID --role "Cognitive Services OpenAI User" --scope $SUB
az role assignment create --assignee $USER_OID --role "Cognitive Services User" --scope $SUB
az role assignment create --assignee $USER_OID --role "Search Index Data Reader" --scope $SUB
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AZURE_SEARCH_ENDPOINT` | — | Azure AI Search endpoint (e.g. `https://<name>.search.windows.net`) |
| `AZURE_AI_PROJECT_ENDPOINT` | — | AI Foundry project endpoint (e.g. `https://<resource>.services.ai.azure.com/api/projects/<project>`) |
| `AZURE_OPENAI_ENDPOINT` | *(auto-derived from project endpoint)* | OpenAI-compatible endpoint for stateless router |
| `AZURE_OPENAI_DEPLOYMENT` | `gpt-4.1` | Model deployment name |

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check — returns `{"status": "healthy", "version": "0.1.0"}` |
| `POST` | `/chat` | Send a query to the multi-agent orchestrator |
| `GET` | `/agents` | List available agents and metadata |
| `GET` | `/knowledge-bases` | List configured FoundryIQ knowledge bases |

### POST /chat

**Request:**
```json
{
  "message": "I need to rebook my London to Dubai flight due to a travel advisory"
}
```

**Response:**
```json
{
  "agent": "customer_service-agent",
  "message": "Based on Zava Airlines' Geo-Political Disruption Policy, you are eligible for free rebooking to the next available flight or a full refund...",
  "sources": [
    {"kb": "kb1-customer-service", "title": "Rebooking_Policy.pdf", "filepath": "customer-service/Rebooking_Policy.pdf"}
  ]
}
```

---

## Sample Queries

| Query | Routed To | KB |
|-------|-----------|-----|
| "I need to rebook my London to Dubai flight due to a travel advisory" | Customer Service | kb1-customer-service |
| "What airspace closures affect our Eastern European routes?" | Operations | kb2-operations |
| "How many miles to upgrade from Silver to Gold?" | Loyalty | kb3-loyalty |
| "What is the baggage allowance for Business class?" | Customer Service | kb1-customer-service |
| "What is the crew duty time limit for long-haul flights?" | Operations | kb2-operations |
| "How do I redeem miles for a hotel stay?" | Loyalty | kb3-loyalty |

---

## Geo-Political Intelligence

The Operations agent is augmented with **Bing Search** via the `ks-geopolitical-bing` knowledge source, providing real-time awareness of:

- Airspace closures and NOTAM alerts
- Conflict zone routing restrictions
- Government sanctions affecting flight operations
- Travel ban advisories
- Natural disasters and volcanic activity
- Breaking geo-political developments

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| `403 Forbidden` on /chat | Missing RBAC roles | Assign `Cognitive Services OpenAI User`, `Cognitive Services User`, `Search Index Data Reader` |
| `ImportError: ChatAgent` | Old agent-framework version | `pip install --pre agent-framework>=1.0.0rc3` |
| Specialist echoes routing token (e.g. returns "customer_service") | `AzureAIAgentClient` shares state between Agent instances | Use `AzureOpenAIChatClient` for router — see [State-Sharing Bug & Fix](#state-sharing-bug--fix) |
| `Port 8000 in use` | Ghost process from previous run | Find PID: `Get-NetTCPConnection -LocalPort 8000`, or use `--port 8001` |
| Empty/generic KB responses | Indexes have no data | Run `python scripts/setup_all.py` to create indexes and upload sample docs |
| `algorithmConfigurationName` error | Wrong vector search field name for API version | Use `algorithm` (not `algorithmConfigurationName`) with API `2024-11-01-preview` |
| Module not found: `agents.orchestrator` | Wrong working directory for uvicorn | Run from `app/backend/`: `cd app/backend && python -m uvicorn main:app --reload` |

---

## Azure Deployment

```bash
az login && azd auth login
azd up
```

This deploys the full stack (Container App + AI Search + AI Foundry + Storage) using the Bicep templates in `infra/`.

---

## License

MIT License
