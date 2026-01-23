document.addEventListener('DOMContentLoaded', () => {
    const searchInput = document.getElementById('search-input');
    const searchBtn = document.getElementById('search-btn');
    const resultsContainer = document.getElementById('results');

    // Generate or retrieve session ID
    let threadId = localStorage.getItem('pdd_agent_thread_id');
    if (!threadId) {
        threadId = 'user_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('pdd_agent_thread_id', threadId);
    } else {
        // Load history if threadId exists
        loadHistory(threadId);
    }

    async function loadHistory(tid) {
        try {
            const res = await fetch(`/api/history/${tid}`);
            const data = await res.json();
            if (data.history && data.history.length > 0) {
                // Clear default greeting if we have history
                resultsContainer.innerHTML = '';
                data.history.forEach(msg => {
                    const formattedContent = parseMarkdown(msg.content);
                    addMessage(formattedContent, msg.role, true);
                });

                // If history is empty, we keep the default greeting in HTML
            }
        } catch (e) {
            console.error("Failed to load history:", e);
        }
    }

    // Handle Search
    async function handleSearch() {
        const query = searchInput.value.trim();
        if (!query) return;

        // Add User Message
        addMessage(query, 'user');
        searchInput.value = '';

        // Show Loading
        const loadingId = showLoading();
        searchBtn.disabled = true;

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    message: query,
                    thread_id: threadId
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();

            // Remove Loading
            removeLoading(loadingId);

            // Add Agent Message
            // Simple markdown parsing for bold and newlines
            const formattedResponse = parseMarkdown(data.response);
            addMessage(formattedResponse, 'agent', true);

        } catch (error) {
            removeLoading(loadingId);
            addMessage(`Error: ${error.message}`, 'agent');
        } finally {
            searchBtn.disabled = false;
        }
    }

    // Event Listeners
    searchBtn.addEventListener('click', handleSearch);
    searchInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSearch();
    });

    // Helper: Add Message
    function addMessage(text, sender, isHtml = false) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${sender}`;

        if (isHtml) {
            msgDiv.innerHTML = text;
        } else {
            msgDiv.textContent = text;
        }

        resultsContainer.appendChild(msgDiv);
        // Scroll to bottom of container
        resultsContainer.scrollTop = resultsContainer.scrollHeight;
    }

    // Helper: Show Loading
    function showLoading() {
        const id = 'loading-' + Date.now();
        const loader = document.createElement('div');
        loader.id = id;
        loader.className = 'loading';
        loader.innerHTML = '<div class="spinner"></div>';
        resultsContainer.appendChild(loader);
        resultsContainer.scrollTop = resultsContainer.scrollHeight;
        return id;
    }

    // Helper: Remove Loading
    function removeLoading(id) {
        const loader = document.getElementById(id);
        if (loader) loader.remove();
    }

    // Simple Markdown Parser (can be improved or use library)
    function parseMarkdown(text) {
        if (!text) return '';
        let html = text
            // Headers
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            // Bold
            .replace(/\*\*(.*?)\*\*/gim, '<strong>$1</strong>')
            // Lists
            .replace(/^\s*-\s(.*$)/gim, '<ul><li>$1</li></ul>')
            // Newlines
            .replace(/\n/gim, '<br>');

        // Fix adjacent ULs
        html = html.replace(/<\/ul><br><ul>/gim, '');
        return html;
    }
});
