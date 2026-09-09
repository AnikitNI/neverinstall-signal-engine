import re


DIRECT_CUSTOMER_SIGNALS = {
    "citrix",
    "vdi",
    "azure_virtual_desktop",
    "vmware_horizon",
    "gpu_workloads",
}


DIRECT_PARTNER_SIGNALS = {
    "vdi_services",
    "citrix_services",
    "vmware_services",
    "managed_desktop_services",
    "managed_service_provider",
    "systems_integrator",
}


SIGNAL_LABELS = {
    "citrix": "Citrix",
    "vdi": "VDI",
    "azure_virtual_desktop": "Azure Virtual Desktop",
    "vmware_horizon": "VMware Horizon",
    "gpu_workloads": "GPU workloads",
    "cloud_migration": "cloud migration",
    "remote_workforce": "remote workforce",
    "rapid_hiring": "rapid hiring",
    "compliance": "compliance",
    "vdi_services": "VDI services",
    "citrix_services": "Citrix services",
    "vmware_services": "VMware services",
    "azure_services": "Azure services",
    "cloud_migration_services": "cloud migration services",
    "cloud_consulting": "cloud consulting",
    "managed_service_provider": "managed services",
    "systems_integrator": "systems integration",
    "managed_desktop_services": "managed desktop services",
    "it_infrastructure_services": "IT infrastructure services",
    "cloud_infrastructure_services": "cloud infrastructure services",
    "reseller_or_channel": "channel/reseller capability",
}


def clean_sales_text(text):
    """
    Remove Markdown links, raw URLs and citation artifacts
    from sales-facing text.
    """

    if not isinstance(
        text,
        str
    ):
        return ""

    # Convert Markdown links to their visible text.
    text = re.sub(
        r"\[([^\]]+)\]\([^)]+\)",
        r"\1",
        text
    )

    # Remove raw URLs.
    text = re.sub(
        r"https?://\S+",
        "",
        text
    )

    # Remove empty parentheses.
    text = re.sub(
        r"\(\s*\)",
        "",
        text
    )

    # Remove standalone citation labels.
    text = re.sub(
        r"\bSource\b",
        "",
        text,
        flags=re.IGNORECASE
    )

    # Remove numeric citation markers.
    text = re.sub(
        r"\[\s*\d+\s*\]",
        "",
        text
    )

    # Fix words accidentally joined after URL removal.
    text = re.sub(
        r"([a-z])([A-Z])",
        r"\1 \2",
        text
    )

    # Fix missing spaces after commas.
    text = re.sub(
        r",([A-Za-z])",
        r", \1",
        text
    )

    # Normalize whitespace.
    text = re.sub(
        r"\s+",
        " ",
        text
    )

    # Remove spaces before punctuation.
    text = re.sub(
        r"\s+([,.!?;:])",
        r"\1",
        text
    )

    return text.strip()


def get_best_buyer(research):
    """
    Return the highest-confidence recommended buyer persona.
    """

    personas = research.get(
        "buyer_personas",
        []
    )

    if not personas:

        return "No buyer identified"

    confidence_order = {
        "high": 1,
        "medium": 2,
        "low": 3,
    }

    sorted_personas = sorted(
        personas,
        key=lambda persona: confidence_order.get(
            persona.get(
                "confidence",
                "low"
            ),
            3
        )
    )

    return sorted_personas[0].get(
        "title",
        "No buyer identified"
    )


def classify_triggers(research):
    """
    Separate direct technology/service triggers from
    supporting business/contextual triggers.
    """

    classification = research.get(
        "classification",
        {}
    )

    bucket = classification.get(
        "bucket",
        "LOW_FIT"
    )

    if bucket == "PARTNER":

        signals = research.get(
            "partner_signals",
            []
        )

        direct_set = (
            DIRECT_PARTNER_SIGNALS
        )

    else:

        signals = research.get(
            "customer_signals",
            []
        )

        direct_set = (
            DIRECT_CUSTOMER_SIGNALS
        )

    direct = []

    supporting = []

    for evidence in signals:

        signal = evidence.get(
            "signal",
            ""
        )

        if not signal:
            continue

        label = SIGNAL_LABELS.get(
            signal,
            signal.replace(
                "_",
                " "
            )
        )

        if signal in direct_set:

            direct.append(
                label
            )

        else:

            supporting.append(
                label
            )

    return {
        "direct": direct,
        "supporting": supporting,
    }


def get_trigger(research):
    """
    Build a concise trigger description.
    """

    triggers = classify_triggers(
        research
    )

    direct = triggers["direct"]

    supporting = triggers["supporting"]

    parts = []

    if direct:

        parts.append(
            "Direct: " + " + ".join(
                direct[:3]
            )
        )

    if supporting:

        parts.append(
            "Supporting: " + " + ".join(
                supporting[:3]
            )
        )

    if not parts:

        return "No strong trigger identified"

    return " | ".join(
        parts
    )


def get_outbound_angle(research):
    """
    Return a cleaned Neverinstall positioning angle.
    """

    angle = research.get(
        "neverinstall_angle",
        ""
    )

    angle = clean_sales_text(
        angle
    )

    if angle:

        return angle

    return (
        "No specific Neverinstall angle identified."
    )


