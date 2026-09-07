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
| `index.html` | the entire app — vanilla HTML/CSS/JS, no dependencies, no build |
| `sw.js` | service worker, cache-first so it opens with no signal |
| `manifest.webmanifest` | standalone display, icons, theme |
| `icon*.png`, `icon.svg` | app icons |

## Install on iOS

Open the Pages URL in Safari, then Share → Add to Home Screen. It launches
fullscreen and works offline.

Updates land on the **next** launch: the service worker serves the cached copy
immediately and refreshes in the background, so a new deploy needs one extra
open to appear.
