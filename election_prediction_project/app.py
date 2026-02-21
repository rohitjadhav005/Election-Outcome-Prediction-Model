from flask import Flask, render_template, jsonify, request
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

app = Flask(__name__)

# Global variables for model and data
model = None
data = None

# Party icons mapping
PARTY_ICONS = {
    'BJP': '🟠',
    'INC': '🔵',
    'NCP': '🟢',
    'Shiv Sena': '🟡',
    'Independent': '⚪'
}

# Party descriptions
PARTY_DESCRIPTIONS = {
    'BJP': 'Bharatiya Janata Party - Major national party with strong presence in Maharashtra',
    'INC': 'Indian National Congress - Historic national party with significant influence',
    'NCP': 'Nationalist Congress Party - Regional party with strong Maharashtra base',
    'Shiv Sena': 'Shiv Sena - Regional party focused on Maharashtra politics',
    'Independent': 'Independent Candidates'
}

def load_and_train_model():
    """Load data and train the model using ONLY dataset features"""
    global model, data
    
    # Load the data - UPDATED TO USE NEW FILE
    csv_path = os.path.join(os.path.dirname(__file__), "data", "converted_data.csv")
    data = pd.read_csv(csv_path)
    
    # Encode candidate_type from text to numbers
    # new=0, incumbent=1, mixed=2
    candidate_type_mapping = {
        'new': 0,
        'incumbent': 1,
        'mixed': 2
    }
    data['candidate_type_encoded'] = data['candidate_type'].map(candidate_type_mapping)
    
    # Features from the dataset: year, mla_strength, alliance_mla_strength, past_rs_wins, candidate_type
    X = data[[
        "year",
        "mla_strength",
        "alliance_mla_strength",
        "past_rs_wins",
        "candidate_type_encoded"
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
    
    return accuracy

def get_party_info(party_name):
    """Get detailed information about a party"""
    if data is None:
        load_and_train_model()
    
    party_data = data[data['party'] == party_name].sort_values('year', ascending=False)
    
    if len(party_data) == 0:
        return None
    
    # Get latest data
    latest = party_data.iloc[0]
    
    # Calculate win rate
    total_elections = len(party_data)
    wins = len(party_data[party_data['winner'] == 1])
    win_rate = (wins / total_elections * 100) if total_elections > 0 else 0
    
    # Get historical data
    historical_data = []
    for _, row in party_data.iterrows():
        historical_data.append({
            'year': int(row['year']),
            'mla_strength': int(row['mla_strength']),
            'alliance_mla_strength': int(row['alliance_mla_strength']),
            'past_rs_wins': int(row['past_rs_wins']),
            'winner': int(row['winner'])
        })
    
    return {
        'party_name': party_name,
        'icon': PARTY_ICONS.get(party_name, '🏛️'),
        'description': PARTY_DESCRIPTIONS.get(party_name, f'{party_name} - Political Party'),
        'current_mla_strength': int(latest['mla_strength']),
        'current_alliance_strength': int(latest['alliance_mla_strength']),
        'total_rs_wins': int(latest['past_rs_wins']),
        'win_rate': round(win_rate, 1),
        'historical_data': historical_data
    }

# ==================== ROUTES ====================

@app.route('/')
def index():
    """Render the main prediction page"""
    return render_template('index.html')

@app.route('/parties')
def parties():
    """Render the parties listing page"""
    return render_template('parties.html')

@app.route('/party/<party_name>')
def party_detail(party_name):
    """Render individual party detail page"""
    party_info = get_party_info(party_name)
    
    if party_info is None:
        return f"Party '{party_name}' not found", 404
    
    return render_template('party_detail.html', party=party_info)

@app.route('/about')
def about():
    """Render the about page"""
    return render_template('about.html')

# ==================== API ENDPOINTS ====================

@app.route('/api/parties')
def api_parties():
    """API endpoint to get all parties"""
    if data is None:
        load_and_train_model()
    
    parties_list = data['party'].unique().tolist()
    parties_info = []
    
    for party_name in parties_list:
        if party_name != 'Independent':  # Skip independent for main listing
            info = get_party_info(party_name)
            if info:
                parties_info.append(info)
    
    # Sort by current MLA strength
    parties_info.sort(key=lambda x: x['current_mla_strength'], reverse=True)
    
    return jsonify({
        'success': True,
        'parties': parties_info
    })

@app.route('/api/party/<party_name>')
def api_party_detail(party_name):
    """API endpoint to get detailed party information"""
    party_info = get_party_info(party_name)
    
    if party_info is None:
        return jsonify({
            'success': False,
            'error': f'Party "{party_name}" not found'
        }), 404
    
    return jsonify({
        'success': True,
        'party': party_info
    })

@app.route('/predict', methods=['POST'])
def predict():
    """
    Simplified prediction using ONLY dataset features:
    - party_name
    - mla_strength
    - alliance_mla_strength
    - past_rs_wins
    - candidate_type
    """
    try:
        # Ensure model is loaded
        if model is None:
            load_and_train_model()
        
        # Get JSON data from request
        request_data = request.get_json()
        
        # Validate required fields (only dataset features)
        required_fields = ['party_name', 'mla_strength', 'alliance_mla_strength', 'past_rs_wins', 'candidate_type']
        
        missing_fields = [field for field in required_fields if field not in request_data or request_data[field] == '']
        if missing_fields:
            return jsonify({
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            }), 400
        
        # Validate numeric fields
        try:
            mla_strength = float(request_data['mla_strength'])
            alliance_mla_strength = float(request_data['alliance_mla_strength'])
            past_rs_wins = float(request_data['past_rs_wins'])
            
            # Handle candidate_type - can be text or number
            candidate_type_value = request_data['candidate_type']
            
            # Map text values to numbers
            candidate_type_mapping = {
                'new': 0,
                'incumbent': 1,
                'mixed': 2,
                '0': 0,
                '1': 1,
                '2': 2
            }
            
            if isinstance(candidate_type_value, str):
                candidate_type_value = candidate_type_value.lower()
                if candidate_type_value in candidate_type_mapping:
                    candidate_type = candidate_type_mapping[candidate_type_value]
                else:
                    candidate_type = float(candidate_type_value)
            else:
                candidate_type = float(candidate_type_value)
            
            if mla_strength < 0 or alliance_mla_strength < 0 or past_rs_wins < 0:
                return jsonify({
                    'success': False,
                    'error': 'All numeric values must be positive'
                }), 400
                
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'Invalid numeric values provided'
            }), 400
        
        # Prepare prediction data using ONLY dataset features
        # Features: year, mla_strength, alliance_mla_strength, past_rs_wins, candidate_type
        prediction_data = np.array([[
            2027,  # Current prediction year
            mla_strength,
            alliance_mla_strength,
            past_rs_wins,
            candidate_type
        ]])
        
        # Get prediction and probability from ML model
        prediction = model.predict(prediction_data)[0]
        probability = model.predict_proba(prediction_data)[0]
        
        # Get party info
        party_info = get_party_info(request_data['party_name'])
        
        # Return prediction result
        return jsonify({
            'success': True,
            'prediction': int(prediction),  # 0 or 1
            'win_probability': round(probability[1] * 100, 2),  # Probability of winning
            'party_name': request_data['party_name'],
            'party': request_data['party_name'],
            'party_info': party_info
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/api/stats')
def get_stats():
    """API endpoint to get model statistics"""
    if data is None:
        load_and_train_model()
    
    # Calculate statistics
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
    print("=" * 60)
    print("ELECTION OUTCOME PREDICTION SYSTEM")
    print("=" * 60)
    print("\nLoading data and training model...")
    print("Dataset: 1952-2024 Historical Election Data")
    print("\nUsing features from dataset:")
    print("  - Year")
    print("  - MLA Strength")
    print("  - Alliance MLA Strength")
    print("  - Past Rajya Sabha Wins")
    print("  - Candidate Type (new/incumbent/mixed)")
    print()
    
    accuracy = load_and_train_model()
    
    print(f"✓ Model trained successfully!")
    print(f"✓ Model Accuracy: {accuracy * 100:.2f}%")
    print(f"✓ Total Records: {len(data)}")
    print(f"✓ Years Covered: 1952-2024")
    print()
    print("=" * 60)
    print("Starting Flask application...")
    print("Open your browser and go to: http://localhost:5000")
    print("=" * 60)
    print()
    
    app.run(debug=True, host='0.0.0.0', port=5000)
