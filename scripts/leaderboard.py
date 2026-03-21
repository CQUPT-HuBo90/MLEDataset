import argparse
import imaplib
from email.message import EmailMessage
import json
from dataclasses import dataclass
from datetime import datetime, timedelta
from email import policy
from email.parser import BytesParser
from email.utils import parsedate_to_datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import numpy
from scipy.stats import spearmanr, pearsonr

from common import ROOT_PATH, read_json, DATASET_FILENAME_DICT_PATH


@dataclass
class Record:
    team_name: str
    avg: float
    srcc: float
    plcc: float
    submit_time: datetime

@dataclass
class Submission:
    team_name: str
    submit_time: datetime
    results: dict[str, float]

    def to_record(self, origin: dict[str, float]) -> Record:
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
    
        return Record(
            team_name=self.team_name,
            avg=avg,
            srcc=srcc,
            plcc=plcc,
            submit_time=self.submit_time
        )


email_prefix = "[QoMEX 2026]"

def fetch_mails(
    host: str,
    username: str,
    password: str,
    time: datetime,
    port: int = 993,
    ssl: bool = True,
    mailbox: str = "INBOX",
) -> list[EmailMessage]:
    print("fetching mails")
    start = datetime.combine(time.date() - timedelta(days=1), datetime.min.time(), time.tzinfo) + timedelta(hours=20, minutes=30)
    end = datetime.combine(time.date(), datetime.min.time(), time.tzinfo) + timedelta(hours=21, minutes=30)

    if ssl:
        imap = imaplib.IMAP4_SSL(host, port)
    else:
        imap = imaplib.IMAP4(host, port)
    imap.login(username, password)
    imap.select(mailbox)

    since = (start.date() - timedelta(days=1)).strftime("%d-%b-%Y")
    before = (end.date() + timedelta(days=1)).strftime("%d-%b-%Y")

    status, data = imap.search(None,
        f'SINCE "{since}"',
        f'BEFORE "{before}"',
        f'SUBJECT "{email_prefix}"'
    )

    mails = []

    print("parsing mails")
    for num in data[0].split():
        status, msg_data = imap.fetch(num, "(RFC822)")
        raw = None
        for item in msg_data:
            if isinstance(item, tuple):
                raw = item[1]
                break
        if raw is None:
            continue

        msg = BytesParser(policy=policy.default).parsebytes(raw)

        mail_time = parsedate_to_datetime(msg["date"]).astimezone(time.tzinfo)

        if start <= mail_time <= end:
            mails.append(msg)

    imap.logout()
    print(f"fetched {len(mails)} mails")
    return mails

def collect_submissions(mails: list[EmailMessage], today: datetime) -> list[Submission]:
    print("collecting submissions")
    start = datetime.combine(today - timedelta(days=1), datetime.min.time(), today.tzinfo) + timedelta(hours=21)
    end = datetime.combine(today, datetime.min.time(), today.tzinfo) + timedelta(hours=20, minutes=59, seconds=59)

    submissions: list[Submission] = []

    for msg in mails:
        try:
            subject = msg["subject"]
            if not subject or not subject.startswith(email_prefix):
                continue

            team = subject[len(email_prefix):].strip()

            date = msg["date"]
            if not date:
                continue

            mail_time = msg["date"].datetime
            if mail_time.tzinfo is None:
                mail_time = mail_time.replace(tzinfo=today.tzinfo)

            mail_time = mail_time.astimezone(today.tzinfo)

            if not (start <= mail_time <= end):
                continue

            for part in msg.iter_attachments():
                if part.get_filename() != "result.json":
                    continue
                data = part.get_payload(decode=True).decode("utf-8")
                raw = json.loads(data)

                results = {r["id"]: r["mos"] for r in raw}

                submissions.append(Submission(
                    team_name=team,
                    submit_time=mail_time,
                    results=results
                ))
        except Exception as e:
            print("failed to parse submission", e)

    print(f"fetched {len(submissions)} submissions")
    return submissions


def output(records: list[Record], time: datetime, path: Path):
    records.sort(key=lambda r: (-r.avg, -r.srcc, -r.plcc, r.submit_time))
    path.parent.mkdir(parents=True, exist_ok=True)

    headers = ["Rank", "Team Name", "Avg", "SRCC", "PLCC", "Submit Time"]

    rows = []
    for i, r in enumerate(records, 1):
        rows.append([
            str(i),
            r.team_name,
            f"{r.avg:.6f}",
            f"{r.srcc:.6f}",
            f"{r.plcc:.6f}",
            r.submit_time.strftime('%Y-%m-%d %H:%M %z')
        ])

    col_widths = [
        max(len(headers[i]), max(len(row[i]) for row in rows))
        for i in range(len(headers))
    ]

    def format_row(row):
        return "| " + " | ".join(
            row[i].ljust(col_widths[i]) for i in range(len(row))
        ) + " |"

    with path.open("w", encoding="utf-8") as f:
        f.write("# Leaderboard\n\n")
        f.write(f"Update: {time.strftime('%Y-%m-%d %H:%M %z')}\n\n")
        f.write(format_row(headers) + "\n")
        f.write("|" + "|".join("-" * (w + 2) for w in col_widths) + "|\n")
        for row in rows:
            f.write(format_row(row) + "\n")

def origin_mos() -> dict[str, float]:
    filename_dict = read_json(DATASET_FILENAME_DICT_PATH)
    # origin: mask
    filename_dict = {r.split(".")[0]: filename_dict[r].split(".")[0] for r in filename_dict}

    origin_mos_data = read_json(ROOT_PATH / 'MLE-test-release.json')
    # origin: mos
    origin_mos_data = {filename_dict[r["id"]]: float(r["mos"]) for r in origin_mos_data}

    # mask: mos
    contest_test = read_json(ROOT_PATH / 'MLE-test.json')
    return {r["id"]: origin_mos_data[r["id"]] for r in contest_test}


def main(
    host: str,
    username: str,
    password: str,
    port: int,
    ssl: bool,
    mailbox: str,
):
    now = datetime.now(ZoneInfo("Asia/Shanghai"))
    print(f"update leaderboard: {now.strftime('%Y-%m-%d %H:%M %z')}")
    mails = fetch_mails(host, username, password, now, port, ssl, mailbox)
    submissions = collect_submissions(mails, now)

    latest_submission: dict[str, Submission] = {}
    for s in submissions:
        if s.team_name not in latest_submission or s.submit_time > latest_submission[s.team_name].submit_time:
            latest_submission[s.team_name] = s

    print(f"submissions collected from {len(latest_submission)} teams")
    test_release: dict[str, float] = origin_mos()
    records = [latest_submission[submission].to_record(test_release) for submission in latest_submission]
    print("outputing results")
    output(records, now, ROOT_PATH / 'LEADERBOARD.md')
    print("finished")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Fetch mails from IMAP")
    parser.add_argument("--config", required=True, help="Path to config json")
    args = parser.parse_args()
    cfg = json.loads(Path(args.config).read_text(encoding="utf-8"))
    main(**cfg)
