"""Customer Service Agent - Connected to kb1-customer-service Knowledge Base.

Handles passenger interactions: rebooking, refunds, complaints,
baggage issues, seat upgrades, and general travel assistance for Zava Airlines.
"""

import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from agent_framework import ChatAgent, ChatMessage, Role
from agent_framework.azure import AzureAIAgentClient, AzureAISearchContextProvider

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "https://srch-zava-airlines.search.windows.net")
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "https://foundry-zava-airlines.services.ai.azure.com/api/projects/proj1-zava-airlines")
MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")

CUSTOMER_SERVICE_INSTRUCTIONS = """You are the Customer Service Agent for Zava Airlines.
You handle all passenger-facing interactions with empathy, professionalism, and efficiency.

Your responsibilities include:
- Flight rebooking and itinerary changes
- Refund requests and compensation claims (EU261, DOT regulations)
- Baggage issues: lost, delayed, or damaged luggage
- Seat upgrades and special seating requests
- Complaint resolution and service recovery
- Travel document requirements and visa information
- Special assistance requests (wheelchair, unaccompanied minors, medical needs)
- General travel inquiries and airport information

When geo-political situations affect travel (airspace closures, travel bans, conflict zones):
- Proactively inform passengers about impacts to their itinerary
- Offer alternative routing options
- Explain rebooking policies for affected routes
- Provide safety-related travel advisories

Always:
- Be empathetic and solution-oriented
- Cite specific Zava Airlines policies when applicable
- Provide booking reference numbers and next steps
- Escalate to a supervisor when compensation exceeds standard thresholds
- Reference the knowledge base for the most current policies"""


async def run_customer_service_agent(query: str) -> str:
    """Run the Customer Service agent with a query."""
    credential = DefaultAzureCredential()

    async with (
        AzureAIAgentClient(
            project_endpoint=PROJECT_ENDPOINT,
            model_deployment_name=MODEL,
            credential=credential,
        ) as client,
        AzureAISearchContextProvider(
            endpoint=SEARCH_ENDPOINT,
            knowledge_base_name="kb1-customer-service",
            credential=credential,
            mode="agentic",
            knowledge_base_output_mode="answer_synthesis",
        ) as kb_context,
    ):
        agent = ChatAgent(
            chat_client=client,
            context_provider=kb_context,
            instructions=CUSTOMER_SERVICE_INSTRUCTIONS,
        )

        message = ChatMessage(role=Role.USER, text=query)
        response = await agent.run(message)
        return response.text

    await credential.close()


async def main():
    print("\n✈️  Customer Service Agent (kb1-customer-service)")
    print("=" * 55)

    query = "I need to rebook my flight from London to Dubai due to a travel advisory. What are my options?"
    print(f"\n❓ Query: {query}")

    response = await run_customer_service_agent(query)
    print(f"\n💬 Response:\n{response}")


if __name__ == "__main__":
    asyncio.run(main())
