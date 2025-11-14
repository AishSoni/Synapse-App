// Global error handler
window.addEventListener('error', (e) => {
    console.error('Global error:', e.error);
    console.error('Message:', e.message);
    console.error('Stack:', e.error?.stack);
});

const { ipcRenderer } = require('electron');

// State
let captures = [];
let spaces = [];
let selectedNodes = new Set();
let simulation = null;
let searchMode = 'search';  // 'search' or 'ask'

// Helper to open external URLs
async function openExternal(url) {
    try {
        await ipcRenderer.invoke('open-external', url);
    } catch (error) {
        console.error('Failed to open URL:', error);
    }
}

// Make it available globally for onclick handlers
window.openExternal = openExternal;

console.log('App.js loaded successfully');

// Constants
const BACKEND_URL = 'http://localhost:8000';
const WS_URL = 'ws://localhost:8000/ws';
const COLORS = {
    default: '#6366f1', // indigo-500
    article: '#8b5cf6', // violet-500
    product: '#ec4899', // pink-500
    video: '#f59e0b', // amber-500
    code: '#10b981',   // emerald-500
    chat: '#3b82f6',   // blue-500
};

// WebSocket connection
let ws = null;
let wsReconnectTimer = null;

// WebSocket functions
function connectWebSocket() {
    console.log('[WS] Connecting to', WS_URL);

    try {
        ws = new WebSocket(WS_URL);

        ws.onopen = () => {
            console.log('[WS] Connected!');
            if (wsReconnectTimer) {
                clearTimeout(wsReconnectTimer);
                wsReconnectTimer = null;
            }
        };

        ws.onmessage = (event) => {
            try {
                const message = JSON.parse(event.data);
                handleWebSocketMessage(message);
            } catch (error) {
                console.error('[WS] Failed to parse message:', error);
            }
        };

        ws.onerror = (error) => {
            console.error('[WS] Error:', error);
        };

        ws.onclose = () => {
            console.log('[WS] Disconnected. Reconnecting in 3s...');
            wsReconnectTimer = setTimeout(connectWebSocket, 3000);
        };

    } catch (error) {
        console.error('[WS] Connection failed:', error);
        wsReconnectTimer = setTimeout(connectWebSocket, 3000);
    }
}

function handleWebSocketMessage(message) {
    console.log('[WS] Message:', message.type, message.data);

    switch (message.type) {
        case 'capture_started':
            handleCaptureStarted(message.data);
            break;
        case 'capture_complete':
            handleCaptureComplete(message.data);
            break;
        case 'capture_error':
            handleCaptureError(message.data);
            break;
        default:
            console.log('[WS] Unknown message type:', message.type);
    }
}

function handleCaptureStarted(data) {
    console.log('[WS] Capture started:', data.title);

    // Show toast notification
    showToast(`Capturing: ${data.title}`, 'info');

    // TODO: Add to capture queue UI
}

function handleCaptureComplete(data) {
    console.log('[WS] Capture complete:', data.capture_id);

    const captureTitle = data.capture?.analysis?.title || data.capture?.title || 'New capture';
    const contentType = data.capture?.analysis?.content_type || 'item';

    // Show success notification with more detail
    showToast(`✓ Captured: ${captureTitle} (${contentType})`, 'success');

    // Reload captures and update mind map
    console.log('[WS] Reloading captures after completion...');
    loadCaptures().then(() => {
        console.log('[WS] Captures reloaded, count:', captures.length);
        if (captures.length > 0) {
            console.log('[WS] Initializing mind map...');
            initializeMindMap();
        }
    });
}

function handleCaptureError(data) {
    console.error('[WS] Capture error:', data.error);
    showToast(`Capture failed: ${data.error}`, 'error');
}

function showToast(message, type = 'info') {
    // Simple toast notification
    const toast = document.createElement('div');
    toast.className = `fixed top-4 right-4 px-6 py-3 rounded-lg shadow-lg text-white z-50 ${
        type === 'success' ? 'bg-green-600' :
        type === 'error' ? 'bg-red-600' :
        'bg-indigo-600'
    }`;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.3s';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    setupKeyboardShortcuts();
    connectWebSocket();  // Connect to WebSocket
});

