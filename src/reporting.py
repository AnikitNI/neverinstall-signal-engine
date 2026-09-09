import pandas as pd
from pathlib import Path


INPUT_FILE = Path(
    "Data/signal_results.csv"
)

OUTPUT_FILE = Path(
    "Data/ranked_signal_report.csv"
)


ACTIONABILITY_POINTS = {
    "HIGH": 100,
    "MEDIUM": 60,
    "LOW": 20,
}

CONFIDENCE_POINTS = {
    "HIGH": 100,
    "MEDIUM": 60,
    "LOW": 20,
}

PRIORITY_POINTS = {
    "P1": 100,
    "P2": 70,
    "P3": 40,
    "P4": 20,
}


def count_triggers(value):

    if not isinstance(
        value,
        str
    ):
        return 0

    value = value.strip()

    if not value:
        return 0

    return len(
        [
            item
            for item in value.split("+")
            if item.strip()
        ]
    )


def get_trigger_type(row):

    direct_count = row[
        "direct_trigger_count"
    ]

    supporting_count = row[
        "supporting_trigger_count"
    ]

    if direct_count > 0:
        return "DIRECT"

    if supporting_count > 0:
        return "SUPPORTING"

    return "NONE"


def calculate_trigger_rank_score(row):

    actionability = (
        ACTIONABILITY_POINTS.get(
            row["actionability"],
            20
        )
    )

    confidence = (
        CONFIDENCE_POINTS.get(
            row["signal_confidence"],
            20
        )
    )

    priority = (
        PRIORITY_POINTS.get(
            row["priority"],
            20
        )
    )

    score = float(
        row["score"]
    )

    direct_count = float(
        row["direct_trigger_count"]
    )

    supporting_count = float(
        row["supporting_trigger_count"]
    )

    direct_points = min(
        direct_count * 50,
        100
    )

    supporting_points = min(
        supporting_count * 30,
        100
    )

    rank_score = (
        actionability * 0.40
        + direct_points * 0.25
        + confidence * 0.15
        + priority * 0.10
        + score * 0.10
        + supporting_points * 0.05
    )

    return round(
        rank_score,
        1
    )


def build_report():

    if not INPUT_FILE.exists():

        raise FileNotFoundError(
            f"Input file not found: "
            f"{INPUT_FILE}"
        )

    df = pd.read_csv(
        INPUT_FILE
    )

    # --------------------------------------------------
    # Clean empty CSV cells
    # --------------------------------------------------

    df["direct_triggers"] = (
        df["direct_triggers"]
        .fillna("")
    )

    df["supporting_triggers"] = (
        df["supporting_triggers"]
        .fillna("")
    )

    df["best_buyer"] = (
        df["best_buyer"]
        .fillna("")
    )

    df["recommended_action"] = (
        df["recommended_action"]
        .fillna("")
    )

    if df.empty:

        raise ValueError(
            "signal_results.csv is empty."
        )

    required_columns = [
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
    ]

    missing_columns = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing_columns:

        raise ValueError(
            "Missing required columns: "
            + ", ".join(
                missing_columns
            )
        )

    # ==================================================
    # APPLICABLE SCORE
    # ==================================================

    df["score"] = df.apply(
        lambda row: (
            row["partner_score"]
            if row["bucket"] == "PARTNER"
            else row["customer_score"]
        ),
        axis=1
    )

    # ==================================================
    # TRIGGER COUNTS
    # ==================================================

    df["direct_trigger_count"] = (
        df["direct_triggers"]
        .apply(
            count_triggers
        )
    )

    df["supporting_trigger_count"] = (
        df["supporting_triggers"]
        .apply(
            count_triggers
        )
    )

    # ==================================================
    # TRIGGER TYPE
    # ==================================================

    df["trigger_type"] = (
        df.apply(
            get_trigger_type,
            axis=1
        )
    )

    # ==================================================
    # TRIGGER RANKING
    # ==================================================

    df["trigger_rank_score"] = (
        df.apply(
            calculate_trigger_rank_score,
            axis=1
        )
    )

    # ==================================================
    # SORT STRONGEST OPPORTUNITIES FIRST
    # ==================================================

    df = df.sort_values(
        by=[
            "trigger_rank_score",
            "direct_trigger_count",
            "score",
        ],
        ascending=[
            False,
            False,
            False,
        ],
    ).reset_index(
        drop=True
    )

    # ==================================================
    # RANK
    # ==================================================

    df.insert(
        0,
        "trigger_rank",
        range(
            1,
            len(df) + 1
        )
    )

    # ==================================================
    # SAVE REPORT
    # ==================================================

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    return df


