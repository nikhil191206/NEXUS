const API_BASE_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM fully loaded. Setting up app.');
    loadAvailableNodes();
    setupEventListeners();
});

function setupEventListeners() {
    console.log('Setting up event listeners...');
    document.getElementById('uploadBtn').addEventListener('click', uploadDocument);
    document.getElementById('executeBtn').addEventListener('click', executeQuery);
    document.getElementById('queryType').addEventListener('change', handleQueryTypeChange);
    console.log('Event listeners SET.');
}

async function uploadDocument() {
    // (This function is working, no changes)
    const fileInput = document.getElementById('fileInput');
    const statusDiv = document.getElementById('uploadStatus');
    if (!fileInput.files.length) {
        showStatus('Please select a file first', 'error');
        return;
    }
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);
    try {
        statusDiv.textContent = 'Processing document with Gemini API. This may take 30-60 seconds...';
        statusDiv.className = 'status';
        statusDiv.style.display = 'block';
        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });
        if (!response.ok) throw new Error(`Server error: ${response.status}`);
        const data = await response.json();
        if (data.success) {
            showStatus('✓ ' + data.message, 'success');
            loadAvailableNodes();
        } else {
            showStatus('Error: ' + data.error, 'error');
        }
    } catch (error) {
        showStatus('Error: ' + error.message, 'error');
    }
}

async function executeQuery() {
    // --- DEBUGGER ---
    console.log('Execute Query button clicked.');
    
    const queryType = document.getElementById('queryType').value;
    const resultsDiv = document.getElementById('results');

    // --- DEBUGGER ---
    console.log(`Query type selected: ${queryType}`);

    let queryData = { query_type: queryType };

    switch (queryType) {
        case 'path':
            queryData.start = document.getElementById('startNode').value.trim();
            queryData.end = document.getElementById('endNode').value.trim();
            if (!queryData.start || !queryData.end) { alert('Please enter both start and end nodes'); return; }
            break;
        case 'mindmap':
            queryData.start = document.getElementById('mindmapNode').value.trim();
            if (!queryData.start) { alert('Please enter a root node'); return; }
            break;
        case 'qa':
            queryData.node = document.getElementById('qaNode').value.trim();
            if (!queryData.node) { alert('Please enter a node name'); return; }
            break;
        case 'complete':
            queryData.prefix = document.getElementById('completePrefix').value.trim();
            if (!queryData.prefix) { alert('Please enter a prefix'); return; }
            break;
    }

    try {
        resultsDiv.innerHTML = '<p class="placeholder">Executing query...</p>';

        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(queryData)
        });

        // --- DEBUGGER ---
        console.log('Query sent to backend. Awaiting response...');

        const data = await response.json();

        // --- DEBUGGER ---
        console.log('Backend response received:', data);

        if (data.success) {
            displayResults(data.result, queryType);
        } else {
            resultsDiv.innerHTML = `<p style="color: #cc0000;">Error: ${data.error}</p>`;
        }
    } catch (error) {
        // --- DEBUGGER ---
        console.error('An error occurred in executeQuery:', error);
        resultsDiv.innerHTML = `<p style="color: #cc0000;">Error: ${error.message}</p>`;
    }
}

function displayResults(result, queryType) {
    // --- DEBUGGER ---
    console.log('Displaying results. Query type:', queryType);
    console.log('Raw result string:', JSON.stringify(result)); // Show the exact string with newlines

    const resultsDiv = document.getElementById('results');

    // --- DEBUGGER ---
    // Check our conditions
    const isMindmap = (queryType === 'mindmap');
    const startsWithHeader = result.startsWith('MINDMAP_DATA:');
    console.log(`Is this a mindmap query? ${isMindmap}`);
    console.log(`Does result start with 'MINDMAP_DATA:'? ${startsWithHeader}`);


    if (isMindmap && startsWithHeader) {
        // --- DEBUGGER ---
        console.log('Entering Mermaid.js render block.');

        let mermaidString = "graph TD;\n";
        const lines = result.replace('MINDMAP_DATA:\n', '').trim().split('\n');

        if (lines.length === 0 || (lines.length === 1 && lines[0] === '')) {
            resultsDiv.innerHTML = '<pre>Mindmap generated. No outgoing edges found for this node.</pre>';
            return;
        }

        let edgeCount = 0;
        lines.forEach(line => {
            const parts = line.split('|');
            if (parts.length === 3) {
                const [source, relation, target] = parts;
                mermaidString += `    "${source.trim()}" -- "${relation.trim()}" --> "${target.trim()}";\n`;
                edgeCount++;
            }
        });

        if (edgeCount === 0) {
            resultsDiv.innerHTML = '<pre>Mindmap generated. No edges found in data.</pre>';
            return;
        }

        resultsDiv.innerHTML = `<div class="mermaid">${mermaidString}</div>`;
        
        // --- DEBUGGER ---
        console.log('Attempting to call mermaid.init()');

        if (typeof mermaid !== 'undefined') {
            mermaid.init(undefined, resultsDiv.querySelectorAll('.mermaid'));
            console.log('Mermaid.js render complete.');
        } else {
            console.error('Mermaid.js library is not defined!');
            resultsDiv.innerHTML = '<pre>Error: Mermaid.js library not loaded. (Check index.html)</pre>';
        }
    
    } else {
        // --- DEBUGGER ---
        console.log('Entering standard <pre> block. (Not a mindmap or check failed).');
        resultsDiv.innerHTML = `<pre>${result}</pre>`;
    }
}


function handleQueryTypeChange() {
    // (This function is fine, no changes)
    const queryType = document.getElementById('queryType').value;
    document.querySelectorAll('.query-inputs').forEach(div => div.style.display = 'none');
    switch (queryType) {
        case 'path': document.getElementById('pathQuery').style.display = 'block'; break;
        case 'topics': document.getElementById('topicsQuery').style.display = 'block'; break;
        case 'mindmap': document.getElementById('mindmapQuery').style.display = 'block'; break;
        case 'qa': document.getElementById('qaQuery').style.display = 'block'; break;
        case 'complete': document.getElementById('completeQuery').style.display = 'block'; break;
    }
}

async function loadAvailableNodes() {
    // (This function is fine, no changes)
    try {
        const response = await fetch(`${API_BASE_URL}/nodes`);
        const data = await response.json();
        if (data.success) {
            const nodeList = document.getElementById('nodeList');
            nodeList.innerHTML = '';
            data.nodes.forEach(node => {
                const option = document.createElement('option');
                option.value = node;
                nodeList.appendChild(option);
            });
        }
    } catch (error) {
        console.error('Failed to load nodes:', error);
    }
}

function showStatus(message, type) {
    // (This function is fine, no changes)
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.style.display = 'block';
}