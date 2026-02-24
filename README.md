# 🗳️ Maharashtra Election Outcome Predictor

A machine learning project that predicts the probability of a political party winning a Maharashtra election. Built with Python, Flask, scikit-learn, and a clean web interface.

---

## 💡 What does this project do?

It analyzes historical Maharashtra election data (1952–2024) to predict election outcomes (e.g., for 2027). You can use the interactive web interface to view party statistics or enter specific scenario details to get an instant prediction.

The model incorporates real-world political dynamics, including recency weighting (recent elections matter more) and tracking post-split party factions like the NCP (Ajit/Sharad) and Shiv Sena (Shinde/UBT).

---

## 📁 Project Structure

```text
Election-Outcome-Prediction-Model/
├── app.py                  # The main Flask web app & prediction API
├── requirements.txt        # Python package dependencies
├── data/
│   └── clean_election.csv  # Cleaned 1952-2024 historical election data
├── templates/              # HTML files for the web interface
│   ├── index.html          # Main prediction page
│   ├── parties.html        # Parties list
│   ├── party_detail.html   # Detailed party info
│   └── about.html          # About page
└── static/                 # (Optional) CSS and JS files
```

---

## 🚀 How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the Web App
```bash
python app.py
```
Wait for the model to train automatically, then open your browser and go to 👉 `http://localhost:5000`

---

## 🧠 How does the Model Work?

The prediction engine is a **Random Forest Classifier** that evaluates multiple features:

- **Party Identity** — learned patterns specific to each party.
- **MLA Strength** & **Alliance Strength** — current numbers and normalized percentages.
- **Alliance Majority Flag** — checks if the alliance crosses the magic number (145+ out of 288 seats).
- **Candidate Type** — whether the candidate is an incumbent, new, or mixed.
- **Past Wins** — historical track record.
- **⚡ Recency Weighting** — uses an exponential decay of `0.85/yearly` so recent elections (2024, 2022) heavily influence predictions compared to older data (e.g., 1952).

---

## 🌐 API Endpoints

The app exposes several JSON APIs you can interact with programmatically:
- `GET /api/parties` — List of all parties and their current strength.
- `GET /api/party/<party_name>` — Detailed historical performance of a specific party.
- `GET /api/stats` — Overall model statistics and party wins.
- `POST /predict` — Submit predictor features (`party_name`, `mla_strength`, `alliance_mla_strength`, `past_rs_wins`, `candidate_type`) to get a win probability.

---

## ⚠️ Important Notes

- Predictions use purely **historical data** (1952–2024), applying logic based on past trends.
- The model treats alliances and split factions (e.g., Mahayuti vs MVA components) as they currently stand.
- Real-world elections can be influenced by unexpected political events that data cannot foresee.

---

## 🛠️ Tech Stack

| Tool | Usage |
|------|-------------------|
| Python 3 | Core logic |
| Flask | Web server & REST API |
| scikit-learn | Random Forest ML Model |
| pandas & numpy | Data manipulation |
| HTML / JS | Frontend interface |

---

*Disclaimer: Predictions are for educational purposes only and are not guaranteed to reflect actual election outcomes.*