async function initializeApp() {
    console.log('[Init] Initializing Synapse...');

    // Load captures
    await loadCaptures();

    // Load spaces from localStorage
    loadSpaces();

    // Initialize mind map if there are captures
    if (captures.length > 0) {
        console.log('[Init] Found captures, initializing mind map...');
        document.getElementById('empty-state').classList.add('hidden');
        initializeMindMap();
    } else {
        console.log('[Init] No captures found, showing empty state');
    }
}

async function loadCaptures() {
    try {
        console.log('[Load] Fetching captures...');
        captures = await ipcRenderer.invoke('get-captures', 100);
        console.log(`[Load] Loaded ${captures.length} captures`);

        // Update counter
        document.getElementById('total-captures').textContent = `${captures.length} items`;

        // Show/hide empty state
        if (captures.length > 0) {
            console.log('[Load] Hiding empty state, showing mind map');
            document.getElementById('empty-state').classList.add('hidden');
        } else {
            console.log('[Load] No captures, showing empty state');
            document.getElementById('empty-state').classList.remove('hidden');
        }

        return captures;
    } catch (error) {
        console.error('[Load] Failed to load captures:', error);
        captures = [];
        return [];
    }
}

function loadSpaces() {
    const savedSpaces = localStorage.getItem('synapse-spaces');
    spaces = savedSpaces ? JSON.parse(savedSpaces) : [];

    // Render spaces list
    renderSpacesList();
}

function saveSpaces() {
    localStorage.setItem('synapse-spaces', JSON.stringify(spaces));
    renderSpacesList();
}

function renderSpacesList() {
    const spacesList = document.getElementById('spaces-list');
    const existingAllCaptures = spacesList.querySelector(':first-child');

    // Clear existing spaces (keep "All Captures")
    spacesList.innerHTML = '';
    if (existingAllCaptures) {
        spacesList.appendChild(existingAllCaptures);
    }

    // Render user spaces
    spaces.forEach(space => {
        const spaceEl = document.createElement('div');
        spaceEl.className = 'px-3 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 cursor-pointer transition-smooth';
        spaceEl.innerHTML = `
            <div class="text-sm font-medium">${space.name}</div>
            <div class="text-xs text-gray-400">${space.nodeIds.length} items</div>
        `;
        spaceEl.addEventListener('click', () => filterBySpace(space));
        spacesList.appendChild(spaceEl);
    });
}

function initializeMindMap() {
    const svg = d3.select('#mind-map-canvas');
    const width = window.innerWidth - 320; // Subtract sidebar
    const height = window.innerHeight - 40; // Subtract title bar

    svg.attr('viewBox', [0, 0, width, height]);

    // Clear existing
    svg.selectAll('*').remove();

    // Create container for zoom/pan
    const g = svg.append('g');

    // Convert captures to graph data
    const nodes = captures.map((capture, i) => ({
        id: capture.id,
        title: capture.title,
        url: capture.url,
        contentType: capture.content_type || 'article',
        tags: capture.tags || [],
        x: Math.random() * width,
        y: Math.random() * height,
        data: capture
    }));

    // Generate links based on semantic similarity (simulated with tags for now)
    const links = [];
    for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
            const node1 = nodes[i];
            const node2 = nodes[j];

            // Create link if they share tags
            const sharedTags = node1.tags.filter(tag => node2.tags.includes(tag));
            if (sharedTags.length > 0) {
                links.push({
                    source: node1.id,
                    target: node2.id,
                    strength: sharedTags.length
                });
            }
        }
    }

    console.log(`Mind map: ${nodes.length} nodes, ${links.length} links`);

    // Create force simulation
    simulation = d3.forceSimulation(nodes)
        .force('link', d3.forceLink(links).id(d => d.id).distance(150))
        .force('charge', d3.forceManyBody().strength(-300))
        .force('center', d3.forceCenter(width / 2, height / 2))
        .force('collision', d3.forceCollide().radius(50));

    // Draw links
    const link = g.append('g')
        .selectAll('line')
        .data(links)
        .join('line')
        .attr('class', d => `link ${d.strength > 1 ? 'strong' : ''}`)
        .attr('stroke-width', d => d.strength > 1 ? 2.5 : 1.5);

    // Draw nodes
    const node = g.append('g')
        .selectAll('g')
        .data(nodes)
        .join('g')
        .attr('class', 'node')
        .call(drag(simulation));

    // Node circles
    node.append('circle')
        .attr('r', 30)
        .attr('fill', d => COLORS[d.contentType] || COLORS.default)
        .attr('stroke', '#1f2937')
        .attr('stroke-width', 2);

    // Node labels - show truncated title
    node.append('text')
        .attr('text-anchor', 'middle')
        .attr('dy', '-35px')  // Above the node
        .attr('font-size', '11px')
        .attr('fill', 'white')
        .attr('font-weight', 'bold')
        .attr('pointer-events', 'none')
        .text(d => {
            // Truncate title to 25 characters
            const title = d.title || 'Untitled';
            return title.length > 25 ? title.substring(0, 22) + '...' : title;
        });

    // Node titles (on hover)
    node.append('title')
        .text(d => d.title);

    // Node interactions
    node.on('click', (event, d) => {
        if (event.ctrlKey || event.metaKey) {
            // Multi-select
            toggleNodeSelection(d.id, event.currentTarget);
        } else {
            // Single click - show detail
            showNodeDetail(d);
        }
    });

    // Update positions on simulation tick
    simulation.on('tick', () => {
        link
            .attr('x1', d => d.source.x)
            .attr('y1', d => d.source.y)
            .attr('x2', d => d.target.x)
            .attr('y2', d => d.target.y);

        node.attr('transform', d => `translate(${d.x},${d.y})`);
    });

    // Zoom behavior
    const zoom = d3.zoom()
        .scaleExtent([0.5, 3])
        .on('zoom', (event) => {
            g.attr('transform', event.transform);
        });

    svg.call(zoom);

    // Legend
    createLegend(svg, width, height);
}

