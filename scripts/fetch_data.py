#!/usr/bin/env python3
"""Fetch the Pitchless applications Google Sheet and build data.json for the funnel site."""
import csv
import io
import json
import urllib.request
from datetime import datetime, timezone

SHEET_ID = "18JeWMZA968ecOfQN2ypQPjn93Bdxz6ehRyjJXfHljco"
CSV_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid=0"

# Test submissions to exclude from the funnel
TEST_EMAILS = {"jayshankarpure@gmail.com", "a@gmail.com"}

# Co-founders who applied together but don't have their own sheet row
EXTRA_PEOPLE = [
    {"name": "Pablo Albaladejo", "city": "Madrid", "submitted": "", "source": "",
     "stage": "Payment Sent"},
    {"name": "Issam Aarida", "city": "Madrid", "submitted": "", "source": "",
     "stage": "Payment Sent"},
]

# Startup pairings (matched on first word of Full name)
TEAMS = {
    "pablo": "Maria Eugenia", "maria": "Pablo",
    "issam": "Javier", "javier": "Issam",
    "dylan": "Quinton", "quinton": "Dylan",
}


def sent(row, idx, col):
    i = idx.get(col)
    return i is not None and len(row) > i and row[i].strip() != ""


def main():
    raw = urllib.request.urlopen(CSV_URL, timeout=60).read().decode("utf-8")
    rows = list(csv.reader(io.StringIO(raw)))
    header, data = rows[0], [r for r in rows[1:] if any(c.strip() for c in r)]

    email_i = header.index("Email")
    data = [r for r in data
            if len(r) > email_i and r[email_i].strip().lower() not in TEST_EMAILS]

    # Header has duplicate names (Q1 /10 etc.); map by first occurrence which is
    # fine for the email/status columns we use.
    idx = {}
    for i, name in enumerate(header):
        idx.setdefault(name.strip(), i)

    def count(col):
        return sum(1 for r in data if sent(r, idx, col))

    applied = len(data)
    interview = count("Interview Invite")
    accepted = count("Accepted Email")
    payments = count("Payments Email")
    onboarded = count("Onboarding Email")
    rejected = count("Rejected Email")
    waitlist = count("Waitlist Email")

    people = []
    for r in data:
        def get(col):
            i = idx.get(col)
            return r[i].strip() if i is not None and len(r) > i else ""

        if get("Onboarding Email"):
            stage = "Onboarded"
        elif get("Payments Email"):
            stage = "Payment Sent"
        elif get("Accepted Email"):
            stage = "Accepted"
        elif get("Rejected Email"):
            stage = "Rejected"
        elif get("Waitlist Email") and get("Interview Invite"):
            stage = "Interview"
        elif get("Waitlist Email"):
            stage = "Waitlisted"
        elif get("Interview Invite"):
            stage = "Interview"
        else:
            stage = "Applied"
        people.append({
            "name": get("Full name"),
            "city": get("City"),
            "submitted": get("Submitted at"),
            "source": get("utm_source"),
            "stage": stage,
        })

    people.extend(EXTRA_PEOPLE)
    extra_payments = sum(1 for p in EXTRA_PEOPLE if p["stage"] == "Payment Sent")
    applied += len(EXTRA_PEOPLE)
    interview += len(EXTRA_PEOPLE)
    accepted += len(EXTRA_PEOPLE)
    payments += extra_payments

    for p in people:
        first = p["name"].split()[0].lower() if p["name"] else ""
        p["team"] = TEAMS.get(first, "")

    out = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
        "funnel": [
            {"stage": "Applied", "count": applied},
            {"stage": "Interview", "count": interview},
            {"stage": "Accepted", "count": accepted},
            {"stage": "Payment Sent", "count": payments},
            {"stage": "Onboarded", "count": onboarded},
        ],
        "side": {"rejected": rejected, "waitlisted": waitlist},
        "people": people,
    }
    with open("data.json", "w") as f:
        json.dump(out, f, indent=2)
    print(f"data.json written: {applied} applied, {interview} interview, "
          f"{accepted} accepted, {payments} payments, {onboarded} onboarded")


if __name__ == "__main__":
    main()
