/**
 * Election Outcome Prediction - Frontend JavaScript
 * Simplified to use only dataset features
 */

// Get DOM elements
const form = document.getElementById('predictionForm');
const submitBtn = document.getElementById('submitBtn');
const errorMessage = document.getElementById('errorMessage');
const resultSection = document.getElementById('resultSection');
const formSection = document.querySelector('.form-section');

/**
 * Form submission handler
 */
form.addEventListener('submit', async (e) => {
    e.preventDefault();

    // Clear previous error messages
    hideError();

    // Get form data
    const formData = new FormData(form);
    const data = {
        party_name: formData.get('party_name'),
        mla_strength: formData.get('mla_strength'),
        alliance_mla_strength: formData.get('alliance_mla_strength'),
        past_rs_wins: formData.get('past_rs_wins'),
        candidate_type: formData.get('candidate_type')
    };

    // Client-side validation
    if (!validateForm(data)) {
        return;
    }

    // Show loading state
    setLoadingState(true);

    try {
        // Send POST request to backend
        const response = await fetch('/predict', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        // Hide loading state
        setLoadingState(false);

        // Check if request was successful
        if (result.success) {
            displayResult(result);
        } else {
            showError(result.error || 'An error occurred while processing your request');
        }

    } catch (error) {
        setLoadingState(false);
        showError('Unable to connect to the server. Please try again later.');
        console.error('Error:', error);
    }
});

/**
 * Validates form data
 */
function validateForm(data) {
    // Check for empty fields
    const requiredFields = ['party_name', 'mla_strength', 'alliance_mla_strength', 'past_rs_wins', 'candidate_type'];

    for (const field of requiredFields) {
        if (!data[field] || data[field].toString().trim() === '') {
            showError('Please fill in all required fields');
            return false;
        }
    }

    // Validate numeric fields
    const mlaStrength = parseFloat(data.mla_strength);
    if (isNaN(mlaStrength) || mlaStrength < 0) {
        showError('MLA strength must be a positive number');
        return false;
    }

    const allianceMlaStrength = parseFloat(data.alliance_mla_strength);
    if (isNaN(allianceMlaStrength) || allianceMlaStrength < 0) {
        showError('Alliance MLA strength must be a positive number');
        return false;
    }

    const pastRsWins = parseFloat(data.past_rs_wins);
    if (isNaN(pastRsWins) || pastRsWins < 0) {
        showError('Past RS wins must be a positive number');
        return false;
    }

    return true;
}

/**
 * Displays the prediction result
 */
function displayResult(result) {
    // Get result elements
    const resultCard = document.querySelector('.result-card');
    const resultIcon = document.getElementById('resultIcon');
    const resultPrediction = document.getElementById('resultPrediction');
    const resultParty = document.getElementById('resultParty');
    const resultConfidence = document.getElementById('resultConfidence');
    const confidenceFill = document.getElementById('confidenceFill');
    const partyInfoBox = document.getElementById('partyInfoBox');

    // Set result values
    resultParty.textContent = result.party_name || result.party || '-';
    resultConfidence.textContent = result.win_probability || result.confidence || 0;

    // Set prediction text
    if (result.prediction === 1 || result.prediction === 'Win') {
        resultPrediction.textContent = 'Win';
        resultIcon.textContent = '🏆';
        resultCard.classList.remove('lose');
        resultCard.classList.add('win');
    } else {
        resultPrediction.textContent = 'Lose';
        resultIcon.textContent = '📊';
        resultCard.classList.remove('win');
        resultCard.classList.add('lose');
    }

    // Animate confidence bar
    const confidenceValue = result.win_probability || result.confidence || 0;
    setTimeout(() => {
        confidenceFill.style.width = confidenceValue + '%';
    }, 100);

    // Display party information if available
    if (result.party_info) {
        displayPartyInfo(result.party_info);
    } else if (result.party_name) {
        fetchPartyInfo(result.party_name);
    }

    // Hide form and show result
    formSection.classList.add('hidden');
    resultSection.classList.remove('hidden');

    // Scroll to result
    resultSection.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Display party information
 */
function displayPartyInfo(partyInfo) {
    const partyInfoBox = document.getElementById('partyInfoBox');
    const partyStats = document.getElementById('partyStats');
    const viewPartyLink = document.getElementById('viewPartyLink');

    // Build stats HTML
    let statsHTML = '';
    if (partyInfo.current_mla_strength !== undefined) {
        statsHTML += `
            <div class="party-stat">
                <div class="stat-label">MLA Strength</div>
                <div class="stat-value">${partyInfo.current_mla_strength}</div>
            </div>
        `;
    }
    if (partyInfo.total_rs_wins !== undefined) {
        statsHTML += `
            <div class="party-stat">
                <div class="stat-label">RS Wins</div>
                <div class="stat-value">${partyInfo.total_rs_wins}</div>
            </div>
        `;
    }
    if (partyInfo.win_rate !== undefined) {
        statsHTML += `
            <div class="party-stat">
                <div class="stat-label">Win Rate</div>
                <div class="stat-value">${partyInfo.win_rate}%</div>
            </div>
        `;
    }

    partyStats.innerHTML = statsHTML;
    viewPartyLink.href = `/party/${partyInfo.party_name || partyInfo.name}`;
    partyInfoBox.classList.remove('hidden');
}

/**
 * Fetch party information from API
 */
async function fetchPartyInfo(partyName) {
    try {
        const response = await fetch(`/api/party/${encodeURIComponent(partyName)}`);
        const data = await response.json();

        if (data.success) {
            displayPartyInfo(data.party);
        }
    } catch (error) {
        console.error('Error fetching party info:', error);
    }
}

/**
 * Shows error message
 */
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
    errorMessage.scrollIntoView({ behavior: 'smooth', block: 'center' });
}

/**
 * Hides error message
 */
function hideError() {
    errorMessage.classList.add('hidden');
    errorMessage.textContent = '';
}

/**
 * Sets loading state for submit button
 */
function setLoadingState(isLoading) {
    if (isLoading) {
        submitBtn.disabled = true;
        submitBtn.classList.add('loading');
        submitBtn.querySelector('.btn-text').textContent = 'Processing';
    } else {
        submitBtn.disabled = false;
        submitBtn.classList.remove('loading');
        submitBtn.querySelector('.btn-text').textContent = 'Predict Outcome';
    }
}

/**
 * Resets the form
 */
function resetForm() {
    form.reset();
    resultSection.classList.add('hidden');
    formSection.classList.remove('hidden');
    hideError();
    document.getElementById('confidenceFill').style.width = '0%';
    document.getElementById('partyInfoBox').classList.add('hidden');
    formSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/**
 * Add input enhancements
 */
document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('.form-input, .form-select');

    inputs.forEach(input => {
        input.addEventListener('focus', function () {
            this.parentElement.classList.add('focused');
        });

        input.addEventListener('blur', function () {
            this.parentElement.classList.remove('focused');
        });
    });

    // Number input validation
    const numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(input => {
        input.addEventListener('input', function () {
            this.value = this.value.replace(/[^0-9.]/g, '');
            const parts = this.value.split('.');
            if (parts.length > 2) {
                this.value = parts[0] + '.' + parts.slice(1).join('');
            }
        });
    });
});

/**
 * Prevent form submission on Enter in inputs
 */
form.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && e.target.tagName !== 'BUTTON') {
        e.preventDefault();
    }
});
