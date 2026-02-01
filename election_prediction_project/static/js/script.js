// Party color mapping
const partyColors = {
    'BJP': '#FF9933',
    'INC': '#19AAED',
    'NCP': '#00B2A9',
    'Shiv Sena': '#F37020'
};

// Fetch and display predictions
async function loadPredictions() {
    try {
        const response = await fetch('/api/predictions');
        const data = await response.json();

        if (data.success) {
            displayWinner(data.winner, data.runner_up);
            displayAllParties(data.predictions);
            hideLoading();
        }
    } catch (error) {
        console.error('Error loading predictions:', error);
        hideLoading();
        showError();
    }
}

// Display winner section
function displayWinner(winner, runnerUp) {
    if (!winner) return;

    document.getElementById('winner-party').textContent = winner.party;
    document.getElementById('winner-probability').textContent = winner.win_probability + '%';
    document.getElementById('winner-mla').textContent = winner.mla_strength;
    document.getElementById('winner-alliance').textContent = winner.alliance_strength;

    // Update runner-up
    if (runnerUp) {
        document.getElementById('runner-up-party').textContent = runnerUp.party;
        document.getElementById('runner-up-probability').textContent = runnerUp.win_probability + '%';
    }

    // Show winner section
    document.getElementById('winner-section').classList.remove('hidden');
}

// Display all parties
function displayAllParties(predictions) {
    const grid = document.getElementById('parties-grid');
    grid.innerHTML = '';

    predictions.forEach((party, index) => {
        const card = createPartyCard(party, index);
        grid.appendChild(card);
    });
}

// Create party card
function createPartyCard(party, index) {
    const card = document.createElement('div');
    card.className = 'party-card';
    card.style.animationDelay = `${index * 0.1}s`;

    const badgeClass = party.prediction === 1 ? 'badge-win' : 'badge-lose';
    const badgeText = party.prediction === 1 ? 'WIN' : 'LOSE';

    card.innerHTML = `
        <div class="party-header">
            <div class="party-name" style="color: ${partyColors[party.party] || '#333'}">${party.party}</div>
            <div class="party-badge ${badgeClass}">${badgeText}</div>
        </div>
        <div class="party-probability">${party.win_probability}%</div>
        <div class="party-details">
            <div class="detail-row">
                <span class="detail-label">MLA Strength</span>
                <span class="detail-value">${party.mla_strength}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Alliance Strength</span>
                <span class="detail-value">${party.alliance_strength}</span>
            </div>
            <div class="detail-row">
                <span class="detail-label">Past RS Wins</span>
                <span class="detail-value">${party.past_rs_wins}</span>
            </div>
        </div>
    `;

    return card;
}

// Hide loading spinner
function hideLoading() {
    document.getElementById('loading').classList.add('hidden');
}

// Show error message
function showError() {
    const loading = document.getElementById('loading');
    loading.innerHTML = `
        <div style="color: #fff; text-align: center;">
            <h2>⚠️ Error Loading Predictions</h2>
            <p>Unable to fetch prediction data. Please refresh the page.</p>
            <button onclick="location.reload()" style="
                margin-top: 20px;
                padding: 10px 30px;
                background: #fff;
                color: #667eea;
                border: none;
                border-radius: 25px;
                font-size: 1rem;
                cursor: pointer;
                font-weight: 600;
            ">Refresh Page</button>
        </div>
    `;
}

// Add smooth scroll behavior
document.addEventListener('DOMContentLoaded', () => {
    // Load predictions on page load
    loadPredictions();

    // Add intersection observer for animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    // Observe sections
    document.querySelectorAll('.parties-section, .info-section').forEach(section => {
        section.style.opacity = '0';
        section.style.transform = 'translateY(30px)';
        section.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(section);
    });
});

// Add party card hover effect with color
document.addEventListener('mouseover', (e) => {
    if (e.target.closest('.party-card')) {
        const card = e.target.closest('.party-card');
        const partyName = card.querySelector('.party-name').textContent;
        const color = partyColors[partyName];
        if (color) {
            card.style.borderLeft = `5px solid ${color}`;
        }
    }
});

document.addEventListener('mouseout', (e) => {
    if (e.target.closest('.party-card')) {
        const card = e.target.closest('.party-card');
        card.style.borderLeft = 'none';
    }
});
