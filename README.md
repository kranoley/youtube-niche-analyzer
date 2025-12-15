


#  YouTube Niche Analyzer


![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![CustomTkinter](https://img.shields.io/badge/UI-CustomTkinter-orange)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows-lightgrey)

---

##  Screenshots

<div align="center">
  <img src="https://github.com/user-attachments/assets/2fe537e3-1a46-40c3-803b-1905ec79946c" alt="Input Query" width="400"/>
  <img src="https://github.com/user-attachments/assets/65a69e2c-1eb4-4058-af8e-3d6a33f433d1" alt="Results" width="400"/>
</div>

---

##  Features

-  Search YouTube videos by keyword
-  Auto-calculate **SEO score** for each video
-  Compute a **Niche Opportunity Score** using:

---

##  Installation

1. [Download source code.](https://github.com/kranoley/youtube-niche-analyzer/archive/refs/heads/main.zip)

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   python main.py
   ```

---

##  Important Notes
- YouTube may temporarily throttle frequent requests. Avoid rapid repeated analyses.
- Use responsibly and in compliance with YouTube’s [Terms of Service](https://www.youtube.com/t/terms).

---

## Development

Install dependencies (recommended in a virtualenv):

```bash
pip install -r requirements.txt
```

Run the GUI:

```bash
python main.py
```

Run tests (without pytest installed):

```bash
python scripts/run_tests.py
```

Or, if you have pytest available:

```bash
pytest -q
```

## Recent changes

- Added validation, retries and logging to `core/youtube_api.py`.
- Hardened `core/analyzer.py` with type checks and defensive handling.
- Added unit tests and a lightweight test runner at `scripts/run_tests.py`.
- Improved UI input validation and added Export/Cancel actions to `ui/app.py`.

Made with ❤️



