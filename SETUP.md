# Nexus Setup Guide

Complete installation and setup instructions for Nexus Knowledge Base.

---

## Prerequisites

- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **GCC Compiler** (for compiling C-Core)
  - Windows: [MinGW](http://mingw.org/) or [WSL](https://docs.microsoft.com/en-us/windows/wsl/)
  - Linux: `sudo apt-get install build-essential`
  - macOS: Xcode Command Line Tools (`xcode-select --install`)
- **4GB RAM** minimum (8GB recommended)
- **2GB disk space** for dependencies

---

## Step 1: Install Python Dependencies

Navigate to the backend directory:

```bash
cd nexus/backend
```

### Option A: Install All at Once

```bash
pip install flask flask-cors transformers torch
```

### Option B: Install from Requirements File

```bash
pip install -r requirements.txt
```

### Option C: CPU-Only PyTorch (Faster Download)

If you don't have a GPU or want faster installation:

```bash
pip install flask flask-cors transformers
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

---

## Step 2: Compile the C-Core Engine

Navigate to the C-Core directory:

```bash
cd nexus/c_core
```

### Compile with GCC:

**Windows:**
```bash
gcc -Wall -Wextra -std=c11 -O2 -o nexus_engine.exe nexus_engine.c graph.c hash_table.c trie.c queue.c stack.c
```

**Linux/Mac:**
```bash
gcc -Wall -Wextra -std=c11 -O2 -o nexus_engine nexus_engine.c graph.c hash_table.c trie.c queue.c stack.c
```

### Using Makefile (if `make` is installed):

```bash
make
```

### Verify Compilation:

```bash
# Windows
nexus_engine.exe --help

# Linux/Mac
./nexus_engine --help
```

You should see usage instructions.

---

## Step 3: Test the C-Core Engine (Optional)

Test with the provided sample data:

```bash
# Windows
nexus_engine.exe --file ../data/graph_data.txt --query path --start BERT --end NLP

# Linux/Mac
./nexus_engine --file ../data/graph_data.txt --query path --start BERT --end NLP
```

Expected output:
```
PATH: BERT -[revolutionized]-> NLP
```

---

## Step 4: Start the Backend Server

Navigate to the backend directory:

```bash
cd nexus/backend
```

Start the Flask server:

```bash
python app.py
```

You should see:

```
============================================================
NEXUS: PERSONAL KNOWLEDGE BASE
============================================================
C-Engine: C:\...\nexus_engine.exe
Graph Data: C:\...\graph_data.txt
AI: Transformer (BERT + T5)
============================================================
Server running on http://localhost:5000
Press CTRL+C to stop
============================================================
```

---

## Step 5: Open the Frontend

Open `nexus/frontend/index.html` in your web browser.

### Ways to Open:

1. **Double-click** `index.html` in file explorer
2. **Drag and drop** `index.html` into browser
3. **File > Open** in browser menu

The application should load and display the Nexus interface.

---

## Usage Workflow

### 1. Upload a Document

1. Click "Choose File" under "1. Upload Document"
2. Select a `.txt` file with knowledge content
3. Click "Process Document"
4. Wait for AI processing (10-30 seconds for first run)
5. You'll see: "✓ Document processed successfully..."

### 2. Query the Knowledge Graph

1. Select a query type from the dropdown
2. Enter required parameters (e.g., node names)
3. Click "Execute Query"
4. Results appear instantly (< 1ms via C-Core)

### 3. Explore Results

- Results are displayed in the "3. Results" section
- Try different query types to explore your knowledge graph
- Node autocomplete helps you find concepts

---

## Troubleshooting

### Python Dependencies

**Problem:** `ModuleNotFoundError: No module named 'flask'`

**Solution:**
```bash
pip install flask flask-cors
```

**Problem:** `ModuleNotFoundError: No module named 'transformers'`

**Solution:**
```bash
pip install transformers torch
```

**Problem:** PyTorch installation takes too long

**Solution:** Use CPU-only version:
```bash
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### C-Core Compilation

**Problem:** `gcc: command not found`

**Solution:**
- Windows: Install MinGW or use WSL
- Linux: `sudo apt-get install build-essential`
- macOS: `xcode-select --install`

**Problem:** Compilation errors

**Solution:** Make sure you're in the `c_core` directory and all `.c` and `.h` files are present.

### Backend Server

**Problem:** `Address already in use` (port 5000)

**Solution:** Kill the process on port 5000:

**Windows:**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Linux/Mac:**
```bash
lsof -i :5000
kill -9 <PID>
```

**Problem:** Backend starts but frontend can't connect

**Solution:**
1. Check that backend shows: "Server running on http://localhost:5000"
2. Check browser console for CORS errors
3. Make sure both backend and frontend are running

### AI Processing

**Problem:** "Out of memory" during document processing

**Solution:**
- Close other applications
- Process smaller documents
- Use CPU-only PyTorch (uses less RAM)

**Problem:** AI processing is very slow

**Solution:**
- First run downloads models (~500MB) - this is normal
- Subsequent runs are much faster
- Consider using a GPU for faster processing

### Frontend

**Problem:** Frontend shows but nothing happens when clicking buttons

**Solution:**
1. Open browser console (F12)
2. Check for JavaScript errors
3. Ensure backend is running on port 5000
4. Check CORS settings

**Problem:** "No nodes found" in autocomplete

**Solution:**
1. Upload a document first
2. Wait for processing to complete
3. Refresh the page

---

## Testing the Complete System

### Test C-Core Directly:

```bash
cd nexus/c_core

# Test different queries
./nexus_engine.exe --file ../data/graph_data.txt --query path --start BERT --end NLP
./nexus_engine.exe --file ../data/graph_data.txt --query topics
./nexus_engine.exe --file ../data/graph_data.txt --query complete --prefix "Deep"
```

### Test Backend API:

With backend running, open a new terminal:

```bash
# Test health endpoint
curl http://localhost:5000/api/health

# Expected response:
{"c_engine_available":true,"graph_data_loaded":true, ...}
```

### Test Full System:

1. Start backend
2. Open frontend in browser
3. Upload a sample document
4. Run queries
5. Verify results appear

---

## Platform-Specific Notes

### Windows

- Use PowerShell or Command Prompt
- Python command: `python` (not `python3`)
- Use backslashes in paths: `nexus\backend`
- If `gcc` not found, install MinGW or use WSL

### Linux

- Python command: `python3`
- Use `pip3` instead of `pip`
- Slashes in paths: `nexus/backend`
- May need `sudo` for system-wide package installation

### macOS

- Python command: `python3`
- Use `pip3` instead of `pip`
- Apple Silicon (M1/M2): PyTorch has native support
- Install Xcode Command Line Tools for gcc

---

## Uninstallation

### Remove Python Packages:

```bash
pip uninstall flask flask-cors transformers torch -y
```

### Delete Project:

Simply delete the `nexus` folder.

---

## Next Steps

After successful setup:

1. **Upload your own documents**: Try with research papers, notes, or documentation
2. **Explore query types**: Each provides different insights
3. **Examine graph_data.txt**: See how AI extracted relationships
4. **Modify C-Core**: Add custom algorithms or features

---

## Support

If you encounter issues:

1. Check this guide's Troubleshooting section
2. Verify all prerequisites are installed
3. Test each component individually (C-Core, Backend, Frontend)
4. Check system resource availability (RAM, disk space)

---

## Development

### Adding New Features:

**C-Core algorithms:** Edit files in `c_core/`
**AI extraction:** Modify `backend/ai_helper.py`
**Frontend UI:** Edit files in `frontend/`

### Rebuilding:

```bash
# Recompile C-Core
cd c_core
make clean && make

# Restart backend
cd backend
python app.py
```

---

## Performance Optimization

### For Faster AI Processing:

1. Use GPU if available
2. Process documents in batch
3. Cache processed graphs

### For Faster Queries:

C-Core is already optimized! Query performance:
- Path finding: <1ms
- Autocomplete: <1ms
- Topic discovery: <1ms

---

Enjoy using Nexus! 🚀
