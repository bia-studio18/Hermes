from pydantic import BaseModel


class CheckResult(BaseModel):
    name: str
    passed: bool
    message: str | None = None
    severity: str = "error"


class ValidationReport(BaseModel):
    passed: bool = True
    checks: list[CheckResult] = []
    errors: list[str] = []
    warnings: list[str] = []

    def summary(self) -> str:
        total = len(self.checks)
        passed = sum(1 for c in self.checks if c.passed)
        failed = total - passed
        lines = [
            f"Validation Report: {'PASSED' if self.passed else 'FAILED'}",
            f"  Total checks: {total}",
            f"  Passed: {passed}",
            f"  Failed: {failed}",
        ]
        for check in self.checks:
            icon = "\u2713" if check.passed else "\u2717"
            lines.append(f"  {icon} {check.name}: {check.message or 'ok'}")
        return "\n".join(lines)

    def add_check(self, check: CheckResult) -> None:
        self.checks.append(check)
        if not check.passed and check.severity == "error":
            self.passed = False
        if not check.passed and check.severity == "warning":
            self.warnings.append(check.message or check.name)
