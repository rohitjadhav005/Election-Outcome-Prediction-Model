from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

app = FastAPI()

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates setup
templates = Jinja2Templates(directory="templates")

# Global variables for model and data
model      = None
data       = None
le_party   = None   # LabelEncoder for party names

# Party icons mapping (includes split factions)
PARTY_ICONS = {
    'BJP':          '🟠',
    'INC':          '🔵',
    'NCP':          '🟢',
    'NCP(Ajit)':   '🟢',
    'NCP(Sharad)': '🫐',
    'SS':           '🟡',
    'SS(Shinde)':  '🟡',
    'SS(UBT)':     '🔥',
    'Shiv Sena':   '🟡',
    'Independent': '⚪'
}

# Party descriptions (includes split factions)
PARTY_DESCRIPTIONS = {
    'BJP':          'Bharatiya Janata Party — Leading party in Mahayuti alliance (132 MLAs, 2024)',
    'INC':          'Indian National Congress — Part of MVA alliance (16 MLAs, 2024)',
    'NCP':          'Nationalist Congress Party — Regional party (pre-2023 split)',
    'NCP(Ajit)':   'NCP (Ajit Pawar faction) — Part of Mahayuti alliance (41 MLAs, 2024)',
    'NCP(Sharad)': 'NCP (Sharad Pawar faction) — Part of MVA alliance (10 MLAs, 2024)',
    'SS':           'Shiv Sena — Maharashtra party (pre-2022 split)',
    'SS(Shinde)':  'Shiv Sena (Eknath Shinde) — Part of Mahayuti alliance (57 MLAs, 2024)',
    'SS(UBT)':     'Shiv Sena (UBT / Uddhav Thackeray) — Part of MVA alliance (20 MLAs, 2024)',
    'Shiv Sena':   'Shiv Sena — Maharashtra regional party',
    'Independent': 'Independent Candidates'
}

def load_and_train_model():
    """Load data and train a Random Forest model with:
    - Party name encoding (model knows party identity)
    - Alliance majority flag (>144 MLAs in alliance = very strong signal)
    - MLA share features (normalised %)
    - Recency weighting (recent elections matter more)
    """
    global model, data, le_party

    # Load the data
    csv_path = os.path.join(os.path.dirname(__file__), "data", "clean_election.csv")
    data = pd.read_csv(csv_path)

    # ── Feature Engineering ────────────────────────────────────────
    # 1. Encode party name → integer so model learns party-specific patterns
    le_party = LabelEncoder()
    data['party_encoded'] = le_party.fit_transform(data['party'])

    # 2. Alliance majority flag — the single most decisive RS election factor
    #    In Maharashtra (288 seats), majority = 145+. Alliances above this win RS.
    data['has_majority'] = (data['alliance_mla_strength'] >= 145).astype(int)

    # 3. Normalised strength ratios (0-1 scale)
    data['mla_share']      = data['mla_strength']          / 288
    data['alliance_share'] = data['alliance_mla_strength'] / 288

    # ── Build feature matrix ───────────────────────────────────────
    FEATURES = [
        'year',
        'party_encoded',       # ← party identity (NEW)
        'mla_strength',
        'alliance_mla_strength',
        'past_rs_wins',
        'candidate_type',
        'has_majority',        # ← alliance majority flag (NEW)
        'mla_share',           # ← normalised MLA % (NEW)
        'alliance_share',      # ← normalised alliance % (NEW)
    ]
    X = data[FEATURES]
    y = data['winner']

    # ── Recency Weighting ──────────────────────────────────────────
    # decay=0.85/year: 2024→1.0, 2022→0.85, 2020→0.72, 1952→~0.00
    max_year = data['year'].max()
    decay    = 0.85
    sample_weights = decay ** (max_year - data['year'])

    # ── Train / Test Split ─────────────────────────────────────────
    X_train, X_test, y_train, y_test, w_train, w_test = train_test_split(
        X, y, sample_weights, test_size=0.2, random_state=42
    )

    # ── Random Forest Classifier ───────────────────────────────────
    model = RandomForestClassifier(
        n_estimators=200,       # 200 decision trees
        max_depth=6,            # limit overfitting on small dataset
        min_samples_leaf=2,
        random_state=42
    )
    model.fit(X_train, y_train, sample_weight=w_train)

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
    
    # Calculate win rate using RECENCY WEIGHTING (exponential decay)
    # This is the same decay we use in model training.
    # decay=0.85 per year: 2024 win = full weight, 1952 win = ~0.001 weight
    # Result: old INC dominance fades out; recent BJP wins dominate.
    # Much better than all-time average (inflated) or last-3 (too binary).
    DECAY = 0.85
    max_year = int(party_data['year'].max())
    weights        = DECAY ** (max_year - party_data['year'])
    weighted_wins  = (party_data['winner'] * weights).sum()
    total_weight   = weights.sum()
    win_rate = round((weighted_wins / total_weight * 100), 1) if total_weight > 0 else 0
    
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

