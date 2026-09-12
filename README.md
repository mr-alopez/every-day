# Every Day

A personal habit tracker, inspired by Simone Giertz's Every Day Calendar. A full
year shown at once as 365 cells; tapping today lights it up, and the reward is
watching an unbroken run accumulate.

## Rules

- Only **today** is tappable. Past and future cells are inert.
- Tapping again before midnight undoes a mis-tap. After midnight the day is fixed.
- No backfilling. A missed day stays dark.
- Optional **skip days** (long-press today), off by default. A skip bridges a
  streak without extending it, and is not counted as a lit day.

A thin rule in the left gutter traces each run of days down the year — bright
for the run you're currently in, dim for finished ones — so a streak reads as a
length rather than just a number. Isolated single days are left out.

Current streak has a grace period: it counts through yesterday and stays alive
all day, so it doesn't read zero every morning before you've tapped.

## Data

Everything lives in `localStorage` on the device — one key per habit, plus an
index. Nothing is sent anywhere; the app makes no network calls of its own.
Settings has JSON export/import for backup and for moving between devices.

Each calendar year is its own board. When the year turns, habits carry over with
a fresh grid and prior years stay readable through the year selector.

## Files

| | |
|---|---|
| `index.html` | the entire web app — vanilla HTML/CSS/JS, no dependencies, no build |
| `sw.js` | service worker, cache-first so the web version opens with no signal |
| `manifest.webmanifest` | standalone display, icons, theme |
| `icon*.png`, `icon.svg` | app icons |
| `src/bridge.js` | the only bundled file — exposes the notification plugin on `window` |
| `scripts/copy-web.mjs` | stages the web app into `www/` for the Android build |
| `android/` | Capacitor project for the native build |

The repo root is what GitHub Pages serves. The Android build is assembled into
`www/` (generated, gitignored) so the two never drift.

## Install

**Android app (with reminders):** see *Building the Android app* below.

**Android / iOS as a web app (no reminders):** open the Pages URL, then Chrome's
⋮ menu → Add to Home screen, or Safari's Share → Add to Home Screen. Launches
fullscreen and works offline. Updates land on the *next* launch — the service
worker serves the cached copy immediately and refreshes in the background.

## Reminders

A daily reminder is only available in the Android app. Web can't do it: the API
for scheduling a local notification, Notification Triggers, was abandoned, and
Web Push would need a server — which can't know whether you already tapped
today, because your days never leave the device.

The native build schedules a rolling 14-day window of one-shot notifications and
recomputes it whenever anything changes. A day's notification is dropped once
**every** habit is lit or skipped, so a reminder that does fire always means a
genuinely dark day. If you stop opening the app they keep arriving daily.

Alarms are inexact — expect a few minutes' drift, more if the phone is dozing.

## Building the Android app

Needs Android Studio (bundles the JDK) and Node.

```
npm install
npm run sync     # stage www/, bundle the bridge, sync the Android project
npm run open     # open in Android Studio, then Run
```

`npm run sync` after every change to `index.html` — the Android build uses the
copy in `www/`, not the repo root.

### Careful

- **Uninstalling the app deletes your history.** It lives in the WebView's
  localStorage. Export JSON regularly; that's the only backup.
- **Back up the signing keystore.** Without it a new build can't install over
  the old one, and reinstalling means uninstalling — which wipes your days.
- A debug build and a release build have different signatures, so moving from
  one to the other also wipes storage. Settle on the release build *before*
  importing real data.
