# Smart Tourist Crowd Prediction — Advanced Starter

## Features
- Responsive tourism dashboard
- Five destinations with date and time-slot selection
- Deterministic rule-based estimates (no random crowd results)
- Recommended lowest-estimate time slot
- Chart.js time-slot comparison
- SQLite prediction history and dashboard
- About page and input validation

## Accuracy note
Percentages are illustrative estimates created from baseline values and simple date/time adjustments. They are NOT live crowd data, verified forecasts, or a trained machine-learning model. A credible ML version needs historical visitor-count data and evaluation.

## Run on Windows / VS Code
1. Back up your existing project.
2. Extract this ZIP into a new folder (recommended) or carefully copy files after backup.
3. Open terminal in the extracted folder:
   ```powershell
   py -3.12 -m venv .venv
   .\.venv\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   python app.py
   ```
4. Open http://127.0.0.1:5000

The local SQLite database `tourism.db` is created automatically.

## Images
Copy your existing `goa.jpg`, `tajmahal.jpg`, `gateway.jpg`, `lonavala.jpg`, and `shaniwarwada.jpg` into `static/images/`.

## Suggested next research phase
Collect reliable historical visitor data, define the prediction target, compare a baseline with suitable ML models on held-out dates, and report metrics and limitations. Add MySQL/authentication only after requirements are finalized.
