import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from flask import Flask, request, jsonify
from flask_cors import CORS
import subprocess
import sys
import atexit
import shutil
import re
from ai_helper import process_text_file

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C_ENGINE_PATH = os.path.join(BASE_DIR, 'c_core', 'nexus_engine.exe' if sys.platform == 'win32' else 'nexus_engine')
GRAPH_DATA_PATH = os.path.join(BASE_DIR, 'data', 'graph_data.txt')
UPLOAD_FOLDER = os.path.join(BASE_DIR, 'data', 'uploads')

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(GRAPH_DATA_PATH), exist_ok=True)

def cleanup_on_exit():
    if os.path.exists(UPLOAD_FOLDER):
        try:
            shutil.rmtree(UPLOAD_FOLDER)
        except:
            pass

atexit.register(cleanup_on_exit)

def parse_mindmap_output(c_output):
    """
    Convert hierarchical mindmap format from C to pipe-separated format for frontend.
    Input format: 
        MINDMAP:
        Root Node
          -[relation]->
          Child Node
            -[relation]->
            Grandchild
    Output format: Root|relation|Child (one per line)
    """
    # Handle both MINDMAP: and MINDMAP_DATA: headers
    if not (c_output.startswith('MINDMAP:') or c_output.startswith('MINDMAP_DATA:')):
        return c_output
    
    # Remove header and get data
    if c_output.startswith('MINDMAP_DATA:'):
        data = c_output.replace('MINDMAP_DATA:\n', '').replace('MINDMAP_DATA:', '').strip()
    else:
        data = c_output.replace('MINDMAP:\n', '').replace('MINDMAP:', '').strip()
    
    if not data:
        return "MINDMAP_DATA:\n"
    
    lines = data.split('\n')
    result = "MINDMAP_DATA:\n"
    
    # Stack to keep track of parent nodes at each indentation level
    parent_stack = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Calculate indentation level (number of leading spaces / 2)
        indent = len(line) - len(line.lstrip(' '))
        content = line.strip()
        
        # Skip empty lines
        if not content:
            i += 1
            continue
        
        # If line contains -[relation]->
        if '-[' in content and ']->' in content:
            # Extract relation
            match = re.search(r'-\[(.*?)\]->', content)
            if match:
                relation = match.group(1)
                
                # Get the next non-empty line which should be the target node
                i += 1
                while i < len(lines) and not lines[i].strip():
                    i += 1
                
                if i < len(lines):
                    target_line = lines[i]
                    target_indent = len(target_line) - len(target_line.lstrip(' '))
                    target = target_line.strip()
                    
                    # Get parent from stack based on indentation
                    # The parent is the node at the previous indentation level
                    if parent_stack:
                        # Find the appropriate parent
                        while parent_stack and parent_stack[-1][1] >= indent:
                            parent_stack.pop()
                        
                        if parent_stack:
                            parent = parent_stack[-1][0]
                            result += f"{parent}|{relation}|{target}\n"
                    
                    # Add current target to stack for future children
                    parent_stack.append((target, target_indent))
        else:
            # This is a node name (not a relation)
            parent_stack.append((content, indent))
        
        i += 1
    
    return result

@app.route('/api/upload', methods=['POST'])
def upload_document():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        filename = file.filename
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        process_text_file(input_path, GRAPH_DATA_PATH)

        return jsonify({
            'success': True,
            'message': 'Document processed successfully',
            'graph_file': GRAPH_DATA_PATH
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/query', methods=['POST'])
def query_graph():
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

        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')

        if result.returncode != 0:
            return jsonify({'error': result.stderr}), 500

        # Get the output
        output = result.stdout.strip()
        
        # Parse mindmap output to convert from hierarchical format to pipe-separated format
        if query_type == 'mindmap':
            output = parse_mindmap_output(output)

        return jsonify({
            'success': True,
            'result': output,
            'query_type': query_type
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
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
    try:
        from transformers import pipeline
        ner_pipeline = pipeline("ner", model="dslim/bert-base-NER", aggregation_strategy="simple")
        relation_pipeline = pipeline("text2text-generation", model="google/flan-t5-small")
        
        return jsonify({
            'success': True,
            'message': 'Models preloaded successfully'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("NEXUS: PERSONAL KNOWLEDGE BASE")
    print("Server running on http://localhost:5000")
    app.run(debug=False, port=5000, use_reloader=False)