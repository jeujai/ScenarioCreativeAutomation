# Creative Automation Pipeline

A GenAI-powered creative automation pipeline that generates localized social ad campaign assets at scale. This system automates the creation of campaign creatives across multiple products, aspect ratios, and global markets with intelligent asset management and real-time preview.

**Available as both a Web Application and Command-Line Tool!**

## Features

### 🎨 Web Interface
- **Modern Dark UI**: Professional creative tool design with real-time preview and process logs
- **Dynamic Form Loading**: Defaults automatically loaded from YAML configuration (single source of truth)
- **Azure Integration**: Browse and select assets directly from Azure Blob Storage with SAS URL support
- **Visual Controls**: Color picker for brand colors, logo positioning controls, hero image management
- **Real-time Preview**: Live gallery view with organized product sections and cache-busting
- **400px Sidebar**: Optimized for comfortable product name and description editing (7-row textareas)

### 🤖 GenAI Image Generation
- **Primary**: Google Gemini 2.5 Flash Image for high-quality creative generation
- **Fallback**: OpenAI DALL-E 3 for redundancy
- **Smart Hero Logic**: 
  - Reuses uploaded hero images across all outputs
  - Generates region-specific backgrounds when no hero provided
- **Parallel Processing**: Simultaneous generation of all products (up to 4x speed improvement)

### 🌍 Global Localization
- **52 Regions Supported**: Automatic translation of campaign messages
- **Autocomplete Region Picker**: Easy selection from all supported markets
- **Multi-Script Font Support**: Automatic font selection for Thai, Arabic, Hebrew, Bengali, Greek, Devanagari, Ethiopic, Korean, Traditional/Simplified Chinese, Japanese, Cyrillic, and Latin scripts
- **Cultural Adaptation**: Region-specific image generation with culturally appropriate backgrounds

### 📦 Asset Management
- **Azure Blob Storage**: Cloud-based asset storage with intelligent filtering
- **Smart Versioning**: Azure-based incremental versioning (v1, v2, v3...) with session persistence
- **Organized Folders**: Separate directories for uploads, generated assets, and logos
- **Hero Image Workflow**: Upload hero images or let GenAI create region-specific visuals
- **Logo Management**: Select, position, and deselect brand logos with transparency support

### 🎯 Multi-Format Output
- **Three Aspect Ratios**: 1:1 (Instagram), 9:16 (Stories/Reels), 16:9 (YouTube)
- **Smart Text Overlay**: Campaign messages with brand colors and automatic text wrapping
- **Version Control**: Incremental versioning persists in Azure across sessions
- **Organized Gallery**: Product sections with sorted aspect ratios for easy viewing

## Quick Start

### Web Interface (Recommended)

1. **Start the server**:
   ```bash
   python app.py
   ```

2. **Open browser** to `http://localhost:5000`

3. **The form pre-populates** with default Superman/Batman campaign from `examples/multi_product_campaign.yaml`

4. **Generate creatives**:
   - Modify campaign message, region, and products as needed
   - Optionally select hero images and logo from Azure
   - Click "Generate Creatives"
   - Preview and download results!

### Command-Line Interface

Run the pipeline with a campaign brief:

```bash
python main.py examples/multi_product_campaign.yaml
```

## Project Structure

```
creative-automation-pipeline/
├── app.py                          # Flask web application
├── main.py                         # CLI entry point
├── src/
│   ├── config.py                   # Configuration and constants
│   ├── brief_parser.py             # Campaign brief parsing (JSON/YAML)
│   ├── asset_manager.py            # Asset discovery and management
│   ├── image_generator.py          # GenAI image generation (Gemini/DALL-E)
│   ├── image_processor.py          # Image resizing and text overlay
│   ├── azure_uploader.py           # Azure Blob Storage integration
│   ├── regional_translator.py      # 52-region translation system
│   └── pipeline.py                 # Main pipeline orchestrator
├── templates/
│   └── index.html                  # Web interface (loads YAML defaults)
├── examples/
│   ├── multi_product_campaign.yaml # Default campaign (single source of truth)
│   ├── campaign_brief.yaml         # Simple example
│   └── campaign_brief.json         # JSON format example
├── assets/
│   └── input/
│       ├── uploads/                # User-uploaded hero images
│       ├── generated/              # AI-generated region-specific assets
│       └── logos/                  # Brand logos (exclusive source)
├── outputs/                        # Generated creatives (cleared per session)
└── fonts/                          # Multi-script font collection
```

## Installation

### Requirements
- Python 3.11+
- Azure Blob Storage account (for cloud features)
- Google Gemini API key (primary GenAI)
- OpenAI API key (fallback GenAI)

### Setup

1. **Install dependencies**:
   ```bash
   pip install flask pillow pyyaml requests openai google-genai azure-storage-blob python-dotenv werkzeug gunicorn
   ```

