/**
 * Parties Page JavaScript
 * Loads and displays all political parties
 */

document.addEventListener('DOMContentLoaded', async () => {
    const partiesGrid = document.getElementById('partiesGrid');

    try {
        // Fetch parties data from API
        const response = await fetch('/api/parties');
        const data = await response.json();

        if (data.success && data.parties) {
            displayParties(data.parties);
        } else {
            showError('Failed to load parties data');
        }
    } catch (error) {
        console.error('Error loading parties:', error);
        showError('Unable to load parties. Please try again later.');
    }
});

/**
 * Display parties in grid layout
 * @param {Array} parties - Array of party objects
 */
function displayParties(parties) {
    const partiesGrid = document.getElementById('partiesGrid');

    // Clear loading message
    partiesGrid.innerHTML = '';

    // Create party cards
    parties.forEach(party => {
        const card = createPartyCard(party);
        partiesGrid.appendChild(card);
    });
}

/**
 * Create a party card element
 * @param {Object} party - Party object
 * @returns {HTMLElement} - Party card element
 */
function createPartyCard(party) {
    const card = document.createElement('div');
    card.className = 'party-card glass-panel';
    card.onclick = () => {
        window.location.href = `/party/${encodeURIComponent(party.party_name)}`;
    };

    card.innerHTML = `
        <div class="party-card-header">
            <div class="party-icon">${party.icon || '🏛️'}</div>
            <div class="party-name">${party.party_name}</div>
        </div>
        <div class="party-card-body">
            <div class="party-detail-item">
                <span class="party-detail-label">MLA Strength:</span>
                <span class="party-detail-value">${party.current_mla_strength}</span>
            </div>
            <div class="party-detail-item">
                <span class="party-detail-label">Alliance Strength:</span>
                <span class="party-detail-value">${party.current_alliance_strength}</span>
            </div>
            <div class="party-detail-item">
                <span class="party-detail-label">RS Wins:</span>
                <span class="party-detail-value">${party.total_rs_wins}</span>
            </div>
            <div class="party-detail-item">
                <span class="party-detail-label">Weighted Win Rate:</span>
                <span class="party-detail-value" style="color: ${party.win_rate >= 70 ? '#2ecc71' : party.win_rate <= 20 ? '#e74c3c' : '#f39c12'}">
                    ${party.win_rate.toFixed(1)}%
                </span>
            </div>
        </div>
        <div class="party-card-footer">
            <a href="/party/${encodeURIComponent(party.party_name)}" class="view-details-btn" onclick="event.stopPropagation();">
                View Details →
            </a>
        </div>
    `;

    return card;
}

/**
 * Show error message
 * @param {string} message - Error message
 */
function showError(message) {
    const partiesGrid = document.getElementById('partiesGrid');
    partiesGrid.innerHTML = `
        <div style="grid-column: 1/-1; text-align: center; padding: 40px;">
            <div class="glass-panel" style="padding: 30px; text-align: center;">
                <div style="font-size: 3rem; margin-bottom: 15px;">⚠️</div>
                <div style="color: #ef4444; font-size: 1.2rem; font-weight: 600;">${message}</div>
            </div>
        </div>
    `;
}
