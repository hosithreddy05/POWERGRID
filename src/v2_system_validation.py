from src.project_service import (
    get_project_list,
    get_project_information
)

from src.predictor import predict_project


def main():

    print("=" * 75)
    print("       SIH 25192 - V2 SYSTEM VALIDATION")
    print("=" * 75)

    projects = get_project_list()

    print("\n[1] PROJECT VALIDATION")
    print("Projects:", len(projects))

    if len(projects) != 92:
        raise RuntimeError(
            f"Expected 92 projects, found {len(projects)}"
        )

    print("✓ 92 validated projects available")

    # --------------------------------------------------------
    # Test first, middle and last project
    # --------------------------------------------------------

    indices = [
        0,
        len(projects) // 2,
        len(projects) - 1
    ]

    print("\n[2] MULTI-PROJECT PREDICTION TEST")

    passed = 0

    for index in indices:

        project_code = str(
            projects.iloc[index]["project_code"]
        )

        print(
            f"\nTesting project: {project_code}"
        )

        information = get_project_information(
            project_code
        )

        model_input = information[
            "model_input"
        ]

        if len(model_input) != 12:
            print(
                "✗ Incorrect feature count"
            )
            continue

        result = predict_project(
            model_input
        )

        print(
            "Cost prediction:",
            result["cost_prediction_pct"],
            "%"
        )

        print(
            "Schedule prediction:",
            result["schedule_prediction_months"],
            "months"
        )

        print(
            "Risk score:",
            result["cost_risk_score"]
        )

        print(
            "Risk level:",
            result["cost_risk_level"]
        )

        passed += 1

    # --------------------------------------------------------
    # Final validation
    # --------------------------------------------------------

    print("\n[3] FINAL VALIDATION")

    print(
        f"Projects successfully tested: "
        f"{passed}/3"
    )

    if passed == 3:

        print(
            "✓ MULTI-PROJECT V2 VALIDATION PASSED"
        )

    else:

        print(
            "✗ MULTI-PROJECT V2 VALIDATION FAILED"
        )

    print("\n" + "=" * 75)
    print(
        "V2 SYSTEM VALIDATION COMPLETED"
    )
    print("=" * 75)


if __name__ == "__main__":
    main()