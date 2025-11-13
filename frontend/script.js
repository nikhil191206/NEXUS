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
    console.log('Execute Query button clicked.');
    
    const queryType = document.getElementById('queryType').value;
    const resultsDiv = document.getElementById('results');

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

        console.log('Query sent to backend. Awaiting response...');

        const data = await response.json();

        console.log('Backend response received:', data);
        console.log('Raw result:', data.result);

        if (data.success) {
            displayResults(data.result, queryType);
        } else {
            resultsDiv.innerHTML = `<p style="color: #cc0000;">Error: ${data.error}</p>`;
        }
    } catch (error) {
        console.error('An error occurred in executeQuery:', error);
        resultsDiv.innerHTML = `<p style="color: #cc0000;">Error: ${error.message}</p>`;
    }
}

function displayResults(result, queryType) {
    console.log('=== DISPLAY RESULTS DEBUG ===');
    console.log('Query type:', queryType);
    console.log('Result type:', typeof result);
    console.log('Result length:', result.length);
    console.log('Result (first 200 chars):', result.substring(0, 200));
    console.log('Result includes MINDMAP_DATA:', result.includes('MINDMAP_DATA:'));

    const resultsDiv = document.getElementById('results');

    if (queryType === 'mindmap') {
        console.log('Processing mindmap...');
        
        // Check if result contains MINDMAP_DATA:
        if (!result.includes('MINDMAP_DATA:')) {
            console.error('No MINDMAP_DATA: header found!');
            resultsDiv.innerHTML = `<pre>Error: Invalid mindmap format\n${result}</pre>`;
            return;
        }

        // Extract data after MINDMAP_DATA:
        let dataString = result.split('MINDMAP_DATA:')[1];
        if (!dataString) {
            resultsDiv.innerHTML = '<pre>Mindmap generated but no data found.</pre>';
            return;
        }
        
        dataString = dataString.trim();
        console.log('Data string:', dataString);
        
        // Split by lines and parse pipe-separated format
        const lines = dataString.split('\n').filter(line => line.trim());
        console.log('Number of lines:', lines.length);
        console.log('Lines:', lines);

        if (lines.length === 0) {
            resultsDiv.innerHTML = '<pre>Mindmap generated but no relationships found.</pre>';
            return;
        }

        // Build Mermaid graph
        let mermaidString = "graph TD;\n";
        const processedEdges = new Set(); // Avoid duplicate edges
        
        lines.forEach((line, idx) => {
            console.log(`Processing line ${idx}:`, line);
            const parts = line.split('|');
            
            if (parts.length === 3) {
                const source = parts[0].trim();
                const relation = parts[1].trim();
                const target = parts[2].trim();
                
                if (source && target) {
                    // Create unique edge identifier
                    const edgeKey = `${source}::${target}::${relation}`;
                    
                    if (!processedEdges.has(edgeKey)) {
                        processedEdges.add(edgeKey);
                        
                        // Create valid Mermaid node IDs (no spaces or special chars)
                        const sourceId = 'node_' + source.replace(/[^a-zA-Z0-9]/g, '_');
                        const targetId = 'node_' + target.replace(/[^a-zA-Z0-9]/g, '_');
                        
                        // Sanitize labels for display
                        const sanitizedSource = source.replace(/"/g, "'");
                        const sanitizedTarget = target.replace(/"/g, "'");
                        const sanitizedRelation = relation.replace(/"/g, "'");
                        
                        // Add edge to mermaid with proper IDs and labels
                        mermaidString += `    ${sourceId}["${sanitizedSource}"] -->|"${sanitizedRelation}"| ${targetId}["${sanitizedTarget}"]\n`;
                        
                        console.log(`Added edge: ${source} -[${relation}]-> ${target}`);
                    }
                }
            } else {
                console.warn(`Line ${idx} does not have 3 parts (has ${parts.length}):`, parts);
            }
        });

        console.log('Final Mermaid string:\n', mermaidString);

        if (processedEdges.size === 0) {
            resultsDiv.innerHTML = '<pre>Mindmap generated but no valid relationships found.</pre>';
            return;
        }

        // Render with Mermaid
        resultsDiv.innerHTML = `<div class="mermaid">${mermaidString}</div>`;
        
        if (typeof mermaid !== 'undefined') {
            try {
                mermaid.init(undefined, resultsDiv.querySelectorAll('.mermaid'));
                console.log('Mermaid rendered successfully!');
            } catch (e) {
                console.error('Mermaid render error:', e);
                resultsDiv.innerHTML = `<pre>Mermaid render error: ${e.message}\n\nMermaid code:\n${mermaidString}</pre>`;
            }
        } else {
            console.error('Mermaid library not loaded!');
            resultsDiv.innerHTML = '<pre>Error: Mermaid.js library not loaded.</pre>';
        }
    } else {
        // Non-mindmap queries
        resultsDiv.innerHTML = `<pre>${result}</pre>`;
    }
}

function handleQueryTypeChange() {
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
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.textContent = message;
    statusDiv.className = `status ${type}`;
    statusDiv.style.display = 'block';
}