from datetime import datetime, timezone
from urllib.parse import urlparse


def is_valid_url(url):
    """
    Check whether a source looks like a valid HTTP/HTTPS URL.
    """

    if not isinstance(url, str):
        return False

    url = url.strip()

    if not url:
        return False

    try:

        parsed = urlparse(url)

        return (
            parsed.scheme in {
                "http",
                "https",
            }
            and bool(parsed.netloc)
        )

    except Exception:

        return False


def build_evidence_record(
    company,
    signal,
    strength,
    recency,
    reason,
    source,
    signal_type
):
    """
    Convert one research signal into a normalized
    evidence record.
    """

    return {

        "company": company,

        "signal": signal,

        "signal_type": signal_type,

        "strength": strength,

        "recency": recency,

        "reason": reason,

        "source": source,

        "source_valid": is_valid_url(
            source
        ),

        "captured_at": datetime.now(
            timezone.utc
        ).isoformat(),

    }


def extract_evidence(
    company,
    research
):
    """
    Extract and normalize all customer and partner
    evidence from the research response.
    """

    evidence = []

    # ==================================================
    # CUSTOMER EVIDENCE
    # ==================================================

    customer_signals = research.get(
        "customer_signals",
        []
    )

    for signal in customer_signals:

        if not isinstance(
            signal,
            dict
        ):
            continue

        evidence.append(
            build_evidence_record(

                company=company,

                signal=signal.get(
                    "signal",
                    ""
                ),

                strength=signal.get(
                    "strength",
                    "low"
                ),

                recency=signal.get(
                    "recency",
                    "unknown"
                ),

                reason=signal.get(
                    "reason",
                    ""
                ),

                source=signal.get(
                    "source",
                    ""
                ),

                signal_type="customer",

            )
        )

    # ==================================================
    # PARTNER EVIDENCE
    # ==================================================

    partner_signals = research.get(
        "partner_signals",
        []
    )

    for signal in partner_signals:

        if not isinstance(
            signal,
            dict
        ):
            continue

        evidence.append(
            build_evidence_record(

                company=company,

                signal=signal.get(
                    "signal",
                    ""
                ),

                strength=signal.get(
                    "strength",
                    "low"
                ),

                recency=signal.get(
                    "recency",
                    "unknown"
                ),

                reason=signal.get(
                    "reason",
                    ""
                ),

                source=signal.get(
                    "source",
                    ""
                ),

                signal_type="partner",

            )
        )

    return evidence


def summarize_evidence(
    evidence
):
    """
    Create a compact summary of evidence quality.
    """

    total = len(
        evidence
    )

    high = sum(
        1
        for item in evidence
        if item.get(
            "strength"
        ) == "high"
    )

    medium = sum(
        1
        for item in evidence
        if item.get(
            "strength"
        ) == "medium"
    )

    low = sum(
        1
        for item in evidence
        if item.get(
            "strength"
        ) == "low"
    )

    valid_sources = sum(
        1
        for item in evidence
        if item.get(
            "source_valid"
        )
    )

    return {

        "total_signals": total,

        "high_strength": high,

        "medium_strength": medium,

        "low_strength": low,

        "valid_sources": valid_sources,

    }


if __name__ == "__main__":

    test_research = {

        "customer_signals": [

            {
                "signal": "citrix",

                "strength": "high",

                "recency": "recent",

                "reason": (
                    "Example Citrix evidence."
                ),

                "source": (
                    "https://example.com"
                ),
            }

        ],

        "partner_signals": [

            {
                "signal": "systems_integrator",

                "strength": "medium",

                "recency": "recent",

                "reason": (
                    "Example SI evidence."
                ),

                "source": (
                    "https://example.com"
                ),
            }

        ]

    }

    evidence = extract_evidence(
        "Example Company, Australia",
        test_research
    )

    print(
        "Evidence test passed."
    )

    print()

    print(
        evidence
    )

    print()

    print(
        summarize_evidence(
            evidence
        )
    )