function createLegend(svg, width, height) {
    const legend = svg.append('g')
        .attr('class', 'legend')
        .attr('transform', `translate(20, ${height - 150})`);

    const contentTypes = Object.keys(COLORS);
    contentTypes.forEach((type, i) => {
        const legendRow = legend.append('g')
            .attr('transform', `translate(0, ${i * 25})`);

        legendRow.append('circle')
            .attr('r', 8)
            .attr('fill', COLORS[type]);

        legendRow.append('text')
            .attr('x', 15)
            .attr('y', 4)
            .attr('font-size', '12px')
            .attr('fill', '#9ca3af')
            .text(type.charAt(0).toUpperCase() + type.slice(1));
    });
}

function drag(simulation) {
    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    return d3.drag()
        .on('start', dragstarted)
        .on('drag', dragged)
        .on('end', dragended);
}

function toggleNodeSelection(nodeId, element) {
    if (selectedNodes.has(nodeId)) {
        selectedNodes.delete(nodeId);
        d3.select(element).classed('selected', false);
    } else {
        selectedNodes.add(nodeId);
        d3.select(element).classed('selected', true);
    }

    updateSelectionToolbar();
}

function updateSelectionToolbar() {
    const toolbar = document.getElementById('selection-toolbar');
    const count = document.getElementById('selected-count');

    count.textContent = selectedNodes.size;

    if (selectedNodes.size > 0) {
        toolbar.classList.remove('hidden');
    } else {
        toolbar.classList.add('hidden');
    }
}

