# 🗳️ Maharashtra Election Outcome Predictor

A simple machine learning project that predicts which political party is likely to win the Maharashtra Rajya Sabha election — built with Python, Flask, and a clean web interface.

---

## 💡 What does this project do?

It looks at past Maharashtra election data (2014–2024) and uses that to predict which party has the best chance of winning in 2027. You can either run it from the command line or use the web interface to enter details and get an instant prediction.

---

## 📁 Project Structure

```
Election-Outcome-Prediction-Model/
├── app.py                  # The main Flask web app
├── requirements.txt        # All Python packages needed
├── data/
│   └── clean_election.csv  # Cleaned historical election data
├── src/
│   └── main.py             # Standalone prediction script
├── notebook/
│   └── election_analysis.ipynb  # Full analysis with charts
├── templates/
│   └── index.html          # Web page UI
└── static/                 # CSS and JavaScript files
```

---

## 🚀 How to Run

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Run the web app
```bash
python app.py
```
Then open your browser and go to 👉 `http://localhost:5000`

Fill in the form and hit **Predict** — that's it!

### 3. Or run from the command line
```bash
python src/main.py
```
This will print win probabilities for each party directly in your terminal.

---

## 🧠 How does it work?

The model is trained on real election data. It looks at factors like:

- **MLA Strength** — how many MLAs the party has
- **Alliance Strength** — combined strength with partners
- **Past Rajya Sabha Wins** — the party's track record
- **Candidate Type** — what kind of candidate is being fielded

Based on these, it calculates a **win probability** for each party and tells you who is most likely to win.

---

## 📊 Sample Output

```
🏆 BJP is predicted to WIN the 2027 Rajya Sabha seat!
   Win Probability: 85.23%

🥈 Runner-up: NCP (45.67%)
```

---

## ⚠️ Things to keep in mind

- Predictions are based only on **historical data** — real elections can be unpredictable!
- The dataset only covers **Maharashtra Rajya Sabha elections** (2014–2024)
- Political changes, alliances, or events not in the data won't be reflected

---

## 🛠️ Tech Stack

| Tool | What it's used for |
|------|-------------------|
| Python | Core language |
| Flask | Web framework |
| scikit-learn | Machine learning model |
| pandas | Data handling |
| HTML/CSS/JS | Frontend interface |

---

## 🙋 Who is this for?

This project is great for students or anyone learning how machine learning can be applied to real-world data like elections. It's educational and open to improvements!

Feel free to fork it, experiment with it, or add your own features. 😊

---

*Predictions are for educational purposes only and may not reflect actual election outcomes.*
