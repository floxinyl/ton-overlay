# ToN Overlay

A lightweight always-on-top overlay for **Terrors of Nowhere** on VRChat.

[![Overlay preview](https://github.com/floxinyl/ton-overlay/raw/main/assets/preview.png)](assets/preview.png)

---

## Requirements

- VRChat OSC must be enabled *(Settings → OSC)*
- [ToNSaveManager](https://github.com/ChrisFeline/ToNSaveManager) must be running with **WebSocket API Server enabled** *(Settings → WebSocket API Server)*

Without both of these the overlay won't receive any data.

---

## Download

[![Download](https://img.shields.io/badge/Download-.exe-blue?style=for-the-badge&logo=windows)](https://github.com/floxinyl/ton-overlay/releases/latest/download/ton_overlay.exe)

Or run the `.py` directly with Python 3.x if you prefer:
```
python ton_overlay.py
```

> Some antivirus tools flag PyInstaller-compiled executables as suspicious. This is a known false positive.

---

## Features

- Terror name + stun info panel *(click terror name)*
- Round type + **Next Round Predictor** — shows Classic / 50-50 / Special during Intermission
- Speed display with **6.50 m/s detection** for 8 Pages / Punished
- Session survival counter + round type history
- Full Unbound round terror lineup *(84 rounds)*
- **VR Mode** — click **VR** in the top-left to open a detectable window for XSOverlay

---

## 8 Pages / Punished Detection

During Intermission, hold **A or D** to strafe. If the next round is 8 Pages or Punished your movement speed will be capped at **6.50 m/s** instead of the normal 6.60 m/s. The overlay detects this automatically and shows a **8 Pages / Punished** label in the speed row.

---

## Changelog

### v3.5.0
- Next Round Predictor with host-change **(HC)** flag
- Smile Walker added, Distorted Yan Korean alias, Maze Things unbound rename
- April Fools event reverted (Punished / Sabotage back to real names)
- 6.50 m/s detection for 8 Pages / Punished during Intermission
- VR Mode window (XSOverlay compatible)

### v3.4.0 and earlier
See commit history.
