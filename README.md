# Daily Reddit Meme Scheduler — iPhone Setup

Free forever. Posts one native **image** post per day to your subreddit, adds a
first comment, and pins an "actual name" explainer comment. Runs on GitHub
Actions (free). No computer required — but two settings screens need **Safari in
Desktop mode** (tap the **ᴀA** icon in the address bar → *Request Desktop
Website*). The GitHub app itself does not expose Secrets, so use Safari there.

Files in this repo:
- `post_to_reddit.py` — the poster
- `requirements.txt` — dependency (PRAW)
- `schedule.csv` — one row per day (date, title, image, comment, pinned_comment, flair_id)
- `.github/workflows/daily-post.yml` — the daily timer
- `images/` — put `day01.jpg` … `day28.jpg` here (names must match the CSV)

---

## PART A — Reddit (in Safari)

**A1. Create a dedicated bot account (recommended).**
Sign up for a second Reddit account, e.g. `u/YourSubBot`. Use a strong, unique
password. **Do NOT enable two-factor auth on this account** — automated login
cannot pass a rotating 2FA code. Your main account keeps its 2FA; this throwaway
only ever mods your one sub, so its blast radius is tiny.

**A2. Make the bot a moderator of your sub.**
From your **main** account: your subreddit → *Mod Tools* → *Moderators* →
*Invite* → enter the bot's username → grant **Manage Posts & Comments** and
**Manage Flair** (nothing else — least privilege). Then log in as the bot and
**accept** the invite. (Pinning the explainer comment needs this.)

**A3. Create a Reddit API app.**
Safari (Desktop mode) → `https://www.reddit.com/prefs/apps` while logged in as
the **bot** → *create another app…* →
- type: **script**
- name: `daily-meme`
- redirect uri: `http://localhost:8080`
- *create app*

Now copy two values:
- **client id** = the string just under the app name ("personal use script")
- **secret** = the value next to "secret"

---

## PART B — GitHub (Safari + GitHub app both fine)

**B1.** Create a free account at `https://github.com` if you don't have one.

**B2. Make a new PRIVATE repository**, e.g. `reddit-meme-scheduler`.

**B3. Add the four text files.** In the repo: *Add file → Create new file*.
For the workflow, type the full path as the filename:
`.github/workflows/daily-post.yml` — typing the slashes creates the folders.
Paste each file's contents, then *Commit*. Repeat for `post_to_reddit.py`,
`requirements.txt`, and `schedule.csv`.

**B4. Upload your images.** *Add file → Upload files* → pick from Photos.
Name them exactly `day01.jpg` … `day28.jpg` so they match `schedule.csv`.
(If yours are `.png`, change the extensions in the CSV's `image` column to match.)

**B5. Edit two values in the workflow.** Open `.github/workflows/daily-post.yml`
→ pencil icon → set:
- `SUBREDDIT: "YourSubredditName"` (no `r/`)
- `TIMEZONE: "Europe/London"` (or `America/New_York`, `Asia/Kolkata`, …)
Also set the post time in the `cron:` line — it is in **UTC**.
`"0 18 * * *"` = 18:00 UTC daily. Convert your desired local time to UTC.

**B6. Add your secrets (Safari, Desktop mode).**
Repo → *Settings* → *Secrets and variables* → *Actions* →
*New repository secret*. Add these four, one at a time:
- `REDDIT_CLIENT_ID`
- `REDDIT_CLIENT_SECRET`
- `REDDIT_USERNAME` (the bot's username, no `u/`)
- `REDDIT_PASSWORD` (the bot's password)

**B7. Enable Actions** if prompted: the *Actions* tab → enable workflows.

---

## PART C — Test it

**C1.** *Actions* tab → **Daily Reddit meme** → *Run workflow* → *Run*.
**C2.** Tap the run → open the *post* job → read the logs.
- Green check = it posted. Go look at your sub.
- Red X = read the error. Almost always one of: a mistyped secret, an image
  filename that doesn't match the CSV, or the wrong subreddit name.

**C3. Set real dates.** Edit `schedule.csv` so the first `date` is your actual
start day; the rest are sequential. Any date with no row is simply skipped.

---

## Good to know (for running all year)

- **Cost:** private repos get generous free Actions minutes; one ~1-minute run
  per day is a tiny fraction of them. Effectively free.
- **Timing:** cron can fire a few minutes late under load — fine for memes.
  A scheduled post still lives or dies on upvotes in its first 30–60 minutes,
  so pick a time your audience is online and drop in to reply early.
- **The 60-day rule:** GitHub auto-pauses scheduled workflows if a repo has NO
  activity for 60 days. Committing new memes counts as activity, so a weekly
  upload keeps it alive. If it ever pauses, one manual *Run workflow* re-enables it.
- **Re-running is safe:** the script checks your recent posts by title and skips
  if today's is already up, so a manual re-run won't double-post.
- **Adding more days:** just append rows to `schedule.csv` and upload more
  images. It scales from 28 to 365+ with no other change.

---

## Full-year schedule (optional, recommended for all-year posting)

Use **`schedule-full-year.csv`** instead of `schedule.csv` — same columns, but
364 rows (a full year) that rotate **52 concepts**, each appearing 7 times,
evenly spaced ~52 days apart. This means you only create **52 reusable images**
(`meme01.jpg` … `meme52.jpg`) instead of 365.

To use it:
1. Upload your 52 images to `images/`, named `meme01.jpg` … `meme52.jpg`.
2. See **`image-concept-map.csv`** for what each numbered image should depict.
3. Either rename `schedule-full-year.csv` to `schedule.csv`, or set
   `SCHEDULE_PATH: "schedule-full-year.csv"` in the workflow's `env:` block.
4. Edit the first `date` to your real start day (the rest follow in sequence).

Because each image is reused every 52 days, swap a few out occasionally to keep
the sub fresh — but nothing breaks if you don't.

---

## Failure ping (optional — you're already covered by default)

GitHub **emails you automatically** whenever a scheduled run fails. No setup.

If you'd rather get a faster push, add a Discord ping (easy on iPhone):
1. In any Discord server you own: *Server Settings → Integrations → Webhooks →
   New Webhook → Copy Webhook URL*.
2. In your repo Secrets, add a secret named `DISCORD_WEBHOOK` with that URL.
The workflow already has the step; it fires only on failure, only if that
secret exists.

---

## Preparing images on iPhone (no computer)

1. Save your finished memes into the **Files** app (Long-press → Save to Files,
   or export from your design app to Files).
2. Rename each to match the CSV: `day01.jpg` … or `meme01.jpg` … (tap the name
   in Files to rename).
3. If a file is **HEIC**, convert to JPG first: open in Photos → share →
   *Save as File* often yields JPG, or use a one-tap "Convert Image" Shortcut.
4. In GitHub, *Add file → Upload files* → pick from **Files** (cleaner than
   Photos, which auto-names `IMG_####`).
