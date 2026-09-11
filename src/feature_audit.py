import pandas as pd

from src.config import CLEANED_DATA_PATH


def main():

    print("=" * 70)
    print("       SIH 25192 - FEATURE AUDIT")
    print("=" * 70)

    df = pd.read_csv(
        CLEANED_DATA_PATH
    )

    columns = [
        "project_code",
        "project_name",
        "snapshot_date",
        "original_doc",
        "start_date",
        "planned_duration_months",
        "elapsed_months",
        "months_to_original_target",
        "target_schedule_overrun_months",
    ]

    print("\nSelected columns:\n")

    print(
        df[columns].head(30).to_string(
            index=False
        )
    )

    print("\n" + "=" * 70)
    print("CORRELATION CHECK")
    print("=" * 70)

    numeric_columns = [
        "planned_duration_months",
        "elapsed_months",
        "months_to_original_target",
        "target_schedule_overrun_months",
    ]

    print(
        df[numeric_columns]
        .corr()
        .to_string()
    )

    print("\n" + "=" * 70)
    print("FEATURE AUDIT COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()