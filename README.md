# pk_bingo_generator

Tkinter GUI app for generating printable Bingo cards and exporting them to a PDF (A4). It renders cards using Pillow and lays them out on PDF pages using ReportLab.

## What it does

- Generates a grid of random numbers (default: 5x5) using a “BINGO-style” column range when enabled.
- Lets you customize card size (cm), margins, cell spacing, optional fixed cell size, fonts, and colors.
- Supports a background image and an optional center image (placed in the middle cell on odd x odd grids).
- Shows an on-screen preview.
- Exports multiple cards into a single PDF, laid out across A4 pages.

Default assets live in `assets/` (backgrounds, center images, and the Luckiest Guy font).

## Requirements

- Python 3.x
- Tkinter (usually bundled with Python on Windows/macOS; on many Linux distros you may need to install `python3-tk` via the system package manager)
- Python packages are pinned in `requirements.txt`

## Setup

From this folder (`pk_bingo_generator/`):

1) Create and activate a virtual environment

- Windows (PowerShell):
	- `python -m venv .venv`
	- `./.venv/Scripts/Activate.ps1`
- macOS/Linux:
	- `python3 -m venv .venv`
	- `source .venv/bin/activate`

2) Install dependencies

- `python -m pip install --upgrade pip`
- `pip install -r requirements.txt`

## Run

- `python script.py`

The app opens a window where you can tweak parameters and then:

- **Podgląd**: render a preview of a single card
- **Generuj PDF**: choose a save location and generate a multi-card PDF

## Build a Windows .exe (PyInstaller)

From this folder (`pk_bingo_generator/`) with the venv activated:

- `pip install pyinstaller`
- `pyinstaller --noconsole --onefile --clean --name pk-bingo-generator --add-data "assets;assets" script.py`

Result:

- `dist/pk-bingo-generator.exe`

## Notes

- The default paths in the UI point to `./assets/karta.png`, `./assets/kwadrat_kolor_cut_no_border.png`, and `./assets/Luckiest_Guy/LuckiestGuy-Regular.ttf`.
- During PDF generation, the app creates temporary PNG files named like `_tmp_card_0.png` in the current working directory and deletes them after placing them into the PDF.