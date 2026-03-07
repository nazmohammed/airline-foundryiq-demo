# Zava Airlines — Architecture & Sequence Diagrams

## 1. High-Level System Architecture

```mermaid
graph TB
    subgraph Frontend["🖥️ Frontend (React + Vite)"]
        UI[Chat UI<br/>React + TypeScript]
    end

    subgraph Backend["⚙️ Backend (FastAPI)"]
        API[FastAPI Server<br/>POST /chat · GET /health · GET /agents]
    end

    subgraph Orchestrator["🧠 Orchestrator Layer"]
        Router["Router Agent<br/><i>AzureOpenAIChatClient</i><br/>(stateless)"]
        CS["Customer Service Agent<br/><i>AzureAIAgentClient</i><br/>(stateful, KB-grounded)"]
        OPS["Operations Agent<br/><i>AzureAIAgentClient</i><br/>(stateful, KB-grounded)"]
        LOY["Loyalty Agent<br/><i>AzureAIAgentClient</i><br/>(stateful, KB-grounded)"]
    end

    subgraph FoundryIQ["🔍 Azure AI Foundry + FoundryIQ"]
        KB1["kb1-customer-service<br/>ks-cs-aisearch"]
        KB2["kb2-operations<br/>ks-ops-aisearch<br/>ks-geopolitical-bing"]
        KB3["kb3-loyalty<br/>ks-loyalty-aisearch"]
    end

    subgraph AzureSearch["📊 Azure AI Search"]
        IDX1["index-customer-service"]
        IDX2["index-operations"]
        IDX3["index-loyalty"]
    end

    subgraph Models["🤖 Azure OpenAI"]
        GPT["gpt-4.1"]
        EMB["text-embedding-3-large<br/>(3072 dims)"]
    end

    subgraph Auth["🔐 Authentication"]
        RBAC["DefaultAzureCredential<br/>RBAC (no API keys)"]
    end

    UI -->|HTTP POST /chat| API
    API -->|run_single_query| Router
    Router -->|route decision| CS
    Router -->|route decision| OPS
    Router -->|route decision| LOY

    CS -->|AzureAISearchContextProvider| KB1
    OPS -->|AzureAISearchContextProvider| KB2
    LOY -->|AzureAISearchContextProvider| KB3

    KB1 -->|agentic retrieval| IDX1
    KB2 -->|agentic retrieval| IDX2
    KB2 -->|Bing Search| BING["🌐 Bing Search API"]
    KB3 -->|agentic retrieval| IDX3

    IDX1 -->|vector + semantic| EMB
    IDX2 -->|vector + semantic| EMB
    IDX3 -->|vector + semantic| EMB

    CS -->|inference| GPT
    OPS -->|inference| GPT
    LOY -->|inference| GPT
    Router -->|inference| GPT

    RBAC -.->|authenticates| Router
    RBAC -.->|authenticates| CS
    RBAC -.->|authenticates| OPS
    RBAC -.->|authenticates| LOY

    style Router fill:#1E40AF,color:#fff
    style CS fill:#7C3AED,color:#fff
    style OPS fill:#DC2626,color:#fff
    style LOY fill:#D97706,color:#fff
    style KB1 fill:#059669,color:#fff
    style KB2 fill:#059669,color:#fff
    style KB3 fill:#059669,color:#fff
```

---

## 2. Agent Framework SDK — Class Relationship

```mermaid
classDiagram
    class Agent {
        +client: ChatClient
        +instructions: str
        +context_providers: list
        +run(query: str) AgentResponse
    }

    class AzureOpenAIChatClient {
        +endpoint: str
        +deployment_name: str
        +credential: TokenCredential
        <<stateless>>
    }

    class AzureAIAgentClient {
        +project_endpoint: str
        +model_deployment_name: str
        +credential: TokenCredential
        <<stateful / server-side>>
    }

    class AzureAISearchContextProvider {
        +endpoint: str
        +knowledge_base_name: str
        +credential: TokenCredential
        +mode: str = "agentic"
        +knowledge_base_output_mode: str
    }

    class AgentResponse {
        +text: str
        +citations: list
    }

    class DefaultAzureCredential {
        <<RBAC authentication>>
    }

    Agent --> AzureOpenAIChatClient : "Router uses (stateless)"
    Agent --> AzureAIAgentClient : "Specialists use (stateful)"
    Agent --> AzureAISearchContextProvider : "context_providers[]"
    Agent ..> AgentResponse : "returns"
    AzureOpenAIChatClient --> DefaultAzureCredential : "credential"
    AzureAIAgentClient --> DefaultAzureCredential : "credential"
    AzureAISearchContextProvider --> DefaultAzureCredential : "credential"

    note for AzureOpenAIChatClient "Used by Router Agent only.\nNo server-side state.\nPrevents state contamination\nbetween agents."

    note for AzureAIAgentClient "Used by all 3 specialist agents.\nShares server-side state.\nSupports KB grounding via\ncontext_providers."
```

---

