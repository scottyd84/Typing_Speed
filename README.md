# Typing Speed Test

A desktop typing-speed test built with **Python** and **PyQt6**. Type the
displayed passage as accurately as you can — characters light up green when
correct and red when wrong, and your words-per-minute, accuracy, and elapsed
time update live.

![Python](https://img.shields.io/badge/python-3.11%2B-blue) ![PyQt6](https://img.shields.io/badge/GUI-PyQt6-41cd52)

## Features

- **Live feedback** — each character you type is coloured green (correct) or
  red (incorrect) against the target passage.
- **Real-time stats** — WPM, accuracy, and a running timer that starts on your
  first keystroke.
- **15 random passages** — a new one is picked each round.
- **Restart** any time for a fresh passage.
- Clean dark theme (Catppuccin-inspired palette).

## Requirements

- **Python 3.11+**
- **PyQt6** (`>=6.7`)

## Installation & running

This project uses [`uv`](https://docs.astral.sh/uv/) for dependency management
(a `uv.lock` is committed).

### With uv (recommended)

```bash
uv run main.py
```

`uv` will create the environment and install dependencies from the lockfile
automatically.

### With pip

```bash
python -m venv .venv
source .venv/bin/activate        # on Windows: .venv\Scripts\activate
pip install "pyqt6>=6.7"
python main.py
```

## How it works

- **WPM** is calculated the standard way — correct characters ÷ 5, divided by
  elapsed minutes — so it reflects accurate keystrokes rather than raw speed.
- **Accuracy** is the percentage of typed characters that match the passage.
- The timer starts on your first keypress and stops when the passage is
  complete. You can't type past the end of the passage.

## Project layout

| File | Purpose |
| --- | --- |
| `main.py` | Entry point — creates the `QApplication` and shows the window. |
| `app.py` | The `TypingApp` window and `TypingWidget` (UI, stats, game logic). |
| `texts.py` | The collection of practice passages. |
| `pyproject.toml` | Project metadata and dependencies. |
| `uv.lock` | Pinned dependency lockfile for reproducible installs. |
