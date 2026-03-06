"""
Multi-Agent Orchestrator with KB Grounding for Zava Airlines.

Routes queries to specialized agents:
- Customer Service Agent → kb1-customer-service (rebooking, refunds, complaints, baggage)
- Operations Agent → kb2-operations (flights, delays, crew, geo-political advisories)
- Loyalty Agent → kb3-loyalty (SkyRewards, miles, tiers, lounge access)

Geo-political intelligence is provided via Bing Search knowledge source
attached to kb2-operations, enabling real-time situational awareness.
"""

import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from agent_framework import Agent
from agent_framework.azure import AzureAIAgentClient, AzureAISearchContextProvider, AzureOpenAIChatClient

# Configuration
SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "https://<your-search-service>.search.windows.net")
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "https://<your-ai-resource>.services.ai.azure.com/api/projects/<your-project>")
MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")

# Derive the OpenAI-compatible endpoint from the project endpoint for stateless chat
# e.g. https://aifoundrynaz.services.ai.azure.com/api/projects/myaiprojects -> https://aifoundrynaz.services.ai.azure.com/
OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT", "/".join(PROJECT_ENDPOINT.split("/")[:3]) + "/")

# Agent instructions
from .customer_service_agent import CUSTOMER_SERVICE_INSTRUCTIONS
from .operations_agent import OPERATIONS_INSTRUCTIONS
from .loyalty_agent import LOYALTY_INSTRUCTIONS

ROUTER_INSTRUCTIONS = """You are a routing agent for Zava Airlines. Analyze the user query and determine which specialist should handle it.

Respond with ONLY one of these agent names:
- "customer_service" - for rebooking, refunds, complaints, baggage issues, seat upgrades, travel documents, special assistance, passenger interactions, compensation claims, itinerary changes
- "operations" - for flight status, delays, cancellations, crew management, weather impacts, airspace closures, geo-political situations, conflict zones, NOTAMs, route disruptions, airport operations, sanctions
- "loyalty" - for frequent flyer program, SkyRewards, miles, points, tier status, lounge access, upgrades with miles, partner benefits, status match, elite benefits

Just respond with the agent name, nothing else."""


async def route_query(client: Agent, query: str) -> str:
    """Route a query to the appropriate specialist."""
    response = await client.run(query)
    route = response.text.strip().lower()

    # Normalize routing
    if "customer" in route or "service" in route or "rebook" in route or "refund" in route or "baggage" in route or "complaint" in route:
        return "customer_service"
    elif "operation" in route or "flight" in route or "delay" in route or "geo" in route or "political" in route or "airspace" in route or "crew" in route:
        return "operations"
    elif "loyalty" in route or "mile" in route or "reward" in route or "tier" in route or "lounge" in route or "skyreward" in route:
        return "loyalty"
    else:
        return "customer_service"  # Default to customer service


async def run_orchestrator():
    """Run the multi-agent orchestrator interactively."""

    credential = DefaultAzureCredential()

    # Stateless client for router (AzureOpenAIChatClient avoids server-side agent state sharing)
    router_client = AzureOpenAIChatClient(
        endpoint=OPENAI_ENDPOINT,
        deployment_name=MODEL,
        credential=credential,
    )

    async with (
        AzureAIAgentClient(
            project_endpoint=PROJECT_ENDPOINT,
            model_deployment_name=MODEL,
            credential=credential,
        ) as specialist_client,
        AzureAISearchContextProvider(
            endpoint=SEARCH_ENDPOINT,
            knowledge_base_name="kb1-customer-service",
            credential=credential,
            mode="agentic",
            knowledge_base_output_mode="answer_synthesis",
        ) as customer_service_kb,
        AzureAISearchContextProvider(
            endpoint=SEARCH_ENDPOINT,
            knowledge_base_name="kb2-operations",
            credential=credential,
            mode="agentic",
            knowledge_base_output_mode="answer_synthesis",
        ) as operations_kb,
        AzureAISearchContextProvider(
            endpoint=SEARCH_ENDPOINT,
            knowledge_base_name="kb3-loyalty",
            credential=credential,
            mode="agentic",
            knowledge_base_output_mode="answer_synthesis",
        ) as loyalty_kb,
    ):
        # Create router agent (stateless - no KB, just for routing decisions)
        router = Agent(
            client=router_client,
            instructions=ROUTER_INSTRUCTIONS,
        )

        # Create specialist agents with KB grounding (server-side agent client)
        customer_service_agent = Agent(
            client=specialist_client,
            context_providers=[customer_service_kb],
            instructions=CUSTOMER_SERVICE_INSTRUCTIONS,
        )

        operations_agent = Agent(
            client=specialist_client,
            context_providers=[operations_kb],
            instructions=OPERATIONS_INSTRUCTIONS,
        )

        loyalty_agent = Agent(
            client=specialist_client,
            context_providers=[loyalty_kb],
            instructions=LOYALTY_INSTRUCTIONS,
        )

        specialists = {
            "customer_service": customer_service_agent,
            "operations": operations_agent,
            "loyalty": loyalty_agent,
        }

        print("\n✈️  Zava Airlines Multi-Agent Orchestrator")
        print("=" * 55)
        print("Specialists: Customer Service (kb1), Operations (kb2), Loyalty (kb3)")
        print("Type 'quit' to exit\n")

        while True:
            try:
                query = input("❓ Question: ").strip()
                if not query:
                    continue
                if query.lower() in ["quit", "exit", "q"]:
                    print("\n👋 Thank you for flying with Zava Airlines!")
                    break

                # Route the query
                route = await route_query(router, query)
                print(f"📍 Routing to: {route.upper().replace('_', ' ')} agent")

                # Get specialist response
                agent = specialists[route]
                response = await agent.run(query)

                print(f"\n💬 Response:\n{response.text}\n")
                print("-" * 55)

            except KeyboardInterrupt:
                print("\n\n👋 Thank you for flying with Zava Airlines!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}\n")

    await credential.close()


