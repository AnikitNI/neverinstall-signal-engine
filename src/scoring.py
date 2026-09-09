CUSTOMER_WEIGHTS = {
    # Tier 1 — direct technology triggers
    "citrix": 35,
    "vdi": 30,
    "azure_virtual_desktop": 30,
    "vmware_horizon": 30,

    # Tier 2 — strong contextual triggers
    "gpu_workloads": 20,
    "cloud_migration": 15,

    # Tier 3 — supporting triggers
    "compliance": 7,
    "remote_workforce": 5,
    "rapid_hiring": 5,
}


PARTNER_WEIGHTS = {
    "managed_service_provider": 20,
    "systems_integrator": 20,
    "cloud_consulting": 15,
    "it_infrastructure_services": 15,
    "vdi_services": 20,
    "citrix_services": 20,
    "vmware_services": 15,
    "azure_services": 15,
    "cloud_migration_services": 15,
    "reseller_or_channel": 10,
    "managed_desktop_services": 20,
    "cloud_infrastructure_services": 15,
}


STRENGTH_MULTIPLIERS = {
    "high": 1.0,
    "medium": 0.7,
    "low": 0.4,
}


RECENCY_MULTIPLIERS = {
    "recent": 1.0,
    "old": 0.6,
    "unknown": 0.8,
}


# ============================================================
# CUSTOMER COMBINATIONS
# ============================================================

CUSTOMER_COMBINATIONS = [

    # Direct VDI / Citrix trigger + modernization trigger
    ({"citrix", "cloud_migration"}, 20),
    ({"vdi", "cloud_migration"}, 15),
    ({"azure_virtual_desktop", "cloud_migration"}, 15),
    ({"vmware_horizon", "cloud_migration"}, 15),

    # Multiple direct desktop signals
    ({"citrix", "vdi"}, 10),

    # Technology + security/compliance
    ({"citrix", "compliance"}, 10),
    ({"vdi", "compliance"}, 10),

    # Modernization + distributed workforce
    ({"cloud_migration", "remote_workforce"}, 5),

    # GPU + cloud modernization
    ({"gpu_workloads", "cloud_migration"}, 10),
]


# ============================================================
# PARTNER COMBINATIONS
# ============================================================

PARTNER_COMBINATIONS = [

    ({"systems_integrator", "vdi_services"}, 20),

    ({"managed_service_provider", "managed_desktop_services"}, 15),

    ({"azure_services", "cloud_migration_services"}, 15),

    ({"systems_integrator", "cloud_consulting"}, 10),

    ({"reseller_or_channel", "azure_services"}, 10),

    ({"cloud_consulting", "cloud_migration_services"}, 10),

    ({"managed_service_provider", "cloud_infrastructure_services"}, 10),

]


# ============================================================
# BASE SIGNAL SCORE
# ============================================================

def calculate_signal_score(signals, weights):
    """
    Calculate the score contributed by individual signals.

    Each signal is adjusted for:
    - signal importance
    - evidence strength
    - evidence recency
    """

    score = 0

    for evidence in signals:

        signal = evidence.get(
            "signal"
        )

        strength = evidence.get(
            "strength",
            "low"
        )

        recency = evidence.get(
            "recency",
            "unknown"
        )

        weight = weights.get(
            signal,
            0
        )

        strength_multiplier = STRENGTH_MULTIPLIERS.get(
            strength,
            0.4
        )

        recency_multiplier = RECENCY_MULTIPLIERS.get(
            recency,
            0.8
        )

        score += (
            weight
            * strength_multiplier
            * recency_multiplier
        )

    return score


# ============================================================
# COMBINATION BONUS
# ============================================================

