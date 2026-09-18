from typing import Any

from rich import box
from rich.panel import Panel
from rich.table import Table

COLUMN_HEADERS = ("Column", "Type", "Unique", "Nulls", "Null%", "Min", "Max", "Mean", "Median")


def fmt(value: Any) -> str:
    if value is None:
        return "—"
    if isinstance(value, float):
        return f"{value:.4g}"
    return str(value)


def kv_panel(title: str, rows: list[tuple[str, str]]) -> Panel:
    table = Table(show_header=False, box=None, padding=(0, 2))
    table.add_column(style="bold cyan", justify="right")
    table.add_column()
    for label, value in rows:
        table.add_row(label, value)
    return Panel(table, title=f"[bold]{title}[/bold]", border_style="cyan")


def columns_table(report) -> Panel:
    columns = Table(header_style="bold cyan", box=box.SIMPLE_HEAVY)
    for header in COLUMN_HEADERS:
        columns.add_column(
            header,
            justify="right" if header not in ("Column", "Type") else "left",
            no_wrap=header == "Column",
        )
    for col in report.columns:
        columns.add_row(
            col.name,
            col.dtype,
            f"{col.unique_count:,}",
            f"{col.null_count:,}",
            f"{col.null_ratio:.2%}",
            *(fmt(v) for v in (col.min_value, col.max_value, col.mean, col.median)),
        )
    return Panel(columns, title="[bold]Columns[/bold]", border_style="cyan")


def top_values_table(report) -> Panel | None:
    top_values = Table(show_header=False, box=None, padding=(0, 2))
    top_values.add_column(style="bold", no_wrap=True)
    top_values.add_column()
    for col in report.columns:
        if col.top_values:
            top_values.add_row(col.name, ", ".join(f"{k} ({v})" for k, v in col.top_values[:5]))
    return Panel(top_values, title="[bold]Top Values[/bold]", border_style="cyan") if top_values.rows else None


def quality_panel(report) -> Panel | None:
    quality = report.quality
    if not quality:
        return None

    incomplete = {k: v for k, v in (quality.completeness or {}).items() if v < 1.0}
    comp = ", ".join(f"{k} {v:.2%}" for k, v in incomplete.items()) or "100% (all columns complete)"

    anomalies = {k: v for k, v in (quality.anomaly_count or {}).items() if v > 0}
    anom = ", ".join(f"{k}: {v}" for k, v in anomalies.items()) or "none detected"

    return kv_panel(
        "Quality",
        [
            ("Completeness", comp),
            ("Duplicates", str(quality.duplicate_count)),
            ("Anomalies", anom),
        ],
    )
