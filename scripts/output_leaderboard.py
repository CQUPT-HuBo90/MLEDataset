from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any, TextIO


class LeaderboardWriter:
    def __init__(self, time: datetime, path: Path):
        self.time = time
        self.path = path
        self._file: TextIO | None = None
        self._has_table = False

    def __enter__(self) -> "LeaderboardWriter":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._file = self.path.open("w", encoding="utf-8")
        self._file.write("# Leaderboard\n\n")
        self._file.write(f"Update: {self.time.strftime('%Y-%m-%d %H:%M %z')}\n\n")
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None

    def new_table(
        self,
        records: list[Any],
        field_map: dict[str, str],
        sort_fields: list[tuple[str, bool]],
        include_rank: bool,
        description: str | None = None,
    ) -> None:
        if self._file is None:
            raise RuntimeError("LeaderboardWriter must be used inside a with block.")

        for field_name, reverse in reversed(sort_fields):
            records.sort(key=lambda record: getattr(record, field_name), reverse=reverse)

        headers = list(field_map.keys())
        if include_rank:
            headers = ["Rank", *headers]

        rows = []
        for i, record in enumerate(records, 1):
            row = [self._format_value(getattr(record, field_name)) for field_name in field_map.values()]
            if include_rank:
                row = [str(i), *row]
            rows.append(row)

        col_widths = []
        for i in range(len(headers)):
            row_width = max((len(row[i]) for row in rows), default=0)
            col_widths.append(max(len(headers[i]), row_width))

        if self._has_table:
            self._file.write("\n")
        self._has_table = True

        if description:
            self._file.write(f"{description}\n\n")

        self._file.write(self._format_row(headers, col_widths) + "\n")
        self._file.write("|" + "|".join("-" * (w + 2) for w in col_widths) + "|\n")
        for row in rows:
            self._file.write(self._format_row(row, col_widths) + "\n")

    @staticmethod
    def _format_value(value: Any) -> str:
        if isinstance(value, float):
            return f"{value:.6f}"
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M %z")
        return str(value)

    @staticmethod
    def _format_row(row: list[str], col_widths: list[int]) -> str:
        return "| " + " | ".join(
            row[i].ljust(col_widths[i]) for i in range(len(row))
        ) + " |"


def open_leaderboard(time: datetime, path: Path) -> LeaderboardWriter:
    return LeaderboardWriter(time, path)


def output_leaderboard(
    records: list[Any],
    field_map: dict[str, str],
    sort_fields: list[tuple[str, bool]],
    include_rank: bool,
    time: datetime,
    path: Path,
    description: str | None = None,
):
    with open_leaderboard(time, path) as writer:
        writer.new_table(records, field_map, sort_fields, include_rank, description)
