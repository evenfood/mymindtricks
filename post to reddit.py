"""Post the day's scheduled meme to a subreddit as a native image post.

Reads a CSV schedule, finds the row matching today's date (in a configurable
timezone), submits the image, and then adds an optional comment plus an
optional stickied "explainer" comment. Designed to run once per day from a
GitHub Actions cron job.

All credentials are read from environment variables (GitHub Actions Secrets).
Nothing sensitive is ever stored in the repository.
"""

from __future__ import annotations

import csv
import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

import praw
from prawcore.exceptions import PrawcoreException


def require_env(name: str) -> str:
    """Return a required environment variable, or exit with a clear message."""
    value = os.environ.get(name)
    if not value:
        sys.exit(f"ERROR: missing required environment variable: {name}")
    return value


# Non-secret configuration (set in the workflow file, with sensible defaults).
SUBREDDIT_NAME = require_env("SUBREDDIT")
SCHEDULE_PATH = Path(os.environ.get("SCHEDULE_PATH", "schedule.csv"))
IMAGE_DIR = Path(os.environ.get("IMAGE_DIR", "images"))
TIMEZONE = os.environ.get("TIMEZONE", "UTC")


def build_reddit_client() -> praw.Reddit:
    """Create an authenticated Reddit client from environment credentials."""
    return praw.Reddit(
        client_id=require_env("REDDIT_CLIENT_ID"),
        client_secret=require_env("REDDIT_CLIENT_SECRET"),
        username=require_env("REDDIT_USERNAME"),
        password=require_env("REDDIT_PASSWORD"),
        user_agent=os.environ.get(
            "REDDIT_USER_AGENT", "daily-meme-scheduler by u/unknown"
        ),
    )


def today_string() -> str:
    """Return today's date as YYYY-MM-DD in the configured timezone."""
    return datetime.now(ZoneInfo(TIMEZONE)).strftime("%Y-%m-%d")


def find_todays_row(schedule_path: Path, target_date: str) -> dict[str, str] | None:
    """Return the schedule row whose 'date' equals target_date, or None."""
    with schedule_path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("date", "").strip() == target_date:
                return row
    return None


def already_posted(reddit: praw.Reddit, title: str) -> bool:
    """Guard against double-posting if the job is manually re-run the same day.

    Checks the bot account's own recent submissions for a matching title. This
    needs no write-back to the repo, so the workflow stays read-only on Git.
    """
    me = reddit.user.me()
    for submission in me.submissions.new(limit=25):
        if submission.title.strip() == title.strip():
            return True
    return False


def main() -> None:
    target_date = today_string()
    print(f"Scheduler running for {target_date} (timezone: {TIMEZONE}).")

    if not SCHEDULE_PATH.exists():
        sys.exit(f"ERROR: schedule file not found: {SCHEDULE_PATH}")

    row = find_todays_row(SCHEDULE_PATH, target_date)
    if row is None:
        # No content scheduled for today is a normal, non-error state.
        print(f"No scheduled post for {target_date}. Nothing to do.")
        return

    title = row["title"].strip()
    image_path = IMAGE_DIR / row["image"].strip()
    if not image_path.exists():
        sys.exit(f"ERROR: image file not found: {image_path}")

    reddit = build_reddit_client()
    subreddit = reddit.subreddit(SUBREDDIT_NAME)

    if already_posted(reddit, title):
        print(f"A post titled '{title}' already exists. Skipping (no duplicate).")
        return

    # Flair is optional: only pass it through when the CSV cell is non-empty.
    flair_id = row.get("flair_id", "").strip() or None

    print(f"Submitting image post: {title}")
    submission = subreddit.submit_image(
        title=title,
        image_path=str(image_path),
        flair_id=flair_id,
    )
    print(f"Posted: https://reddit.com{submission.permalink}")

    # Optional first comment (the casual explainer).
    comment_text = row.get("comment", "").strip()
    if comment_text:
        submission.reply(body=comment_text)
        print("Added the first comment.")

    # Optional pinned explainer comment. Pinning needs mod permission on the
    # sub; if the bot is not a mod, we keep the comment and skip the sticky.
    pinned_text = row.get("pinned_comment", "").strip()
    if pinned_text:
        pinned = submission.reply(body=pinned_text)
        try:
            pinned.mod.distinguish(how="yes", sticky=True)
            print("Added and pinned the explainer comment.")
        except PrawcoreException as error:
            print(f"Explainer comment added, but could not pin it ({error}).")


if __name__ == "__main__":
    try:
        main()
    except PrawcoreException as error:
        # Surface a non-zero exit so GitHub marks the run failed and emails you.
        sys.exit(f"ERROR: a Reddit API call failed: {error}")
