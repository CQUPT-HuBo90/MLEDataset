import argparse
import html
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime

import numpy
from scipy.stats import pearsonr, spearmanr

from leaderboard import fetch_mails, collect_submissions, Submission, origin_mos, parse_result
from common import ROOT_PATH, REPRODUCTION_PATH
from output_leaderboard import dense_ranks, output_leaderboard, sort_records, Score


@dataclass
class CheckedRecord:
    team_name: str
    avg: Score
    srcc: Score
    plcc: Score
    submit_time: datetime
    avg_err: float
    max_err: float

@dataclass
class ReproducedRecord:
    team_name: str
    avg: float
    srcc: float
    plcc: float

@dataclass
class Reproduction:
    team_name: str
    mail: str
    results: dict[str, float]

    def to_record(self, origin: dict[str, float]) -> ReproducedRecord:
        keys = list(origin.keys())
        keys.sort()

        preds = []
        gts = []

        for key in keys:
            preds.append(origin[key])
            gts.append(self.results[key])

        preds = numpy.array(preds)
        gts = numpy.array(gts)

        srcc = spearmanr(preds, gts).correlation
        plcc = pearsonr(preds, gts).statistic
        avg = (srcc + plcc) / 2

        return ReproducedRecord(
            team_name=self.team_name,
            avg=avg,
            srcc=srcc,
            plcc=plcc,
        )


@dataclass
class SubmissionPair:
    reproduction: Reproduction
    submission: Submission
    key_matched: bool = True

    def to_checked_record(self, origin: dict[str, float]) -> CheckedRecord:
        submitted_record = self.submission.to_record(origin)
        reproduced_record = self.reproduction.to_record(origin)
        errors = [
            abs(self.reproduction.results[key] - self.submission.results[key])
            for key in self.submission.results
        ]
        return CheckedRecord(
            team_name=submitted_record.team_name,
            avg=Score(
                submitted=submitted_record.avg,
                reproduced=reproduced_record.avg,
            ),
            srcc=Score(
                submitted=submitted_record.srcc,
                reproduced=reproduced_record.srcc,
            ),
            plcc=Score(
                submitted=submitted_record.plcc,
                reproduced=reproduced_record.plcc,
            ),
            submit_time=submitted_record.submit_time,
            avg_err=sum(errors) / len(errors),
            max_err=max(errors),
        )

def submission_of(reproduction: Reproduction, submission: Submission) -> SubmissionPair:
    submission_results = submission.results
    reproduction_results = reproduction.results
    if submission_results.keys() != reproduction_results.keys():
        return SubmissionPair(
            submission=submission,
            reproduction=reproduction,
            key_matched=False,
        )

    error_val = 0.0
    max_err = -1.0
    for key, submission_value in submission_results.items():
        exponent = Decimal(str(submission_value)).as_tuple().exponent
        decimal_places = -exponent if isinstance(exponent, int) and exponent < 0 else 0
        rounded_reproduction_value = round(reproduction_results[key], decimal_places)
        current_err = abs(rounded_reproduction_value - submission_value)
        error_val += current_err
        max_err = max(max_err, current_err)
    error_val /= len(submission_results)
    return SubmissionPair(
        submission=submission,
        reproduction=reproduction,
    )

def get_submits() -> dict[str, Reproduction]:
    mails = json.loads((REPRODUCTION_PATH / "mails.json").read_text(encoding="utf-8"))
    reproductions: dict[str, Reproduction] = {}
    for team, mail in mails.items():
        reproduced_path = REPRODUCTION_PATH / str(team) / "reproduced.json"
        results = parse_result(reproduced_path.read_text(encoding="utf-8"))
        reproductions[str(team)] = Reproduction(
            team_name=str(team),
            mail=str(mail),
            results=results,
        )
    return reproductions

