from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import os
import json
import yaml
from pathlib import Path
from werkzeug.utils import secure_filename
import logging

from src.brief_parser import BriefParser, CampaignBrief
from src.pipeline import CreativeAutomationPipeline
from src.config import ASSETS_DIR, OUTPUTS_DIR

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = ASSETS_DIR

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/examples')
def examples():
    examples_dir = Path('examples')
    example_files = {}
    
    for file_path in examples_dir.glob('*.yaml'):
        with open(file_path, 'r') as f:
            example_files[file_path.stem] = yaml.safe_load(f)
    
    for file_path in examples_dir.glob('*.json'):
        with open(file_path, 'r') as f:
            example_files[file_path.stem] = json.load(f)
    
    return jsonify(example_files)


@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        logger.info(f"Received campaign data: {data}")
        
        campaign_brief = BriefParser.parse_dict(data)
        
        pipeline = CreativeAutomationPipeline()
        results, azure_upload_count = pipeline.run(campaign_brief)
        
        output_files = []
        for product_name, paths in results.items():
            for path in paths:
                relative_path = str(path.relative_to(Path.cwd()))
                output_files.append({
                    'product': product_name,
                    'path': relative_path,
                    'url': f'/outputs/{path.relative_to(OUTPUTS_DIR)}',
                    'filename': path.name
                })
        
        return jsonify({
            'success': True,
            'message': f'Generated {len(output_files)} creatives',
            'files': output_files,
            'azure_uploads': azure_upload_count
        })
    
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        logger.error(f"Error generating campaign: {e}", exc_info=True)
        return jsonify({'error': f'Error generating campaign: {str(e)}'}), 500


@app.route('/upload-asset', methods=['POST'])
def upload_asset():
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        product_name = request.form.get('product_name', '')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Invalid file type. Allowed: png, jpg, jpeg, webp'}), 400
        
        filename = secure_filename(file.filename)
        
        # Save user uploads to uploads/ subdirectory
        uploads_dir = ASSETS_DIR / 'uploads'
        uploads_dir.mkdir(parents=True, exist_ok=True)
        
        if product_name:
            normalized_name = product_name.lower().replace(' ', '_').replace('-', '_')
            ext = filename.rsplit('.', 1)[1].lower()
            filename = f"{normalized_name}_hero.{ext}"
        
        filepath = uploads_dir / filename
        file.save(filepath)
        
        logger.info(f"Uploaded asset: {filepath}")
        
        return jsonify({
            'success': True,
            'message': f'Asset uploaded successfully: {filename}',
            'filename': filename
        })
    
    except Exception as e:
        logger.error(f"Error uploading asset: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/outputs/<path:filename>')
def serve_output(filename):
    return send_from_directory(OUTPUTS_DIR, filename)


@app.route('/assets/<path:filename>')
def serve_asset(filename):
    return send_from_directory(ASSETS_DIR, filename)


@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'service': 'Creative Automation Pipeline'})


if __name__ == '__main__':
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