function showNodeDetail(node) {
    const panel = document.getElementById('detail-panel');
    const content = document.getElementById('detail-content');

    // Populate detail panel
    content.innerHTML = `
        <div class="space-y-4">
            <div>
                <div class="text-xs text-gray-400 uppercase mb-1">Title</div>
                <div class="font-medium">${node.title}</div>
            </div>

            <div>
                <div class="text-xs text-gray-400 uppercase mb-1">URL</div>
                <a href="#" onclick="event.preventDefault(); openExternal('${node.url.replace(/'/g, "\\'")}')" class="text-indigo-400 hover:underline text-sm break-all">${node.url}</a>
            </div>

            <div>
                <div class="text-xs text-gray-400 uppercase mb-1">Type</div>
                <span class="inline-block px-3 py-1 rounded-full text-xs font-medium" style="background-color: ${COLORS[node.contentType]}20; color: ${COLORS[node.contentType]}">
                    ${node.contentType}
                </span>
            </div>

            ${node.tags && node.tags.length > 0 ? `
                <div>
                    <div class="text-xs text-gray-400 uppercase mb-1">Tags</div>
                    <div class="flex flex-wrap gap-2">
                        ${node.tags.map(tag => `<span class="px-2 py-1 bg-gray-700 rounded text-xs">${tag}</span>`).join('')}
                    </div>
                </div>
            ` : ''}

            ${node.data.summary ? `
                <div>
                    <div class="text-xs text-gray-400 uppercase mb-1">Summary</div>
                    <div class="text-sm text-gray-300">${node.data.summary}</div>
                </div>
            ` : ''}

            ${node.data.screenshot ? `
                <div>
                    <div class="text-xs text-gray-400 uppercase mb-1">Screenshot</div>
                    <img src="data:image/jpeg;base64,${node.data.screenshot}" class="w-full rounded-lg border border-gray-700" />
                </div>
            ` : ''}
        </div>
    `;

    // Show panel
    panel.classList.remove('hidden');
    setTimeout(() => {
        panel.style.transform = 'translateX(0)';
    }, 10);
}

function setupEventListeners() {
    // Mode toggle buttons
    document.getElementById('mode-search').addEventListener('click', () => {
        setSearchMode('search');
    });

    document.getElementById('mode-ask').addEventListener('click', () => {
        setSearchMode('ask');
    });

    // Search inputs
    document.getElementById('search-input').addEventListener('focus', () => {
        document.getElementById('chat-collapsed').classList.add('hidden');
        document.getElementById('chat-expanded').classList.remove('hidden');
        document.getElementById('search-input-expanded').focus();
    });

    document.getElementById('search-input-expanded').addEventListener('input', debounce(handleSearch, 300));

    // Close chat
    document.getElementById('close-chat-btn').addEventListener('click', () => {
        document.getElementById('chat-expanded').classList.add('hidden');
        document.getElementById('chat-collapsed').classList.remove('hidden');
        document.getElementById('search-input').value = '';
        document.getElementById('search-input-expanded').value = '';
    });

    // Close detail panel
    document.getElementById('close-detail-btn').addEventListener('click', () => {
        const panel = document.getElementById('detail-panel');
        panel.style.transform = 'translateX(100%)';
        setTimeout(() => panel.classList.add('hidden'), 300);
    });

    // Create space modal
    document.getElementById('create-space-btn').addEventListener('click', () => {
        document.getElementById('create-space-modal').classList.remove('hidden');
        document.getElementById('space-name-input').focus();
    });

    document.getElementById('create-space-cancel').addEventListener('click', () => {
        document.getElementById('create-space-modal').classList.add('hidden');
        document.getElementById('space-name-input').value = '';
    });

    document.getElementById('create-space-confirm').addEventListener('click', createSpace);

    // Group nodes
    document.getElementById('group-nodes-btn').addEventListener('click', groupSelectedNodes);

    // Clear selection
    document.getElementById('clear-selection-btn').addEventListener('click', () => {
        selectedNodes.clear();
        d3.selectAll('.node').classed('selected', false);
        updateSelectionToolbar();
    });

    // Setup guide
    document.getElementById('setup-guide-btn').addEventListener('click', () => {
        alert('Setup Guide\n\n1. Install Chrome Extension\n2. Press Alt+B to capture any webpage\n3. Search and organize in Spaces\n4. Connect AI apps with MCP server\n\nSee SETUP_GUIDE.md for details.');
    });
}

function setSearchMode(mode) {
    searchMode = mode;

    // Update button styles
    const searchBtn = document.getElementById('mode-search');
    const askBtn = document.getElementById('mode-ask');

    if (mode === 'search') {
        searchBtn.className = 'mode-btn flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-smooth bg-indigo-600 text-white';
        askBtn.className = 'mode-btn flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-smooth bg-gray-700 text-gray-400 hover:bg-gray-600';
        document.getElementById('search-input-expanded').placeholder = 'Search your memories and sources...';
    } else {
        searchBtn.className = 'mode-btn flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-smooth bg-gray-700 text-gray-400 hover:bg-gray-600';
        askBtn.className = 'mode-btn flex-1 px-4 py-2 rounded-lg text-sm font-medium transition-smooth bg-indigo-600 text-white';
        document.getElementById('search-input-expanded').placeholder = 'Ask a question about your memories...';
    }

    // Re-run search if there's a query
    const query = document.getElementById('search-input-expanded').value.trim();
    if (query) {
        handleSearch({ target: { value: query } });
    }
}

