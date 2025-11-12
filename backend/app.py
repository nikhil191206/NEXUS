from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import os
import sys
import atexit
import shutil

from ai_helper import process_text_file

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C_ENGINE_PATH = os.path.join(BASE_DIR, 'c_core', 'nexus_engine.exe' if sys.platform == 'win32' else 'nexus_engine')
GRAPH_DATA_PATH = os.path.join(BASE_DIR, 'data', 'graph_data.txt')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

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
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # Save uploaded file
        filename = file.filename
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        print(f"\n{'='*60}")
        print(f"Processing: {filename}")
        print(f"{'='*60}")

        # Process with transformer AI
        process_text_file(input_path, GRAPH_DATA_PATH)

        return jsonify({
            'success': True,
            'message': 'Document processed successfully with Transformer AI',
            'graph_file': GRAPH_DATA_PATH
        })

    except Exception as e:
        import traceback
        traceback.print_exc()
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
    """Pre-load transformer models before document processing."""
    try:
        from flask import Response
        import json

        def generate():
            """Generator to stream progress updates."""
            preload_script = os.path.join(os.path.dirname(__file__), 'preload_models.py')

            # Run preload script and capture output
            process = subprocess.Popen(
                [sys.executable, preload_script],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )

            for line in iter(process.stdout.readline, ''):
                if line:
                    # Send progress update to frontend
                    yield f"data: {json.dumps({'message': line.strip()})}\n\n"

            process.wait()

            if process.returncode == 0:
                yield f"data: {json.dumps({'success': True, 'message': 'Models loaded successfully'})}\n\n"
            else:
                yield f"data: {json.dumps({'success': False, 'error': 'Failed to load models'})}\n\n"

        return Response(generate(), mimetype='text/event-stream')

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

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
        app.run(debug=True, port=5000)
    except KeyboardInterrupt:
        print("\n\nShutting down...")
        cleanup_on_exit()