2. **Configure environment variables**:
   ```bash
   # Required for full functionality
   GEMINI_API_KEY=your_gemini_api_key
   OPENAI_API_KEY=your_openai_api_key
   
   # Google Cloud Translation API (for dynamic translation of any message)
   GOOGLE_TRANSLATE_API_KEY=your_google_translate_api_key
   
   # Azure Blob Storage (SAS URL for secure, time-limited, scoped access)
   AZURE_STORAGE_SAS_URL=https://account.blob.core.windows.net/container?sp=racwdli&st=2025-10-24T04:45:54Z&se=2026-10-01T13:00:54Z&sv=2024-11-04&sr=c&sig=...
   
   # Optional Azure settings
   AZURE_CONTAINER_NAME=campaign-assets           # Default: "campaign-assets" (overridden by container in SAS URL)
   AZURE_UPLOAD_ENABLED=true                      # Default: "true"
   
   # Optional
   SESSION_SECRET=your_session_secret             # For Flask sessions
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

## Campaign Brief Format

### Default Configuration (Single Source of Truth)

The web UI automatically loads defaults from `examples/multi_product_campaign.yaml`:

```yaml
region: "Japan"
audience: "Young, style-conscious professionals"
message: "Clothes that make the man"
brand_color: "#6366f1"

products:
  - name: "Business Casual for a Superman"
    description: "Superman (as Clark) blending into a culturally specific newsroom environment..."
    
  - name: "Super Suit for a Superman"
    description: "Clark (as Superman) blending into a culturally specific metropolitan environment..."
    
  - name: "Business Casual for a Batman"
    description: "Batman (as Bruce) blending into a culturally specific Wayne Enterprises..."
    
  - name: "Bat Suit for a Dark Knight"
    description: "Bruce (as Batman) blending into a culturally specific metropolitan environment..."
```

**To change web UI defaults**: Simply edit `examples/multi_product_campaign.yaml` - the web form will load these values on page load!

### Custom Campaign Brief

Create your own YAML or JSON file:

```yaml
region: "France"
audience: "Fashion-conscious millennials"
message: "Style That Speaks Volumes"
brand_color: "#e74c3c"

products:
  - name: "Designer Sunglasses"
    description: "Luxury designer sunglasses with UV protection"
    
  - name: "Leather Handbag"
    description: "Premium leather handbag with modern design"
```

### JSON Format

```json
{
  "region": "Spain",
  "audience": "Tech enthusiasts aged 25-40",
  "message": "Innovation Meets Design",
  "brand_color": "#3498db",
  "products": [
    {
      "name": "Smart Watch",
      "description": "Premium smartwatch with fitness tracking"
    },
    {
      "name": "Wireless Earbuds",
      "description": "Noise-cancelling wireless earbuds"
    }
  ]
}
```

## Supported Regions (52 Total)

### Asia-Pacific
Japan, South Korea, China, Taiwan, Hong Kong, Thailand, Vietnam, Philippines, Singapore, India, Pakistan, Bangladesh, Indonesia, Malaysia, Australia, New Zealand

### Middle East & North Africa
Saudi Arabia, UAE, Egypt, Israel, Iran, Morocco, Turkey

### Europe
France, Germany, Spain, Italy, UK, Netherlands, Poland, Sweden, Norway, Denmark, Finland, Portugal, Greece, Czech Republic, Romania, Hungary, Russia, Ukraine

### Americas
USA, Canada, Mexico, Brazil, Argentina, Colombia, Chile, Peru

### Africa
South Africa, Nigeria, Kenya, Ethiopia

## Key Architecture Decisions

### 1. Single Source of Truth (YAML)
- **Web UI defaults** are loaded from `examples/multi_product_campaign.yaml` via JavaScript on page load
- **CLI examples** use the same YAML file
- **Graceful fallback** to HTML hardcoded defaults if YAML fails to load
- **Easy updates**: Edit one file to change defaults across entire application

### 2. Azure-Based Versioning
- Version numbers determined by querying Azure Blob Storage for highest existing version
- Local `/outputs/` folder cleared each session for clean results
- Version history persists in Azure (v1, v2, v3... continue across sessions)
- Fallback to local versioning if Azure unavailable

### 3. Intelligent Hero Image Logic
- **User-uploaded heroes** (`/assets/input/uploads/`): Reused across all variants
- **Missing heroes**: Trigger fresh GenAI generation with region-specific prompts
- **AI-generated assets** (`/assets/input/generated/`): Culturally relevant backgrounds per region
- **Logo assets** (`/assets/input/logos/`): Exclusive source for brand logos

### 4. Parallel Processing
- All products processed simultaneously using `ThreadPoolExecutor`
- Up to 4x speed improvement for multi-product campaigns
- Maintains quality while reducing generation time

### 5. Multi-Script Font Support
Automatic detection and font selection for:
- **Thai**: Noto Sans Thai (213KB)
- **Arabic/Persian/Urdu**: Noto Sans Arabic (824KB)
- **Hebrew**: Noto Sans Hebrew (110KB)
- **Bengali**: Noto Sans Bengali (446KB)
- **Greek**: Noto Sans Greek (2MB)
- **Devanagari/Hindi**: Noto Sans Devanagari (631KB)
- **Ethiopic/Ge'ez**: Noto Sans Ethiopic (1.1MB)
- **Korean/Hangul**: Noto Sans KR (10MB)
- **Traditional Chinese**: Noto Sans TC (11.3MB)
- **Japanese**: Noto Sans JP (9.2MB)
- **Simplified Chinese**: Uses TC font
- **Cyrillic/Latin**: System defaults

### 6. Smart Text Overlay
- Dynamic sizing based on image dimensions
- Automatic text wrapping for optimal readability
- Brand color customization
- Shadow effects for visibility on any background

### 7. Browser Cache Busting
- Timestamp-based query parameters on image URLs
- Ensures fresh image loading after regeneration
- Prevents stale cache issues in web preview

## Output Organization

Generated creatives are organized by product and aspect ratio with incremental versioning:

```
outputs/
├── business_casual_for_a_superman/
│   ├── business_casual_for_a_superman_1x1_v1.png
│   ├── business_casual_for_a_superman_9x16_v1.png
│   └── business_casual_for_a_superman_16x9_v1.png
├── super_suit_for_a_superman/
│   ├── super_suit_for_a_superman_1x1_v1.png
│   ├── super_suit_for_a_superman_9x16_v1.png
│   └── super_suit_for_a_superman_16x9_v1.png
└── ...
```

**Azure Storage** (version history persists):
```
assets/
├── business_casual_for_a_superman/
│   ├── business_casual_for_a_superman_1x1_v1.png
│   ├── business_casual_for_a_superman_1x1_v2.png
│   ├── business_casual_for_a_superman_1x1_v3.png
│   └── ...
└── ...
```

## CLI Usage

### Basic Command
```bash
python main.py examples/multi_product_campaign.yaml
```

### Options
```bash
python main.py <brief_file> [options]

