import polars as pl

from hermes.validation.checks import ValidationResult
from hermes.validation.reports import CheckResult, ValidationReport


def validate(data: pl.DataFrame, checks: list) -> ValidationReport:
    report = ValidationReport()
    for check in checks:
        result: ValidationResult = check.run(data)
        report.add_check(
            CheckResult(
                name=result.check,
                passed=result.passed,
                message=result.message,
            )
        )
    return report


if __name__ == "__main__":
    from hermes.validation.checks import NotNull

    data = pl.read_csv("/run/media/haider/DATA/projects/Hermes/hermes/connectors/lib/datasets/cpi.csv")
    report = validate(data=data, checks=[NotNull("score")])
    print(report.summary())
