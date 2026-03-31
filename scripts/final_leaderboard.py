import argparse
import json
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo
from datetime import datetime
from leaderboard import fetch_mails, collect_submissions, Submission, origin_mos, output, parse_result
from common import ROOT_PATH, REPRODUCTION_PATH

@dataclass
class Reproduction:
    team_name: str
    mail: str
    results: dict[str, float]

@dataclass
class SubmissionPair:
    reproduction: Reproduction
    submission: Submission

    def check(self) -> bool:
        print(f"[{self.submission.team_name}] checking submission")

        submission_results = self.submission.results
        reproduction_results = self.reproduction.results
        if submission_results.keys() != reproduction_results.keys():
            print(f"[{self.submission.team_name}] keys mismatched")
            return False

        is_mismatched = False
        for key, submission_value in submission_results.items():
            exponent = Decimal(str(submission_value)).as_tuple().exponent
            decimal_places = -exponent if isinstance(exponent, int) and exponent < 0 else 0
            rounded_reproduction_value = round(reproduction_results[key], decimal_places)
            if rounded_reproduction_value != submission_value:
                print(f"[{self.submission.team_name}] value mismatched of '{key}', submitted: {submission_value}, reproduced: {rounded_reproduction_value}")
                is_mismatched = True
        if is_mismatched:
            return False

        print(f"[{self.submission.team_name}] checking submission passed")
        return True

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
        team_name: SubmissionPair(
            submission=submission,
            reproduction=submit_teams[team_name]
        )
        for team_name, submission in latest_submission.items()
        if team_name in submit_teams
        and submission.mail.strip().lower() == submit_teams[team_name].mail.strip().lower()
    }
    for team_name, submission in submitted_submission.items():
        team_path = REPRODUCTION_PATH / team_name
        team_path.mkdir(parents=True, exist_ok=True)
        submitted_path = team_path / "submitted.json"
        submitted_path.write_text(submission.submission.raw_result)
    valid_submission = [
        submitted_submission[team_name].submission for team_name in submitted_submission
        if submitted_submission[team_name].check()
    ]

    print(f"valid submissions collected from {len(valid_submission)} teams")
    test_release: dict[str, float] = origin_mos()
    records = [submission.to_record(test_release) for submission in valid_submission]
    print("outputing reproduction")
    output(records, now, ROOT_PATH / 'LEADERBOARD.md')
    print("finished")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fetch mails from IMAP")
    parser.add_argument("--config", required=True, help="Path to config json")
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    main(**cfg)
