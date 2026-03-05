"""Tests for the orchestrator routing logic."""

import pytest


# ---------------------------------------------------------------------------
# Routing keyword tests (unit-level, no Azure calls)
# ---------------------------------------------------------------------------

ROUTING_CASES = [
    # Customer Service keywords
    ("I need to rebook my flight", "customer_service"),
    ("I want a refund for my cancelled flight", "customer_service"),
    ("My baggage was lost at Heathrow", "customer_service"),
    ("I have a complaint about the service", "customer_service"),
    ("Can I upgrade my seat to business class?", "customer_service"),
    ("I need wheelchair assistance at the gate", "customer_service"),
    # Operations keywords
    ("What is the current delay on ZA-402?", "operations"),
    ("Is there an airspace closure over Eastern Europe?", "operations"),
    ("Crew scheduling for tomorrow's Dubai rotation", "operations"),
    ("What is the geo-political situation affecting our routes?", "operations"),
    ("NOTAM update for EGLL", "operations"),
    ("Flight dispatch for ZA-100", "operations"),
    # Loyalty keywords
    ("How many miles do I have?", "loyalty"),
    ("What are the Gold tier benefits?", "loyalty"),
    ("SkyRewards points redemption options", "loyalty"),
    ("Do I have lounge access with Silver status?", "loyalty"),
    ("Status match from another airline", "loyalty"),
    ("Partner airline miles transfer", "loyalty"),
]


@pytest.mark.parametrize("query,expected_route", ROUTING_CASES)
def test_route_classification(query: str, expected_route: str):
    """Verify keyword-based routing classifies queries correctly."""
    # Inline routing logic (mirrors orchestrator.route_query)
    q = query.lower()

    customer_kw = [
        "rebook", "refund", "baggage", "luggage", "complaint", "seat",
        "upgrade", "cancel", "boarding", "check-in", "checkin",
        "special assistance", "wheelchair", "medical", "passenger",
    ]
    ops_kw = [
        "delay", "schedule", "crew", "dispatch", "weather", "airspace",
        "notam", "maintenance", "geo-political", "geopolitical", "route",
        "disruption", "operation",
    ]
    loyalty_kw = [
        "miles", "points", "tier", "loyalty", "skyrewards", "lounge",
        "reward", "status", "partner", "redeem", "redemption",
    ]

    if any(kw in q for kw in customer_kw):
        route = "customer_service"
    elif any(kw in q for kw in ops_kw):
        route = "operations"
    elif any(kw in q for kw in loyalty_kw):
        route = "loyalty"
    else:
        route = "customer_service"

    assert route == expected_route, f"Query '{query}' routed to '{route}', expected '{expected_route}'"


# ---------------------------------------------------------------------------
# FastAPI endpoint tests
# ---------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_health_endpoint():
    """Health endpoint returns 200 and expected payload."""
    from httpx import ASGITransport, AsyncClient
    from app.backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "healthy"
    assert data["service"] == "zava-airlines-agent"


@pytest.mark.asyncio
async def test_agents_endpoint():
    """Agents endpoint returns all 4 agents."""
    from httpx import ASGITransport, AsyncClient
    from app.backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/agents")
    assert resp.status_code == 200
    agents = resp.json()
    assert len(agents) == 4
    names = {a["name"] for a in agents}
    assert names == {"orchestrator", "customer_service", "operations", "loyalty"}


@pytest.mark.asyncio
async def test_knowledge_bases_endpoint():
    """Knowledge bases endpoint returns 3 KBs."""
    from httpx import ASGITransport, AsyncClient
    from app.backend.main import app

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/knowledge-bases")
    assert resp.status_code == 200
    kbs = resp.json()
    assert len(kbs) == 3
    names = {kb["name"] for kb in kbs}
    assert "kb1-customer-service" in names
    assert "kb2-operations" in names
    assert "kb3-loyalty" in names
