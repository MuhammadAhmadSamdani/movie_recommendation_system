# Movie Recommendation System


**Project**
- **Description:** A small Python project that loads movie metadata and provides recommendation/search features and a simple app interface.

**Prerequisites**
- Python 3.8+
- Git (optional)

**Setup**
1. Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Ensure `movies_metadata.csv` is in the project root (already included).

**Run**
- To start the app (if `app.py` provides the UI/API):

```powershell
python app.py
```

- Or run the main script:

```powershell
python main.py
```

(If your project uses a different entrypoint, run that file.)

**Tests**
- Tests are in the `tests/` folder. Run them with `pytest`:

```powershell
pip install pytest
pytest -q
```

**Files & Structure**
- `app.py` : Application entry / web UI (if present).
- `main.py`: Secondary entry or CLI runner.
- `model.py`: Recommendation / ML logic.
- `movieflix_database.py`: DB helpers.
- `movies_metadata.csv`: Movie dataset used for recommendations.
- `requirements.txt`: Python dependencies.
- `tests/`: Unit tests for core features.

**Notes**
- Update `requirements.txt` if you add packages.
- If you need a specific DB or API keys, add them to environment variables and document here.

**Contributing**
- Create an issue or PR for changes. Keep changes focused and add/update tests.

**License**
- Add a license file if you want to open-source this project.
