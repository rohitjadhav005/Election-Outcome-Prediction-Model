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

const PARTY_LOGO_MAP = {
    'BJP': '/static/images/parties/bjp.png',
    'INC': '/static/images/parties/inc.png',
    'NCP': '/static/images/parties/ncp.png',
    'NCP(Ajit)': '/static/images/parties/ncp_ajit.png',
    'NCP(Sharad)': '/static/images/parties/ncp_sharad.png',
    'SS': '/static/images/parties/ss.png',
    'SS(Shinde)': '/static/images/parties/ss_shinde.png',
    'SS(UBT)': '/static/images/parties/ss_ubt.png',
    'Shiv Sena': '/static/images/parties/ss.png',
    'PWP': '/static/images/parties/pwp.png',
    'Janata Party': '/static/images/parties/janata.png'
};

function getPartyLogoUrl(party) {
    if (party.logo_url && party.logo_url.startsWith('/')) return party.logo_url;
    if (party.icon && party.icon.startsWith('/')) return party.icon;
    if (PARTY_LOGO_MAP[party.party_name]) return PARTY_LOGO_MAP[party.party_name];
    const slug = (party.party_name || '').toLowerCase().replace(/[^a-z0-9]/g, '_');
    return `/static/images/parties/${slug}.png`;
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

    const logoSrc = getPartyLogoUrl(party);

    card.innerHTML = `
        <div class="party-card-header">
            <div class="party-logo-box">
                <img src="${logoSrc}" alt="${party.party_name} Logo" class="party-logo-img" onerror="this.onerror=null; this.src='/static/images/logo.png';">
            </div>
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
                <span class="party-detail-label">Seat Wins:</span>
                <span class="party-detail-value">${party.total_rs_wins}</span>
            </div>
            <div class="party-detail-item">
                <span class="party-detail-label">Weighted Win Rate:</span>
                <span class="party-detail-value" style="color: ${party.win_rate >= 70 ? '#15803d' : party.win_rate <= 20 ? '#dc2626' : '#d97706'}">
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
                <div style="color: #ef4444; font-size: 1.2rem; font-weight: 600;">${message}</div>
            </div>
        </div>
    `;
}
