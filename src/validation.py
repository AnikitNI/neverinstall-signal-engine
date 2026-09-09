import copy


VALID_BUCKETS = {
    "CUSTOMER",
    "PARTNER",
    "ECOSYSTEM",
    "LOW_FIT",
}


VALID_CUSTOMER_SIGNALS = {
    "citrix",
    "vdi",
    "azure_virtual_desktop",
    "vmware_horizon",
    "cloud_migration",
    "remote_workforce",
    "rapid_hiring",
    "compliance",
    "gpu_workloads",
}


VALID_PARTNER_SIGNALS = {
    "managed_service_provider",
    "systems_integrator",
    "cloud_consulting",
    "it_infrastructure_services",
    "vdi_services",
    "citrix_services",
    "vmware_services",
    "azure_services",
    "cloud_migration_services",
    "reseller_or_channel",
    "managed_desktop_services",
    "cloud_infrastructure_services",
}


VALID_STRENGTHS = {
    "high",
    "medium",
    "low",
}


VALID_RECENCY = {
    "recent",
    "old",
    "unknown",
}


VALID_FIT_VALUES = {
    "high",
    "medium",
    "low",
}


VALID_MOTIONS = {
    "direct_outbound",
    "partner_outreach",
    "ecosystem_outreach",
    "manual_review",
    "do_not_prioritize",
}


def validate_signal(
    evidence,
    valid_signals
):
    """
    Validate and clean one signal.
    """

    if not isinstance(
        evidence,
        dict
    ):
        return None

    signal = evidence.get(
        "signal"
    )

    if signal not in valid_signals:
        return None

    strength = evidence.get(
        "strength",
        "low"
    )

    if strength not in VALID_STRENGTHS:
        strength = "low"

    recency = evidence.get(
        "recency",
        "unknown"
    )

    if recency not in VALID_RECENCY:
        recency = "unknown"

    reason = evidence.get(
        "reason",
        ""
    )

    source = evidence.get(
        "source",
        ""
    )

    if not isinstance(
        reason,
        str
    ):
        reason = ""

    if not isinstance(
        source,
        str
    ):
        source = ""

    return {
        "signal": signal,
        "strength": strength,
        "recency": recency,
        "reason": reason,
        "source": source,
    }


def validate_signals(
    signals,
    valid_signals
):
    """
    Validate all signals and remove unsupported ones.
    """

    if not isinstance(
        signals,
        list
    ):
        return []

    validated = []

    seen = set()

    for evidence in signals:

        clean_signal = validate_signal(
            evidence,
            valid_signals
        )

        if clean_signal is None:
            continue

        signal_name = clean_signal[
            "signal"
        ]

        # Prevent duplicate signals.
        if signal_name in seen:
            continue

        seen.add(
            signal_name
        )

        validated.append(
            clean_signal
        )

    return validated


def validate_personas(personas):
    """
    Validate buyer persona recommendations.
    """

    if not isinstance(
        personas,
        list
    ):
        return []

    validated = []

    for persona in personas:

        if not isinstance(
            persona,
            dict
        ):
            continue

        title = persona.get(
            "title",
            ""
        )

        confidence = persona.get(
            "confidence",
            "low"
        )

        reason = persona.get(
            "reason",
            ""
        )

        if not isinstance(
            title,
            str
        ):
            continue

        if not title.strip():
            continue

        if confidence not in {
            "high",
            "medium",
            "low",
        }:
            confidence = "low"

        if not isinstance(
            reason,
            str
        ):
            reason = ""

        validated.append({
            "title": title.strip(),
            "confidence": confidence,
            "reason": reason,
        })

    return validated[:3]


