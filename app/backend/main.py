"""
Zava Airlines - FoundryIQ and Agent Framework Demo Backend

FastAPI wrapper around the multi-agent orchestrator for airline customer interactions.
Provides chat, agent listing, and health check endpoints.
"""

import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    agent: str | None = None


class ChatResponse(BaseModel):
    message: str
    agent: str
    sources: list[dict] = []


class HealthResponse(BaseModel):
    status: str
    version: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler."""
    print("✈️  Starting Zava Airlines Agent Framework Demo...")
    yield
    print("Shutting down Zava Airlines agents...")


app = FastAPI(
    title="Zava Airlines - FoundryIQ Agent Framework Demo",
    description="Multi-agent orchestration for airline customer service, operations, and loyalty using Microsoft Agent Framework",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", response_model=HealthResponse)
async def health():
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Chat with the Zava Airlines multi-agent system.
    Uses the orchestrator to route queries to Customer Service, Operations, or Loyalty agents.
    """
    try:
        # Lazy import to avoid startup hang
        from agents.orchestrator import run_single_query

        route, response_text, sources = await run_single_query(request.message)

        return ChatResponse(
            message=response_text,
            agent=f"{route}-agent",
            sources=sources,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/agents")
async def list_agents():
    """List available agents with their metadata."""
    return {
        "agents": [
            {
                "id": "orchestrator",
                "name": "Orchestrator",
                "description": "Routes passenger requests to specialized agents based on query content and intent",
                "color": "#1E40AF",
            },
            {
                "id": "customer_service",
                "name": "Customer Service Agent",
                "description": "Handles rebooking, refunds, complaints, baggage issues, seat upgrades, and passenger interactions",
                "kb": "kb1-customer-service",
                "color": "#7C3AED",
            },
            {
                "id": "operations",
                "name": "Operations Agent",
                "description": "Manages flight ops, delays, disruptions, crew scheduling, and geo-political situation awareness",
                "kb": "kb2-operations",
                "color": "#DC2626",
            },
            {
                "id": "loyalty",
                "name": "Loyalty Agent",
                "description": "Handles SkyRewards program, miles, tier status, lounge access, and partner benefits",
                "kb": "kb3-loyalty",
                "color": "#D97706",
            },
        ]
    }


@app.get("/knowledge-bases")
async def list_knowledge_bases():
    """List FoundryIQ knowledge bases configured for Zava Airlines."""
    return {
        "knowledge_bases": [
            {
                "id": "kb1-customer-service",
                "name": "Customer Service KB",
                "description": "Rebooking policies, refund guidelines, baggage rules, compensation procedures",
                "knowledge_sources": ["ks-cs-aisearch", "ks-cs-web", "ks-cs-sharepoint"],
            },
            {
                "id": "kb2-operations",
                "name": "Operations KB",
                "description": "Flight ops manual, disruption playbook, geo-political advisory, NOTAM data",
                "knowledge_sources": ["ks-ops-aisearch", "ks-ops-web", "ks-geopolitical-bing"],
            },
            {
                "id": "kb3-loyalty",
                "name": "Loyalty KB",
                "description": "SkyRewards program guide, tier benefits, miles catalog, partner agreements",
                "knowledge_sources": ["ks-loyalty-aisearch", "ks-loyalty-web"],
            },
        ]
    }


# Mount static files (built frontend)
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/", StaticFiles(directory=static_dir, html=True), name="static")
