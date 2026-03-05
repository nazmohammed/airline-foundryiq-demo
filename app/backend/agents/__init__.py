"""
Agents module for Zava Airlines FoundryIQ + Agent Framework demo.

CONFIGURATION:
- SEARCH_ENDPOINT: Configured via AZURE_SEARCH_ENDPOINT env var
- PROJECT_ENDPOINT: Configured via AZURE_AI_PROJECT_ENDPOINT env var
- MODEL: gpt-4.1
- KBs: kb1-customer-service, kb2-operations, kb3-loyalty
"""

# KB-grounded agents
from .customer_service_agent import run_customer_service_agent, CUSTOMER_SERVICE_INSTRUCTIONS
from .operations_agent import run_operations_agent, OPERATIONS_INSTRUCTIONS
from .loyalty_agent import run_loyalty_agent, LOYALTY_INSTRUCTIONS

# Orchestrator
from .orchestrator import run_orchestrator, run_single_query

__all__ = [
    # KB agents
    "run_customer_service_agent",
    "run_operations_agent",
    "run_loyalty_agent",
    "CUSTOMER_SERVICE_INSTRUCTIONS",
    "OPERATIONS_INSTRUCTIONS",
    "LOYALTY_INSTRUCTIONS",
    # Orchestrator
    "run_orchestrator",
    "run_single_query",
]
