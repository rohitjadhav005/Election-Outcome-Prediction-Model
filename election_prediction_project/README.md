# Maharashtra Rajya Sabha Election Prediction System

A machine learning project that predicts election outcomes using historical data and provides an interactive web interface for real-time predictions based on user input.

## 📊 Project Overview

This project analyzes Maharashtra Rajya Sabha election data from 2014 to 2024 and builds a predictive model to forecast which political party is most likely to win in future elections. The system uses various political indicators such as MLA strength, alliance strength, and past performance to make predictions.

### Key Features

- **🌐 Interactive Web Interface**: Modern, responsive form-based UI for real-time predictions
- **📊 Historical Data Analysis**: Comprehensive analysis of election data spanning 2014-2024
- **🤖 Machine Learning Prediction**: Smart prediction algorithm based on multiple election factors
- **✅ Form Validation**: Client-side and server-side validation for data accuracy
- **📱 Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **⚡ Real-time Results**: Instant predictions without page refresh
- **🎨 Modern UI/UX**: Clean, gradient-themed interface with smooth animations

## 🗂️ Project Structure

```
election_prediction_project/
│
├── data/
│   └── maharashtra_election.csv          # Historical election data (2014-2024)
│
├── notebook/
│   └── election_analysis.ipynb           # Jupyter notebook with comprehensive analysis
│
├── src/
│   └── main.py                           # Main prediction script
│
├── templates/
│   └── index.html                        # Web interface HTML
│
├── static/
│   ├── css/
│   │   └── style.css                     # Modern styling with animations
│   └── js/
│       └── script.js                     # Form handling and API integration
│
├── app.py                                # Flask web application
├── requirements.txt                      # Python dependencies
└── README.md                             # Project documentation (this file)
```

### Component Details

#### 1. **data/maharashtra_election.csv**
Contains historical election data with the following features:
- `year`: Election year (2014-2024)
- `party`: Political party name (BJP, INC, NCP, Shiv Sena, Independent)
- `mla_strength`: Number of MLAs the party has
- `alliance_mla_strength`: Combined MLA strength including alliance partners
- `past_rs_wins`: Number of previous Rajya Sabha seats won
- `candidate_type`: Type of candidate (encoded as 0, 1, 2)
- `winner`: Target variable (1 = Won, 0 = Lost)

#### 2. **src/main.py**
The main Python script that:
- Loads and preprocesses the election data
- Trains a Logistic Regression model
- Evaluates model performance
- Predicts the winning party for 2027 elections
- Displays win probabilities for all major parties

#### 3. **notebook/election_analysis.ipynb**
A comprehensive Jupyter notebook featuring:
- Exploratory Data Analysis (EDA)
- Data visualizations (bar charts, scatter plots, heatmaps, trend lines)
- Feature correlation analysis
- Model training and evaluation
- Confusion matrix and classification metrics
- Feature importance analysis
- 2027 election predictions with visualizations

## 🤖 Machine Learning Approach

### Algorithm: Logistic Regression

**Why Logistic Regression?**
- **Binary Classification**: Perfect for predicting win/lose outcomes
- **Interpretability**: Coefficients show which features are most important
- **Probabilistic Output**: Provides win probability percentages, not just binary predictions
- **Efficiency**: Fast training and prediction, suitable for small to medium datasets
- **Proven Effectiveness**: Well-established algorithm for classification tasks

### Model Features

The model uses the following features to make predictions:

