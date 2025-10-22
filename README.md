# Creative Automation Pipeline

A proof-of-concept creative automation pipeline that generates social ad campaign assets using GenAI. This system automates the creation of localized campaign creatives for multiple products, aspect ratios, and markets.

**Available as both a Web Application and Command-Line Tool!**

## Features

- **🌐 Web Interface**: Modern, intuitive web UI for easy campaign creation and asset preview
- **💻 CLI Tool**: Command-line interface for automation and batch processing
- **Campaign Brief Management**: Accept campaign briefs in JSON or YAML format
- **Multi-Product Support**: Generate creatives for multiple products in a single campaign
- **Intelligent Asset Management**: Reuse existing assets when available, generate new ones when needed
- **GenAI Image Generation**: Integrate with OpenAI DALL-E for automated image creation
- **Multi-Aspect Ratio Support**: Generate creatives for 1:1, 9:16, and 16:9 aspect ratios
- **Text Overlay System**: Automatically add campaign messages to creatives with proper formatting
- **Organized Output**: Systematically organize outputs by product and aspect ratio
- **Localization Ready**: Support for localized campaign messages (with extensibility for full localization)

## Project Structure

```
creative-automation-pipeline/
├── app.py                      # Flask web application
├── main.py                     # CLI entry point
├── src/
│   ├── __init__.py
│   ├── config.py               # Configuration and constants
│   ├── brief_parser.py         # Campaign brief parsing (JSON/YAML)
│   ├── asset_manager.py        # Asset discovery and management
│   ├── image_generator.py      # GenAI image generation (OpenAI DALL-E)
│   ├── image_processor.py      # Image resizing and text overlay
│   └── pipeline.py             # Main pipeline orchestrator
├── templates/
│   └── index.html              # Web interface template
├── static/
│   └── css/
│       └── style.css           # Web interface styling
├── examples/
│   ├── campaign_brief.yaml     # Example YAML campaign brief
│   ├── campaign_brief.json     # Example JSON campaign brief
│   └── multi_product_campaign.yaml
├── assets/
│   └── input/                  # Input assets directory
├── outputs/                    # Generated creatives output
└── README.md
```

## Requirements

- Python 3.11+
- Dependencies (see pyproject.toml):
  - Flask (web framework)
  - Pillow (image processing)
  - PyYAML (YAML parsing)
  - requests (HTTP requests)
  - openai (OpenAI API integration)
  - python-dotenv (environment management)

## Installation

1. **Clone or download this project**

2. **Install dependencies**:
   ```bash
   pip install flask pillow pyyaml requests openai python-dotenv
   ```
   
   Or if using uv (Replit environment):
   ```bash
   uv pip install flask pillow pyyaml requests openai python-dotenv
   ```

3. **Configure OpenAI API Key** (optional, for GenAI image generation):
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```
   
   If no API key is provided, the system will generate placeholder images instead.

## Usage

### Option 1: Web Interface (Recommended)

The easiest way to use the Creative Automation Pipeline is through the web interface.

1. **Start the web server**:
   ```bash
   python app.py
   ```

2. **Open your browser** and navigate to `http://localhost:5000`

3. **Create your campaign**:
   - Fill in the campaign details (region, audience, message)
   - Add at least 2 products with descriptions
   - Click "Generate Campaign Assets"
   - View and download your generated creatives!

4. **Load Examples**: Use the "Load Example" buttons to see pre-configured campaigns

### Option 2: Command-Line Interface

For automation and batch processing, use the CLI tool.

**Basic Usage**

Run the pipeline with a campaign brief:

```bash
python main.py examples/campaign_brief.yaml
```

### Command-Line Options

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

**Example 1: Run with YAML brief**
```bash
python main.py examples/campaign_brief.yaml
```

**Example 2: Run with JSON brief and verbose logging**
```bash
python main.py examples/campaign_brief.json --verbose
```

**Example 3: Custom asset and output directories**
```bash
python main.py examples/campaign_brief.yaml --assets-dir ./my_assets --outputs-dir ./my_outputs
```

## Campaign Brief Format

### YAML Format

```yaml
region: "North America"
audience: "Health-conscious millennials aged 25-40"
message: "Transform Your Morning Routine"

products:
  - name: "Premium Green Tea"
    description: "Organic premium green tea in elegant packaging"
    
  - name: "Protein Energy Bar"
    description: "High-protein energy bar with natural ingredients"

localized_messages:
  en: "Transform Your Morning Routine"
  es: "Transforma Tu Rutina Matutina"
  fr: "Transformez Votre Routine Matinale"
```

### JSON Format

```json
{
  "region": "Europe",
  "audience": "Tech-savvy professionals aged 30-50",
  "message": "Elevate Your Workspace Experience",
  "products": [
    {
      "name": "Wireless Ergonomic Mouse",
      "description": "Premium wireless ergonomic mouse with precision tracking"
    },
    {
      "name": "Mechanical Keyboard",
      "description": "Professional mechanical keyboard with RGB lighting"
    }
  ],
  "localized_messages": {
    "en": "Elevate Your Workspace Experience",
    "de": "Verbessern Sie Ihr Arbeitsplatzerlebnis"
  }
}
```

### Required Fields

- **products** (array, min 2): List of products with `name` and optional `description`
- **message** (string): Primary campaign message
- **region** (string, optional): Target market/region
- **audience** (string, optional): Target audience description
- **localized_messages** (object, optional): Localized versions of the message

