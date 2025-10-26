from flask import Flask, render_template, request, jsonify, send_from_directory, redirect, url_for
import os
import json
import yaml
from pathlib import Path
from werkzeug.utils import secure_filename
import logging
import sys

from src.brief_parser import BriefParser, CampaignBrief
from src.pipeline import CreativeAutomationPipeline
from src.config import ASSETS_DIR, OUTPUTS_DIR
from src.azure_uploader import AzureUploader

# Configure logging early
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SESSION_SECRET', 'dev-secret-key-change-in-production')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['UPLOAD_FOLDER'] = ASSETS_DIR

# Ensure required directories exist on startup
try:
    ASSETS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'uploads').mkdir(parents=True, exist_ok=True)
    (ASSETS_DIR / 'logos').mkdir(parents=True, exist_ok=True)
    logger.info(f"Initialized directories: {ASSETS_DIR}, {OUTPUTS_DIR}")
except Exception as e:
    logger.error(f"Failed to create directories: {e}")
    # Continue anyway - directories might already exist

# Log configuration on startup
logger.info("=" * 60)
logger.info("Creative Automation Pipeline - Starting")
logger.info(f"Python version: {sys.version}")
logger.info(f"Assets directory: {ASSETS_DIR}")
logger.info(f"Outputs directory: {OUTPUTS_DIR}")
logger.info(f"Gemini API Key configured: {bool(os.getenv('GEMINI_API_KEY'))}")
logger.info(f"Azure configured: {bool(os.getenv('AZURE_STORAGE_CONNECTION_STRING'))}")
logger.info("=" * 60)

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
        
        # Clear outputs folder to start fresh versioning at v1
        import shutil
        if OUTPUTS_DIR.exists():
            shutil.rmtree(OUTPUTS_DIR)
        OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
        logger.info("Cleared outputs folder - versioning will start at v1")
        
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
        
        if not file.filename or file.filename == '':
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


@app.route('/azure-images')
def azure_images():
    """List available images from Azure Blob Storage"""
    try:
        folder = request.args.get('folder', '')
        product_name = request.args.get('product', '')
        
        uploader = AzureUploader()
        
        if not uploader.enabled:
            return jsonify({
                'error': 'Azure Blob Storage not configured. Please set AZURE_STORAGE_CONNECTION_STRING environment variable.'
            }), 400
        
        images = uploader.list_blobs(prefix=folder, only_images=True)
        
        # If folder is 'assets', filter based on product
        if folder == 'assets':
            # Always exclude logos subfolder
            images = [img for img in images if not img['name'].startswith('assets/logos/')]
            
            # If product name provided, filter to only that product's assets
            if product_name:
                normalized_product = product_name.lower().replace(' ', '_').replace('-', '_')
                images = [img for img in images if f'/{normalized_product}/' in img['name'] or f'/{normalized_product}_' in img['name']]
        
        return jsonify({
            'success': True,
            'images': images,
            'count': len(images),
            'folder': folder,
            'product': product_name
        })
    
    except Exception as e:
        logger.error(f"Error listing Azure images: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/download-azure-image', methods=['POST'])
def download_azure_image():
    """Download an image from Azure Blob Storage (secure - no SSRF vulnerability)"""
    try:
        data = request.get_json()
        blob_name = data.get('blob_name')
        product_name = data.get('product_name', '')
        is_logo = data.get('is_logo', False)
        
        if not blob_name:
            return jsonify({'error': 'No blob name provided'}), 400
        
        uploader = AzureUploader()
        
        if not uploader.enabled:
            return jsonify({'error': 'Azure Blob Storage not configured'}), 400
        
        # Determine directory and filename based on type
        if is_logo:
            # Save to dedicated logos directory
            target_dir = ASSETS_DIR / 'logos'
            target_dir.mkdir(parents=True, exist_ok=True)
            filename = Path(blob_name).name
        else:
            # Save to uploads directory for hero images
            target_dir = ASSETS_DIR / 'uploads'
            target_dir.mkdir(parents=True, exist_ok=True)
            
            if product_name:
                normalized_name = product_name.lower().replace(' ', '_').replace('-', '_')
                ext = Path(blob_name).suffix
                filename = f"{normalized_name}_hero{ext}"
            else:
                filename = Path(blob_name).name
        
        filepath = target_dir / filename
        
        # Download via Azure SDK (secure - validates blob exists in our container)
        success = uploader.download_blob(blob_name, filepath)
        
        if not success:
            return jsonify({'error': 'Failed to download blob from Azure'}), 500
        
        logger.info(f"Downloaded Azure blob to: {filepath}")
        
        return jsonify({
            'success': True,
            'message': f'Image downloaded successfully: {filename}',
            'filename': filename,
            'local_path': str(filepath)
        })
    
    except Exception as e:
        logger.error(f"Error downloading Azure image: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/delete-hero-image', methods=['POST'])
def delete_hero_image():
    """Delete a hero image from uploads directory"""
    try:
        data = request.get_json()
        product_name = data.get('product_name', '')
        
        if not product_name:
            return jsonify({'error': 'No product name provided'}), 400
        
        uploads_dir = ASSETS_DIR / 'uploads'
        normalized_name = product_name.lower().replace(' ', '_').replace('-', '_')
        
        # Look for hero image with various extensions
        deleted = False
        for ext in ['jpeg', 'jpg', 'png', 'webp']:
            filename = f"{normalized_name}_hero.{ext}"
            filepath = uploads_dir / filename
            
            if filepath.exists():
                filepath.unlink()
                logger.info(f"Deleted hero image: {filepath}")
                deleted = True
                break
        
        if deleted:
            return jsonify({
                'success': True,
                'message': 'Hero image deleted successfully'
            })
        else:
            return jsonify({
                'success': True,
                'message': 'No hero image found to delete'
            })
    
    except Exception as e:
        logger.error(f"Error deleting hero image: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/health')
def health():
    """Health check endpoint for deployment monitoring"""
    health_status = {
        'status': 'healthy',
        'service': 'Creative Automation Pipeline',
        'version': '1.0.0',
        'checks': {
            'gemini_api_key': bool(os.getenv('GEMINI_API_KEY')),
            'azure_storage': bool(os.getenv('AZURE_STORAGE_CONNECTION_STRING')),
            'directories': {
                'assets': ASSETS_DIR.exists(),
                'outputs': OUTPUTS_DIR.exists()
            }
        }
    }
    return jsonify(health_status), 200


if __name__ == '__main__':
    # Directories already created at module load
    logger.info("Starting Flask development server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
