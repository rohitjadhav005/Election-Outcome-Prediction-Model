/**
 * Election Outcome Prediction — Frontend JavaScript
 * Aligned with backend API: /predict, /api/stats, /api/party/<name>
 */

// ── DOM Elements ──────────────────────────────────────────────
const form = document.getElementById('predictionForm');
const submitBtn = document.getElementById('submitBtn');
const errorMessage = document.getElementById('errorMessage');
const resultSection = document.getElementById('resultSection');
const formSection = document.getElementById('formSection');

// ── Load live stats into banner ───────────────────────────────
async function loadStats() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();
        if (!data.success) return;

        document.getElementById('totalRecords').textContent = data.total_records ?? '—';
        document.getElementById('totalParties').textContent = (data.unique_parties ?? []).length || '—';

        // Find the party with the most wins
        const wins = data.party_wins ?? {};
        const topParty = Object.entries(wins).sort((a, b) => b[1] - a[1])[0];
        if (topParty) {
            document.getElementById('topParty').textContent = `${topParty[0]} (${topParty[1]})`;
        }
    } catch (e) {
        console.warn('Could not load stats:', e);
    }
}

// ── Auto-select party from URL (e.g. /?party=BJP) ─────────────
function autoSelectParty() {
    const params = new URLSearchParams(window.location.search);
    const party = params.get('party');
    if (party) {
        const select = document.getElementById('partyName');
        for (const opt of select.options) {
            if (opt.value === party) {
                select.value = party;
                break;
            }
        }
    }
}

// ── Form submission ───────────────────────────────────────────
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    hideError();

    const formData = new FormData(form);
    const payload = {
        party_name: formData.get('party_name'),
        mla_strength: formData.get('mla_strength'),
        alliance_mla_strength: formData.get('alliance_mla_strength'),
        past_rs_wins: formData.get('past_rs_wins'),
        candidate_type: formData.get('candidate_type')
    };

    if (!validateForm(payload)) return;

    setLoadingState(true);

    try {
        const response = await fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        setLoadingState(false);

        if (result.success) {
            displayResult(result);
        } else {
            showError(result.error || 'An error occurred. Please try again.');
        }

    } catch (err) {
        setLoadingState(false);
        showError('Unable to connect to the server. Please try again.');
        console.error('Fetch error:', err);
    }
});

// ── Validation ────────────────────────────────────────────────
function validateForm(data) {
    const required = ['party_name', 'mla_strength', 'alliance_mla_strength', 'past_rs_wins', 'candidate_type'];
    for (const field of required) {
        if (!data[field] || data[field].toString().trim() === '') {
            showError('Please fill in all required fields.');
            return false;
        }
    }

    if (isNaN(parseFloat(data.mla_strength)) || parseFloat(data.mla_strength) < 0) {
        showError('MLA Strength must be a positive number.'); return false;
    }
    if (isNaN(parseFloat(data.alliance_mla_strength)) || parseFloat(data.alliance_mla_strength) < 0) {
        showError('Alliance MLA Strength must be a positive number.'); return false;
    }
    if (isNaN(parseFloat(data.past_rs_wins)) || parseFloat(data.past_rs_wins) < 0) {
        showError('Past Rajya Sabha Wins must be a positive number.'); return false;
    }

    return true;
}

// ── Display result ────────────────────────────────────────────
function displayResult(result) {
    const resultCard = document.querySelector('.result-card');
    const resultIcon = document.getElementById('resultIcon');
    const resultPrediction = document.getElementById('resultPrediction');
    const resultParty = document.getElementById('resultParty');
    const resultConfidence = document.getElementById('resultConfidence');
    const confidenceFill = document.getElementById('confidenceFill');

    const partyName = result.party_name || result.party || '-';
    const winProb = result.win_probability ?? 0;
    const isWin = result.prediction === 1;

    resultParty.textContent = partyName;
    resultConfidence.textContent = winProb;

    if (isWin) {
        resultPrediction.textContent = '🏆 Likely to WIN';
        resultIcon.textContent = '🏆';
        resultCard.classList.replace('lose', 'win') || resultCard.classList.add('win');
    } else {
        resultPrediction.textContent = '📉 Likely to LOSE';
        resultIcon.textContent = '📊';
        resultCard.classList.replace('win', 'lose') || resultCard.classList.add('lose');
    }

    // Animate probability bar
    setTimeout(() => {
        confidenceFill.style.width = winProb + '%';
    }, 100);

    // Show party background stats if returned by backend
    if (result.party_info) {
        displayPartyInfo(result.party_info);
    } else {
        fetchAndDisplayPartyInfo(partyName);
    }

    // Swap form → result
    formSection.classList.add('hidden');
    resultSection.classList.remove('hidden');
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

// ── Party info box ────────────────────────────────────────────
function displayPartyInfo(info) {
    const box = document.getElementById('partyInfoBox');
    const partyStats = document.getElementById('partyStats');
    const viewPartyLink = document.getElementById('viewPartyLink');

    partyStats.innerHTML = `
        <div class="party-stat">
            <div class="stat-label">MLA Strength</div>
            <div class="stat-value">${info.current_mla_strength ?? '—'}</div>
        </div>
        <div class="party-stat">
            <div class="stat-label">Alliance Strength</div>
            <div class="stat-value">${info.current_alliance_strength ?? '—'}</div>
        </div>
        <div class="party-stat">
            <div class="stat-label">RS Wins</div>
            <div class="stat-value">${info.total_rs_wins ?? '—'}</div>
        </div>
        <div class="party-stat">
            <div class="stat-label">Win Rate</div>
            <div class="stat-value">${info.win_rate ?? '—'}%</div>
        </div>
    `;

    viewPartyLink.href = `/party/${encodeURIComponent(info.party_name || info.name || '')}`;
    box.classList.remove('hidden');
}

async function fetchAndDisplayPartyInfo(partyName) {
    try {
        const res = await fetch(`/api/party/${encodeURIComponent(partyName)}`);
        const data = await res.json();
        if (data.success) displayPartyInfo(data.party);
    } catch (e) {
        console.warn('Could not fetch party info:', e);
    }
}

// ── UI helpers ────────────────────────────────────────────────
function showError(msg) {
    errorMessage.textContent = msg;
    errorMessage.classList.remove('hidden');
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

function hideError() {
    errorMessage.classList.add('hidden');
    errorMessage.textContent = '';
}

function setLoadingState(loading) {
    submitBtn.disabled = loading;
    submitBtn.classList.toggle('loading', loading);
    submitBtn.querySelector('.btn-text').textContent = loading ? 'Processing' : 'Predict Outcome';
}

function resetForm() {
    form.reset();
    resultSection.classList.add('hidden');
    formSection.classList.remove('hidden');
    hideError();
    document.getElementById('confidenceFill').style.width = '0%';
    document.getElementById('partyInfoBox').classList.add('hidden');
    document.querySelector('.result-card')?.classList.remove('win', 'lose');
    formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Input enhancements ────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    loadStats();
    autoSelectParty();

    document.querySelectorAll('.form-input, .form-select').forEach(el => {
        el.addEventListener('focus', () => el.parentElement.classList.add('focused'));
        el.addEventListener('blur', () => el.parentElement.classList.remove('focused'));
    });

    // Prevent non-numeric characters in number fields
    document.querySelectorAll('input[type="number"]').forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9]/g, '');
        });
    });
});

// Prevent accidental Enter submission
form.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && e.target.tagName !== 'BUTTON') e.preventDefault();
});