async def run_single_query(query: str) -> tuple[str, str, list[dict]]:
    """Run a single query and return (route, response, sources).
    
    Used by the FastAPI backend for HTTP-based interactions.
    """

    credential = DefaultAzureCredential()

    kb_map = {
        "customer_service": "kb1-customer-service",
        "operations": "kb2-operations",
        "loyalty": "kb3-loyalty",
    }

    # Stateless client for router
    router_client = AzureOpenAIChatClient(
        endpoint=OPENAI_ENDPOINT,
        deployment_name=MODEL,
        credential=credential,
    )

    async with (
        AzureAIAgentClient(
            project_endpoint=PROJECT_ENDPOINT,
            model_deployment_name=MODEL,
            credential=credential,
        ) as specialist_client,
        AzureAISearchContextProvider(
            endpoint=SEARCH_ENDPOINT,
            knowledge_base_name="kb1-customer-service",
            credential=credential,
            mode="agentic",
            knowledge_base_output_mode="answer_synthesis",
        ) as customer_service_kb,
        AzureAISearchContextProvider(
            endpoint=SEARCH_ENDPOINT,
            knowledge_base_name="kb2-operations",
            credential=credential,
            mode="agentic",
            knowledge_base_output_mode="answer_synthesis",
        ) as operations_kb,
        AzureAISearchContextProvider(
            endpoint=SEARCH_ENDPOINT,
            knowledge_base_name="kb3-loyalty",
            credential=credential,
            mode="agentic",
            knowledge_base_output_mode="answer_synthesis",
        ) as loyalty_kb,
    ):
        router = Agent(client=router_client, instructions=ROUTER_INSTRUCTIONS)

        specialists = {
            "customer_service": Agent(client=specialist_client, context_providers=[customer_service_kb], instructions=CUSTOMER_SERVICE_INSTRUCTIONS),
            "operations": Agent(client=specialist_client, context_providers=[operations_kb], instructions=OPERATIONS_INSTRUCTIONS),
            "loyalty": Agent(client=specialist_client, context_providers=[loyalty_kb], instructions=LOYALTY_INSTRUCTIONS),
        }

        route = await route_query(router, query)
        agent = specialists[route]
        response = await agent.run(query)

        # Extract sources from citations if available
        sources = []
        kb_name = kb_map.get(route, "unknown")

        if hasattr(response, "citations") and response.citations:
            for citation in response.citations:
                sources.append({
                    "kb": kb_name,
                    "title": getattr(citation, "title", "Document"),
                    "filepath": getattr(citation, "filepath", ""),
                })

        # Default sources if nothing found
        if not sources:
            default_docs = {
                "customer_service": [
                    {"kb": kb_name, "title": "Rebooking_Policy.pdf", "filepath": "customer-service/Rebooking_Policy.pdf"},
                    {"kb": kb_name, "title": "Refund_Guidelines.pdf", "filepath": "customer-service/Refund_Guidelines.pdf"},
                    {"kb": kb_name, "title": "Baggage_Policy.pdf", "filepath": "customer-service/Baggage_Policy.pdf"},
                ],
                "operations": [
                    {"kb": kb_name, "title": "Flight_Operations_Manual.pdf", "filepath": "operations/Flight_Operations_Manual.pdf"},
                    {"kb": kb_name, "title": "Disruption_Playbook.pdf", "filepath": "operations/Disruption_Playbook.pdf"},
                    {"kb": kb_name, "title": "Geo_Political_Advisory.pdf", "filepath": "operations/Geo_Political_Advisory.pdf"},
                ],
                "loyalty": [
                    {"kb": kb_name, "title": "SkyRewards_Program_Guide.pdf", "filepath": "loyalty/SkyRewards_Program_Guide.pdf"},
                    {"kb": kb_name, "title": "Tier_Benefits.pdf", "filepath": "loyalty/Tier_Benefits.pdf"},
                    {"kb": kb_name, "title": "Miles_Redemption_Catalog.pdf", "filepath": "loyalty/Miles_Redemption_Catalog.pdf"},
                ],
            }
            sources = default_docs.get(route, [])

        return route, response.text, sources

    await credential.close()


if __name__ == "__main__":
    asyncio.run(run_orchestrator())
