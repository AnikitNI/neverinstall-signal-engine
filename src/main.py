import argparse
import json
import pandas as pd

from research import research_company

from scoring import (
    calculate_scores,
    calculate_priority,
    get_gtm_motion,
    calculate_score_details,
)

from cache import (
    load_cached_research,
    save_research,
    load_cache_metadata,
)

from validation import (
    validate_research,
)

from evidence import (
    extract_evidence,
    summarize_evidence,
)

from outbound import (
    build_outbound_brief,
    format_outbound_brief,
)

from actionability import (
    calculate_actionability,
)


INPUT_FILE = "Data/accounts.csv"
OUTPUT_FILE = "Data/signal_results.csv"


def build_failure_result(
    company,
    region,
    status,
    message
):
    """
    Build a structured result when research cannot
    be completed.
    """

    return {

        "company": company,
        "region": region,

        "resolved_name": "",
        "identity_confidence": "unknown",

        "bucket": status,
        "priority": "P4",

        "gtm_motion": "Manual review",

        "customer_score": 0,
        "partner_score": 0,

        "customer_fit": "unknown",
        "partner_fit": "unknown",

        "buyer_personas": "",

        "customer_signals": "",
        "partner_signals": "",

        "why_now": "",
        "neverinstall_angle": "",

        "recommended_motion": "manual_review",

        "score_explanation": message,
        "summary": message,

        "research_source": status,

        "cached_at": "",

        "validation_warnings": "",

        "evidence_count": 0,

        "high_strength_evidence": 0,
        "medium_strength_evidence": 0,
        "low_strength_evidence": 0,

        "valid_source_count": 0,

        "trigger": "",
        "direct_triggers": "",
        "supporting_triggers": "",

        "best_buyer": "",
        "outbound_motion": "Manual review",

        "actionability": "LOW",
        "signal_confidence": "LOW",

        "direct_signal_count": 0,
        "supporting_signal_count": 0,

        "high_strength_signal_count": 0,
        "recent_signal_count": 0,

        "relevant_buyer": False,

        "recommended_action": "Manual review",

        "actionability_explanation": message,

        "evidence": "",
    }


def is_quota_error(error):
    """
    Detect an exhausted API credit/quota error.
    """

    error_text = str(
        error
    ).lower()

    quota_indicators = [
        "insufficient_quota",
        "credit_balance_exhausted",
        "no credits remaining",
        "429",
    ]

    return any(
        indicator in error_text
        for indicator in quota_indicators
    )