async function handleAskQuestion(query) {
    const resultsEl = document.getElementById('search-results');

    // Show loading
    resultsEl.innerHTML = '<div class="text-sm text-gray-400">🤔 Thinking...</div>';

    try {
        const response = await ipcRenderer.invoke('ask-question', query);

        if (!response || !response.answer) {
            resultsEl.innerHTML = '<div class="text-sm text-red-400">Failed to get answer. Is the backend running?</div>';
            return;
        }

        // Show AI answer + sources (no confidence/scores shown)
        console.log('[Ask] Confidence:', response.confidence);

        resultsEl.innerHTML = `
            <div class="mb-6 p-4 bg-gray-700 rounded-xl">
                <div class="flex items-center gap-2 mb-3">
                    <div class="text-sm font-semibold text-indigo-400">AI Answer</div>
                </div>
                <div class="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">${response.answer}</div>
            </div>

            ${response.sources && response.sources.length > 0 ? `
                <div class="mb-2 text-xs font-semibold text-gray-400 uppercase">Sources Used:</div>
                ${response.sources.map((source, idx) => {
                    console.log(`[Ask] Source ${idx + 1}: ${source.title} (${(source.relevance * 100).toFixed(0)}% relevant)`);
                    return `
                    <div class="mb-3 p-3 bg-gray-700 rounded-lg hover:bg-gray-600 transition-smooth">
                        <a href="#"
                           onclick="event.preventDefault(); openExternal('${source.url.replace(/'/g, "\\'")}')"
                           class="font-medium text-white hover:text-indigo-400 block mb-1 text-sm">
                            ${source.title}
                        </a>
                        <div class="text-xs text-gray-400">${source.url}</div>
                    </div>
                `;}).join('')}
            ` : ''}
        `;

    } catch (error) {
        console.error('Ask error:', error);
        resultsEl.innerHTML = '<div class="text-sm text-red-400">Failed to get answer. Is the backend running?</div>';
    }
}

async function handleSearch(event) {
    const query = event.target.value.trim();
    if (!query) {
        document.getElementById('search-results').innerHTML = '<div class="text-sm text-gray-400">Type to search your memories...</div>';
        return;
    }

    // Route to appropriate handler based on mode
    if (searchMode === 'ask') {
        await handleAskQuestion(query);
        return;
    }

    // Default: semantic search mode
    try {
        const results = await ipcRenderer.invoke('search-captures', query);

        const resultsEl = document.getElementById('search-results');

        if (!results || results.length === 0) {
            resultsEl.innerHTML = '<div class="text-sm text-gray-400">No memories found matching "${query}".</div>';
            return;
        }

        // Show direct sources with screenshots and links (no scores shown)
        resultsEl.innerHTML = results.map((result, idx) => {
            console.log(`[Search] Result ${idx + 1}: ${result.title} (${(result.similarity_score * 100).toFixed(0)}% match)`);
            return `
            <div class="mb-4 p-4 bg-gray-700 rounded-xl hover:bg-gray-600 transition-smooth">
                <!-- Screenshot Preview (if available) -->
                ${result.screenshot ? `
                    <div class="mb-3">
                        <img src="data:image/jpeg;base64,${result.screenshot}"
                             class="w-full rounded-lg border border-gray-600 cursor-pointer"
                             onclick="openExternal('${result.url.replace(/'/g, "\\'")}')"
                             alt="${result.title}"
                        />
                    </div>
                ` : ''}

                <!-- Title as clickable link -->
                <a href="#"
                   onclick="event.preventDefault(); openExternal('${result.url.replace(/'/g, "\\'")}')"
                   class="font-semibold text-white hover:text-indigo-400 block mb-2 transition-smooth">
                    ${result.title}
                </a>

                <!-- Direct source URL -->
                <div class="flex items-center gap-2 mb-2">
                    <svg class="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    <a href="#"
                       onclick="event.preventDefault(); openExternal('${result.url.replace(/'/g, "\\'")}')"
                       class="text-xs text-indigo-400 hover:underline break-all">
                        ${result.url}
                    </a>
                </div>

                <!-- Captured summary (not AI generated - from original capture) -->
                ${result.summary ? `
                    <div class="text-sm text-gray-300 mb-2 line-clamp-2">
                        ${result.summary}
                    </div>
                ` : ''}

                <!-- Metadata -->
                <div class="flex items-center gap-3 mt-3 text-xs">
                    ${result.content_type ? `
                        <span class="px-2 py-1 bg-gray-800 rounded">${result.content_type}</span>
                    ` : ''}
                    ${result.tags ? result.tags.slice(0, 3).map(tag => `
                        <span class="px-2 py-1 bg-gray-800 rounded">${tag}</span>
                    `).join('') : ''}

                    <!-- View details button -->
                    <button onclick="showResultDetail('${result.id}')"
                            class="ml-auto text-gray-400 hover:text-white">
                        View Details →
                    </button>
                </div>
            </div>
        `;}).join('');

    } catch (error) {
        console.error('Search error:', error);
        document.getElementById('search-results').innerHTML = '<div class="text-sm text-red-400">Search failed. Is the backend running?</div>';
    }
}