def output_appendix(
    records: list[CheckedRecord],
    time: datetime,
    path: Path,
    description: str | None = None,
    float_precision: int = 6,
):
    sort_fields = [
        ("avg", True),
        ("srcc", True),
        ("plcc", True),
        ("submit_time", False),
    ]
    sorted_records = sort_records(records, sort_fields)
    record_ranks = dense_ranks(sorted_records, ["avg", "srcc", "plcc"], float_precision=float_precision)

    def format_value(value) -> str:
        if isinstance(value, float):
            return f"{value:.{float_precision}f}"
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M %z")
        return str(value)

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        f.write("# Appendix\n\n")
        f.write(f"Update: {time.strftime('%Y-%m-%d %H:%M %z')}\n\n")
        if description:
            f.write(f"{description}\n\n")

        f.write("<table>\n")
        f.write("  <thead>\n")
        f.write("    <tr>\n")
        f.write('      <th rowspan="2">Rank</th>\n')
        f.write('      <th rowspan="2">Team Name</th>\n')
        f.write('      <th colspan="2">Avg</th>\n')
        f.write('      <th colspan="2">SRCC</th>\n')
        f.write('      <th colspan="2">PLCC</th>\n')
        f.write('      <th rowspan="2">Submit Time</th>\n')
        f.write('      <th rowspan="2">Avg Error</th>\n')
        f.write('      <th rowspan="2">Max Error</th>\n')
        f.write("    </tr>\n")
        f.write("    <tr>\n")
        f.write("      <th>Submitted</th>\n")
        f.write("      <th>Reproduced</th>\n")
        f.write("      <th>Submitted</th>\n")
        f.write("      <th>Reproduced</th>\n")
        f.write("      <th>Submitted</th>\n")
        f.write("      <th>Reproduced</th>\n")
        f.write("    </tr>\n")
        f.write("  </thead>\n")
        f.write("  <tbody>\n")

        for index, record in enumerate(sorted_records):
            f.write("    <tr>\n")
            f.write(f"      <td>{record_ranks[index]}</td>\n")
            f.write(f"      <td>{html.escape(format_value(record.team_name))}</td>\n")
            f.write(f"      <td>{html.escape(format_value(record.avg.submitted))}</td>\n")
            f.write(f"      <td>{html.escape(format_value(record.avg.reproduced))}</td>\n")
            f.write(f"      <td>{html.escape(format_value(record.srcc.submitted))}</td>\n")
            f.write(f"      <td>{html.escape(format_value(record.srcc.reproduced))}</td>\n")
            f.write(f"      <td>{html.escape(format_value(record.plcc.submitted))}</td>\n")
            f.write(f"      <td>{html.escape(format_value(record.plcc.reproduced))}</td>\n")
            f.write(f"      <td>{html.escape(format_value(record.submit_time))}</td>\n")
            f.write(f"      <td>{html.escape(format_value(record.avg_err))}</td>\n")
            f.write(f"      <td>{html.escape(format_value(record.max_err))}</td>\n")
            f.write("    </tr>\n")

        f.write("  </tbody>\n")
        f.write("</table>\n")

def main(
    host: str,
    username: str,
    password: str,
    port: int,
    ssl: bool,
    mailbox: str,
):
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    last_day = datetime(2026, 3, 22, tzinfo=ZoneInfo("Asia/Shanghai"))
    print(f"update leaderboard: {now.strftime('%Y-%m-%d %H:%M %z')}")
    mails = fetch_mails(host, username, password, last_day, port, ssl, mailbox)
    submissions = collect_submissions(mails, last_day)

    latest_submission: dict[str, Submission] = {}
    for s in submissions:
        if s.team_name not in latest_submission or s.submit_time > latest_submission[s.team_name].submit_time:
            latest_submission[s.team_name] = s
    print(f"submissions collected from {len(latest_submission)} teams")

    submit_teams = get_submits()
    submitted_submission = {
        team_name: submission_of(
            submission=submission,
            reproduction=submit_teams[team_name]
        )
        for team_name, submission in latest_submission.items()
        if team_name in submit_teams
        and submission.mail.strip().lower() == submit_teams[team_name].mail.strip().lower()
    }
    valid_submission: list[CheckedRecord] = []
    test_release: dict[str, float] = origin_mos()
    for team_name, submission in submitted_submission.items():
        if not submission.key_matched:
            print(f"[{team_name}] keys mismatched")
            continue
        team_path = REPRODUCTION_PATH / team_name
        team_path.mkdir(parents=True, exist_ok=True)
        submitted_path = team_path / "submitted.json"
        submitted_path.write_text(submission.submission.raw_result)
        record = submitted_submission[team_name].to_checked_record(test_release)
        valid_submission.append(record)

    print(f"valid submissions collected from {len(valid_submission)} teams")
    print("outputting final leaderboard")
    output_leaderboard(
        records=valid_submission,
        field_map={
            "Team Name": "team_name",
        },
        sort_fields=[
            ("avg", True),
            ("srcc", True),
            ("plcc", True),
            ("submit_time", False),
        ],
        include_rank=True,
        time=now,
        path=ROOT_PATH / "LEADERBOARD.md",
        float_precision=6,
        rank_fields=["avg", "srcc", "plcc"],
    )
    print("outputting appendix")
    output_appendix(
        records=valid_submission,
        time=now,
        path=ROOT_PATH / "APPENDIX.md",
        description="""
        Reproduced results may differ slightly due to hardware/software differences and are not used for ranking.
        """.strip(),
        float_precision=6,
    )
    print("finished")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fetch mails from IMAP")
    parser.add_argument("--config", required=True, help="Path to config json")
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    main(**cfg)
