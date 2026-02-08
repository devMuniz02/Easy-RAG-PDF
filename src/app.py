from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
from rag_processor import RAGProcessor
import json

app = Flask(__name__)
CORS(app)

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'uploads'))
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Global RAG processor
rag_processor = RAGProcessor()

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_files():
    if 'files' not in request.files:
        return jsonify({'error': 'No files provided'}), 400

    files = request.files.getlist('files')
    uploaded_files = []

    for file in files:
        if file.filename == '':
            continue
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            uploaded_files.append(filepath)

    if uploaded_files:
        # Process the uploaded PDFs
        success = rag_processor.process_pdfs(uploaded_files)
        if success:
            # Normalize paths to use forward slashes for web compatibility
            normalized_paths = [path.replace('\\', '/') for path in uploaded_files]
            return jsonify({
                'message': f'Successfully processed {len(uploaded_files)} PDF(s)',
                'uploaded_files': normalized_paths  # Return the server paths
            })
        else:
            return jsonify({'error': 'Failed to process PDFs'}), 500
    else:
        return jsonify({'error': 'No valid PDF files uploaded'}), 400

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        return jsonify({'error': 'No message provided'}), 400

    message = data['message']
    api_url = data.get('api_url', 'http://localhost:1234/v1/chat/completions')
    model = data.get('model', 'local-model')
    selected_files = data.get('selected_files', None)  # List of selected file paths

    if not selected_files or len(selected_files) == 0:
        return jsonify({'error': 'Please select at least one file to chat with'}), 400

    try:
        response = rag_processor.chat(message, api_url, model, selected_files)
        return jsonify({'response': response})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_page_counts', methods=['POST'])
def get_page_counts():
    data = request.get_json()
    if not data or 'file_paths' not in data:
        return jsonify({'error': 'No file paths provided'}), 400

    file_paths = data['file_paths']
    page_counts = {}
    
    for path in file_paths:
        if os.path.exists(path):
            page_count = rag_processor.get_pdf_page_count(path)
            page_counts[path] = page_count
        else:
            page_counts[path] = 0

    return jsonify({'page_counts': page_counts})

@app.route('/remove_file', methods=['POST'])
def remove_file():
    data = request.get_json()
    if not data or 'file_path' not in data:
        return jsonify({'error': 'No file path provided'}), 400

    file_path = data['file_path']
    
    # Remove the file from disk if it exists
    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception as e:
            print(f"Error removing file from disk: {e}")
    
    # Remove from RAG processor
    success = rag_processor.remove_file(file_path)
    
    if success:
        return jsonify({'message': 'File removed successfully'})
    else:
        return jsonify({'error': 'Failed to remove file'}), 500

@app.route('/save_uploaded_files', methods=['POST'])
def save_uploaded_files():
    data = request.get_json()
    if not data or 'uploaded_files' not in data:
        return jsonify({'error': 'No uploaded files data provided'}), 400

    result = rag_processor.save_uploaded_files_list(data['uploaded_files'])
    
    if 'error' in result:
        return jsonify({'error': result['error']}), 500
    
    message = f"Saved {result['saved']} new files"
    if result['duplicates'] > 0:
        message += f", {result['duplicates']} were duplicates"
    message += f" (total: {result['total']})"
    
    return jsonify({
        'message': message,
        'saved': result['saved'],
        'duplicates': result['duplicates'],
        'total': result['total']
    })

@app.route('/load_uploaded_files', methods=['GET'])
def load_uploaded_files():
    uploaded_files = rag_processor.load_uploaded_files_list()
    return jsonify({'uploaded_files': uploaded_files})

@app.route('/get_config', methods=['GET'])
def get_config():
    return jsonify({
        'default_api_url': 'http://localhost:1234/v1/chat/completions',
        'default_model': 'local-model'
    })

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)