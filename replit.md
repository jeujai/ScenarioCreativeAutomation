# Creative Automation Pipeline - Replit Project

## Project Overview
A Python-based creative automation pipeline that generates social ad campaign assets using GenAI. This proof-of-concept system automates the creation of localized campaign creatives for multiple products, aspect ratios, and markets.

## Purpose
Built as a technical demonstration for scalable social ad campaign automation. The system addresses the business needs of:
- Accelerating campaign velocity
- Ensuring brand consistency
- Maximizing relevance & personalization
- Optimizing marketing ROI
- Gaining actionable insights

## Current State
**Status**: Fully functional proof-of-concept
**Last Updated**: October 22, 2025

### Features Implemented
- ✅ Campaign brief parser (JSON/YAML support)
- ✅ Multi-product support (minimum 2 products)
- ✅ Intelligent asset management (reuse existing, generate when missing)
- ✅ GenAI image generation with OpenAI DALL-E integration
- ✅ Multi-aspect ratio support (1:1, 9:16, 16:9)
- ✅ Text overlay system with campaign messages
- ✅ Organized output by product and aspect ratio
- ✅ Command-line interface
- ✅ Comprehensive documentation

## Recent Changes

### October 22, 2025 - Initial Implementation
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
- **Image Processing**: Pillow (PIL)
- **GenAI**: OpenAI DALL-E 3 API
- **Data Formats**: JSON, YAML
- **Dependencies**: pillow, pyyaml, requests, openai, python-dotenv

### Design Decisions
1. **Modular Architecture**: Clear separation of concerns for maintainability
2. **Asset Reusability**: Check existing assets before generating to optimize costs
3. **Fallback Mechanism**: Placeholder images when GenAI unavailable
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
- `OPENAI_API_KEY`: Optional - for GenAI image generation. If not provided, system generates placeholder images.

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
- Requires OpenAI API key for actual GenAI (falls back to placeholders)
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