## Asset Management

The pipeline intelligently manages assets:

1. **Existing Assets**: If an asset exists in `assets/input/` with a matching product name (e.g., `premium_green_tea.jpg`), it will be reused.

2. **Generated Assets**: If no matching asset is found, the system generates one using GenAI based on the product name and description.

3. **Asset Naming Convention**: 
   - Normalize product names (lowercase, underscores)
   - Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`
   - Example: "Premium Green Tea" → `premium_green_tea.jpg`

## Output Organization

Generated creatives are organized by product and aspect ratio:

```
outputs/
├── premium_green_tea/
│   ├── premium_green_tea_1x1.png
│   ├── premium_green_tea_9x16.png
│   └── premium_green_tea_16x9.png
├── protein_energy_bar/
│   ├── protein_energy_bar_1x1.png
│   ├── protein_energy_bar_9x16.png
│   └── protein_energy_bar_16x9.png
└── ...
```

## Aspect Ratios

The pipeline generates creatives in three standard aspect ratios:

- **1:1** (1080x1080) - Instagram posts, Facebook posts
- **9:16** (1080x1920) - Instagram/TikTok Stories, Reels
- **16:9** (1920x1080) - YouTube, landscape videos

## Key Design Decisions

### 1. Modular Architecture
The system is designed with clear separation of concerns:
- **Brief Parser**: Handles input validation and parsing
- **Asset Manager**: Manages asset discovery and storage
- **Image Generator**: Interfaces with GenAI services
- **Image Processor**: Handles resizing and text overlay
- **Pipeline Orchestrator**: Coordinates the entire workflow

### 2. Asset Reusability
To optimize costs and time, the system always checks for existing assets before generating new ones. This is particularly important for:
- Recurring campaigns
- Localized variants of the same product
- A/B testing scenarios

### 3. GenAI Integration
The system integrates with OpenAI DALL-E 3 for image generation but includes a fallback to placeholder images if:
- No API key is configured
- API calls fail
- Cost control is needed for testing

### 4. Text Overlay System
Text is added with:
- Automatic text wrapping based on image width
- Shadow effects for readability on any background
- Dynamic font sizing based on image dimensions
- Centered positioning with proper padding

### 5. Error Handling
The pipeline includes comprehensive error handling:
- Input validation for campaign briefs
- Graceful fallbacks for failed image generation
- Detailed logging for debugging
- Clear error messages for users

## Assumptions and Limitations

### Assumptions
1. **Input Format**: Campaign briefs are well-formed JSON or YAML
2. **Product Count**: Minimum 2 products per campaign (as per requirements)
3. **Asset Quality**: Input assets are of sufficient quality for social media
4. **Font Availability**: System has common fonts (DejaVu, Liberation) installed
5. **Message Language**: Primary message is in English (localized versions supported but not auto-translated)

### Current Limitations
1. **Image Generation**: Requires OpenAI API key for actual GenAI; falls back to placeholders otherwise
2. **Text Localization**: Accepts localized messages but doesn't auto-translate
3. **Brand Compliance**: Not implemented in this POC (future enhancement)
4. **Legal Checks**: Not implemented in this POC (future enhancement)
5. **Storage Integration**: Uses local filesystem; cloud storage integration not included
6. **Performance Tracking**: No analytics or performance metrics included
7. **Batch Processing**: Processes one campaign at a time

## Future Enhancements

### Nice-to-Have Features (Next Phase)
1. **Brand Compliance Checks**
   - Logo presence detection
   - Brand color validation
   - Font compliance verification

2. **Legal Content Filtering**
   - Prohibited words detection
   - Regulatory compliance checks
   - Disclaimer requirements

3. **Advanced Localization**
   - Automatic translation integration
   - Cultural adaptation (images, colors)
   - Regional regulations compliance

4. **Performance Analytics**
   - Campaign tracking dashboard
   - A/B testing support
   - ROI metrics

5. **Cloud Storage Integration**
   - Azure Blob Storage
   - AWS S3
   - Dropbox Business

6. **Batch Processing**
   - Multiple campaigns simultaneously
   - Queue management
   - Priority handling

## Logging

The pipeline generates detailed logs:
- **Console Output**: Real-time progress and results
- **pipeline.log**: Detailed log file for debugging

Enable verbose logging with the `-v` flag for more detailed information.

## Troubleshooting

### Issue: "No module named 'src'"
**Solution**: Run from the project root directory

### Issue: GenAI images not generating
**Solution**: Check that your `OPENAI_API_KEY` is set correctly in `.env`

### Issue: Text not appearing on images
**Solution**: Ensure system fonts are installed (DejaVu or Liberation fonts)

### Issue: "Campaign brief must include at least two products"
**Solution**: Add at least 2 products to your campaign brief

## Example Workflow

1. **Prepare your campaign brief** (YAML or JSON)
2. **Add existing assets** (optional) to `assets/input/`
3. **Run the pipeline**: `python main.py examples/campaign_brief.yaml`
4. **Review outputs** in the `outputs/` directory
5. **Check logs** in `pipeline.log` for detailed execution info

## License

This is a proof-of-concept implementation for demonstration purposes.

## Contact

For questions or support regarding this implementation, please refer to the project documentation.