## 3. Query Routing — Sequence Diagram

Shows the complete flow from user input to grounded response.

```mermaid
sequenceDiagram
    actor Passenger
    participant UI as React Frontend
    participant API as FastAPI Backend
    participant Router as Router Agent<br/>(AzureOpenAIChatClient)
    participant GPT as gpt-4.1
    participant Specialist as Specialist Agent<br/>(AzureAIAgentClient)
    participant KB as FoundryIQ<br/>Knowledge Base
    participant Search as Azure AI Search
    participant Bing as Bing Search API

    Passenger->>UI: "I need to rebook my London-Dubai<br/>flight due to a travel advisory"
    UI->>API: POST /chat {message: "..."}

    Note over API: run_single_query()

    API->>Router: route_query(query)
    Router->>GPT: Analyze intent<br/>(stateless call)
    GPT-->>Router: "customer_service"
    Router-->>API: route = "customer_service"

    Note over API: Select specialist agent<br/>based on route

    API->>Specialist: agent.run(query)

    Note over Specialist: AzureAISearchContextProvider<br/>triggers agentic retrieval

    Specialist->>KB: kb1-customer-service<br/>(agentic mode)
    KB->>Search: Vector + Semantic search<br/>index-customer-service
    Search-->>KB: Matching documents<br/>(rebooking policy, refund guidelines)
    KB-->>Specialist: Grounded context +<br/>answer_synthesis

    Specialist->>GPT: Generate response with<br/>KB context + instructions
    GPT-->>Specialist: Grounded response<br/>with citations

    Specialist-->>API: AgentResponse(text, citations)
    API-->>UI: {message: "...", agent: "customer_service-agent", sources: [...]}
    UI-->>Passenger: Display response with<br/>agent badge + source citations
```

---

## 4. Geo-Political Query — Sequence Diagram (Operations Agent + Bing Search)

```mermaid
sequenceDiagram
    actor Passenger
    participant API as FastAPI Backend
    participant Router as Router Agent<br/>(Stateless)
    participant GPT as gpt-4.1
    participant OpsAgent as Operations Agent<br/>(Stateful)
    participant KB2 as kb2-operations
    participant Search as Azure AI Search<br/>index-operations
    participant Bing as Bing Search API<br/>(ks-geopolitical-bing)

    Passenger->>API: "What is the geo-political situation<br/>with Iran? When will Zava Airlines<br/>resume operations from Dubai?"

    API->>Router: route_query(query)
    Router->>GPT: Analyze intent
    GPT-->>Router: "operations"

    API->>OpsAgent: agent.run(query)

    Note over OpsAgent,KB2: AzureAISearchContextProvider<br/>mode="agentic"

    OpsAgent->>KB2: Agentic retrieval request

    par Parallel Knowledge Source Retrieval
        KB2->>Search: Search index-operations<br/>(vector + semantic)
        Search-->>KB2: Disruption playbook,<br/>geo-political advisory docs
    and
        KB2->>Bing: Real-time Bing search<br/>"Iran airspace situation 2026"
        Bing-->>KB2: Latest news, sanctions,<br/>airspace closure updates
    end

    KB2-->>OpsAgent: Synthesized context<br/>(indexed docs + live Bing results)

    OpsAgent->>GPT: Generate response with<br/>combined context
    GPT-->>OpsAgent: "The situation is assessed as<br/>AMBER... Red Sea corridor at<br/>AMBER... alternative routings via<br/>Turkiyegazi corridor..."

    OpsAgent-->>API: AgentResponse with citations
    API-->>Passenger: Grounded response with<br/>real-time intelligence
```

---

## 5. Stateless Router vs Stateful Specialists — Why It Matters

```mermaid
graph LR
    subgraph Problem["❌ Problem: Shared State Contamination"]
        direction TB
        P_Client["AzureAIAgentClient<br/>(single instance)"]
        P_Router["Router Agent"]
        P_CS["Customer Service Agent"]
        P_OPS["Operations Agent"]
        P_State["☠️ Server-side State<br/>(shared across ALL agents)"]

        P_Client --> P_Router
        P_Client --> P_CS
        P_Client --> P_OPS
        P_Router -.->|contaminates| P_State
        P_CS -.->|contaminates| P_State
        P_OPS -.->|contaminates| P_State
    end

    subgraph Solution["✅ Solution: Separate Client Types"]
        direction TB
        S_Stateless["AzureOpenAIChatClient<br/>(stateless)"]
        S_Stateful["AzureAIAgentClient<br/>(stateful)"]
        S_Router["Router Agent<br/>(no state needed)"]
        S_CS["Customer Service Agent"]
        S_OPS["Operations Agent"]
        S_LOY["Loyalty Agent"]

        S_Stateless --> S_Router
        S_Stateful --> S_CS
        S_Stateful --> S_OPS
        S_Stateful --> S_LOY
    end

    style Problem fill:#FEE2E2,stroke:#DC2626
    style Solution fill:#D1FAE5,stroke:#059669
    style P_State fill:#DC2626,color:#fff
    style S_Stateless fill:#1E40AF,color:#fff
    style S_Stateful fill:#7C3AED,color:#fff
```

