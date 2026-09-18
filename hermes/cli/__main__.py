from pathlib import Path

import typer
from rich.console import Console

from hermes.api.data import profile
from hermes.cli.cmds.profile import (
    kv_panel,
    fmt,
    columns_table,
    top_values_table,
    quality_panel,
)
from hermes.credentials.manager import (
    get_cred,
    delete_cred,
    list_creds,
    set_cred,
)
from hermes.credentials.storage import init_credentials


app = typer.Typer(
    name="hermes",
    help="Foundational intelligence data platform.",
    no_args_is_help=True,
)

@app.command()
def version():
    typer.echo("Hermes v0.2.16")


@app.command()
def info():
    typer.echo("Hermes v0.2.16")
    typer.echo("Foundational intelligence data platform")


@app.command()
def profile_data(
    path: Path = typer.Argument(
        help="Path to the dataset.",
        exists=True,
        readable=True,
        resolve_path=True,
    ),
):
    report = profile(path=path)

    summary = [("File", str(path))]

    if report.source:
        summary.append(("Source", report.source))

    summary.extend([
        ("Rows", f"{report.row_count:,}"),
        ("Columns", str(report.column_count)),
    ])

    if report.date_range:
        summary.append(
            (
                "Date range",
                ", ".join(
                    f"{c}: {lo} → {hi}"
                    for c, (lo, hi) in report.date_range.items()
                ),
            )
        )

    if report.frequency:
        summary.append(("Frequency", report.frequency))

    if report.retrieved_at:
        summary.append(
            (
                "Retrieved",
                report.retrieved_at.strftime(
                    "%Y-%m-%d %H:%M:%S %Z"
                ),
            )
        )

    console = Console()

    console.print(
        kv_panel("Profile Report", summary)
    )

    console.print(
        columns_table(report)
    )

    if top := top_values_table(report):
        console.print(top)

    if quality := quality_panel(report):
        console.print(quality)

cred_app = typer.Typer(
    name="cred",
    help="Manage Hermes credentials.",
    no_args_is_help=True,
)

app.add_typer(cred_app)


@cred_app.command()
def init():
    path = init_credentials()

    typer.echo(
        f"Credentials initialized at {path}"
    )


@cred_app.command("set")
def set_credential(
    name: str = typer.Argument(
        help="Credential name.",
    ),
):
    value = typer.prompt(
        "Credential value",
        hide_input=True,
    )

    set_cred(
        name=name,
        value=value,
    )

    typer.echo(
        f"Credential '{name}' saved."
    )


@cred_app.command("get")
def get_credential(
    name: str = typer.Argument(
        help="Credential name.",
    ),
    show: bool = typer.Option(
        False,
        "--show",
        help="Show the credential value.",
    ),
):
    value = get_cred(name)

    if show:
        typer.echo(f"{name}: {value}")
    else:
        typer.echo(
            f"{name}: ********"
        )


@cred_app.command("list")
def list_credentials():

    credentials = list_creds()

    if not credentials:
        typer.echo("No credentials stored.")
        return

    for name in credentials:
        typer.echo(name)


@cred_app.command("delete")
def delete_credential(
    name: str = typer.Argument(
        help="Credential name.",
    ),
):

    delete_cred(name)

    typer.echo(
        f"Credential '{name}' deleted."
    )


if __name__ == "__main__":
    app()