def calculate_combination_bonus(
    signals,
    combinations
):
    """
    Add bonus points when multiple related signals
    appear together.

    The bonus is adjusted based on the weakest evidence
    quality among the signals involved.
    """

    signal_map = {
        evidence.get("signal"): evidence
        for evidence in signals
    }

    bonus = 0

    for required_signals, points in combinations:

        if not required_signals.issubset(
            signal_map.keys()
        ):
            continue

        quality_values = []

        for signal in required_signals:

            evidence = signal_map[signal]

            strength = evidence.get(
                "strength",
                "low"
            )

            recency = evidence.get(
                "recency",
                "unknown"
            )

            strength_multiplier = STRENGTH_MULTIPLIERS.get(
                strength,
                0.4
            )

            recency_multiplier = RECENCY_MULTIPLIERS.get(
                recency,
                0.8
            )

            quality_values.append(
                min(
                    strength_multiplier,
                    recency_multiplier
                )
            )

        quality_multiplier = min(
            quality_values
        )

        bonus += (
            points
            * quality_multiplier
        )

    return bonus


# ============================================================
# SIGNAL CONTRIBUTIONS
# ============================================================

def get_signal_contributions(
    signals,
    weights
):
    """
    Return the points contributed by each signal.
    """

    contributions = []

    for evidence in signals:

        signal = evidence.get(
            "signal"
        )

        strength = evidence.get(
            "strength",
            "low"
        )

        recency = evidence.get(
            "recency",
            "unknown"
        )

        weight = weights.get(
            signal,
            0
        )

        strength_multiplier = STRENGTH_MULTIPLIERS.get(
            strength,
            0.4
        )

        recency_multiplier = RECENCY_MULTIPLIERS.get(
            recency,
            0.8
        )

        contribution = (
            weight
            * strength_multiplier
            * recency_multiplier
        )

        contributions.append({
            "signal": signal,
            "points": round(
                contribution,
                1
            ),
            "strength": strength,
            "recency": recency,
        })

    return contributions


# ============================================================
# COMBINATION CONTRIBUTIONS
# ============================================================

def get_combination_contributions(
    signals,
    combinations
):
    """
    Return the combination bonuses that were triggered.
    """

    signal_map = {
        evidence.get("signal"): evidence
        for evidence in signals
    }

    contributions = []

    for required_signals, points in combinations:

        if not required_signals.issubset(
            signal_map.keys()
        ):
            continue

        quality_values = []

        for signal in required_signals:

            evidence = signal_map[signal]

            strength = evidence.get(
                "strength",
                "low"
            )

            recency = evidence.get(
                "recency",
                "unknown"
            )

            strength_multiplier = STRENGTH_MULTIPLIERS.get(
                strength,
                0.4
            )

            recency_multiplier = RECENCY_MULTIPLIERS.get(
                recency,
                0.8
            )

            quality_values.append(
                min(
                    strength_multiplier,
                    recency_multiplier
                )
            )

        quality_multiplier = min(
            quality_values
        )

        adjusted_bonus = (
            points
            * quality_multiplier
        )

        contributions.append({
            "signals": sorted(
                required_signals
            ),
            "points": round(
                adjusted_bonus,
                1
            ),
        })

    return contributions


# ============================================================
# SCORE EXPLANATION
# ============================================================

def build_score_explanation(
    bucket,
    customer_score,
    partner_score,
    customer_contributions,
    partner_contributions,
    customer_combinations,
    partner_combinations
):
    """
    Create a human-readable explanation of the score.
    """

    if bucket == "CUSTOMER":

        contributions = customer_contributions
        combinations = customer_combinations
        score = customer_score
        label = "customer"

    elif bucket == "PARTNER":

        contributions = partner_contributions
        combinations = partner_combinations
        score = partner_score
        label = "partner"

    else:

        if customer_score >= partner_score:

            contributions = customer_contributions
            combinations = customer_combinations
            score = customer_score
            label = "customer"

        else:

            contributions = partner_contributions
            combinations = partner_combinations
            score = partner_score
            label = "partner"

    if not contributions and not combinations:

        return (
            f"{score}/100 — No meaningful scored "
            f"{label} signals detected."
        )

    signal_text = ", ".join(
        f"{item['signal']} (+{item['points']})"
        for item in sorted(
            contributions,
            key=lambda item: item["points"],
            reverse=True
        )
    )

    combination_text = ""

    if combinations:

        combination_parts = []

        for combination in combinations:

            names = " + ".join(
                combination["signals"]
            )

            combination_parts.append(
                f"{names} (+{combination['points']})"
            )

        combination_text = (
            "; combinations: "
            + ", ".join(
                combination_parts
            )
        )

    return (
        f"{score}/100 — "
        f"{label.title()} score driven by "
        f"{signal_text}"
        f"{combination_text}."
    )


