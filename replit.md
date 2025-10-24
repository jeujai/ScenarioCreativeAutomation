# Creative Automation Pipeline - Replit Project

## Project Overview
A Python-based creative automation pipeline that generates social ad campaign assets using GenAI. This proof-of-concept system automates the creation of localized campaign creatives for multiple products, aspect ratios, and markets.

**Available as both a Web Application and Command-Line Tool!**

## Purpose
Built as a technical demonstration for scalable social ad campaign automation. The system addresses the business needs of:
- Accelerating campaign velocity
- Ensuring brand consistency
- Maximizing relevance & personalization
- Optimizing marketing ROI
- Gaining actionable insights

## Current State
**Status**: Fully functional web application and CLI tool
**Last Updated**: October 22, 2025

### Features Implemented
- ✅ **Web Interface**: Modern, responsive web UI with campaign form and asset gallery
- ✅ **Flask Backend**: RESTful API for campaign generation and asset management
- ✅ Campaign brief parser (JSON/YAML support)
- ✅ Multi-product support (minimum 2 products)
- ✅ Intelligent asset management (reuse existing, generate when missing)
- ✅ GenAI image generation with OpenAI DALL-E integration
- ✅ Multi-aspect ratio support (1:1, 9:16, 16:9)
- ✅ Text overlay system with campaign messages
- ✅ Organized output by product and aspect ratio
- ✅ Command-line interface for automation
- ✅ Example loading functionality
- ✅ Real-time asset preview and download
- ✅ Azure Blob Storage integration for cloud uploads
- ✅ Comprehensive documentation

## Recent Changes

### October 24, 2025 - Enhanced UI with Azure Integration
- **Product management improvements**:
  - Added remove/delete button for each product (red trash icon)
  - Minimum 1 product required (prevents deleting last product)
- **Color picker palette**:
  - Changed brand color from text input to visual color picker
  - Live hex value display updates as you select colors
- **Azure Blob Storage image browser**:
  - Hero images now selected from Azure container instead of local upload
  - Modal image browser with grid layout
  - Click to select images directly from Azure
  - Images automatically downloaded to uploads/ directory
  - New backend endpoints: `/azure-images` and `/download-azure-image`

