from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, TextIO


@dataclass
class Score:
    submitted: float
    reproduced: float

    def __lt__(self, other):
        return self.submitted < other.submitted

    def __gt__(self, other):
        return self.submitted > other.submitted



def sort_records(records: list[Any], sort_fields: list[tuple[str, bool]]) -> list[Any]:
    sorted_records = list(records)
    for field_name, reverse in reversed(sort_fields):
        sorted_records.sort(key=lambda record: getattr(record, field_name), reverse=reverse)
    return sorted_records


def dense_ranks(records: list[Any], rank_fields: list[str], float_precision: int = 6) -> list[int]:
    ranks: list[int] = []
    current_rank = 0
    previous_key: tuple[Any, ...] | None = None

    for record in records:
        current_key = tuple(
            _normalize_rank_value(getattr(record, field_name), float_precision)
            for field_name in rank_fields
        )
        if current_key != previous_key:
            current_rank += 1
        previous_key = current_key
        ranks.append(current_rank)

    return ranks


def _normalize_rank_value(value: Any, float_precision: int) -> Any:
    if isinstance(value, float):
        return f"{value:.{float_precision}f}"
    elif isinstance(value, Score):
        return _normalize_rank_value(value.submitted, float_precision)
    return value


class LeaderboardWriter:
    def __init__(self, time: datetime, path: Path, float_precision: int = 6):
        self.time = time
        self.path = path
        self.float_precision = float_precision
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
        rank_fields: list[str] | None = None,
    ) -> None:
        if self._file is None:
            raise RuntimeError("LeaderboardWriter must be used inside a with block.")

        sorted_records = sort_records(records, sort_fields)

        headers = list(field_map.keys())
        if include_rank:
            headers = ["Rank", *headers]

        record_ranks = dense_ranks(
            sorted_records,
            rank_fields or [field_name for field_name, _ in sort_fields],
            float_precision=self.float_precision,
        )

        rows = []
        for i, record in enumerate(sorted_records):
            row = [
                self._format_value(getattr(record, field_name), self.float_precision)
                for field_name in field_map.values()
            ]
            if include_rank:
                row = [str(record_ranks[i]), *row]
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
    def _format_value(value: Any, float_precision: int) -> str:
        if isinstance(value, float):
            return f"{value:.{float_precision}f}"
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M %z")
        return str(value)

    @staticmethod
    def _format_row(row: list[str], col_widths: list[int]) -> str:
        return "| " + " | ".join(
            row[i].ljust(col_widths[i]) for i in range(len(row))
        ) + " |"


def open_leaderboard(time: datetime, path: Path, float_precision: int = 6) -> LeaderboardWriter:
    return LeaderboardWriter(time, path, float_precision=float_precision)


def output_leaderboard(
    records: list[Any],
    field_map: dict[str, str],
    sort_fields: list[tuple[str, bool]],
    include_rank: bool,
    time: datetime,
    path: Path,
    description: str | None = None,
    float_precision: int = 6,
    rank_fields: list[str] | None = None,
):
    with open_leaderboard(time, path, float_precision=float_precision) as writer:
        writer.new_table(
            records,
            field_map,
            sort_fields,
            include_rank,
            description,
            rank_fields=rank_fields,
        )