async function showResultDetail(captureId) {
    try {
        const capture = await ipcRenderer.invoke('get-capture-detail', captureId);
        const node = captures.find(c => c.id === captureId);

        if (node) {
            showNodeDetail({
                id: node.id,
                title: node.title,
                url: node.url,
                contentType: node.content_type || 'article',
                tags: node.tags || [],
                data: capture
            });
        }

        // Close search
        document.getElementById('chat-expanded').classList.add('hidden');
        document.getElementById('chat-collapsed').classList.remove('hidden');

    } catch (error) {
        console.error('Failed to load capture detail:', error);
    }
}

function createSpace() {
    const name = document.getElementById('space-name-input').value.trim();

    if (!name) {
        alert('Please enter a space name');
        return;
    }

    const newSpace = {
        id: Date.now().toString(),
        name: name,
        nodeIds: [],
        createdAt: new Date().toISOString()
    };

    spaces.push(newSpace);
    saveSpaces();

    // Close modal
    document.getElementById('create-space-modal').classList.add('hidden');
    document.getElementById('space-name-input').value = '';
}

function groupSelectedNodes() {
    if (selectedNodes.size === 0) {
        alert('Please select nodes first (Cmd/Ctrl + Click)');
        return;
    }

    const spaceName = prompt('Name this Space:');
    if (!spaceName) return;

    const newSpace = {
        id: Date.now().toString(),
        name: spaceName,
        nodeIds: Array.from(selectedNodes),
        createdAt: new Date().toISOString()
    };

    spaces.push(newSpace);
    saveSpaces();

    // Clear selection
    selectedNodes.clear();
    d3.selectAll('.node').classed('selected', false);
    updateSelectionToolbar();

    alert(`Space "${spaceName}" created with ${newSpace.nodeIds.length} nodes!`);
}

function filterBySpace(space) {
    console.log('Filtering by space:', space.name);
    // TODO: Implement space filtering in mind map
}

function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (event) => {
        // Cmd+K or Ctrl+K - Focus search
        if ((event.metaKey || event.ctrlKey) && event.key === 'k') {
            event.preventDefault();
            document.getElementById('search-input').focus();
        }

        // Escape - Close panels
        if (event.key === 'Escape') {
            const detailPanel = document.getElementById('detail-panel');
            if (!detailPanel.classList.contains('hidden')) {
                detailPanel.style.transform = 'translateX(100%)';
                setTimeout(() => detailPanel.classList.add('hidden'), 300);
            }

            const chatExpanded = document.getElementById('chat-expanded');
            if (!chatExpanded.classList.contains('hidden')) {
                chatExpanded.classList.add('hidden');
                document.getElementById('chat-collapsed').classList.remove('hidden');
            }
        }
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Handle window resize
window.addEventListener('resize', () => {
    if (simulation && captures.length > 0) {
        initializeMindMap();
    }
});
