"""Loyalty Agent - Connected to kb3-loyalty Knowledge Base.

Handles frequent flyer program, miles/points, tier status, lounge access,
partner benefits, and reward redemption for Zava Airlines SkyRewards program.
"""

import asyncio
import os
from azure.identity.aio import DefaultAzureCredential
from agent_framework import ChatAgent, ChatMessage, Role
from agent_framework.azure import AzureAIAgentClient, AzureAISearchContextProvider

SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "https://srch-zava-airlines.search.windows.net")
PROJECT_ENDPOINT = os.getenv("AZURE_AI_PROJECT_ENDPOINT", "https://foundry-zava-airlines.services.ai.azure.com/api/projects/proj1-zava-airlines")
MODEL = os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4.1")

LOYALTY_INSTRUCTIONS = """You are the Loyalty Program Agent for Zava Airlines SkyRewards.
You are the expert on all aspects of the Zava Airlines frequent flyer and loyalty program.

Your responsibilities include:
- SkyRewards tier status: Blue, Silver, Gold, Platinum, Diamond
- Miles earning rates by fare class, route, and partner airlines
- Miles redemption for flights, upgrades, and partner rewards
- Lounge access rules (Zava Lounges and partner lounges like Star Alliance)
- Tier qualification criteria and status match programs
- Credit card partnerships and bonus mile promotions
- Partner airline earning and redemption (codeshare, alliance partners)
- Family pooling accounts and miles gifting/transfer
- Miles expiration policies and reactivation options
- Elite member benefits: priority boarding, extra baggage, seat selection

Special promotions and campaigns:
- Seasonal bonus mile offers
- Double/triple mile promotions on specific routes
- Partner hotel and car rental earning opportunities
- Status challenge programs for competitor airline members

Always:
- Reference exact mile amounts and qualification thresholds
- Cite specific SkyRewards program terms and conditions
- Provide tier comparison tables when relevant
- Suggest strategies to maximize miles and achieve tier upgrades
- Be enthusiastic about rewarding loyal customers"""


async def run_loyalty_agent(query: str) -> str:
    """Run the Loyalty agent with a query."""
    credential = DefaultAzureCredential()

    async with (
        AzureAIAgentClient(
            project_endpoint=PROJECT_ENDPOINT,
            model_deployment_name=MODEL,
            credential=credential,
        ) as client,
        AzureAISearchContextProvider(
            endpoint=SEARCH_ENDPOINT,
            knowledge_base_name="kb3-loyalty",
            credential=credential,
            mode="agentic",
            knowledge_base_output_mode="answer_synthesis",
        ) as kb_context,
    ):
        agent = ChatAgent(
            chat_client=client,
            context_provider=kb_context,
            instructions=LOYALTY_INSTRUCTIONS,
        )

        message = ChatMessage(role=Role.USER, text=query)
        response = await agent.run(message)
        return response.text

    await credential.close()


async def main():
    print("\n🏆 Loyalty Agent (kb3-loyalty)")
    print("=" * 55)

    query = "How many miles do I need to upgrade from Silver to Gold status?"
    print(f"\n❓ Query: {query}")

    response = await run_loyalty_agent(query)
    print(f"\n💬 Response:\n{response}")


if __name__ == "__main__":
    asyncio.run(main())