# ============================================================
# CALCULATE SCORES
# ============================================================

def calculate_scores(research):

    customer_signals = research.get(
        "customer_signals",
        []
    )

    partner_signals = research.get(
        "partner_signals",
        []
    )

    customer_score = calculate_signal_score(
        customer_signals,
        CUSTOMER_WEIGHTS
    )

    customer_score += calculate_combination_bonus(
        customer_signals,
        CUSTOMER_COMBINATIONS
    )

    customer_score = round(
        min(
            customer_score,
            100
        )
    )

    partner_score = calculate_signal_score(
        partner_signals,
        PARTNER_WEIGHTS
    )

    partner_score += calculate_combination_bonus(
        partner_signals,
        PARTNER_COMBINATIONS
    )

    partner_score = round(
        min(
            partner_score,
            100
        )
    )

    return (
        customer_score,
        partner_score
    )


# ============================================================
# SCORE DETAILS
# ============================================================

def calculate_score_details(research):

    customer_signals = research.get(
        "customer_signals",
        []
    )

    partner_signals = research.get(
        "partner_signals",
        []
    )

    customer_score, partner_score = calculate_scores(
        research
    )

    customer_contributions = get_signal_contributions(
        customer_signals,
        CUSTOMER_WEIGHTS
    )

    partner_contributions = get_signal_contributions(
        partner_signals,
        PARTNER_WEIGHTS
    )

    customer_combinations = get_combination_contributions(
        customer_signals,
        CUSTOMER_COMBINATIONS
    )

    partner_combinations = get_combination_contributions(
        partner_signals,
        PARTNER_COMBINATIONS
    )

    bucket = research.get(
        "classification",
        {}
    ).get(
        "bucket",
        "UNKNOWN"
    )

    explanation = build_score_explanation(
        bucket,
        customer_score,
        partner_score,
        customer_contributions,
        partner_contributions,
        customer_combinations,
        partner_combinations
    )

    return {
        "customer_score": customer_score,
        "partner_score": partner_score,
        "customer_contributions": customer_contributions,
        "partner_contributions": partner_contributions,
        "customer_combinations": customer_combinations,
        "partner_combinations": partner_combinations,
        "score_explanation": explanation,
    }


# ============================================================
# PRIORITY
# ============================================================

def calculate_priority(
    bucket,
    customer_score,
    partner_score
):

    if bucket == "CUSTOMER":

        score = customer_score

    elif bucket == "PARTNER":

        score = partner_score

    else:

        score = max(
            customer_score,
            partner_score
        )

    if score >= 75:
        return "P1"

    if score >= 50:
        return "P2"

    if score >= 25:
        return "P3"

    return "P4"


# ============================================================
# GTM MOTION
# ============================================================

def get_gtm_motion(bucket):

    motions = {
        "CUSTOMER": "Direct outbound",
        "PARTNER": "Partner outreach",
        "ECOSYSTEM": "Ecosystem / strategic outreach",
        "LOW_FIT": "Do not prioritize",
        "UNKNOWN": "Manual review",
        "ERROR": "Manual review",
    }

    return motions.get(
        bucket,
        "Manual review"
    )