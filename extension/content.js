console.log('Content script loaded - v8');

function createPopup() {
    const popup = document.createElement('div');
    popup.className = 'summary-popup';
    
    // Create internal structure
    popup.innerHTML = `
        <div class="summary-header">
            <div class="summary-icon">📚</div>
            <div class="summary-title">Article Summary</div>
            <div class="read-time">⏱️ <span class="time-value">...</span></div>
        </div>
        <div class="summary-content">
            <div class="summary-loading">
                <div class="loading-spinner"></div>
                <div class="loading-text">Generating summary...</div>
            </div>
        </div>
        <div class="summary-footer">
            <div class="summary-badge">AI Generated</div>
        </div>
    `;
    
    return popup;
}

async function getSummary(url) {
    try {
        const response = await fetch('http://localhost:5001/summarize', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url })
        });

        const data = await response.json();
        return data.summary || 'No summary available';
    } catch (error) {
        console.error('Error:', error);
        return 'Failed to load summary';
    }
}

function processSearchResults() {
    // Target specific Google search result elements
    const results = document.querySelectorAll('div.g, div[data-hveid]');
    console.log(`Found ${results.length} search results`);

    results.forEach(result => {
        // Skip if already processed
        if (result.hasAttribute('data-has-summary')) return;
        result.setAttribute('data-has-summary', 'true');

        // Find the title link
        const titleElement = result.querySelector('h3');
        if (!titleElement) return;

        const link = titleElement.closest('a') || result.querySelector('a');
        if (!link) return;

        // Create and position popup
        const popup = createPopup();
        result.style.position = 'relative';
        result.appendChild(popup);

        let isFetching = false;

        // Add hover handlers
        result.addEventListener('mouseenter', async () => {
            if (isFetching) return;
            isFetching = true;

            console.log('Hovering over:', link.href);
            popup.style.display = 'block';
            
            const summary = await getSummary(link.href);
            if (popup.style.display === 'block') {
                popup.innerHTML = summary;
            }
            
            isFetching = false;
        });

        result.addEventListener('mouseleave', () => {
            popup.style.display = 'none';
        });
    });
}
// Updated styles
const styles = `
    .summary-popup {
        position: absolute;
        top: 100%;
        left: 0;
        width: 80%; /* Decrease width for a smaller popup */
        max-width: 400px; /* Smaller max width */
        background: #ffffff;
        border: 1px solid rgba(0, 0, 0, 0.1);
        border-radius: 8px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        margin-top: 8px;
        z-index: 1000;
        display: none;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
        opacity: 0;
        transform: translateY(-10px);
        transition: all 0.3s ease;
    }

    .summary-popup.visible {
        opacity: 1;
        transform: translateY(0);
    }

    .read-time {
        font-size: 11px;
        color: #5f6368;
        margin-left: auto;
        padding: 2px 8px;
        background: #f1f3f4;
        border-radius: 12px;
        display: flex;
        align-items: center;
        gap: 4px;
    }

    .summary-header {
        display: flex;
        align-items: center;
        padding: 8px 12px;
        gap: 8px;
    }

    .summary-header {
        display: flex;
        align-items: center;
        padding: 8px 12px; /* Reduced padding */
        background: #f8f9fa;
        border-bottom: 1px solid rgba(0, 0, 0, 0.1);
    }

    .summary-icon {
        font-size: 18px;
        margin-right: 6px; /* Reduced margin */
    }

    .summary-title {
        font-size: 12px;
        font-weight: bold;
        color: #1a73e8;
        margin: 0;
        display: inline-block;
    }

    .tab-content {
        padding: 8px 12px; /* Reduced padding */
        background: #ffffff;
    }

    .summary-content {
        padding: 12px;
        font-size: 12px;
        line-height: 1.6;
        color: #333;
        min-height: 80px;
    }

    .summary-loading {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 12px;
    }

    .loading-spinner {
        width: 24px;
        height: 24px;
        border: 3px solid #f3f3f3;
        border-top: 3px solid #1a73e8;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }

    .loading-text {
        color: #666;
        font-size: 13px;
    }

    .summary-footer {
        padding: 6px 12px;
        border-top: 1px solid rgba(0, 0, 0, 0.05);
        display: flex;
        justify-content: flex-end;
    }

    .summary-badge {
        font-size: 9px;
        color: #666;
        background: #f1f3f4;
        padding: 2px 4px;
        border-radius: 10px;
    }

    .summary-popup::before {
        content: '';
        position: absolute;
        top: -8px;
        left: 20px;
        width: 16px;
        height: 16px;
        background: linear-gradient(135deg, #ffffff 50%, transparent 50%);
        transform: rotate(45deg);
        border-left: 1px solid rgba(0, 0, 0, 0.1);
        border-top: 1px solid rgba(0, 0, 0, 0.1);
    }

    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    .summary-error {
        color: #d93025;
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .summary-error::before {
        content: '⚠️';
    }

    .summary-content p {
        margin: 0;
        padding: 0;
    }

    .summary-content.loaded {
        animation: fadeIn 0.3s ease;
    }

    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
`;


// Modified event handler
function attachHoverBehavior(result) {
    if (result.hasAttribute('data-has-summary')) return;
    result.setAttribute('data-has-summary', 'true');

    const link = result.querySelector('h3 a') || result.querySelector('a');
    if (!link) return;

    const popup = createPopup();
    result.style.position = 'relative';
    result.appendChild(popup);

    let isLoading = false;

    // Add the new mouseenter event handler here
    result.addEventListener('mouseenter', async () => {
        if (isLoading) return;
        isLoading = true;
        popup.style.display = 'block';
        setTimeout(() => popup.classList.add('visible'), 10);
        try {
            const response = await fetch('http://localhost:5001/summarize', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ url: link.href })
            });
            const data = await response.json();
            const summaryContent = popup.querySelector('.summary-content');
            const timeValue = popup.querySelector('.time-value');
            
            if (popup.style.display === 'block') {
                summaryContent.innerHTML = data.summary;
                summaryContent.classList.add('loaded');
                // Update read time if available
                if (data.stats && data.stats.read_time) {
                    timeValue.textContent = `${data.stats.read_time} min read`;
                }
            }
        } catch (error) {
            const summaryContent = popup.querySelector('.summary-content');
            summaryContent.innerHTML = `
                <div class="summary-error">
                    Failed to load summary. Please try again.
                </div>
            `;
        } finally {
            isLoading = false;
        }
    });

    result.addEventListener('mouseleave', () => {
        popup.classList.remove('visible');
        setTimeout(() => {
            popup.style.display = 'none';
            const summaryContent = popup.querySelector('.summary-content');
            summaryContent.classList.remove('loaded');
        }, 300);
    });
}


// Add the styles to the page
const styleSheet = document.createElement('style');
styleSheet.textContent = styles;
document.head.appendChild(styleSheet);

// Initialize
function initialize() {
    const searchResults = document.querySelectorAll('div.g, div[data-hveid]');
    searchResults.forEach(attachHoverBehavior);
}

// Initial processing
initialize();

// Observer for dynamic content
const observer = new MutationObserver(() => {
    initialize();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});

