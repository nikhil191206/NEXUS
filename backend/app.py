from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import sys
import atexit
import shutil
import traceback

# Import with error handling
try:
    from ai_helper import process_text_file
    print("SUCCESS: ai_helper imported correctly")
except Exception as e:
    print(f"ERROR: Could not import ai_helper: {e}")
    traceback.print_exc()

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C_ENGINE_PATH = os.path.join(BASE_DIR, 'c_core', 'nexus_engine.exe' if sys.platform == 'win32' else 'nexus_engine')
GRAPH_DATA_PATH = os.path.join(BASE_DIR, 'data', 'graph_data.txt')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')

# Create folders if they don't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(GRAPH_DATA_PATH), exist_ok=True)

print(f"DEBUG: UPLOAD_FOLDER = {UPLOAD_FOLDER}")
print(f"DEBUG: GRAPH_DATA_PATH = {GRAPH_DATA_PATH}")
print(f"DEBUG: Folders exist: uploads={os.path.exists(UPLOAD_FOLDER)}, data={os.path.exists(os.path.dirname(GRAPH_DATA_PATH))}")

def cleanup_on_exit():
    """Clean up uploaded files when application closes."""
    if os.path.exists(UPLOAD_FOLDER):
        try:
            shutil.rmtree(UPLOAD_FOLDER)
            print("\nCleaned up uploaded files")
        except Exception as e:
            print(f"\nCould not clean up uploads: {e}")

# Register cleanup function
atexit.register(cleanup_on_exit)

@app.route('/api/upload', methods=['POST'])
def upload_document():
    """Handle document upload and process with transformer AI."""
    print("\n" + "="*60)
    print("UPLOAD REQUEST RECEIVED")
    print("="*60)
    
    try:
        print("Step 1: Checking for file in request...")
        if 'file' not in request.files:
            print("ERROR: No file in request")
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        print(f"Step 2: File received: {file.filename}")
        
        if file.filename == '':
            print("ERROR: Empty filename")
            return jsonify({'error': 'No file selected'}), 400

        # Save uploaded file
        filename = file.filename
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        
        print(f"Step 3: Saving file to: {input_path}")
        file.save(input_path)
        
        print(f"Step 4: File saved. Checking if exists: {os.path.exists(input_path)}")
        if not os.path.exists(input_path):
            raise Exception(f"File was not saved correctly to {input_path}")
        
        print(f"Step 5: File size: {os.path.getsize(input_path)} bytes")
        
        print(f"\n{'='*60}")
        print(f"Processing: {filename}")
        print(f"Input path: {input_path}")
        print(f"Output path: {GRAPH_DATA_PATH}")
        print(f"{'='*60}\n")

        # Process with transformer AI
        print("Step 6: Calling process_text_file()...")
        process_text_file(input_path, GRAPH_DATA_PATH)
        
        print("Step 7: Processing complete!")
        print(f"Step 8: Checking output file exists: {os.path.exists(GRAPH_DATA_PATH)}")

        return jsonify({
            'success': True,
            'message': 'Document processed successfully with Transformer AI',
            'graph_file': GRAPH_DATA_PATH
        })

    except Exception as e:
        print("\n" + "="*60)
        print("ERROR IN UPLOAD ENDPOINT:")
        print("="*60)
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        print("="*60 + "\n")
        
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query_graph():
    """Handle queries to the C-Core engine."""
    try:
        data = request.json
        query_type = data.get('query_type')

        if not query_type:
            return jsonify({'error': 'Query type required'}), 400

        cmd = [C_ENGINE_PATH, '--file', GRAPH_DATA_PATH, '--query', query_type]

        if query_type == 'path':
            start = data.get('start')
            end = data.get('end')
            if not start or not end:
                return jsonify({'error': 'Path query requires start and end nodes'}), 400
            cmd.extend(['--start', start, '--end', end])

        elif query_type == 'mindmap':
            start = data.get('start')
            if not start:
                return jsonify({'error': 'Mindmap query requires start node'}), 400
            cmd.extend(['--start', start])

        elif query_type == 'qa':
            node = data.get('node')
            if not node:
                return jsonify({'error': 'QA query requires node'}), 400
            cmd.extend(['--node', node])

        elif query_type == 'complete':
            prefix = data.get('prefix')
            if not prefix:
                return jsonify({'error': 'Complete query requires prefix'}), 400
            cmd.extend(['--prefix', prefix])

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({'error': result.stderr}), 500

        return jsonify({
            'success': True,
            'result': result.stdout.strip(),
            'query_type': query_type
        })

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    c_engine_exists = os.path.exists(C_ENGINE_PATH)
    graph_data_exists = os.path.exists(GRAPH_DATA_PATH)

    return jsonify({
        'status': 'healthy',
        'c_engine_available': c_engine_exists,
        'graph_data_loaded': graph_data_exists,
        'c_engine_path': C_ENGINE_PATH
    })

@app.route('/api/nodes', methods=['GET'])
def get_nodes():
    """Get all available nodes for autocomplete/selection."""
    try:
        nodes = []
        if os.path.exists(GRAPH_DATA_PATH):
            with open(GRAPH_DATA_PATH, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.startswith('NODE:'):
                        node_name = line[5:].strip()
                        nodes.append(node_name)

        return jsonify({
            'success': True,
            'nodes': sorted(nodes)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/preload-models', methods=['POST'])
def preload_models():
    """Pre-load transformer models synchronously."""
    try:
        print("\n" + "="*60)
        print("PRELOADING TRANSFORMER MODELS")
        print("="*60)
        
        from transformers import pipeline
        
        # Load NER model (BERT)
        print("Step 1/2: Loading BERT NER model...")
        ner_pipeline = pipeline(
            "ner",
            model="dslim/bert-base-NER",
            aggregation_strategy="simple"
        )
        print("OK - BERT model loaded successfully")
        
        # Load T5 model
        print("Step 2/2: Loading T5 model...")
        relation_pipeline = pipeline(
            "text2text-generation",
            model="google/flan-t5-small"
        )
        print("OK - T5 model loaded successfully")
        
        # Test the models
        print("Testing models...")
        test_text = "Machine Learning is a field of AI."
        ner_pipeline(test_text)
        relation_pipeline("test")
        
        print("OK - All models ready!")
        print("="*60 + "\n")
        
        return jsonify({
            'success': True,
            'message': 'Models preloaded successfully'
        })
        
    except Exception as e:
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("NEXUS: PERSONAL KNOWLEDGE BASE")
    print("="*60)
    print(f"C-Engine: {C_ENGINE_PATH}")
    print(f"Graph Data: {GRAPH_DATA_PATH}")
    print(f"AI: Transformer (BERT + T5)")
    print("="*60)
    print("Server running on http://localhost:5000")
    print("Press CTRL+C to stop")
    print("="*60 + "\n")

    try:
        app.run(debug=True, port=5000, use_reloader=False)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        cleanup_on_exit()