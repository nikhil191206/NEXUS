# NEXUS: Personal Knowledge Base

NEXUS is a high-speed, hybrid query system that transforms your unstructured text documents into a fully queryable, visual knowledge graph.

It uses a Large Language Model (Google's **Gemini API**) for its world-class accuracy in data extraction and a hyper-fast, custom-built **C-Core Engine** for instantaneous graph queries.

This "best of both worlds" architecture gives you the intelligence of a massive AI model and the sub-millisecond query speed of pure C.



## 🏛️ Architecture

NEXUS is built in two distinct phases:

1.  **Phase 1: Ingestion (Slow, Smart)**
    When you upload a document, the text is sent to the Google Gemini API. The AI reads the text, extracts all entities and relationships, and formats them into a simple `graph_data.txt` file. This step is "slow" (it can take 30-60 seconds) but only happens once.

    `Document.txt  -->  [Python Backend]  -->  [Google Gemini API]  -->  graph_data.txt`

2.  **Phase 2: Querying (Instant, Fast)**
    All subsequent queries use the custom C-Core engine. This compiled program loads the `graph_data.txt` file into memory and uses highly-optimized C data structures to perform searches. This step is "fast," with most queries returning in less than 1ms.

    `User Query  -->  [Python Backend]  -->  [C-Core Engine]  -->  Instant Results`

---

## ✨ Features

NEXUS can perform 5 types of advanced queries on your documents:

* **Path Finding:** Finds the shortest path between two concepts (e.g., "Stack" to "LIFO").
* **Topic Discovery:** Uses Depth-First Search (DFS) to find all separate, disconnected clusters of information in your graph.
* **Visual Mind Map:** Generates a visual, interactive graph of how a concept is connected, rendered using Mermaid.js.
* **Q&A:** Lists all direct, 1-to-1 relationships for a given node.
* **Autocomplete:** Provides instant search suggestions using a custom-built Trie data structure.

---

## 🛠️ Tech Stack

| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **AI Extraction** | **Google Gemini API** | World-class entity & relation extraction. |
| **Backend** | **Python Flask** | API server to handle requests. |
| **Query Engine** | **Pure C** | Graph algorithms & data structures (DSA). |
| **Frontend** | **HTML/CSS/JS** | User interface for uploading and querying. |
| **Visualization** | **Mermaid.js** | Renders the visual, interactive mind maps. |

---

## 🚀 Quick Start

1.  **Get Your API Key:** This project requires a Google Gemini API key.
2.  **Set Up the Project:** Follow the **[SETUP.md](SETUP.md)** file for detailed installation and compilation steps.
3.  **Run the Server:**
    ```bash
    # (From the 'backend' folder)
    python app.py
    ```
4.  **Open the Frontend:**
    Open the `frontend/index.html` file in your browser.

## Usage

1.  **Upload:** Click "Process Document" and select a `.txt` file.
2.  **Wait:** Allow 30-60 seconds for the Gemini API to process the text (you only do this once per file).
3.  **Query:** Once the nodes appear in the "Available Nodes" list, use the query interface to explore your new knowledge graph.