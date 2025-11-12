# Nexus: Personal Knowledge Base

A hybrid system that transforms unstructured text documents into a queryable knowledge graph using **Transformer AI** (BERT + T5) for extraction and a **C-Core Engine** with custom Data Structures & Algorithms for blazing-fast queries.

---

## Features

### AI-Powered Extraction
- **BERT NER**: Named Entity Recognition
- **T5 Relation Extraction**: Contextual relationship identification
- **One-time processing**: Extract once, query thousands of times

### C-Core Query Engine
- **Hash Table**: O(1) node lookups
- **BFS**: Shortest path finding
- **DFS**: Topic discovery and mind maps
- **Trie**: Autocomplete suggestions
- **Custom DSA**: Zero external dependencies

### Query Types
1. **Path Finding**: Find shortest connection between concepts
2. **Topic Discovery**: Identify disconnected concept clusters
3. **Mind Map**: Generate hierarchical concept trees
4. **Q&A**: Explore node relationships
5. **Autocomplete**: Suggestion system for concept names

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│ PHASE 1: ONE-TIME DATA INGESTION (Slow, Accurate)      │
├─────────────────────────────────────────────────────────┤
│  Document → [AI Helper: BERT + T5] → graph_data.txt    │
└─────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────┐
│ PHASE 2: LIVE QUERYING (Fast, Always Available)        │
├─────────────────────────────────────────────────────────┤
│  Query → [C-Core: Pure DSA] → Results (<1ms)           │
└─────────────────────────────────────────────────────────┘
```

---

## Tech Stack

| Component | Technology | Purpose |
|-----------|------------|---------|
| **AI Extraction** | BERT + T5 (Transformers) | Entity & relation extraction |
| **Query Engine** | Pure C | Graph algorithms & DSA |
| **Backend** | Python Flask | API server |
| **Frontend** | HTML/CSS/JS | User interface |

---

## Quick Start

See [SETUP.md](SETUP.md) for detailed installation instructions.

### 1. Install Dependencies

```bash
cd nexus/backend
pip install flask flask-cors transformers torch
```

### 2. Compile C-Core

```bash
cd nexus/c_core
gcc -Wall -Wextra -std=c11 -O2 -o nexus_engine.exe *.c
```

### 3. Start Server

```bash
cd nexus/backend
python app.py
```

### 4. Open Frontend

Open `nexus/frontend/landing.html` in your browser to start with the landing page, or open `index.html` directly for the main interface.

---

## Usage

### 1. Upload Document
- Click "Process Document"
- Select a .txt file
- AI processes and extracts knowledge graph

### 2. Query Graph
Choose from 5 query types:
- **Path**: Find connection between two concepts
- **Topics**: Discover concept clusters
- **Mind Map**: Visualize concept hierarchy
- **Q&A**: Explore node relationships
- **Autocomplete**: Get suggestions

### 3. View Results
Results displayed instantly via C-Core engine.

---

## Performance

| Operation | Time | Technology |
|-----------|------|------------|
| **Document Processing** | ~10s | Transformer AI (one-time) |
| **Node Lookup** | <1ms | Hash Table (O(1)) |
| **Path Finding** | <1ms | BFS + Queue |
| **Topic Discovery** | <1ms | DFS + Stack |
| **Autocomplete** | <1ms | Trie |

---

## Project Structure

```
nexus/
├── c_core/              # C Engine with custom DSA
│   ├── nexus_engine.c   # Main engine
│   ├── graph.c          # Graph algorithms
│   ├── hash_table.c     # O(1) lookups
│   ├── trie.c           # Autocomplete
│   ├── queue.c          # BFS
│   ├── stack.c          # DFS
│   └── Makefile
│
├── backend/             # Python Flask API
│   ├── app.py           # API server
│   ├── ai_helper.py     # Transformer AI
│   └── requirements.txt
│
├── frontend/            # Web UI
│   ├── index.html       # Interface
│   ├── style.css        # Styles (black & white)
│   └── script.js        # Logic
│
├── data/                # Knowledge graph storage
│   └── graph_data.txt   # NODE/EDGE format
│
├── README.md            # This file
└── SETUP.md             # Installation guide
```

---

## Data Format

The AI helper generates a simple text format:

```
NODE: Machine Learning
NODE: Deep Learning
NODE: Neural Networks
EDGE: Deep Learning|is_type_of|Machine Learning
EDGE: Neural Networks|is_foundation_of|Deep Learning
```

The C-Core reads this and builds the graph in memory.

---

## Why This Architecture?

### AI for Accuracy
- Transformers understand context
- Extract complex relationships
- Handle natural language

### C-Core for Speed
- Custom DSA implementation
- Zero overhead
- Instant queries

### Best of Both Worlds
- **AI accuracy** (one-time, can be slow)
- **DSA speed** (continuous, must be fast)

**Example:**
- Process document once: 10 seconds
- Query 10,000 times: <10 seconds total
- If AI ran on every query: 27+ hours!

---

## Requirements

### Minimum
- Python 3.8+
- GCC compiler
- 4GB RAM
- Modern web browser

### Recommended
- Python 3.10+
- 8GB RAM
- GPU (for faster AI processing)

---

## Troubleshooting

### "transformers not found"
```bash
pip install transformers torch
```

### "C-Core not compiled"
```bash
cd nexus/c_core
gcc -o nexus_engine.exe *.c
```

### "CORS error in browser"
- Make sure backend is running on port 5000
- Check browser console for details

### "Out of memory"
- AI processing requires ~2-3GB RAM
- Close other applications

---

## Features in Detail

### 1. Path Finding (BFS)
Finds shortest connection between two concepts using Breadth-First Search.

**Example:**
```
Query: BERT → NLP
Result: BERT -[revolutionized]-> NLP
```

### 2. Topic Discovery (DFS)
Identifies disconnected concept clusters using Depth-First Search.

**Example:**
```
TOPIC_1: BERT, GPT, NLP, Transformers
TOPIC_2: CNN, Computer Vision, Image Recognition
```

### 3. Mind Map (DFS)
Generates hierarchical visualization of concept relationships.

**Example:**
```
Deep Learning
  -[is_type_of]->
  Machine Learning
    -[uses]->
    Neural Networks
```

### 4. Q&A
Explores direct relationships from a node.

**Example:**
```
Query: Dropout
Result: Dropout prevents Overfitting
```

### 5. Autocomplete (Trie)
Provides suggestions based on prefix.

**Example:**
```
Query: "Conv"
Result: Convolutional Neural Networks
```

---

## Auto-Cleanup

When the application closes, uploaded files are automatically deleted to save disk space.

---

## License

Educational/Research Use

---

## Credits

Built as a demonstration of hybrid AI + DSA architecture for fast, accurate knowledge retrieval.

**Core Technologies:**
- Transformers (HuggingFace)
- Flask
- Pure C (no external DSA libraries)
