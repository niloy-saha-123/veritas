// Content script - extracts code/docs from GitHub pages and adds floating action button

console.log('Veritas.dev content script loaded');

/**
 * Extract code from GitHub repository pages
 */
function extractGitHubCode() {
    const codeElements = document.querySelectorAll('.blob-code-inner, .highlight pre');
    let code = '';

    codeElements.forEach(element => {
        code += element.textContent + '\n';
    });

    return code.trim();
}

/**
 * Extract documentation content
 */
function extractDocumentation() {
    // Look for common documentation containers
    const docSelectors = [
        'article',
        '.markdown-body',
        '.documentation',
        'main'
    ];

    for (const selector of docSelectors) {
        const element = document.querySelector(selector);
        if (element) {
            return element.textContent.trim();
        }
    }

    return '';
}

/**
 * Detect programming language from page
 */
function detectLanguage() {
    // Check file extension in URL
    const url = window.location.href;
    const extensions = {
        '.py': 'python',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.java': 'java',
        '.go': 'go',
        '.rs': 'rust'
    };

    for (const [ext, lang] of Object.entries(extensions)) {
        if (url.includes(ext)) {
            return lang;
        }
    }

    // Check language badge on GitHub
    const langBadge = document.querySelector('[itemprop="programmingLanguage"]');
    if (langBadge) {
        return langBadge.textContent.toLowerCase();
    }

    return 'python'; // default
}

/**
 * Listen for messages from popup
 */
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'analyze') {
        const data = {
            code: extractGitHubCode(),
            documentation: extractDocumentation(),
            language: detectLanguage(),
            url: window.location.href
        };

        sendResponse({ success: true, data });
    }

    return true; // Keep message channel open for async response
});

/**
 * Add floating action button for quick analysis
 */
function addFloatingButton() {
    const button = document.createElement('button');
    button.id = 'veritas-fab';
    button.innerHTML = '⚖️';
    button.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 56px;
        height: 56px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        color: white;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
        z-index: 10000;
        transition: transform 0.2s ease;
    `;

    button.addEventListener('mouseenter', () => {
        button.style.transform = 'scale(1.1)';
    });

    button.addEventListener('mouseleave', () => {
        button.style.transform = 'scale(1)';
    });

    button.addEventListener('click', () => {
        chrome.runtime.sendMessage({ action: 'openPopup' });
    });

    document.body.appendChild(button);
}

// Initialize
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', addFloatingButton);
} else {
    addFloatingButton();
}
