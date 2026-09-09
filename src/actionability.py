DIRECT_SIGNALS = {
    "citrix",
    "vdi",
    "azure_virtual_desktop",
    "vmware_horizon",
    "gpu_workloads",
}


SUPPORTING_SIGNALS = {
    "cloud_migration",
    "compliance",
    "remote_workforce",
    "rapid_hiring",
}


PARTNER_DIRECT_SIGNALS = {
    "vdi_services",
    "citrix_services",
    "vmware_services",
    "managed_desktop_services",
    "managed_service_provider",
    "systems_integrator",
}


HIGH_VALUE_BUYER_TERMS = {
    "end user computing",
    "euc",
    "digital workplace",
    "workplace technology",
    "infrastructure",
    "cloud",
    "managed services",
    "alliances",
    "partner",
    "channel",
    "modern workplace",
}


def calculate_actionability(
    research,
    customer_score,
    partner_score,
):

    classification = research.get(
        "classification",
        {}
    )

    bucket = classification.get(
        "bucket",
        "LOW_FIT"
    )

    identity = research.get(
        "identity",
        {}
    )

    identity_confidence = identity.get(
        "identity_confidence",
        "low"
    )

    if bucket == "PARTNER":

        signals = research.get(
            "partner_signals",
            []
        )

        direct_signal_set = (
            PARTNER_DIRECT_SIGNALS
        )

        score = partner_score

    else:

        signals = research.get(
            "customer_signals",
            []
        )

        direct_signal_set = (
            DIRECT_SIGNALS
        )

        score = customer_score

    signal_names = {
        item.get("signal")
        for item in signals
        if item.get("signal")
    }

    direct_signals = (
        signal_names
        & direct_signal_set
    )

    supporting_signals = (
        signal_names
        & SUPPORTING_SIGNALS
    )

    high_strength = sum(
        1
        for item in signals
        if item.get("strength") == "high"
    )

    recent_signals = sum(
        1
        for item in signals
        if item.get("recency") == "recent"
    )

    personas = research.get(
        "buyer_personas",
        []
    )

    relevant_buyer = False

    for persona in personas:

        title = persona.get(
            "title",
            ""
        ).lower()

        for term in HIGH_VALUE_BUYER_TERMS:

            if term in title:

                relevant_buyer = True

                break

        if relevant_buyer:
            break

    motion = research.get(
        "recommended_motion",
        "manual_review"
    )

    # ==================================================
    # ACTIONABILITY LEVEL
    # ==================================================

    if identity_confidence == "low":

        level = "LOW"

    elif (
        direct_signals
        and high_strength >= 1
        and relevant_buyer
        and motion != "manual_review"
    ):

        level = "HIGH"

    elif direct_signals:

        level = "MEDIUM"

    elif supporting_signals:

        level = "LOW"

    else:

        level = "LOW"

    # ==================================================
    # SIGNAL CONFIDENCE
    # ==================================================

    if identity_confidence == "high":

        identity_points = 2

    elif identity_confidence == "medium":

        identity_points = 1

    else:

        identity_points = 0

    confidence_points = (
        identity_points
        + min(high_strength, 2)
        + min(recent_signals, 2)
    )

    if confidence_points >= 5:

        confidence = "HIGH"

    elif confidence_points >= 3:

        confidence = "MEDIUM"

    else:

        confidence = "LOW"

    # ==================================================
    # RECOMMENDED ACTION
    # ==================================================

    if level == "HIGH":

        if bucket == "PARTNER":

            action = (
                "Prioritize partner outreach"
            )

        else:

            action = (
                "Prioritize direct outbound"
            )

    elif level == "MEDIUM":

        if bucket == "PARTNER":

            action = (
                "Research partner account further "
                "then begin outreach"
            )

        else:

            action = (
                "Research buyer and trigger further "
                "before personalized outreach"
            )

    else:

        if bucket == "LOW_FIT":

            action = (
                "Do not prioritize"
            )

        else:

            action = (
                "Keep in nurture / monitor for "
                "stronger trigger"
            )

    # ==================================================
    # EXPLANATION
    # ==================================================

    explanation_parts = []

    if direct_signals:

        explanation_parts.append(
            "direct trigger present"
        )

    if supporting_signals:

        explanation_parts.append(
            "supporting business trigger present"
        )

    if high_strength:

        explanation_parts.append(
            f"{high_strength} high-strength evidence"
        )

    if recent_signals:

        explanation_parts.append(
            f"{recent_signals} recent signal"
            + (
                "s"
                if recent_signals != 1
                else ""
            )
        )

    if relevant_buyer:

        explanation_parts.append(
            "relevant buyer identified"
        )

    if not explanation_parts:

        explanation_parts.append(
            "limited actionable evidence"
        )

    explanation = ", ".join(
        explanation_parts
    )

    return {

        "actionability": level,

        "signal_confidence": confidence,

        "direct_signal_count": len(
            direct_signals
        ),

        "supporting_signal_count": len(
            supporting_signals
        ),

        "high_strength_signal_count": (
            high_strength
        ),

        "recent_signal_count": (
            recent_signals
        ),

        "relevant_buyer": (
            relevant_buyer
        ),

        "action": action,

        "explanation": explanation,

        "score_used": score,

    }


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

        "recommended_motion": (
            "direct_outbound"
        ),

    }

    result = calculate_actionability(

        research=test_research,

        customer_score=85,

        partner_score=0,

    )

    print(
        "Actionability test passed."
    )

    print()

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )