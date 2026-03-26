from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, field_validator, model_validator, Field
from typing import Optional, List, Dict, Any
import uvicorn
import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder

# ==================== PYDANTIC SCHEMAS ====================

# ── Candidate-type aliases accepted by the API ─────────────
_CANDIDATE_TYPE_MAP: dict[str, int] = {
    'new': 0, 'first-time': 0, 'firsttime': 0, 'fresh': 0,
    'incumbent': 1, 'experienced': 1, 'experience': 1,
    'senior': 1, 'veteran': 1, 'returning': 1,
    'mixed': 2, 'both': 2,
    '0': 0, '1': 1, '2': 2,
}

class PredictRequest(BaseModel):
    """Validated input for the /predict endpoint."""
    party_name:            str   = Field(..., min_length=1, description="Party name as in the dataset")
    mla_strength:          float = Field(..., ge=0, le=288,  description="Number of MLAs (0-288)")
    alliance_mla_strength: float = Field(..., ge=0, le=288,  description="Alliance MLA count (0-288)")
    past_rs_wins:          float = Field(..., ge=0,           description="Historical Rajya Sabha wins")
    candidate_type:        Any   = Field(..., description="new | incumbent | mixed  (or 0/1/2)")

    @field_validator('candidate_type', mode='before')
    @classmethod
    def parse_candidate_type(cls, v) -> int:
        """Accept text labels or integers and normalise to 0/1/2."""
        key = str(v).lower().strip()
        if key in _CANDIDATE_TYPE_MAP:
            return _CANDIDATE_TYPE_MAP[key]
        try:
            val = int(float(key))
            if val in (0, 1, 2):
                return val
        except (ValueError, TypeError):
            pass
        raise ValueError(
            f'Invalid candidate_type "{v}". Use: new (0), incumbent (1), mixed (2)'
        )

    @model_validator(mode='after')
    def alliance_gte_party(self) -> 'PredictRequest':
        """Alliance strength must be >= party's own MLA count."""
        if self.alliance_mla_strength < self.mla_strength:
            raise ValueError(
                'alliance_mla_strength must be >= mla_strength '
                f'(got {self.alliance_mla_strength} < {self.mla_strength})'
            )
        return self


class HistoricalEntry(BaseModel):
    year:                  int
    mla_strength:          int
    alliance_mla_strength: int
    past_rs_wins:          int
    winner:                int

class PartyInfo(BaseModel):
    party_name:               str
    icon:                     str
    description:              str
    current_mla_strength:     int
    current_alliance_strength:int
    total_rs_wins:            int
    win_rate:                 float
    historical_data:          List[HistoricalEntry]

class PredictResponse(BaseModel):
    success:         bool
    prediction:      int
    win_probability: float
    party_name:      str
    party:           str
    party_info:      Optional[PartyInfo] = None

class PartiesResponse(BaseModel):
    success: bool
    parties: List[PartyInfo]

class PartyDetailResponse(BaseModel):
    success: bool
    party:   PartyInfo

class StatsResponse(BaseModel):
    success:        bool
    total_records:  int
    unique_parties: List[str]
    years:          List[int]
    party_wins:     Dict[str, int]

class ErrorResponse(BaseModel):
    success: bool = False
    error:   str

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
    return templates.TemplateResponse(request, "index.html")

@app.get('/debug-render')
async def debug_render(request: Request):
    """Debug route to expose template rendering errors"""
    import traceback
    try:
        resp = templates.TemplateResponse(request, "index.html")
        return JSONResponse({"status": "ok", "content_length": len(resp.body)})
    except Exception as e:
        return JSONResponse({"status": "error", "error": str(e), "trace": traceback.format_exc()})

@app.get('/parties', response_class=HTMLResponse)
async def parties(request: Request):
    """Render the parties listing page"""
    return templates.TemplateResponse(request, "parties.html")

@app.get('/party/{party_name}', response_class=HTMLResponse)
async def party_detail(request: Request, party_name: str):
    """Render individual party detail page"""
    party_info = get_party_info(party_name)

    if party_info is None:
        return HTMLResponse(content=f"Party '{party_name}' not found", status_code=404)

    return templates.TemplateResponse(request, "party_detail.html", {"party": party_info})

@app.get('/about', response_class=HTMLResponse)
async def about(request: Request):
    """Render the about page"""
    return templates.TemplateResponse(request, "about.html")

@app.get('/sw.js')
async def service_worker():
    """Serve the Service Worker from the root scope"""
    sw_path = os.path.join(os.path.dirname(__file__), 'static', 'js', 'sw.js')
    return FileResponse(sw_path, media_type='application/javascript')

# ==================== API ENDPOINTS ====================

@app.get('/api/parties', response_model=PartiesResponse)
async def api_parties():
    """API endpoint to get all parties"""
    if data is None:
        load_and_train_model()

    parties_info: List[PartyInfo] = []
    for party_name in data['party'].unique():
        if party_name == 'Independent':
            continue
        raw = get_party_info(party_name)
        if raw:
            parties_info.append(PartyInfo(**raw))

    parties_info.sort(key=lambda p: p.current_mla_strength, reverse=True)

    return PartiesResponse(success=True, parties=parties_info)


@app.get('/api/party/{party_name}', response_model=PartyDetailResponse)
async def api_party_detail(party_name: str):
    """API endpoint to get detailed party information"""
    raw = get_party_info(party_name)
    if raw is None:
        raise HTTPException(
            status_code=404,
            detail=f'Party "{party_name}" not found',
        )
    return PartyDetailResponse(success=True, party=PartyInfo(**raw))

@app.post('/predict', response_model=PredictResponse)
async def predict(body: PredictRequest):
    """
    Predict Rajya Sabha election outcome.

    Accepts a validated `PredictRequest` body. Pydantic handles all
    type coercion, range checks, and alias resolution for candidate_type
    before this function is even called.
    """
    # Ensure model is loaded
    if model is None:
        load_and_train_model()

    # Encode party name — fall back to first known class if unseen
    try:
        party_encoded = int(le_party.transform([body.party_name])[0])
    except ValueError:
        party_encoded = int(le_party.transform([le_party.classes_[0]])[0])

    has_majority   = 1 if body.alliance_mla_strength >= 145 else 0
    mla_share      = body.mla_strength / 288
    alliance_share = body.alliance_mla_strength / 288

    # ── Build 9-feature input vector matching training features ────
    prediction_data = np.array([[
        2027,                          # prediction year
        party_encoded,                 # party identity
        body.mla_strength,
        body.alliance_mla_strength,
        body.past_rs_wins,
        body.candidate_type,           # already 0/1/2 after validation
        has_majority,
        mla_share,
        alliance_share,
    ]])

    prediction  = model.predict(prediction_data)[0]
    probability = model.predict_proba(prediction_data)[0]

    party_info_raw = get_party_info(body.party_name)
    party_info = PartyInfo(**party_info_raw) if party_info_raw else None

    return PredictResponse(
        success=True,
        prediction=int(prediction),
        win_probability=round(float(probability[1]) * 100, 2),
        party_name=body.party_name,
        party=body.party_name,
        party_info=party_info,
    )

@app.get('/api/stats', response_model=StatsResponse)
async def get_stats():
    """API endpoint to get model statistics"""
    if data is None:
        load_and_train_model()

    party_wins = data[data['winner'] == 1].groupby('party').size().to_dict()

    return StatsResponse(
        success=True,
        total_records=int(len(data)),
        unique_parties=data['party'].unique().tolist(),
        years=sorted(data['year'].unique().tolist()),
        party_wins={str(k): int(v) for k, v in party_wins.items()},
    )

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
