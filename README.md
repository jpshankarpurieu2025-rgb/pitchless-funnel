# Pitchless Funnel Dashboard

Live funnel of Pitchless applications, auto-synced from the [applications Google Sheet](https://docs.google.com/spreadsheets/d/18JeWMZA968ecOfQN2ypQPjn93Bdxz6ehRyjJXfHljco/edit) every hour via GitHub Actions.

## How it works

- `scripts/fetch_data.py` pulls the sheet as CSV and computes funnel stages from the email-status columns (Interview Invite, Accepted, Payments, Onboarding, Rejected, Waitlist) into `data.json`.
- `.github/workflows/update.yml` runs hourly (and on push / manual dispatch), commits the fresh `data.json`, and redeploys the static site to GitHub Pages.
- `index.html` renders the funnel — no build step, no dependencies.

Run manually: **Actions → Update funnel data → Run workflow**.
