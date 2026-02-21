import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

# Get the directory of the current script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Construct the path to the CSV file
csv_path = os.path.join(script_dir, "..", "data", "clean_election.csv")
data = pd.read_csv(csv_path)

print("=" * 70)
print("MAHARASHTRA ELECTION PREDICTION SYSTEM")
print("=" * 70)
print("\nDataset Loaded Successfully")
print(f"Total Records: {len(data)}")
print("\nFirst few records:")
print(data.head())

# Get unique parties
unique_parties = data['party'].unique()
print(f"\nParties in dataset: {', '.join(unique_parties)}")

# Encode party names for model training
party_encoder = LabelEncoder()
data["party_encoded"] = party_encoder.fit_transform(data["party"])

# Prepare features and target
X = data[[
    "year",
    "mla_strength",
    "alliance_mla_strength",
    "past_rs_wins",
    "candidate_type"
]]

y = data["winner"]

# Split the data
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)


print("MODEL TRAINING")
print("=" * 70)
print(f"Training data size: {X_train.shape[0]} samples")
print(f"Testing data size: {X_test.shape[0]} samples")

model = LogisticRegression(max_iter=1000)
model.fit(X_train, y_train)

print("\nModel training completed successfully!")

# Evaluate the model
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
cm = confusion_matrix(y_test, y_pred)

print("\n" + "=" * 70)
print("MODEL PERFORMANCE")
print("=" * 70)
print(f"Model Accuracy: {accuracy * 100:.2f}%")
print("\nConfusion Matrix:")
print(cm)

print("\n" + "=" * 70)
print("PREDICTION FOR 2027 ELECTIONS")
print("=" * 70)

# Get the latest data for each party to use as baseline
latest_year = data['year'].max()
print(f"\nUsing {latest_year} data as baseline for predictions...")

# Prepare predictions for each major party
parties_to_predict = ['BJP', 'INC', 'NCP', 'Shiv Sena']
predictions = []

for party_name in parties_to_predict:
    # Get the latest record for this party
    party_data = data[data['party'] == party_name].sort_values('year', ascending=False)
    
    if len(party_data) > 0:
        latest_record = party_data.iloc[0]
        
        # Create prediction data for 2027
        # Using latest MLA strength and past performance
        prediction_data = np.array([[
            2027,  # year
            latest_record['mla_strength'],
            latest_record['alliance_mla_strength'],
            latest_record['past_rs_wins'],
            latest_record['candidate_type']
        ]])
        
        # Get prediction and probability
        prediction = model.predict(prediction_data)[0]
        probability = model.predict_proba(prediction_data)[0]
        
        predictions.append({
            'party': party_name,
            'prediction': prediction,
            'win_probability': probability[1] * 100,  # Probability of winning
            'mla_strength': latest_record['mla_strength'],
            'alliance_strength': latest_record['alliance_mla_strength']
        })

# Sort by win probability
predictions.sort(key=lambda x: x['win_probability'], reverse=True)

print("\nPrediction Results for All Major Parties:\n")
print(f"{'Party':<15} {'Win Probability':<20} {'MLA Strength':<15} {'Alliance Strength'}")
print("-" * 70)

for pred in predictions:
    print(f"{pred['party']:<15} {pred['win_probability']:>6.2f}%{'':<13} {pred['mla_strength']:<15} {pred['alliance_strength']}")

# Determine the winner
winner = predictions[0]

print("\n" + "=" * 70)
print("FINAL PREDICTION")
print("=" * 70)
print(f"\n🏆 {winner['party']} is predicted to WIN the Rajya Sabha seat in 2027!")
print(f"   Win Probability: {winner['win_probability']:.2f}%")
print(f"   Current MLA Strength: {winner['mla_strength']}")
print(f"   Alliance Strength: {winner['alliance_strength']}")

# Show runner-up
if len(predictions) > 1:
    runner_up = predictions[1]
    print(f"\n🥈 Runner-up: {runner_up['party']} ({runner_up['win_probability']:.2f}% win probability)")

print("\n" + "=" * 70)
print("Note: Predictions are based on historical data and current political strength.")
print("Actual results may vary based on political alliances and other factors.")
print("=" * 70)
