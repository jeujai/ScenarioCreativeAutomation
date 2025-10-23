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
- ✅ Comprehensive documentation

## Recent Changes

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
- `GEMINI_API_KEY`: Primary - for Google Gemini image generation (recommended)
- `OPENAI_API_KEY`: Fallback - for OpenAI DALL-E 3 image generation
- If neither is provided, system generates placeholder images

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
- Local filesystem storage only
- Single campaign processing at a time

## Future Enhancements
- Brand compliance checks (logo, colors, fonts)
- Legal content filtering
- Advanced localization with auto-translation
- Performance analytics dashboard
- Cloud storage integration (Azure, AWS, Dropbox)
- Batch processing for multiple campaigns

## Technical Notes
- Uses type hints for better code maintainability
- Comprehensive logging to console and file
- Error handling with graceful fallbacks
- LSP-compatible code structure