1. **year**: Election year (helps capture temporal trends)
2. **mla_strength**: Number of MLAs (strong indicator of political power)
3. **alliance_mla_strength**: Combined alliance strength (crucial for coalition politics)
4. **past_rs_wins**: Historical Rajya Sabha wins (indicates party's track record)
5. **candidate_type**: Type of candidate fielded

### Training Process

1. **Data Splitting**: 80% training, 20% testing
2. **Model Training**: Logistic Regression with max 1000 iterations
3. **Evaluation**: Accuracy score, confusion matrix, classification report
4. **Prediction**: Win probabilities for each party in 2027

## 🐍 Python Libraries Used

### Core Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| **pandas** | Latest | Data manipulation and analysis; reading CSV files, data filtering, grouping |
| **numpy** | Latest | Numerical computing; array operations, mathematical functions |
| **scikit-learn** | Latest | Machine learning; model training, evaluation, preprocessing |

### Scikit-learn Components

- `train_test_split`: Splits data into training and testing sets
- `LabelEncoder`: Encodes categorical party names into numerical values
- `LogisticRegression`: The main classification algorithm
- `accuracy_score`: Calculates model accuracy
- `confusion_matrix`: Shows prediction vs actual outcomes
- `classification_report`: Detailed precision, recall, F1-score metrics

### Visualization Libraries (Notebook Only)

| Library | Purpose |
|---------|---------|
| **matplotlib** | Creating static visualizations (line plots, bar charts, scatter plots) |
| **seaborn** | Statistical data visualization (heatmaps, enhanced styling) |

## 🚀 How to Run the Project

### Prerequisites

```bash
# Install required libraries
pip install -r requirements.txt

# Or install manually:
pip install flask pandas numpy scikit-learn matplotlib seaborn jupyter
```

### Option 1: Web Interface (Recommended)

```bash
# Navigate to the project directory
cd election_prediction_project

# Run the Flask web application
python app.py
```

**Then:**
1. Open your browser and go to `http://localhost:5000`
2. Fill in the election details in the form:
   - Candidate Name
   - Party Name
   - Age of Candidate
   - Previous Votes
   - Poll Percentage
   - Constituency Type (Urban/Rural/Mixed)
   - Voter Turnout (%)
   - Development Index Score (0-10)
   - Anti-incumbency Factor (Yes/No)
3. Click "Predict Outcome"
4. View the prediction result with confidence score!

### Option 2: Command Line Script

```bash
# Run the prediction script
python src/main.py
```

**Expected Output:**
- Dataset information and preview
- Model training confirmation
- Model accuracy and confusion matrix
- Win probabilities for all major parties
- **Predicted winner for 2027** with confidence score

### Option 3: Jupyter Notebook Analysis

```bash
# Start Jupyter Notebook
jupyter notebook

# Open notebook/election_analysis.ipynb
# Run all cells to see comprehensive analysis and visualizations
```

## 📈 Model Performance

The Logistic Regression model is evaluated using:

- **Accuracy Score**: Overall percentage of correct predictions
- **Confusion Matrix**: True positives, true negatives, false positives, false negatives
- **Classification Report**: Precision, recall, and F1-score for each class
- **Feature Coefficients**: Shows which features have the most impact on predictions

## 🎯 Sample Prediction Output

```
======================================================================
PREDICTION FOR 2027 ELECTIONS
======================================================================

Prediction Results for All Major Parties:

Party           Win Probability      MLA Strength    Alliance Strength
----------------------------------------------------------------------
BJP             85.23%               132             132
NCP             45.67%               42              98
INC             38.91%               45              98
Shiv Sena       22.15%               41              41

======================================================================
FINAL PREDICTION
======================================================================

🏆 BJP is predicted to WIN the Rajya Sabha seat in 2027!
   Win Probability: 85.23%
   Current MLA Strength: 132
   Alliance Strength: 132

🥈 Runner-up: NCP (45.67% win probability)
```

## 📊 Key Insights

1. **MLA Strength Matters**: Strong positive correlation between MLA strength and winning
2. **Alliance Power**: Alliance strength significantly impacts election outcomes
3. **Historical Performance**: Past Rajya Sabha wins indicate future success
4. **BJP Dominance**: Based on current data, BJP shows highest win probability for 2027

## ⚠️ Limitations

- **Historical Data Only**: Predictions based on past patterns may not account for sudden political changes
- **No Real-time Updates**: Does not include latest political developments or alliance changes
- **Limited Features**: External factors like voter sentiment, economic conditions not included
- **Small Dataset**: Limited to Maharashtra Rajya Sabha elections only

## 🌐 Web Interface Features

### User Input Form
The web interface provides a comprehensive form with:
- **9 Input Fields**: All required election parameters
- **Dropdown Menus**: Easy selection for party, constituency type, and anti-incumbency
- **Number Validation**: Automatic validation for age, percentages, and scores
- **Real-time Feedback**: Instant error messages for invalid inputs

### Prediction Display
- **Win/Lose Prediction**: Clear outcome with color coding (green for win, red for lose)
- **Confidence Score**: Percentage confidence in the prediction
- **Animated Confidence Bar**: Visual representation of prediction strength
- **Detailed Results**: Shows candidate name, party, and all relevant metrics

### Technical Features
- **RESTful API**: `/predict` endpoint accepts POST requests with JSON data
- **Comprehensive Validation**: Both client-side (JavaScript) and server-side (Python) validation
- **Error Handling**: User-friendly error messages for all failure scenarios
- **No Page Refresh**: Results displayed dynamically using fetch API
- **Responsive Design**: Mobile-first approach, works on all screen sizes

### Prediction Algorithm
The web interface uses a weighted scoring system:
- **Poll Percentage** (40% weight)
- **Voter Turnout** (20% weight)
- **Development Index** (20% weight)
- **Anti-incumbency Factor** (20% weight)

## 🔮 Future Enhancements

1. **More Features**: Add economic indicators, opinion polls, demographic data
2. **Advanced Models**: Integrate the trained ML model for more accurate predictions
3. **Real-time Data**: Integrate live political news and alliance updates
4. **Sentiment Analysis**: Analyze social media and news sentiment
5. **Historical Predictions**: Show past predictions and accuracy tracking
6. **Multi-state Support**: Extend to other states' elections
7. **Data Visualization**: Add charts and graphs to the web interface
8. **User Accounts**: Save predictions and track historical queries

## 📝 Dataset Information

- **Source**: Historical Maharashtra Rajya Sabha election records
- **Time Period**: 2014-2024 (6 election cycles)
- **Total Records**: 31 election entries
- **Parties Covered**: BJP, INC, NCP, Shiv Sena, Independent candidates

## 🤝 Contributing

This is an educational project. Feel free to:
- Add more features to improve predictions
- Experiment with different ML algorithms
- Enhance visualizations
- Extend to other elections

## 📄 License

This project is for educational purposes only.

## 👨‍💻 Author

Created as a demonstration of machine learning applications in political analysis.

---

**Note**: Predictions are based on historical data and statistical modeling. Actual election results may vary due to numerous real-world factors not captured in the model.