def validate_research(research):
    """
    Validate and normalize the complete research response.

    Returns:
        cleaned_research, warnings
    """

    if not isinstance(
        research,
        dict
    ):
        raise ValueError(
            "Research response is not a JSON object."
        )

    cleaned = copy.deepcopy(
        research
    )

    warnings = []

    # ==================================================
    # IDENTITY
    # ==================================================

    identity = cleaned.get(
        "identity"
    )

    if not isinstance(
        identity,
        dict
    ):
        identity = {}

        warnings.append(
            "Missing identity object."
        )

    identity_confidence = identity.get(
        "identity_confidence",
        "low"
    )

    if identity_confidence not in {
        "high",
        "medium",
        "low",
    }:
        identity_confidence = "low"

        warnings.append(
            "Invalid identity confidence."
        )

    identity["identity_confidence"] = (
        identity_confidence
    )

    cleaned["identity"] = identity

    # ==================================================
    # CLASSIFICATION
    # ==================================================

    classification = cleaned.get(
        "classification"
    )

    if not isinstance(
        classification,
        dict
    ):
        classification = {}

        warnings.append(
            "Missing classification object."
        )

    bucket = classification.get(
        "bucket",
        "LOW_FIT"
    )

    if bucket not in VALID_BUCKETS:

        warnings.append(
            f"Invalid bucket: {bucket}"
        )

        bucket = "LOW_FIT"

    customer_fit = classification.get(
        "customer_fit",
        "low"
    )

    if customer_fit not in VALID_FIT_VALUES:
        customer_fit = "low"

    partner_fit = classification.get(
        "partner_fit",
        "low"
    )

    if partner_fit not in VALID_FIT_VALUES:
        partner_fit = "low"

    classification["bucket"] = bucket
    classification["customer_fit"] = customer_fit
    classification["partner_fit"] = partner_fit

    cleaned["classification"] = classification

    # ==================================================
    # SIGNALS
    # ==================================================

    customer_signals = validate_signals(
        cleaned.get(
            "customer_signals",
            []
        ),
        VALID_CUSTOMER_SIGNALS
    )

    partner_signals = validate_signals(
        cleaned.get(
            "partner_signals",
            []
        ),
        VALID_PARTNER_SIGNALS
    )

    cleaned["customer_signals"] = (
        customer_signals
    )

    cleaned["partner_signals"] = (
        partner_signals
    )

    # ==================================================
    # IDENTITY SAFETY RULE
    # ==================================================

    if identity_confidence == "low":

        if customer_signals:
            warnings.append(
                "Low identity confidence: "
                "customer signals removed."
            )

        if partner_signals:
            warnings.append(
                "Low identity confidence: "
                "partner signals removed."
            )

        cleaned["customer_signals"] = []
        cleaned["partner_signals"] = []

        cleaned["classification"][
            "bucket"
        ] = "LOW_FIT"

        cleaned["classification"][
            "customer_fit"
        ] = "low"

        cleaned["classification"][
            "partner_fit"
        ] = "low"

        cleaned[
            "recommended_motion"
        ] = "manual_review"

    # ==================================================
    # BUYER PERSONAS
    # ==================================================

    cleaned["buyer_personas"] = (
        validate_personas(
            cleaned.get(
                "buyer_personas",
                []
            )
        )
    )

    # ==================================================
    # TEXT FIELDS
    # ==================================================

    text_fields = [
        "why_now",
        "neverinstall_angle",
        "summary",
    ]

    for field in text_fields:

        value = cleaned.get(
            field,
            ""
        )

        if not isinstance(
            value,
            str
        ):
            cleaned[field] = ""

    # ==================================================
    # RECOMMENDED MOTION
    # ==================================================

    motion = cleaned.get(
        "recommended_motion",
        "manual_review"
    )

    if motion not in VALID_MOTIONS:

        warnings.append(
            f"Invalid recommended motion: {motion}"
        )

        motion = "manual_review"

    cleaned["recommended_motion"] = motion

    # ==================================================
    # MOTION / BUCKET CONSISTENCY
    # ==================================================

    expected_motion = {
        "CUSTOMER": "direct_outbound",
        "PARTNER": "partner_outreach",
        "ECOSYSTEM": "ecosystem_outreach",
        "LOW_FIT": "manual_review",
    }

    expected = expected_motion.get(
        cleaned["classification"]["bucket"]
    )

    if expected:

        if motion != expected:

            warnings.append(
                "Recommended motion did not "
                "match bucket; corrected."
            )

            cleaned["recommended_motion"] = expected

    return cleaned, warnings


if __name__ == "__main__":

    test_research = {
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
                "reason": "Example evidence",
                "source": "https://example.com"
            },
            {
                "signal": "INVALID_SIGNAL",
                "strength": "high",
                "recency": "recent",
                "reason": "Should be removed",
                "source": "https://example.com"
            }
        ],
        "partner_signals": [],
        "buyer_personas": [],
        "recommended_motion": "direct_outbound",
        "why_now": "Example",
        "neverinstall_angle": "Example",
        "summary": "Example"
    }

    cleaned, warnings = validate_research(
        test_research
    )

    print("Validation test passed.")
    print()
    print(
        "Customer signals:",
        cleaned["customer_signals"]
    )
    print()
    print(
        "Warnings:",
        warnings
    )