@app.get('/', response_class=HTMLResponse)
async def index(request: Request):
    """Render the main prediction page"""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get('/parties', response_class=HTMLResponse)
async def parties(request: Request):
    """Render the parties listing page"""
    return templates.TemplateResponse("parties.html", {"request": request})

@app.get('/party/{party_name}', response_class=HTMLResponse)
async def party_detail(request: Request, party_name: str):
    """Render individual party detail page"""
    party_info = get_party_info(party_name)
    
    if party_info is None:
        return HTMLResponse(content=f"Party '{party_name}' not found", status_code=404)
    
    return templates.TemplateResponse("party_detail.html", {"request": request, "party": party_info})

@app.get('/about', response_class=HTMLResponse)
async def about(request: Request):
    """Render the about page"""
    return templates.TemplateResponse("about.html", {"request": request})

@app.get('/sw.js')
async def service_worker():
    """Serve the Service Worker from the root scope"""
    sw_path = os.path.join(os.path.dirname(__file__), 'static', 'js', 'sw.js')
    return FileResponse(sw_path, media_type='application/javascript')

# ==================== API ENDPOINTS ====================

@app.get('/api/parties')
async def api_parties():
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
    
    return {
        'success': True,
        'parties': parties_info
    }

@app.get('/api/party/{party_name}')
async def api_party_detail(party_name: str):
    """API endpoint to get detailed party information"""
    party_info = get_party_info(party_name)
    
    if party_info is None:
        return JSONResponse(status_code=404, content={
            'success': False,
            'error': f'Party "{party_name}" not found'
        })
    
    return {
        'success': True,
        'party': party_info
    }

