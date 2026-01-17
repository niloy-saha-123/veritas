// Background service worker - manages extension lifecycle and API calls

console.log('Veritas.dev background service worker initialized');

/**
 * Handle extension installation
 */
chrome.runtime.onInstalled.addListener((details) => {
    if (details.reason === 'install') {
        console.log('Veritas.dev extension installed');

        // Set default settings
        chrome.storage.sync.set({
            apiUrl: 'http://localhost:8000/api/v1',
            autoAnalyze: false,
            notifications: true
        });
    }
});

/**
 * Handle messages from content scripts and popup
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'openPopup') {
        chrome.action.openPopup();
    }

    if (request.action === 'analyze') {
        // Forward to API or handle background analysis
        handleBackgroundAnalysis(request.data)
            .then(result => sendResponse({ success: true, result }))
            .catch(error => sendResponse({ success: false, error: error.message }));

        return true; // Keep channel open for async response
    }
});

/**
 * Handle background analysis
 */
async function handleBackgroundAnalysis(data) {
    try {
        const settings = await chrome.storage.sync.get(['apiUrl']);
        const apiUrl = settings.apiUrl || 'http://localhost:8000/api/v1';

        const response = await fetch(`${apiUrl}/analyze`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });

        return await response.json();
    } catch (error) {
        console.error('Background analysis error:', error);
        throw error;
    }
}

/**
 * Create context menu items
 */
chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: 'veritas-analyze',
        title: 'Analyze with Veritas.dev',
        contexts: ['selection']
    });
});

/**
 * Handle context menu clicks
 */
chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === 'veritas-analyze') {
        // Send selected text for analysis
        chrome.tabs.sendMessage(tab.id, {
            action: 'analyzeSelection',
            text: info.selectionText
        });
    }
});
