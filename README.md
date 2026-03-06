# COMP-4433-Proj-2

Dog Breeds Dashboard — an interactive Dash application for exploring dog breed data from The Dog API.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python -m app.main
```

Then open http://127.0.0.1:8050/ in your browser.

## Data

Uses `data/breeds.csv`. Regenerate with `python -m app.getdata` (requires `DOG_API_KEY` env var).