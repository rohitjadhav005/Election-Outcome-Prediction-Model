from flask import Flask, render_template, jsonify
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)

# Global variables for model and data
model = None
data = None
predictions_cache = None

def load_and_train_model():
    """Load data and train the model"""
    global model, data, predictions_cache
    
    # Load the data
    csv_path = os.path.join(os.path.dirname(__file__), "data", "maharashtra_election.csv")
    data = pd.read_csv(csv_path)
    
    # Prepare features and target
    X = data[[
        "year",
        "mla_strength",
        "alliance_mla_strength",
        "past_rs_wins",
        "candidate_type"
    ]]
    
    y = data["winner"]
    
    # Split and train
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Train the model
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    
    # Calculate accuracy
    accuracy = model.score(X_test, y_test)
    
    # Generate predictions for 2027
    predictions_cache = generate_predictions()
    
    return accuracy

def generate_predictions():
    """Generate predictions for all major parties for 2027"""
    parties_to_predict = ['BJP', 'INC', 'NCP', 'Shiv Sena']
    predictions = []
    
    for party_name in parties_to_predict:
        # Get the latest record for this party
        party_data = data[data['party'] == party_name].sort_values('year', ascending=False)
        
        if len(party_data) > 0:
            latest_record = party_data.iloc[0]
            
            # Create prediction data for 2027
            prediction_data = np.array([[
                2027,
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
                'prediction': int(prediction),
                'win_probability': round(probability[1] * 100, 2),
                'mla_strength': int(latest_record['mla_strength']),
                'alliance_strength': int(latest_record['alliance_mla_strength']),
                'past_rs_wins': int(latest_record['past_rs_wins'])
            })
    
    # Sort by win probability
    predictions.sort(key=lambda x: x['win_probability'], reverse=True)
    
    return predictions

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@app.route('/api/predictions')
def get_predictions():
    """API endpoint to get predictions"""
    if predictions_cache is None:
        load_and_train_model()
    
    # Get winner and runner-up
    winner = predictions_cache[0] if predictions_cache else None
    runner_up = predictions_cache[1] if len(predictions_cache) > 1 else None
    
    return jsonify({
        'success': True,
        'predictions': predictions_cache,
        'winner': winner,
        'runner_up': runner_up,
        'year': 2027
    })

@app.route('/api/stats')
def get_stats():
    """API endpoint to get model statistics"""
    if data is None:
        load_and_train_model()
    
    # Calculate some statistics
    total_records = len(data)
    unique_parties = data['party'].unique().tolist()
    years = sorted(data['year'].unique().tolist())
    
    # Party-wise wins
    party_wins = data[data['winner'] == 1].groupby('party').size().to_dict()
    
    return jsonify({
        'success': True,
        'total_records': total_records,
        'unique_parties': unique_parties,
        'years': years,
        'party_wins': party_wins
    })

if __name__ == '__main__':
    print("Loading model and training...")
    accuracy = load_and_train_model()
    print(f"Model trained successfully! Accuracy: {accuracy * 100:.2f}%")
    print("\nStarting Flask application...")
    print("Open your browser and go to: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
