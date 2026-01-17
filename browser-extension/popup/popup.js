// Popup UI script - handles analyze button clicks and displays results from API

const API_BASE_URL = 'http://localhost:8000/api/v1';

// DOM Elements
const analyzeBtn = document.getElementById('analyzeBtn');
const settingsBtn = document.getElementById('settingsBtn');
const statusText = document.getElementById('statusText');
const resultsCard = document.getElementById('resultsCard');
const resultsDiv = document.getElementById('results');

// Event Listeners
analyzeBtn.addEventListener('click', handleAnalyze);
settingsBtn.addEventListener('click', handleSettings);

/**
 * Handle analyze button click
 */
async function handleAnalyze() {
    updateStatus('Analyzing...', 'active');

    try {
        // Get current tab
        const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });

        // Send message to content script
        const response = await chrome.tabs.sendMessage(tab.id, { action: 'analyze' });

        if (response && response.data) {
            await performAnalysis(response.data);
        } else {
            updateStatus('No analyzable content found', 'inactive');
        }
    } catch (error) {
        console.error('Analysis error:', error);
        updateStatus('Analysis failed', 'inactive');
    }
}

/**
 * Perform analysis by calling the API
 */
async function performAnalysis(data) {
    try {
        const response = await fetch(`${API_BASE_URL}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                code_content: data.code,
                doc_content: data.documentation,
                language: data.language || 'python'
            })
        });

        const result = await response.json();
        displayResults(result);
        updateStatus('Analysis complete', 'active');
    } catch (error) {
        console.error('API error:', error);
        updateStatus('API connection failed', 'inactive');
    }
}

/**
 * Display analysis results
 */
function displayResults(result) {
    resultsCard.style.display = 'block';

    if (result.discrepancies && result.discrepancies.length > 0) {
        resultsDiv.innerHTML = `
            <p style="margin-bottom: 10px;">Found ${result.discrepancies.length} discrepancies:</p>
            <ul style="padding-left: 20px; font-size: 12px;">
                ${result.discrepancies.map(d => `
                    <li style="margin-bottom: 5px;">
                        <strong>${d.type}</strong>: ${d.description}
                    </li>
                `).join('')}
            </ul>
        `;
    } else {
        resultsDiv.innerHTML = '<p>✅ No discrepancies found!</p>';
    }
}

/**
 * Update status message
 */
function updateStatus(message, state) {
    statusText.textContent = message;
    const indicator = document.querySelector('.status-indicator');
    indicator.className = `status-indicator ${state}`;
}

/**
 * Handle settings button click
 */
function handleSettings() {
    // TODO: Implement settings page
    alert('Settings coming soon!');
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    console.log('Veritas.dev extension loaded');
});
