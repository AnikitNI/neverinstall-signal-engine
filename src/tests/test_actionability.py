import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    )
)

from actionability import (
    calculate_actionability,
)


def test_high_actionability():

    research = {
        "identity": {
            "identity_confidence": "high"
        },

        "classification": {
            "bucket": "CUSTOMER"
        },

        "customer_signals": [
            {
                "signal": "citrix",
                "strength": "high",
                "recency": "recent",
            },
            {
                "signal": "vdi",
                "strength": "high",
                "recency": "recent",
            },
        ],

        "partner_signals": [],

        "buyer_personas": [
            {
                "title": "Head of End User Computing",
                "confidence": "high",
                "reason": "Owns desktop environment."
            }
        ],

        "recommended_motion": "direct_outbound",
    }

    result = calculate_actionability(
        research,
        customer_score=85,
        partner_score=0,
    )

    assert result[
        "actionability"
    ] == "HIGH"

    assert result[
        "signal_confidence"
    ] == "HIGH"

    assert result[
        "direct_signal_count"
    ] == 2

    assert result[
        "relevant_buyer"
    ] is True


def test_medium_actionability_with_direct_signal():

    research = {
        "identity": {
            "identity_confidence": "high"
        },

        "classification": {
            "bucket": "CUSTOMER"
        },

        "customer_signals": [
            {
                "signal": "citrix",
                "strength": "medium",
                "recency": "old",
            }
        ],

        "partner_signals": [],

        "buyer_personas": [],

        "recommended_motion": "direct_outbound",
    }

    result = calculate_actionability(
        research,
        customer_score=35,
        partner_score=0,
    )

    assert result[
        "actionability"
    ] == "MEDIUM"


def test_supporting_only_is_low():

    research = {
        "identity": {
            "identity_confidence": "high"
        },

        "classification": {
            "bucket": "CUSTOMER"
        },

        "customer_signals": [
            {
                "signal": "cloud_migration",
                "strength": "high",
                "recency": "recent",
            },
            {
                "signal": "remote_workforce",
                "strength": "high",
                "recency": "recent",
            },
            {
                "signal": "compliance",
                "strength": "medium",
                "recency": "recent",
            },
        ],

        "partner_signals": [],

        "buyer_personas": [
            {
                "title": "Head of Infrastructure",
                "confidence": "high",
                "reason": "Relevant infrastructure owner."
            }
        ],

        "recommended_motion": "direct_outbound",
    }

    result = calculate_actionability(
        research,
        customer_score=40,
        partner_score=0,
    )

    assert result[
        "actionability"
    ] == "LOW"

    assert result[
        "direct_signal_count"
    ] == 0

    assert result[
        "supporting_signal_count"
    ] == 3


def test_low_identity_is_low():

    research = {
        "identity": {
            "identity_confidence": "low"
        },

        "classification": {
            "bucket": "CUSTOMER"
        },

        "customer_signals": [
            {
                "signal": "citrix",
                "strength": "high",
                "recency": "recent",
            }
        ],

        "partner_signals": [],

        "buyer_personas": [
            {
                "title": "Head of Infrastructure",
                "confidence": "high",
                "reason": "Relevant role."
            }
        ],

        "recommended_motion": "direct_outbound",
    }

    result = calculate_actionability(
        research,
        customer_score=80,
        partner_score=0,
    )

    assert result[
        "actionability"
    ] == "LOW"


def test_partner_actionability():

    research = {
        "identity": {
            "identity_confidence": "high"
        },

        "classification": {
            "bucket": "PARTNER"
        },

        "customer_signals": [],

        "partner_signals": [
            {
                "signal": "systems_integrator",
                "strength": "high",
                "recency": "recent",
            },
            {
                "signal": "vdi_services",
                "strength": "high",
                "recency": "recent",
            },
        ],

        "buyer_personas": [
            {
                "title": "Cloud Practice Director",
                "confidence": "high",
                "reason": "Owns cloud practice."
            }
        ],

        "recommended_motion": "partner_outreach",
    }

    result = calculate_actionability(
        research,
        customer_score=0,
        partner_score=85,
    )

    assert result[
        "actionability"
    ] == "HIGH"

    assert result[
        "action"
    ] == "Prioritize partner outreach"


def test_no_signals_is_low():

    research = {
        "identity": {
            "identity_confidence": "high"
        },

        "classification": {
            "bucket": "CUSTOMER"
        },

        "customer_signals": [],

        "partner_signals": [],

        "buyer_personas": [],

        "recommended_motion": "direct_outbound",
    }

    result = calculate_actionability(
        research,
        customer_score=0,
        partner_score=0,
    )

    assert result[
        "actionability"
    ] == "LOW"

    assert result[
        "direct_signal_count"
    ] == 0

    assert result[
        "supporting_signal_count"
    ] == 0


if __name__ == "__main__":

    test_high_actionability()

    test_medium_actionability_with_direct_signal()

    test_supporting_only_is_low()

    test_low_identity_is_low()

    test_partner_actionability()

    test_no_signals_is_low()

    print(
        "All actionability tests passed."
    )