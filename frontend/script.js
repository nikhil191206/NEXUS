const API_BASE_URL = 'http://localhost:5000/api';

document.addEventListener('DOMContentLoaded', () => {
    loadAvailableNodes();
    setupEventListeners();
});

function setupEventListeners() {
    document.getElementById('uploadBtn').addEventListener('click', uploadDocument);
    document.getElementById('executeBtn').addEventListener('click', executeQuery);
    document.getElementById('queryType').addEventListener('change', handleQueryTypeChange);
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
        statusDiv.textContent = 'Processing document with Transformer AI. This may take 1-2 minutes on first run...';
        statusDiv.className = 'status';
        statusDiv.style.display = 'block';

        const response = await fetch(`${API_BASE_URL}/upload`, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

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
    const queryType = document.getElementById('queryType').value;
    const resultsDiv = document.getElementById('results');

    let queryData = { query_type: queryType };

    switch (queryType) {
        case 'path':
            const startNode = document.getElementById('startNode').value.trim();
            const endNode = document.getElementById('endNode').value.trim();
            if (!startNode || !endNode) {
                alert('Please enter both start and end nodes');
                return;
            }
            queryData.start = startNode;
            queryData.end = endNode;
            break;

        case 'mindmap':
            const mindmapNode = document.getElementById('mindmapNode').value.trim();
            if (!mindmapNode) {
                alert('Please enter a root node');
                return;
            }
            queryData.start = mindmapNode;
            break;

        case 'qa':
            const qaNode = document.getElementById('qaNode').value.trim();
            if (!qaNode) {
                alert('Please enter a node name');
                return;
            }
            queryData.node = qaNode;
            break;

        case 'complete':
            const prefix = document.getElementById('completePrefix').value.trim();
            if (!prefix) {
                alert('Please enter a prefix');
                return;
            }
            queryData.prefix = prefix;
            break;
    }

    try {
        resultsDiv.innerHTML = '<p class="placeholder">Executing query...</p>';

        const response = await fetch(`${API_BASE_URL}/query`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(queryData)
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data.result);
        } else {
            resultsDiv.innerHTML = `<p style="color: #cc0000;">Error: ${data.error}</p>`;
        }
    } catch (error) {
        resultsDiv.innerHTML = `<p style="color: #cc0000;">Error: ${error.message}</p>`;
    }
}

function displayResults(result) {
    const resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = `<pre>${result}</pre>`;
}

function handleQueryTypeChange() {
    const queryType = document.getElementById('queryType').value;

    document.querySelectorAll('.query-inputs').forEach(div => {
        div.style.display = 'none';
    });

    switch (queryType) {
        case 'path':
            document.getElementById('pathQuery').style.display = 'block';
            break;
        case 'topics':
            document.getElementById('topicsQuery').style.display = 'block';
            break;
        case 'mindmap':
            document.getElementById('mindmapQuery').style.display = 'block';
            break;
        case 'qa':
            document.getElementById('qaQuery').style.display = 'block';
            break;
        case 'complete':
            document.getElementById('completeQuery').style.display = 'block';
            break;
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
