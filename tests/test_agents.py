"""Tests for individual agent configurations."""

import pytest


def test_customer_service_instructions_content():
    """Customer service agent instructions contain key policies."""
    from app.backend.agents.customer_service_agent import CUSTOMER_SERVICE_INSTRUCTIONS

    assert "rebook" in CUSTOMER_SERVICE_INSTRUCTIONS.lower()
    assert "refund" in CUSTOMER_SERVICE_INSTRUCTIONS.lower()
    assert "baggage" in CUSTOMER_SERVICE_INSTRUCTIONS.lower()
    assert "zava airlines" in CUSTOMER_SERVICE_INSTRUCTIONS.lower()


def test_operations_instructions_content():
    """Operations agent instructions contain geo-political awareness."""
    from app.backend.agents.operations_agent import OPERATIONS_INSTRUCTIONS

    assert "geo-political" in OPERATIONS_INSTRUCTIONS.lower() or "geopolitical" in OPERATIONS_INSTRUCTIONS.lower()
    assert "airspace" in OPERATIONS_INSTRUCTIONS.lower()
    assert "crew" in OPERATIONS_INSTRUCTIONS.lower()


def test_loyalty_instructions_content():
    """Loyalty agent instructions contain SkyRewards program details."""
    from app.backend.agents.loyalty_agent import LOYALTY_INSTRUCTIONS

    assert "skyrewards" in LOYALTY_INSTRUCTIONS.lower()
    assert "miles" in LOYALTY_INSTRUCTIONS.lower()
    assert "tier" in LOYALTY_INSTRUCTIONS.lower() or "gold" in LOYALTY_INSTRUCTIONS.lower()