def get_outbound_motion(research):
    """
    Translate the machine-readable motion into
    a sales-friendly motion.
    """

    motion = research.get(
        "recommended_motion",
        "manual_review"
    )

    motions = {
        "direct_outbound": "Direct outbound",
        "partner_outreach": "Partner outreach",
        "ecosystem_outreach": (
            "Ecosystem / strategic outreach"
        ),
        "manual_review": "Manual review",
        "do_not_prioritize": "Do not prioritize",
    }

    return motions.get(
        motion,
        "Manual review"
    )


def build_outbound_brief(
    company,
    region,
    research,
    customer_score,
    partner_score,
    priority,
    evidence_summary,
    actionability=None,
):
    """
    Build a concise outbound-ready account brief.

    Actionability is passed in from actionability.py.
    """

    classification = research.get(
        "classification",
        {}
    )

    bucket = classification.get(
        "bucket",
        "LOW_FIT"
    )

    if bucket == "PARTNER":

        score = partner_score

    else:

        score = customer_score

    buyer = get_best_buyer(
        research
    )

    trigger = get_trigger(
        research
    )

    why_now = clean_sales_text(
        research.get(
            "why_now",
            ""
        )
    )

    if not why_now:

        why_now = (
            "No strong time-sensitive trigger identified."
        )

    angle = get_outbound_angle(
        research
    )

    motion = get_outbound_motion(
        research
    )

    evidence_count = evidence_summary.get(
        "total_signals",
        0
    )

    valid_sources = evidence_summary.get(
        "valid_sources",
        0
    )

    triggers = classify_triggers(
        research
    )

    result = {

        "account": company,

        "region": region,

        "account_type": bucket,

        "priority": priority,

        "score": score,

        "trigger": trigger,

        "direct_triggers": " + ".join(
            triggers["direct"]
        ),

        "supporting_triggers": " + ".join(
            triggers["supporting"]
        ),

        "best_buyer": buyer,

        "why_now": why_now,

        "neverinstall_angle": angle,

        "recommended_motion": motion,

        "evidence_count": evidence_count,

        "valid_source_count": valid_sources,

    }

    # ==================================================
    # ACTIONABILITY
    # ==================================================

    if actionability:

        result["actionability"] = (
            actionability.get(
                "actionability",
                "LOW"
            )
        )

        result["signal_confidence"] = (
            actionability.get(
                "signal_confidence",
                "LOW"
            )
        )

        result["recommended_action"] = (
            actionability.get(
                "action",
                ""
            )
        )

        result["actionability_explanation"] = (
            actionability.get(
                "explanation",
                ""
            )
        )

    else:

        result["actionability"] = (
            "UNKNOWN"
        )

        result["signal_confidence"] = (
            "UNKNOWN"
        )

        result["recommended_action"] = ""

        result["actionability_explanation"] = ""

    return result


def format_outbound_brief(
    brief
):
    """
    Turn an outbound brief into a readable
    terminal block.
    """

    return (
        "\n"
        "----------------------------------------\n"
        f"{brief['account']}\n"
        f"{brief['priority']} — "
        f"{brief['account_type']} — "
        f"{brief['score']}/100\n"
        "\n"
        f"Actionability: "
        f"{brief.get('actionability', 'UNKNOWN')}\n"
        f"Signal confidence: "
        f"{brief.get('signal_confidence', 'UNKNOWN')}\n"
        "\n"
        f"Direct triggers: "
        f"{brief['direct_triggers'] or 'None'}\n"
        f"Supporting triggers: "
        f"{brief['supporting_triggers'] or 'None'}\n"
        f"Buyer: "
        f"{brief['best_buyer']}\n"
        f"Why now: "
        f"{brief['why_now']}\n"
        f"Neverinstall angle: "
        f"{brief['neverinstall_angle']}\n"
        f"Motion: "
        f"{brief['recommended_motion']}\n"
        f"Recommended action: "
        f"{brief.get('recommended_action', 'N/A')}\n"
        f"Evidence: "
        f"{brief['evidence_count']} signals / "
        f"{brief['valid_source_count']} valid sources\n"
        "----------------------------------------"
    )


if __name__ == "__main__":

    test_research = {

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

            {
                "signal": "compliance",
                "strength": "medium",
                "recency": "recent",
            },

        ],

        "buyer_personas": [

            {
                "title": "Head of End User Computing",
                "confidence": "high",
            }

        ],

        "why_now": (
            "Existing desktop technology plus "
            "active cloud modernization. "
            "[Source](https://example.com)"
        ),

        "neverinstall_angle": (
            "Position Neverinstall around secure "
            "workspace modernization."
        ),

        "recommended_motion": (
            "direct_outbound"
        ),

    }

    test_actionability = {

        "actionability": "HIGH",

        "signal_confidence": "HIGH",

        "action": (
            "Prioritize direct outbound"
        ),

        "explanation": (
            "Direct trigger present, strong evidence "
            "and relevant buyer identified."
        ),

    }

    brief = build_outbound_brief(

        company="Example Company",

        region="Australia",

        research=test_research,

        customer_score=85,

        partner_score=0,

        priority="P1",

        evidence_summary={
            "total_signals": 3,
            "valid_sources": 3,
        },

        actionability=test_actionability,

    )

    print(
        format_outbound_brief(
            brief
        )
    )