def print_account(row):

    print(
        f"{int(row['trigger_rank'])}. "
        f"{row['company']} "
        f"({row['region']})"
    )

    print(
        f"   {row['actionability']} | "
        f"{row['bucket']} | "
        f"{row['priority']} | "
        f"Trigger score: "
        f"{row['trigger_rank_score']}"
    )

    direct = row["direct_triggers"]

    if not isinstance(
        direct,
        str
    ) or not direct.strip():

        direct = "None"

    supporting = row[
        "supporting_triggers"
    ]

    if not isinstance(
        supporting,
        str
    ) or not supporting.strip():

        supporting = "None"

    buyer = row[
        "best_buyer"
    ]

    if not isinstance(
        buyer,
        str
    ) or not buyer.strip():

        buyer = "No buyer identified"

    action = row[
        "recommended_action"
    ]

    if not isinstance(
        action,
        str
    ) or not action.strip():

        action = "No recommended action"

    print(
        f"   Direct: {direct}"
    )

    print(
        f"   Supporting: {supporting}"
    )

    print(
        f"   Buyer: {buyer}"
    )

    print(
        f"   Action: {action}"
    )

    print()


def print_report(df):

    print()

    print(
        "=" * 70
    )

    print(
        "NEVERINSTALL TRIGGER RANKING"
    )

    print(
        "=" * 70
    )

    print()

    print(
        f"Accounts ranked: {len(df)}"
    )

    print(
        f"Report saved to: {OUTPUT_FILE}"
    )

    print()

    # ==================================================
    # ACTIONABLE ACCOUNTS
    # ==================================================

    actionable = df[
        df["actionability"].isin(
            [
                "HIGH",
                "MEDIUM",
            ]
        )
    ]

    if not actionable.empty:

        print(
            "TOP ACTIONABLE ACCOUNTS"
        )

        print(
            "-" * 70
        )

        for _, row in actionable.head(
            10
        ).iterrows():

            print_account(
                row
            )

    else:

        # ==================================================
        # FALLBACK RESEARCH QUEUE
        # ==================================================

        research_queue = df[
            df["actionability"] == "LOW"
        ].head(
            10
        )

        print(
            "TOP ACCOUNTS TO RESEARCH"
        )

        print(
            "-" * 70
        )

        if research_queue.empty:

            print(
                "No accounts available "
                "for research."
            )

        else:

            for _, row in research_queue.iterrows():

                print_account(
                    row
                )

    # ==================================================
    # FULL RANKING
    # ==================================================

    print(
        "=" * 70
    )

    print(
        "FULL TRIGGER RANKING"
    )

    print(
        "=" * 70
    )

    print()

    display_columns = [
        "trigger_rank",
        "company",
        "region",
        "bucket",
        "priority",
        "actionability",
        "trigger_type",
        "trigger_rank_score",
        "score",
    ]

    available_columns = [
        column
        for column in display_columns
        if column in df.columns
    ]

    print(
        df[
            available_columns
        ].to_string(
            index=False
        )
    )

    print()

    # ==================================================
    # TRIGGER SUMMARY
    # ==================================================

    print(
        "=" * 70
    )

    print(
        "TRIGGER SUMMARY"
    )

    print(
        "=" * 70
    )

    print()

    direct_accounts = len(
        df[
            df["direct_trigger_count"] > 0
        ]
    )

    supporting_only_accounts = len(
        df[
            (
                df["direct_trigger_count"] == 0
            )
            &
            (
                df["supporting_trigger_count"] > 0
            )
        ]
    )

    no_trigger_accounts = len(
        df[
            (
                df["direct_trigger_count"] == 0
            )
            &
            (
                df["supporting_trigger_count"] == 0
            )
        ]
    )

    high_actionability = len(
        df[
            df["actionability"] == "HIGH"
        ]
    )

    medium_actionability = len(
        df[
            df["actionability"] == "MEDIUM"
        ]
    )

    low_actionability = len(
        df[
            df["actionability"] == "LOW"
        ]
    )

    print(
        f"Direct-trigger accounts: "
        f"{direct_accounts}"
    )

    print(
        f"Supporting-only accounts: "
        f"{supporting_only_accounts}"
    )

    print(
        f"No-trigger accounts: "
        f"{no_trigger_accounts}"
    )

    print()

    print(
        f"HIGH actionability: "
        f"{high_actionability}"
    )

    print(
        f"MEDIUM actionability: "
        f"{medium_actionability}"
    )

    print(
        f"LOW actionability: "
        f"{low_actionability}"
    )

    print()

    print(
        "=" * 70
    )

    print(
        "REPORT COMPLETE"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":

    report = build_report()

    print_report(
        report
    )