def main():

    parser = argparse.ArgumentParser(
        description="Neverinstall Signal Engine"
    )

    parser.add_argument(
        "--refresh",
        action="store_true",
        help=(
            "Ignore cached research and run "
            "fresh web research."
        )
    )

    parser.add_argument(
        "--cache-only",
        action="store_true",
        help=(
            "Use only cached research. "
            "Never call the API."
        )
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help=(
            "Process only the first N accounts."
        )
    )

    args = parser.parse_args()

    # ======================================================
    # LOAD ACCOUNTS
    # ======================================================

    accounts = pd.read_csv(
        INPUT_FILE
    )

    if args.limit is not None:

        if args.limit < 1:

            print(
                "ERROR: --limit must be at least 1."
            )

            return

        accounts = accounts.head(
            args.limit
        )

    # ======================================================
    # HEADER
    # ======================================================

    print(
        "\nNeverinstall Signal Engine"
    )

    print(
        "=" * 70
    )

    print(
        f"Accounts loaded: {len(accounts)}"
    )

    if args.cache_only:

        print(
            "Mode: CACHE ONLY — API calls are disabled."
        )

    elif args.refresh:

        print(
            "Mode: REFRESH — fresh API research will be used."
        )

    else:

        print(
            "Mode: CACHE FIRST — cached research will be reused."
        )

    if args.limit is not None:

        print(
            f"Account limit: {args.limit}"
        )

    print()

    # ======================================================
    # RESULTS
    # ======================================================

    results = []

    quota_exhausted = False

    # ======================================================
    # ACCOUNT LOOP
    # ======================================================

    for index, row in accounts.iterrows():

        company = row["company"]

        region = row["region"]

        account_name = (
            f"{company}, {region}"
        )

        print(
            f"[{index + 1}/{len(accounts)}] "
            f"Processing {company} ({region})..."
        )

        try:

            research = None

            research_source = ""

            cache_metadata = None

            validation_warnings = []

            # ==================================================
            # CACHE LOOKUP
            # ==================================================

            if not args.refresh:

                research = load_cached_research(
                    account_name
                )

            # ==================================================
            # CACHE HIT
            # ==================================================

            if research is not None:

                research_source = "CACHE"

                cache_metadata = (
                    load_cache_metadata(
                        account_name
                    )
                )

                print(
                    "    Source: LOCAL CACHE"
                )

            # ==================================================
            # CACHE MISS
            # ==================================================

            else:

                if args.cache_only:

                    print(
                        "    CACHE MISS — skipping "
                        "because cache-only mode is enabled."
                    )

                    results.append(
                        build_failure_result(
                            company,
                            region,
                            "CACHE_MISS",
                            "No cached research available."
                        )
                    )

                    print()

                    continue

                # ==================================================
                # QUOTA ALREADY EXHAUSTED
                # ==================================================

                if quota_exhausted:

                    print(
                        "    API quota exhausted — skipping."
                    )

                    results.append(
                        build_failure_result(
                            company,
                            region,
                            "API_QUOTA_EXHAUSTED",
                            "API quota was exhausted during this run."
                        )
                    )

                    print()

                    continue

                # ==================================================
                # FRESH API RESEARCH
                # ==================================================

                research_source = (
                    "FRESH_RESEARCH"
                )

                print(
                    "    Source: OPENAI WEB RESEARCH"
                )

                try:

                    research = research_company(
                        account_name
                    )

                except Exception as error:

                    if is_quota_error(
                        error
                    ):

                        quota_exhausted = True

                        print(
                            "    API QUOTA EXHAUSTED."
                        )

                        print(
                            "    Remaining uncached accounts "
                            "will be skipped."
                        )

                        results.append(
                            build_failure_result(
                                company,
                                region,
                                "API_QUOTA_EXHAUSTED",
                                "API credits exhausted during this run."
                            )
                        )

                        print()

                        continue

                    raise

                # ==================================================
                # VALIDATION
                # ==================================================

                print(
                    "    Validating research..."
                )

                research, validation_warnings = (
                    validate_research(
                        research
                    )
                )

                if validation_warnings:

                    print(
                        f"    Validation warnings: "
                        f"{len(validation_warnings)}"
                    )

                    for warning in validation_warnings:

                        print(
                            f"      - {warning}"
                        )

                else:

                    print(
                        "    Validation: PASSED"
                    )

                # ==================================================
                # SAVE CACHE
                # ==================================================

                save_research(
                    account_name,
                    research
                )

                cache_metadata = (
                    load_cache_metadata(
                        account_name
                    )
                )

                print(
                    "    Validated research cached locally."
                )

            # ==================================================
            # VALIDATE CACHED RESEARCH
            # ==================================================

            if research_source == "CACHE":

                research, validation_warnings = (
                    validate_research(
                        research
                    )
                )

                if validation_warnings:

                    print(
                        f"    Cache validation warnings: "
                        f"{len(validation_warnings)}"
                    )

                    for warning in validation_warnings:

                        print(
                            f"      - {warning}"
                        )

            # ==================================================
            # EVIDENCE
            # ==================================================

            evidence = extract_evidence(
                account_name,
                research
            )

            evidence_summary = (
                summarize_evidence(
                    evidence
                )
            )

            print(
                f"    Evidence records: "
                f"{evidence_summary['total_signals']}"
            )

            # ==================================================
            # SCORING
            # ==================================================

            customer_score, partner_score = (
                calculate_scores(
                    research
                )
            )

            score_details = (
                calculate_score_details(
                    research
                )
            )

            score_explanation = (
                score_details.get(
                    "score_explanation",
                    ""
                )
            )

            # ==================================================
            # CLASSIFICATION
            # ==================================================

            classification = research.get(
                "classification",
                {}
            )

            identity = research.get(
                "identity",
                {}
            )

            bucket = classification.get(
                "bucket",
                "UNKNOWN"
            )

            priority = calculate_priority(
                bucket,
                customer_score,
                partner_score
            )

            gtm_motion = get_gtm_motion(
                bucket
            )

            # ==================================================
            # ACTIONABILITY
            # ==================================================

            actionability = calculate_actionability(

                research=research,

                customer_score=customer_score,

                partner_score=partner_score,

            )

            print(
                f"    Actionability: "
                f"{actionability['actionability']}"
            )

            print(
                f"    Signal Confidence: "
                f"{actionability['signal_confidence']}"
            )

            # ==================================================
            # SIGNALS
            # ==================================================

            customer_signals = [

                item["signal"]

                for item in research.get(
                    "customer_signals",
                    []
                )

            ]

            partner_signals = [

                item["signal"]

                for item in research.get(
                    "partner_signals",
                    []
                )

            ]

            # ==================================================
            # BUYER PERSONAS
            # ==================================================

            buyer_personas = research.get(
                "buyer_personas",
                []
            )

            persona_titles = [

                persona.get(
                    "title",
                    ""
                )

                for persona in buyer_personas

                if persona.get(
                    "title"
                )

            ]

            # ==================================================
            # CACHE TIMESTAMP
            # ==================================================

            cached_at = ""

            if cache_metadata:

                cached_at = cache_metadata.get(
                    "cached_at",
                    ""
                )

            # ==================================================
            # OUTBOUND BRIEF
            # ==================================================

            outbound_brief = build_outbound_brief(

                company=company,

                region=region,

                research=research,

                customer_score=customer_score,

                partner_score=partner_score,

                priority=priority,

                evidence_summary=evidence_summary,

                actionability=actionability,

            )

            print(
                format_outbound_brief(
                    outbound_brief
                )
            )

            # ==================================================
            # VALIDATION WARNINGS
            # ==================================================

            warnings_text = "; ".join(
                validation_warnings
            )

            # ==================================================
            # BUILD RESULT
            # ==================================================

            results.append({

                "company": company,

                "region": region,

                "resolved_name": identity.get(
                    "resolved_name",
                    ""
                ),

                "identity_confidence": identity.get(
                    "identity_confidence",
                    "unknown"
                ),

                "bucket": bucket,

                "priority": priority,

                "gtm_motion": gtm_motion,

                "customer_score": customer_score,

                "partner_score": partner_score,

                "customer_fit": classification.get(
                    "customer_fit",
                    "unknown"
                ),

                "partner_fit": classification.get(
                    "partner_fit",
                    "unknown"
                ),

                "buyer_personas": ", ".join(
                    persona_titles
                ),

                "customer_signals": ", ".join(
                    customer_signals
                ),

                "partner_signals": ", ".join(
                    partner_signals
                ),

                "why_now": research.get(
                    "why_now",
                    ""
                ),

                "neverinstall_angle": research.get(
                    "neverinstall_angle",
                    ""
                ),

                "recommended_motion": research.get(
                    "recommended_motion",
                    ""
                ),

                "score_explanation": (
                    score_explanation
                ),

                "summary": research.get(
                    "summary",
                    ""
                ),

                "research_source": (
                    research_source
                ),

                "cached_at": cached_at,

                "validation_warnings": (
                    warnings_text
                ),

                "evidence_count": (
                    evidence_summary[
                        "total_signals"
                    ]
                ),

                "high_strength_evidence": (
                    evidence_summary[
                        "high_strength"
                    ]
                ),

                "medium_strength_evidence": (
                    evidence_summary[
                        "medium_strength"
                    ]
                ),

                "low_strength_evidence": (
                    evidence_summary[
                        "low_strength"
                    ]
                ),

                "valid_source_count": (
                    evidence_summary[
                        "valid_sources"
                    ]
                ),

                # ==========================================
                # OUTBOUND
                # ==========================================

                "trigger": outbound_brief[
                    "trigger"
                ],

                "direct_triggers": (
                    outbound_brief[
                        "direct_triggers"
                    ]
                ),

                "supporting_triggers": (
                    outbound_brief[
                        "supporting_triggers"
                    ]
                ),

                "best_buyer": outbound_brief[
                    "best_buyer"
                ],

                "outbound_motion": outbound_brief[
                    "recommended_motion"
                ],

                # ==========================================
                # ACTIONABILITY
                # ==========================================

                "actionability": (
                    actionability[
                        "actionability"
                    ]
                ),

                "signal_confidence": (
                    actionability[
                        "signal_confidence"
                    ]
                ),

                "direct_signal_count": (
                    actionability[
                        "direct_signal_count"
                    ]
                ),

                "supporting_signal_count": (
                    actionability[
                        "supporting_signal_count"
                    ]
                ),

                "high_strength_signal_count": (
                    actionability[
                        "high_strength_signal_count"
                    ]
                ),

                "recent_signal_count": (
                    actionability[
                        "recent_signal_count"
                    ]
                ),

                "relevant_buyer": (
                    actionability[
                        "relevant_buyer"
                    ]
                ),

                "recommended_action": (
                    actionability[
                        "action"
                    ]
                ),

                "actionability_explanation": (
                    actionability[
                        "explanation"
                    ]
                ),

                # ==========================================
                # FULL EVIDENCE JSON
                # ==========================================

                "evidence": json.dumps(

                    {

                        "records": evidence,

                        "summary": (
                            evidence_summary
                        ),

                        "customer": research.get(
                            "customer_signals",
                            []
                        ),

                        "partner": research.get(
                            "partner_signals",
                            []
                        ),

                        "buyer_personas": (
                            buyer_personas
                        ),

                        "outbound_brief": (
                            outbound_brief
                        ),

                        "score_details": (
                            score_details
                        ),

                        "actionability": (
                            actionability
                        ),

                        "validation_warnings": (
                            validation_warnings
                        ),

                    },

                    ensure_ascii=False

                ),

            })

            # ==================================================
            # STANDARD RESULT OUTPUT
            # ==================================================

            print(
                f"    Bucket: {bucket}"
            )

            print(
                f"    Priority: {priority}"
            )

            print(
                f"    Customer Score: "
                f"{customer_score}/100"
            )

            print(
                f"    Partner Score: "
                f"{partner_score}/100"
            )

            print()

        except Exception as error:

            print(
                f"    ERROR: {error}"
            )

            print()

            results.append(
                build_failure_result(
                    company,
                    region,
                    "ERROR",
                    f"Processing failed: {error}"
                )
            )

    # ======================================================
    # DATAFRAME
    # ======================================================

    output = pd.DataFrame(
        results
    )

    # ======================================================
    # SORTING
    # ======================================================

    priority_order = {

        "P1": 1,
        "P2": 2,
        "P3": 3,
        "P4": 4,

    }

    actionability_order = {

        "HIGH": 1,
        "MEDIUM": 2,
        "LOW": 3,
        "UNKNOWN": 4,

    }

    output["priority_rank"] = (
        output[
            "priority"
        ].map(
            priority_order
        ).fillna(5)
    )

    output["actionability_rank"] = (
        output[
            "actionability"
        ].map(
            actionability_order
        ).fillna(5)
    )

    output["best_score"] = (
        output[
            [
                "customer_score",
                "partner_score",
            ]
        ].max(
            axis=1
        )
    )

    output = output.sort_values(

        [
            "priority_rank",
            "actionability_rank",
            "best_score",
        ],

        ascending=[
            True,
            True,
            False,
        ],

    )

    output = output.drop(

        columns=[
            "priority_rank",
            "actionability_rank",
            "best_score",
        ]

    )

    # ======================================================
    # SAVE CSV
    # ======================================================

    output.to_csv(

        OUTPUT_FILE,

        index=False,

    )

    # ======================================================
    # FINAL SUMMARY
    # ======================================================

    print(
        "=" * 70
    )

    print(
        "RESEARCH COMPLETE"
    )

    print(
        "=" * 70
    )

    print(
        f"Results saved to: {OUTPUT_FILE}"
    )

    print()

    print(

        output[
            [
                "company",
                "region",
                "bucket",
                "priority",
                "actionability",
                "signal_confidence",
                "customer_score",
                "partner_score",
                "direct_triggers",
                "supporting_triggers",
                "best_buyer",
                "recommended_action",
                "evidence_count",
                "valid_source_count",
                "research_source",
            ]
        ].to_string(
            index=False
        )

    )


if __name__ == "__main__":

    main()