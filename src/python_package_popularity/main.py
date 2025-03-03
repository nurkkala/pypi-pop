from enum import StrEnum

import httpx
import typer
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table


class RecentModel(BaseModel):
    package: str
    last_day: int
    last_week: int
    last_month: int


class Duration(StrEnum):
    DAY = "day"
    WEEK = "week"
    MONTH = "month"


def get_pypi_stats(package_name: str):
    url = f"https://pypistats.org/api/packages/{package_name}/recent"

    response = httpx.get(url)
    response.raise_for_status()
    data = response.json()

    return RecentModel(
        package=data["package"],
        last_day=data["data"]["last_day"],
        last_week=data["data"]["last_week"],
        last_month=data["data"]["last_month"],
    )


def compare_packages(packages: list[str], sort_by: Duration = Duration.MONTH):
    stats = [get_pypi_stats(package) for package in packages]
    sort_field_name = "last_" + sort_by.value

    table = Table(title=f"Downloads (sorted by {sort_by})")
    table.add_column("Rank", justify="right")
    table.add_column("Package")
    table.add_column("Last Day", justify="right")
    table.add_column("Last Week", justify="right")
    table.add_column("Last Month", justify="right")

    for rank, stat in enumerate(
        sorted(
            stats,
            key=lambda v: getattr(v, sort_field_name),
            reverse=True,
        ),
        start=1,
    ):
        table.add_row(
            str(rank),
            stat.package,
            f"{stat.last_day:,}",
            f"{stat.last_week:,}",
            f"{stat.last_month:,}",
        )

    console = Console()
    console.print(table)


def app():
    typer.run(compare_packages)