@app.post('/predict')
async def predict(request: Request):
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
        try:
            request_data = await request.json()
        except Exception:
            request_data = {}
        
        # Validate required fields (only dataset features)
        required_fields = ['party_name', 'mla_strength', 'alliance_mla_strength', 'past_rs_wins', 'candidate_type']
        
        missing_fields = [field for field in required_fields if field not in request_data or request_data[field] == '']
        if missing_fields:
            return JSONResponse(status_code=400, content={
                'success': False,
                'error': f'Missing required fields: {", ".join(missing_fields)}'
            })
        
        # Validate numeric fields
        try:
            mla_strength = float(request_data['mla_strength'])
            alliance_mla_strength = float(request_data['alliance_mla_strength'])
            past_rs_wins = float(request_data['past_rs_wins'])
            
            # Handle candidate_type - can be text or number
            candidate_type_value = request_data['candidate_type']
            
            # Map text values to numbers
            # Accepted: new=0, incumbent=1, mixed=2
            # Also accepts common aliases (experienced, senior, veteran → incumbent)
            candidate_type_mapping = {
                'new': 0,
                'first-time': 0,
                'firsttime': 0,
                'fresh': 0,
                'incumbent': 1,
                'experienced': 1,
                'experience': 1,
                'senior': 1,
                'veteran': 1,
                'returning': 1,
                'mixed': 2,
                'both': 2,
                '0': 0,
                '1': 1,
                '2': 2
            }
            
            if isinstance(candidate_type_value, str):
                candidate_type_value_lower = candidate_type_value.lower().strip()
                if candidate_type_value_lower in candidate_type_mapping:
                    candidate_type = candidate_type_mapping[candidate_type_value_lower]
                else:
                    try:
                        candidate_type = float(candidate_type_value_lower)
                    except ValueError:
                        return JSONResponse(status_code=400, content={
                            'success': False,
                            'error': f'Invalid candidate type "{candidate_type_value}". Use: new, incumbent, experienced, mixed'
                        })
            else:
                candidate_type = float(candidate_type_value)
            
            if mla_strength < 0 or alliance_mla_strength < 0 or past_rs_wins < 0:
                return JSONResponse(status_code=400, content={
                    'success': False,
                    'error': 'All numeric values must be positive'
                })
                
        except (ValueError, TypeError):
            return JSONResponse(status_code=400, content={
                'success': False,
                'error': 'Invalid numeric values provided'
            })
        
        # ── Build 9-feature input vector matching training features ────
        # Features: year, party_encoded, mla_strength, alliance_mla_strength,
        #           past_rs_wins, candidate_type, has_majority, mla_share, alliance_share

        # Encode party name — fall back to -1 (unknown) if not seen in training
        party_name_input = request_data['party_name']
        try:
            party_encoded = int(le_party.transform([party_name_input])[0])
        except ValueError:
            # Unknown party: use mean encoding as neutral fallback
            party_encoded = int(le_party.transform([le_party.classes_[0]])[0])

        has_majority   = 1 if alliance_mla_strength >= 145 else 0
        mla_share      = mla_strength / 288
        alliance_share = alliance_mla_strength / 288

        prediction_data = np.array([[
            2027,                   # prediction year
            party_encoded,          # party identity
            mla_strength,
            alliance_mla_strength,
            past_rs_wins,
            candidate_type,
            has_majority,           # alliance majority flag
            mla_share,              # normalised MLA %
            alliance_share          # normalised alliance %
        ]])

        # Get prediction and probability from Random Forest model
        prediction  = model.predict(prediction_data)[0]
        probability = model.predict_proba(prediction_data)[0]

        # Get party info
        party_info = get_party_info(request_data['party_name'])

        return {
            'success': True,
            'prediction':     int(prediction),
            'win_probability': round(float(probability[1]) * 100, 2),
            'party_name':     request_data['party_name'],
            'party':          request_data['party_name'],
            'party_info':     party_info
        }
        
    except Exception as e:
        return JSONResponse(status_code=500, content={
            'success': False,
            'error': f'An error occurred: {str(e)}'
        })

@app.get('/api/stats')
async def get_stats():
    """API endpoint to get model statistics"""
    if data is None:
        load_and_train_model()
    
    # Calculate statistics
    total_records = len(data)
    unique_parties = data['party'].unique().tolist()
    years = sorted(data['year'].unique().tolist())
    
    # Party-wise wins
    party_wins = data[data['winner'] == 1].groupby('party').size().to_dict()
    
    return {
        'success': True,
        'total_records': int(total_records),
        'unique_parties': unique_parties,
        'years': years,
        'party_wins': {str(k): int(v) for k, v in party_wins.items()}
    }

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
    print()
    print("Recency Weighting: ON (decay=0.85 per year)")
    print("Recent elections (2024, 2022, 2020) have the highest influence.")
    print()
    
    accuracy = load_and_train_model()
    
    print(f"OK: Model trained successfully!")
    print(f"OK: Model Accuracy: {accuracy * 100:.2f}%")
    print(f"OK: Total Records: {len(data)}")
    print(f"OK: Years Covered: 1952-2024")
    print()
    print("=" * 60)
    print("Starting FastAPI application...")
    print("Open your browser and go to: http://localhost:5000")
    print("=" * 60)
    print()
    
    port = int(os.environ.get("PORT", 5000))
    uvicorn.run("app:app", host='0.0.0.0', port=port)
