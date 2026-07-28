# Growth GPT — Digital Twin Marketing Simulator

AI-powered growth marketing intelligence system. Submit a campaign, and
Growth GPT generates AI digital-twin customer personas, simulates their
reactions using Gemini, predicts engagement/conversion, and gives you
concrete recommendations — before you spend on live advertising.

## Modules

| Module | What it does |
|---|---|
| Campaign Analysis | Extracts objective, tone, and key themes from your campaign copy |
| Digital Twin Generator | Creates 5 distinct virtual customer personas from your target audience |
| Customer Behaviour Simulation | Each twin reacts in its own voice — quote, emotion, engagement, objection |
| Growth Prediction | Engagement score, conversion probability, sentiment breakdown, growth potential |
| Marketing Recommendation Engine | Weak points, headline/CTA ideas, targeting strategy, priority fix |
| History & Storage | Every simulation is saved to SQLite for longitudinal tracking |

## Setup

1. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your Gemini API key**

   Open `.env` and replace the placeholder:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   GEMINI_MODEL=gemini-2.5-flash-lite
   ```
   Get a key from [Google AI Studio](https://aistudio.google.com/apikey).

3. **Run the app**
   ```bash
   python app.py
   ```
   Visit **http://localhost:5000**

## Notes

- If no valid API key is set, the app automatically falls back to a
  rule-based offline simulator so the interface still works end-to-end —
  you'll see a banner on the results page telling you this happened.
- Data is stored locally in `growthgpt.db` (SQLite), created automatically
  on first run.
- Model used: **gemini-2.5-flash-lite** (configurable via `GEMINI_MODEL` in `.env`).

## Project structure

```
growthgpt/
├── app.py                 # Flask routes
├── gemini_service.py       # AI engine — all 5 AI-driven modules
├── db.py                   # SQLite persistence (History & Storage)
├── .env                     # Gemini API key & model config
├── requirements.txt
├── templates/
│   ├── base.html            # shared shell, nav, animated background
│   ├── index.html           # landing page
│   ├── simulate.html        # campaign submission form
│   ├── results.html         # simulation dashboard
│   └── history.html         # past campaigns table
└── static/
    ├── css/style.css        # design system + animations
    └── js/main.js            # animated emoji background field
```
