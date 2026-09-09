import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    )
)

from validation import validate_research


def test_valid_customer_research():

    research = {
        "identity": {
            "identity_confidence": "high"
        },

        "classification": {
            "bucket": "CUSTOMER",
            "customer_fit": "high",
            "partner_fit": "low"
        },

        "customer_signals": [
            {
                "signal": "citrix",
                "strength": "high",
                "recency": "recent",
                "reason": "Direct evidence",
                "source": "https://example.com"
            }
        ],

        "partner_signals": [],

        "buyer_personas": [
            {
                "title": "Head of Infrastructure",
                "confidence": "high",
                "reason": "Relevant technology owner"
            }
        ],

        "recommended_motion": "direct_outbound",

        "why_now": "Active infrastructure modernization.",

        "neverinstall_angle": (
            "Position Neverinstall around secure "
            "workspace modernization."
        ),

        "summary": "Strong customer opportunity.",
    }

    cleaned, warnings = validate_research(
        research
    )

    assert cleaned[
        "classification"
    ][
        "bucket"
    ] == "CUSTOMER"

    assert len(
        cleaned["customer_signals"]
    ) == 1

    assert cleaned[
        "customer_signals"
    ][0][
        "signal"
    ] == "citrix"

    assert len(warnings) == 0


def test_invalid_signal_is_removed():

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
                "reason": "Valid",
                "source": "https://example.com"
            },
            {
                "signal": "fake_signal",
                "strength": "high",
                "recency": "recent",
                "reason": "Invalid",
                "source": "https://example.com"
            }
        ],

        "partner_signals": [],
    }

    cleaned, warnings = validate_research(
        research
    )

    assert len(
        cleaned["customer_signals"]
    ) == 1

    assert cleaned[
        "customer_signals"
    ][0][
        "signal"
    ] == "citrix"


def test_low_identity_removes_signals():

    research = {
        "identity": {
            "identity_confidence": "low"
        },

        "classification": {
            "bucket": "CUSTOMER",
            "customer_fit": "high",
            "partner_fit": "low"
        },

        "customer_signals": [
            {
                "signal": "citrix",
                "strength": "high",
                "recency": "recent",
                "reason": "Should be removed",
                "source": "https://example.com"
            }
        ],

        "partner_signals": [
            {
                "signal": "systems_integrator",
                "strength": "high",
                "recency": "recent",
                "reason": "Should be removed",
                "source": "https://example.com"
            }
        ],

        "recommended_motion": "direct_outbound",
    }

    cleaned, warnings = validate_research(
        research
    )

    assert (
        cleaned["customer_signals"] == []
    )

    assert (
        cleaned["partner_signals"] == []
    )

    assert (
        cleaned["classification"]["bucket"]
        == "LOW_FIT"
    )

    assert (
        cleaned["recommended_motion"]
        == "manual_review"
    )

    assert len(warnings) >= 1


def test_invalid_motion_is_corrected():

    research = {
        "identity": {
            "identity_confidence": "high"
        },

        "classification": {
            "bucket": "CUSTOMER"
        },

        "customer_signals": [],

        "partner_signals": [],

        "recommended_motion": "something_invalid",
    }

    cleaned, warnings = validate_research(
        research
    )

    assert (
        cleaned["recommended_motion"]
        == "direct_outbound"
    )

    assert len(warnings) >= 1


def test_personas_are_limited_to_three():

    research = {
        "identity": {
            "identity_confidence": "high"
        },

        "classification": {
            "bucket": "CUSTOMER"
        },

        "customer_signals": [],

        "partner_signals": [],

        "buyer_personas": [
            {
                "title": "CIO",
                "confidence": "high",
                "reason": "Technology ownership"
            },
            {
                "title": "CTO",
                "confidence": "high",
                "reason": "Technology ownership"
            },
            {
                "title": "Head of Infrastructure",
                "confidence": "high",
                "reason": "Infrastructure ownership"
            },
            {
                "title": "IT Director",
                "confidence": "medium",
                "reason": "IT ownership"
            }
        ],
    }

    cleaned, _ = validate_research(
        research
    )

    assert len(
        cleaned["buyer_personas"]
    ) == 3


def test_partner_motion():

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
                "reason": "SI capability",
                "source": "https://example.com"
            }
        ],

        "recommended_motion": "direct_outbound",
    }

    cleaned, warnings = validate_research(
        research
    )

    assert (
        cleaned["recommended_motion"]
        == "partner_outreach"
    )

    assert len(warnings) >= 1


if __name__ == "__main__":

    test_valid_customer_research()

    test_invalid_signal_is_removed()

    test_low_identity_removes_signals()

    test_invalid_motion_is_corrected()

    test_personas_are_limited_to_three()

    test_partner_motion()

    print(
        "All validation tests passed."
    )