Arguments:
  brief                 Path to campaign brief file (JSON or YAML)

Options:
  --assets-dir DIR      Directory containing input assets (default: assets/input)
  --outputs-dir DIR     Directory for output creatives (default: outputs)
  --verbose, -v         Enable verbose logging
  --help, -h            Show help message
```

### Examples

**Generate with verbose logging**:
```bash
python main.py examples/multi_product_campaign.yaml --verbose
```

**Custom directories**:
```bash
python main.py examples/campaign_brief.yaml --assets-dir ./custom_assets --outputs-dir ./my_outputs
```

## Deployment

### Development Server
```bash
python app.py
```

### Production (Gunicorn)
```bash
gunicorn --bind=0.0.0.0:5000 --reuse-port --workers=4 --threads=2 --timeout=300 app:app
```

**Recommended settings for multi-user support**:
- `--workers=4` - 4 worker processes
- `--threads=2` - 2 threads per worker
- `--timeout=300` - 5-minute timeout for GenAI operations
- Total capacity: 8 concurrent requests per instance

## Troubleshooting

### Images not loading in web preview
**Solution**: Check browser console for CORS errors. Ensure Azure SAS token is valid and has read permissions.

### Text appears in wrong font/missing characters
**Solution**: Ensure required Noto Sans fonts are installed in `/fonts/` directory.

### Version numbers not incrementing
**Solution**: Verify Azure Blob Storage connection and SAS token permissions (read + list).

### "Default campaign loaded from YAML successfully"
**This is normal!** The web form loads defaults from `examples/multi_product_campaign.yaml` on page load.

### GenAI generation failing
**Solution**: 
1. Check `GEMINI_API_KEY` is set correctly
2. Verify API quota/billing status
3. Check fallback `OPENAI_API_KEY` if Gemini fails

### Parallel processing not working
**Solution**: Ensure Python 3.11+ and `concurrent.futures` module is available.

## Limitations & Future Enhancements

### Current Limitations
1. **Multi-session support**: Shared `/outputs/` directory; needs session-based isolation for true concurrent users
2. **Azure race conditions**: `overwrite=True` may cause issues with simultaneous uploads
3. **Local asset storage**: Generated images stored locally before Azure upload
4. **Single Gunicorn worker**: Default config uses 1 worker; recommend 4+ for production

### Planned Enhancements
1. **Session-based file isolation**: Unique directories per user session
2. **Azure conditional uploads**: Use ETag/if-not-exists to prevent race conditions
3. **Direct Azure generation**: Skip local storage, write directly to cloud
4. **Advanced analytics**: Campaign performance tracking and A/B testing
5. **Brand compliance**: Automated logo presence detection and color validation
6. **Legal content filtering**: Regulatory compliance checks and disclaimers

## Performance Notes

- **Parallel processing**: Reduces multi-product generation time by up to 4x
- **Azure caching**: Version queries cached to minimize API calls
- **Font optimization**: Fonts loaded lazily based on detected script
- **Image optimization**: Smart cropping and resizing for optimal file sizes

## License

This is a proof-of-concept implementation for demonstration purposes.

## Contact

For questions or support regarding this implementation, please refer to the project documentation.
