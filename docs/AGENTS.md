# Agent Architecture - Zava Airlines

## Overview

The Zava Airlines demo uses a **multi-agent orchestration** pattern built on the Microsoft Agent Framework SDK. A central **Orchestrator** agent classifies passenger intent and routes requests to one of three specialist agents, each backed by a dedicated FoundryIQ Knowledge Base.

## Agent Definitions

### Orchestrator

| Property | Value |
|----------|-------|
| Name | `zava-airlines-router` |
| Model | `gpt-4.1` |
| Role | Intent classification & routing |
| Knowledge Bases | None (delegates to specialists) |

**Routing logic:**
1. Parse the incoming passenger query
2. Classify intent into one of: `customer_service`, `operations`, `loyalty`
3. Forward message to the appropriate specialist agent
4. Return the specialist's grounded response to the caller

### Customer Service Agent

| Property | Value |
|----------|-------|
| Name | `zava-customer-service` |
| Model | `gpt-4.1` |
| Knowledge Base | `kb1-customer-service` |
| Retrieval Mode | Agentic |
| Inference Effort | Medium |

**Capabilities:**
- Flight rebooking and schedule changes
- Refund processing (EU261, DOT regulations)
- Baggage claims and lost luggage
- Seat upgrades and special requests
- Special assistance (wheelchair, medical, unaccompanied minors)
- Geo-political disruption rebooking policies

### Operations Agent

| Property | Value |
|----------|-------|
| Name | `zava-operations` |
| Model | `gpt-4.1` |
| Knowledge Base | `kb2-operations` |
| Retrieval Mode | Agentic |
| Inference Effort | High |

**Capabilities:**
- Flight scheduling and delay management
- Weather disruption response
- Crew management and duty-hour compliance
- Airspace advisory and NOTAM analysis
- **Geo-political intelligence** (Bing Search real-time data)
- Route network optimization (LHR, DXB, SIN hubs)

**Special Feature:** The Operations KB includes the `ks-geopolitical-bing` knowledge source, a Bing Search integration that provides real-time geo-political awareness for conflict zones, airspace closures, sanctions, and travel bans.

### Loyalty Agent

| Property | Value |
|----------|-------|
| Name | `zava-loyalty` |
| Model | `gpt-4.1` |
| Knowledge Base | `kb3-loyalty` |
| Retrieval Mode | Agentic |
| Inference Effort | Medium |

**Capabilities:**
- SkyRewards program information
- Tier status and benefits (Blue → Silver → Gold → Platinum → Diamond)
- Miles earning and redemption
- Partner airline rewards
- Lounge access eligibility
- Status match promotions

## FoundryIQ Knowledge Sources

| Knowledge Source | Type | Attached To | Purpose |
|-----------------|------|-------------|---------|
| `ks-cs-aisearch` | Azure AI Search | kb1-customer-service | Customer service index |
| `ks-cs-web` | Web | kb1-customer-service | Zava Airlines customer portal |
| `ks-cs-sharepoint` | SharePoint | kb1-customer-service | Internal CS knowledge |
| `ks-ops-aisearch` | Azure AI Search | kb2-operations | Operations index |
| `ks-ops-web` | Web | kb2-operations | Zava Airlines ops portal |
| `ks-geopolitical-bing` | **Bing Search** | kb2-operations | **Real-time geo-political intel** |
| `ks-loyalty-aisearch` | Azure AI Search | kb3-loyalty | Loyalty index |
| `ks-loyalty-web` | Web | kb3-loyalty | SkyRewards portal |

## Message Flow

```
Passenger ──► FastAPI /chat ──► Orchestrator ──┬──► Customer Service Agent ──► kb1 ──► Response
                                               ├──► Operations Agent ──► kb2 (+ Bing) ──► Response
                                               └──► Loyalty Agent ──► kb3 ──► Response
```

## Error Handling

Each agent follows a fallback pattern:
1. Attempt FoundryIQ agentic retrieval
2. If context_provider yields no results, use agent's built-in instructions
3. Orchestrator applies default document fallback for empty responses
4. All errors logged and returned with appropriate HTTP status codes