### October 24, 2025 - Complete UI/UX Redesign + Subdirectory Asset Management
- **Redesigned to dark professional theme** matching modern creative tools
  - Dark charcoal background (#1a1a1a) with accent colors
  - CSS custom properties for consistent theming
  - Grid-based layout with sidebar (300px), main preview area, and logs panel
  - Responsive design with mobile/tablet support
- **New form fields**:
  - Hero image upload per product (fully functional)
  - Brand color (hex) input (UI ready, future integration)
  - Brand logo upload (UI ready, future integration)
  - All uploads integrated with backend `/upload-asset` endpoint
- **Process logs panel** at bottom
  - Terminal-style log display with color-coded messages
  - Real-time log updates during generation
  - Clear functionality
- **Subdirectory asset management** (critical feature)
  - User uploads saved to `assets/input/uploads/` (preserved across runs)
  - AI-generated images saved to `assets/input/generated/` (purged for fresh generation)
  - AssetManager prioritizes user uploads over AI-generated assets
  - Purge logic ensures fresh AI images while preserving user uploads
- **Improved UX**:
  - File upload indicators (shows selected filename in green)
  - Better visual hierarchy with organized sections
  - Empty states for preview area
  - Download buttons for generated creatives

### October 23, 2025 - Azure Blob Storage Integration
- **Added Azure Blob Storage integration** for automatic cloud uploads
  - Campaign assets automatically upload to Azure after generation
  - Configurable via environment variables
  - Optional feature (can be disabled)
  - Supports custom container names
- Created AzureUploader module for cloud storage management
- Updated pipeline to upload all campaign creatives to Azure
- Added Azure configuration to config.py

### October 23, 2025 - Switched Back to Google Gemini Primary
- **Switched to Google Gemini** as primary AI image generator
  - Google Gemini is now the primary image generator
  - OpenAI DALL-E 3 retained as fallback
  - Placeholder generation as final fallback
- Updated ImageGenerator to prioritize Gemini over OpenAI
- Auto-purge feature ensures fresh AI images every generation
- Updated documentation to reflect new GenAI priority

### October 22, 2025 - Web Interface Implementation
- **Added Flask web application** (`app.py`)
  - RESTful API endpoints for campaign generation
  - File upload support for custom assets
  - Static file serving for generated creatives
  - Example loading endpoint
- **Created responsive web UI**
  - Modern gradient design with purple/blue theme
  - Dynamic campaign form with product management
  - Real-time progress indicators
  - Asset gallery with grouped product displays
  - Download functionality for generated creatives
- **Updated documentation** for both web and CLI usage
- **Configured workflow** for web server on port 5000
- Successfully tested end-to-end campaign generation via web interface

### October 22, 2025 - Initial CLI Implementation
- Created modular architecture with separated concerns:
  - `brief_parser.py`: Campaign brief parsing and validation
  - `asset_manager.py`: Asset discovery and management
  - `image_generator.py`: GenAI integration with OpenAI DALL-E
  - `image_processor.py`: Image resizing and text overlay
  - `pipeline.py`: Main orchestrator
  - `config.py`: Configuration constants
- Implemented CLI interface with argparse
- Added example campaign briefs in YAML and JSON formats
- Created comprehensive README with usage instructions
- Successfully tested with example campaigns

## Project Architecture

### Directory Structure
```
creative-automation-pipeline/
├── main.py                     # CLI entry point
├── src/                        # Source code modules
│   ├── config.py
│   ├── brief_parser.py
│   ├── asset_manager.py
│   ├── image_generator.py
│   ├── image_processor.py
│   └── pipeline.py
├── examples/                   # Example campaign briefs
├── assets/input/              # Input assets directory
├── outputs/                   # Generated creatives
└── README.md
```

### Key Technologies
- **Language**: Python 3.11
- **Web Framework**: Flask
- **Image Processing**: Pillow (PIL)
- **GenAI**: Google Gemini (primary), OpenAI DALL-E 3 (fallback)
- **Data Formats**: JSON, YAML
- **Dependencies**: flask, pillow, pyyaml, requests, google-genai, openai, python-dotenv, werkzeug

### Design Decisions
1. **Modular Architecture**: Clear separation of concerns for maintainability
2. **Auto-Purge Assets**: Automatically clears all previous assets and outputs before each generation to ensure fresh AI-generated images every time
3. **Fallback Mechanism**: Google Gemini → OpenAI DALL-E 3 → Placeholder images
4. **Extensible Format**: Support both JSON and YAML for campaign briefs
5. **Smart Text Overlay**: Dynamic sizing and wrapping based on image dimensions

## Usage

### Basic Command
```bash
python main.py examples/campaign_brief.yaml
```

### With Options
```bash
python main.py examples/campaign_brief.json --verbose
python main.py examples/campaign_brief.yaml --assets-dir ./my_assets --outputs-dir ./my_outputs
```

## Configuration

### Environment Variables

**AI Image Generation:**
- `GEMINI_API_KEY`: Primary - for Google Gemini image generation (recommended)
- `OPENAI_API_KEY`: Fallback - for OpenAI DALL-E 3 image generation
- If neither is provided, system generates placeholder images

**Azure Blob Storage (Optional):**
- `AZURE_STORAGE_CONNECTION_STRING`: Azure credentials (SAS URL or Connection String)
- `AZURE_CONTAINER_NAME`: Container name for uploads (optional, auto-detected from SAS URL)
- `AZURE_UPLOAD_ENABLED`: Enable/disable Azure uploads (default: "true")

**Two authentication methods supported:**

*Option 1: SAS URL (Recommended - More Secure)*
1. Go to Azure Portal > Storage Accounts > Your Account
2. Navigate to "Shared access signature" or your container
3. Generate a SAS token with appropriate permissions (read, write, create, delete, list)
4. Copy the full SAS URL (e.g., `https://account.blob.core.windows.net/container?sp=...`)
5. Paste into `AZURE_STORAGE_CONNECTION_STRING`

*Option 2: Connection String (Full Access)*
1. Go to Azure Portal > Storage Accounts > Your Account
2. Navigate to "Access keys" under Security + networking
3. Copy "Connection string" from Key1 or Key2 (starts with `DefaultEndpointsProtocol=https;...`)
4. Paste into `AZURE_STORAGE_CONNECTION_STRING`

### Campaign Brief Format
Required fields:
- `products` (array, min 2): Product list with name and description
- `message` (string): Campaign message
- `region` (string, optional): Target region
- `audience` (string, optional): Target audience
- `localized_messages` (object, optional): Localized message variants

## Assumptions & Limitations

### Assumptions
- Campaign briefs are well-formed JSON or YAML
- Minimum 2 products per campaign
- Input assets are social-media ready quality
- System fonts (DejaVu, Liberation) available

### Current Limitations
- Requires Gemini API key for best results (falls back to OpenAI, then placeholders)
- No automatic translation (accepts pre-translated messages)
- Brand compliance not implemented (future enhancement)
- Legal content checks not implemented (future enhancement)
- Single campaign processing at a time

## Future Enhancements
- Brand compliance checks (logo, colors, fonts)
- Legal content filtering
- Advanced localization with auto-translation
- Performance analytics dashboard
- Additional cloud storage providers (AWS S3, Dropbox)
- Batch processing for multiple campaigns

## Technical Notes
- Uses type hints for better code maintainability
- Comprehensive logging to console and file
- Error handling with graceful fallbacks
- LSP-compatible code structure
