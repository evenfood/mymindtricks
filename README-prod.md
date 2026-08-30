# Daily Educational Meme Scheduler

A small personal script that posts **one educational meme per day** to a single
subreddit its owner moderates. The subreddit is dedicated to explaining
cognitive biases, illusions, and manipulation tactics — each post teaches one
named concept in meme form, with a plain-language explanation and its formal
scientific name in the comments.

---

## For Reddit Data API reviewers

**Purpose:** Automate a consistent daily educational post to one community I
moderate. Nothing else.

**Exact scope — this is everything the app does:**
1. Once per day, submit **one image post** (title + image) to the single
   subreddit I moderate.
2. Add **one top-level comment** with a short plain-language explanation.
3. Add and sticky **one "explainer" comment** naming the psychological concept.

**What it explicitly does NOT do:**
- Does not operate in any subreddit other than my own.
- Does not read, collect, store, or process other users' data.
- Does not send direct messages.
- Does not vote, manipulate karma, or touch any ranking/safety mechanism.
- Does not scrape, cross-post, or post identical content across subreddits.
- Does not use Reddit data for advertising, resale, or AI/ML training.

**Access profile:**
- App type: **script** (personal use), authenticated as the account that
  moderates the target subreddit.
- Volume: roughly **2–4 API calls per day**. One post, up to two comments.
- Content: **original**, created by me. Non-commercial.
- Account use: a **dedicated account** used solely for this app (no mixed use).

**Compliance:** This app is built to the Responsible Builder Policy — dedicated
app account, single-subreddit scope, honest labeling, least-privilege
permissions (Manage Posts & Comments and Manage Flair only), and no prohibited
activities. Access is used solely to post content to a community I moderate.

**Why the Data API rather than Devvit:** I develop and operate entirely from a
mobile device with no local Node.js/terminal environment, so I cannot run the
Devvit CLI to build, test, and deploy. This single-daily-post use case is fully
served by a lightweight hosted script using the Data API via PRAW.

---

## How it works

- `post_to_reddit.py` — reads a schedule file, finds today's row, submits the
  image post, then adds the two comments. Credentials come only from
  environment variables; nothing sensitive is stored in the repo.
- `schedule.csv` — one row per day: date, title, image filename, comment,
  pinned comment, optional flair.
- `.github/workflows/daily-post.yml` — a once-daily GitHub Actions cron that
  runs the script. Also runnable on demand.
- `images/` — the image assets referenced by the schedule.

The script is idempotent: before posting it checks the account's recent
submissions by title and skips if today's post already exists, so a re-run
cannot create a duplicate.

## Configuration

All secrets are supplied via GitHub Actions Secrets (never committed):
`REDDIT_CLIENT_ID`, `REDDIT_CLIENT_SECRET`, `REDDIT_USERNAME`,
`REDDIT_PASSWORD`. Non-secret settings (`SUBREDDIT`, `TIMEZONE`) live in the
workflow file. See `README.md` for full setup steps.

## License / use

Personal, non-commercial. Original educational content.
