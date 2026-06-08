# ToN Overlay

A desktop overlay for **Terrors of Nowhere** on VRChat.

Displays live game info on a compact always-on-top HUD: current terror, round type, movement speed, session survivals, and round history. Click the terror name for full stun info. Click the round type for session stats.

[![Overlay preview](https://github.com/floxinyl/ton-overlay/raw/main/assets/preview.png)](assets/preview.png)

Desktop only.

> **Work in progress.** Terror data is maintained manually and may be outdated or incorrect — the game updates frequently. If something is wrong, open an issue.

---

## Requirements

- Python 3.x (no extra packages needed) — only required if running the `.py` directly
- [ToNSaveManager](https://github.com/ChrisFeline/ToNSaveManager) running with **WebSocket API Server enabled** (Settings → WebSocket API Server → toggle on)
- VRChat with OSC enabled (Settings → OSC → toggle on)

---

## Download

[![Download](https://img.shields.io/badge/Download-.exe-blue?style=for-the-badge&logo=windows)](https://github.com/floxinyl/ton-overlay/releases/latest/download/ton_overlay.exe)

or go to the [Releases](https://github.com/floxinyl/ton-overlay/releases) page and grab the latest version.

Two options are available:

- **ton_overlay.exe** — no Python needed, just download and run. Windows only.
- **ton_overlay.py** — run with Python 3.x if you prefer the source directly.

> **Antivirus warning:** The `.exe` is compiled from Python using PyInstaller. Some antivirus programs flag PyInstaller executables as suspicious by default even when the code is completely clean. This is a known false positive with compiled Python apps. If your antivirus blocks it, run the `.py` source file directly instead — that requires Python 3.x but no extra packages.

---

## How to run

**Using the exe (recommended)**

1. Start VRChat and enable OSC under Settings → OSC.
2. Start ToNSaveManager and toggle on WebSocket API Server in its settings. Without this the overlay won't receive terror or round data.
3. Run `ton_overlay.exe`.

**Using the Python script**

1. Same steps 1 and 2 as above.
2. Open a terminal in the folder where you saved the file and run:

```
python ton_overlay.py
```

The overlay appears on screen. Drag it wherever you want.

---

## Using the panels

**Terror info panel** — A dot appears next to the terror name when info is available. Click the terror name to open a draggable panel showing the terror's stun status and notes. Click again to close. On multi-terror rounds it shows a block for each terror. On Unbound rounds it shows the full terror lineup for that specific round instead.

**Session round counter** — A dot appears next to the round type label once rounds have been counted. Click the round type label to open a draggable panel listing every round type seen this session and how many times it appeared. Updates live. Click again to close.

---

## Features

- Terror name and stun info for all terrors (click terror name to open panel)
- Seven stun categories: Stunnable, Not Stunnable, Avoid, Do Not Stun, Partial, Conditional, Teleports on Stun
- Phase and add breakdowns for complex terrors
- **Next Round Predictor** — during Intermission the round row shows what type comes next: Classic (white), 50/50 (orange), or Special (red), based on the in-game loop-counter state machine
- Host-change detection: if the lobby host changes mid-session, the predictor flags the forced Special with **(HC)**
- Round type display with session round count popup (click the round label)
- Last 4 rounds history
- Fog round countdown timer
- Speed display in m/s
- Session survival counter
- Lisa auto-reveal on Alternate rounds after 11 seconds
- Full Unbound round terror list (84 rounds)
- Multi-terror support for Bloodbath, Midnight, and Double Trouble
- No external dependencies — standard library only

---

## Notes

- Tested on Windows. Should work on any OS with Python and tkinter installed.
- Terror data sourced from [terror.moe](https://terror.moe).
- All panels are draggable. Close the overlay with the X button on the main window.

---

## Changelog

### v3.5.0
- **April Fools event ended** — Randomizer reverts to Punished, Classic.exe reverts to Sabotage. Detection and display updated accordingly.
- **Next Round Predictor** — during Intermission, the round row now shows what type comes next (Classic / 50-50 / Special) based on the loop-counter state machine. Special in red, 50/50 in orange, Classic in white. Host-change override (MASTER_CHANGE) appends **(HC)** to the prediction.
- **Hijack Round Settings** (Ctrl+Click anywhere on overlay) — configures Ghost, Punished, 8 Pages and RUN. Two global toggles: *After State* (always → 50/50, or slot-dependent) and *Slot Behaviour* (Normal only / Any slot). Settings persist to `ton_overlay_config.json`.
- **VR Mode** — click the **VR** button (top-left of speed row, turns blue when active) to open a separate detectable window for use with XSOverlay. Shows terror name + stun status, round type + next round prediction, speed, and session round counts in a compact two-column layout. Terror names always display on one line. Unbound rounds show their terror lineup. Native title bar hidden; window is still capturable by XSOverlay via its OS title.
- **Smile Walker** — new alternate terror added to the database (replaces Apathy). Conditional stun: tase in phase 1 holds for 5s (can still leap); stun only works during first second of Laugh & Leap. Enrages at 60s.
- **Distorted Yan** — added Korean alt-name alias (`얀샋ㄷ요무`) so the terror is detected correctly under either name.
- **Unbound round 35** renamed from *Seekers (3x Legs)* to *Maze Things (3x Maze Thing)* following the in-game rename.

### v3.4.0
- Unbound rounds: terror info panel shows "Waiting for round to reveal..." for the first 11 seconds, then auto-updates to the actual round details.
- Added Maze Thing to the terror database (renamed from Legs).
- Session Rounds panel now sorted highest count to lowest.
- Classic → Alternate upgrade: if a round changes from Classic to Alternate without an Intermission in between, the history entry and session count are corrected in-place.
- Tiffany: added note that she starts at ~110s left.

### v3.3.1 and earlier
See commit history.

---

## Version

v3.5.0
