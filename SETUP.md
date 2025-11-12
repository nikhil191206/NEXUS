# NEXUS Setup Guide

This guide provides the step-by-step instructions to get the NEXUS project running locally on your machine.

## Requirements

* **Google Gemini API Key:** You must have a valid API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
* **Python 3.10+:** Required for the backend and AI helper.
* **C Compiler:** A C compiler like `gcc` (common on Linux/macOS) or `MinGW` (for Windows).
* **Web Browser:** A modern browser like Chrome, Firefox, or Edge.

---

## Step 1: Get Your Gemini API Key

This is the most important step.

1.  Go to [Google AI Studio](https://aistudio.google.com/app/apikey) and create a new API key.
2.  **Set an Environment Variable:** You must set this key in your terminal. **Do not** hard-code it into the Python files.

    * **Windows (PowerShell):**
        ```powershell
        $env:GEMINI_API_KEY = "YOUR_API_KEY_HERE"
        ```
    * **macOS / Linux:**
        ```bash
        export GEMINI_API_KEY="YOUR_API_KEY_HERE"
        ```
    > **Note:** You must re-run this command every time you open a new terminal.

---

## Step 2: Set Up the Python Environment

It is **highly recommended** to use a clean virtual environment to avoid conflicts.

1.  **Create a Virtual Environment:**
    From the `NEXUS/` root folder:
    ```bash
    python -m venv venv
    ```

2.  **Activate the Environment:**
    * **Windows:** `.\venv\Scripts\activate`
    * **macOS / Linux:** `source venv/bin/activate`

3.  **Install Python Libraries:**
    ```bash
    # These are the only 3 libraries needed for this project
    pip install google-generativeai
    pip install flask
    pip install flask-cors
    ```
    > **Troubleshooting:** If you ever get a `404 v1beta` error, your library is out of date. Run this: `pip install --upgrade google-generativeai`

---

## Step 3: Compile the C-Core Engine

The C-Core must be compiled into an executable file that the Python backend can run.

1.  Navigate to the `c_core` directory:
    ```bash
    cd c_core
    ```
2.  Compile all `.c` files using `gcc`:
    ```bash
    # This command finds all .c files and compiles them into
    # a single executable named "nexus_engine.exe"
    gcc -Wall -Wextra -std=c11 -O2 -o nexus_engine.exe *.c
    ```
3.  Verify that `nexus_engine.exe` (or `nexus_engine` on macOS/Linux) is now present in the `c_core` folder.

---

## Step 4: Run the Application

1.  Navigate back to the `backend` directory:
    ```bash
    cd ../backend
    ```
2.  **Set your API key** in this terminal (if you haven't already).
    ```powershell
    # Windows
    $env:GEMINI_API_KEY = "YOUR_API_KEY_HERE"
    ```
3.  Run the Flask server:
    ```bash
    python app.py
    ```
4.  You should see the server running on `http://127.0.0.1:5000`.

---

## Step 5: Open the Frontend

1.  Navigate to the `frontend` folder.
2.  Open the **`index.html`** file directly in your browser.
3.  You are ready to go. Upload a document to begin.

## Troubleshooting

* **Error:** `429 You exceeded your current quota`
    * **Cause:** You are using the Gemini free tier, which is limited to 1-2 requests per minute. You uploaded too many files too quickly.
    * **Fix:** Stop your server, wait 60 seconds, and restart it.

* **Error:** `500 Internal Server Error` (in the browser)
    * **Cause:** The C-Core engine is missing or cannot run.
    * **Fix:** You forgot to do **Step 3**. Go to `c_core` and run the `gcc` command.

* **Problem:** The Mind Map is just text (e.g., `MINDMAP_DATA:...`)
    * **Cause:** Your browser is using an old, cached version of the `script.js` file.
    * **Fix:** Do a "Hard Refresh" in your browser: **Ctrl+Shift+R** (or **Cmd+Shift+R** on Mac).