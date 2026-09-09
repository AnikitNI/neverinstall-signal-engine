import sys
from pathlib import Path

sys.path.insert(
    0,
    str(
        Path(__file__).resolve().parents[1]
    )
)

from scoring import (
    calculate_scores,
    calculate_score_details,
    calculate_priority,
    get_gtm_motion,
)


def test_customer_score():

    research = {
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
                "signal": "cloud_migration",
                "strength": "high",
                "recency": "recent",
            },
        ],
        "partner_signals": [],
    }

    customer_score, partner_score = (
        calculate_scores(research)
    )

    assert customer_score > 0
    assert partner_score == 0


def test_partner_score():

    research = {
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
    }

    customer_score, partner_score = (
        calculate_scores(research)
    )

    assert customer_score == 0
    assert partner_score > 0


def test_score_is_capped_at_100():

    research = {
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
            {
                "signal": "azure_virtual_desktop",
                "strength": "high",
                "recency": "recent",
            },
            {
                "signal": "vmware_horizon",
                "strength": "high",
                "recency": "recent",
            },
            {
                "signal": "gpu_workloads",
                "strength": "high",
                "recency": "recent",
            },
            {
                "signal": "cloud_migration",
                "strength": "high",
                "recency": "recent",
            },
            {
                "signal": "compliance",
                "strength": "high",
                "recency": "recent",
            },
            {
                "signal": "remote_workforce",
                "strength": "high",
                "recency": "recent",
            },
            {
                "signal": "rapid_hiring",
                "strength": "high",
                "recency": "recent",
            },
        ],
        "partner_signals": [],
    }

    customer_score, _ = (
        calculate_scores(research)
    )

    assert customer_score <= 100


def test_score_details():

    research = {
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
    }

    details = calculate_score_details(
        research
    )

    assert "customer_score" in details
    assert "partner_score" in details
    assert "score_explanation" in details

    assert details[
        "customer_score"
    ] > 0


def test_priority_levels():

    assert (
        calculate_priority(
            "CUSTOMER",
            80,
            0
        )
        == "P1"
    )

    assert (
        calculate_priority(
            "CUSTOMER",
            60,
            0
        )
        == "P2"
    )

    assert (
        calculate_priority(
            "CUSTOMER",
            30,
            0
        )
        == "P3"
    )

    assert (
        calculate_priority(
            "CUSTOMER",
            10,
            0
        )
        == "P4"
    )


def test_gtm_motion():

    assert (
        get_gtm_motion(
            "CUSTOMER"
        )
        == "Direct outbound"
    )

    assert (
        get_gtm_motion(
            "PARTNER"
        )
        == "Partner outreach"
    )

    assert (
        get_gtm_motion(
            "ECOSYSTEM"
        )
        == "Ecosystem / strategic outreach"
    )


if __name__ == "__main__":

    test_customer_score()
    test_partner_score()
    test_score_is_capped_at_100()
    test_score_details()
    test_priority_levels()
    test_gtm_motion()

    print(
        "All scoring tests passed."
    )