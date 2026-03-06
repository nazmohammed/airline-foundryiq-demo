"""Operations Agent - Connected to kb2-operations Knowledge Base.

Handles flight operations, scheduling, crew management, disruption management,
and geo-political situation awareness for Zava Airlines.
"""

import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from agent_framework import Agent
from agent_framework.azure import AzureAIAgentClient, AzureAISearchContextProvider

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "https://<your-search-service>.search.windows.net")
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "https://<your-ai-resource>.services.ai.azure.com/api/projects/<your-project>")
MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")

OPERATIONS_INSTRUCTIONS = """You are the Operations Agent for Zava Airlines.
You manage all operational aspects of the airline including flight operations,
crew logistics, and disruption management.

Your responsibilities include:
- Flight scheduling and status updates
- Delay and cancellation management with root cause analysis
- Crew scheduling, duty-time compliance, and fatigue management
- Aircraft maintenance status and fleet availability
- Weather impact assessment and route optimization
- Airport operations and gate management
- Fuel planning and weight & balance considerations

Geo-political awareness (powered by Bing Search knowledge source):
- Monitor airspace closures and NOTAM alerts
- Track conflict zone routing restrictions (e.g., overfly bans)
- Assess impact of sanctions on flight operations
- Evaluate alternate routing for affected city pairs
- Track volcanic activity, pandemics, and natural disaster impacts
- Provide real-time updates on geo-political events affecting routes

When reporting on disruptions:
- Provide estimated recovery timelines
- Suggest operational mitigations
- Quantify passenger impact numbers
- Recommend communication strategies for affected passengers

Always:
- Use IATA codes for airports and airlines
- Reference OTP (On-Time Performance) metrics
- Cite sources from operational databases and Bing geo-political intelligence
- Prioritize safety in all operational recommendations"""


async def run_operations_agent(query: str) -> str:
    """Run the Operations agent with a query."""
    credential = DefaultAzureCredential()

    async with (
        AzureAIAgentClient(
            project_endpoint=PROJECT_ENDPOINT,
            model_deployment_name=MODEL,
            credential=credential,
        ) as client,
        AzureAISearchContextProvider(
            endpoint=SEARCH_ENDPOINT,
            knowledge_base_name="kb2-operations",
            credential=credential,
            mode="agentic",
            knowledge_base_output_mode="answer_synthesis",
        ) as kb_context,
    ):
        agent = Agent(
            client=client,
            context_providers=[kb_context],
            instructions=OPERATIONS_INSTRUCTIONS,
        )

        response = await agent.run(query)
        return response.text

    await credential.close()


async def main():
    print("\n🛫 Operations Agent (kb2-operations)")
    print("=" * 55)

    query = "What is the current status of flights through Eastern European airspace given the recent conflict escalation?"
    print(f"\n❓ Query: {query}")

    response = await run_operations_agent(query)
    print(f"\n💬 Response:\n{response}")


if __name__ == "__main__":
    asyncio.run(main())