---

## 6. Data Flow — Index Creation & Knowledge Base Setup

```mermaid
flowchart TD
    subgraph DataPrep["📁 Data Preparation (scripts/setup_all.py)"]
        RAW["Sample Documents<br/>(JSON)"]
        EMB_STEP["Generate Embeddings<br/>text-embedding-3-large<br/>(3072 dims)"]
        UPLOAD["Upload to Azure AI Search"]
    end

    subgraph Indexes["📊 Azure AI Search Indexes"]
        IDX1["index-customer-service<br/>5 docs · HNSW vector · semantic config"]
        IDX2["index-operations<br/>5 docs · HNSW vector · semantic config"]
        IDX3["index-loyalty<br/>5 docs · HNSW vector · semantic config"]
    end

    subgraph KBSetup["🔧 FoundryIQ Portal (Manual)"]
        KS1["Knowledge Source<br/>ks-cs-aisearch"]
        KS2A["Knowledge Source<br/>ks-ops-aisearch"]
        KS2B["Knowledge Source<br/>ks-geopolitical-bing"]
        KS3["Knowledge Source<br/>ks-loyalty-aisearch"]

        KB1["KB: kb1-customer-service<br/>gpt-4.1 · medium effort"]
        KB2["KB: kb2-operations<br/>gpt-4.1 · high effort"]
        KB3["KB: kb3-loyalty<br/>gpt-4.1 · medium effort"]
    end

    RAW --> EMB_STEP --> UPLOAD
    UPLOAD --> IDX1
    UPLOAD --> IDX2
    UPLOAD --> IDX3

    IDX1 -.->|linked via| KS1
    IDX2 -.->|linked via| KS2A
    KS2B -.->|Bing connector| KB2
    IDX3 -.->|linked via| KS3

    KS1 --> KB1
    KS2A --> KB2
    KS2B --> KB2
    KS3 --> KB3

    style KB1 fill:#7C3AED,color:#fff
    style KB2 fill:#DC2626,color:#fff
    style KB3 fill:#D97706,color:#fff
```

---

## 7. Authentication & RBAC Flow

```mermaid
sequenceDiagram
    participant App as Zava Airlines App
    participant DAC as DefaultAzureCredential
    participant Entra as Microsoft Entra ID
    participant AOAI as Azure OpenAI<br/>(gpt-4.1)
    participant AIS as Azure AI Search
    participant Foundry as Azure AI Foundry

    App->>DAC: Request token
    DAC->>Entra: az login identity<br/>(CLI / Managed Identity)
    Entra-->>DAC: OAuth2 token

    Note over DAC: Token used for ALL services<br/>(no API keys anywhere)

    par Parallel Auth
        DAC->>AOAI: Token (Cognitive Services OpenAI User)
        DAC->>AIS: Token (Search Index Data Reader)
        DAC->>Foundry: Token (Cognitive Services User)
    end

    AOAI-->>App: ✅ Authorized
    AIS-->>App: ✅ Authorized
    Foundry-->>App: ✅ Authorized

    Note over App: Required RBAC Roles:<br/>• Cognitive Services OpenAI User<br/>• Cognitive Services User<br/>• Search Index Data Reader
```

---

## 8. Deployment Architecture (Azure Container Apps)

```mermaid
graph TB
    subgraph Azure["☁️ Azure Cloud"]
        subgraph RG["Resource Group"]
            subgraph ACA["Azure Container Apps"]
                FE["Frontend Container<br/>React (built static)"]
                BE["Backend Container<br/>FastAPI + Uvicorn"]
            end

            subgraph AI["Azure AI Services"]
                Foundry["Azure AI Foundry<br/>gpt-4.1 deployment"]
                Search["Azure AI Search<br/>3 indexes + semantic config"]
                FoundryIQ["FoundryIQ<br/>3 Knowledge Bases"]
            end

            subgraph Infra["Infrastructure"]
                MI["Managed Identity<br/>DefaultAzureCredential"]
                KV["Key Vault<br/>(optional secrets)"]
            end
        end

        subgraph Bicep["Infrastructure as Code"]
            MAIN["infra/main.bicep"]
            MOD1["modules/container-app.bicep"]
            MOD2["modules/identity.bicep"]
            MOD3["modules/openai.bicep"]
            MOD4["modules/search.bicep"]
            MOD5["modules/storage.bicep"]
        end
    end

    FE -->|proxy| BE
    BE -->|RBAC| Foundry
    BE -->|RBAC| Search
    BE -->|RBAC| FoundryIQ
    MI -.->|authenticates| BE

    MAIN --> MOD1
    MAIN --> MOD2
    MAIN --> MOD3
    MAIN --> MOD4
    MAIN --> MOD5

    style ACA fill:#1E40AF,color:#fff
    style AI fill:#059669,color:#fff
    style Bicep fill:#D97706,color:#fff
```
