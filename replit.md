# Creative Automation Pipeline

## Overview
This project is a Python-based creative automation pipeline that leverages Generative AI to produce social ad campaign assets. It functions as both a web application and a command-line tool, designed to automate the creation of localized campaign creatives across multiple products, aspect ratios, and markets. The system aims to accelerate campaign velocity, ensure brand consistency, maximize relevance and personalization, optimize marketing ROI, and provide actionable insights.

## User Preferences
Not specified.

## System Architecture

### Content Moderation
The system includes dual-layer AI-based content moderation to ensure brand safety before campaign generation. All user-provided text (campaign messages, product names, product descriptions, and audience fields) is checked using:

**Layer 1 - OpenAI Moderation API** (harmful content):
- Violence and threats
- Self-harm content
- Sexual content
- Hate speech
- Harassment
- Dangerous content

**Layer 2 - Google Perspective API** (toxicity/profanity, 70% threshold):
- Toxicity and severe toxicity
- Identity attacks
- Insults
- Profanity
- Threats

If inappropriate content is detected by either API, the system rejects the campaign with specific feedback indicating which fields were flagged and why. Moderation can be bypassed using the `--skip-moderation` flag in the CLI for testing purposes. The system gracefully handles API failures by continuing without moderation rather than blocking campaign generation.

### UI/UX Decisions
The web interface features a modern, responsive design with a dark, professional theme inspired by creative tools. It utilizes a grid-based layout with a 400px-wide sidebar (for comfortable product name visibility), main preview area, and a real-time process logs panel. Key UI elements include a visual color picker, Azure Blob Storage integration for image selection with previews, an autocomplete dropdown for region selection with all 52 supported regions, a redesigned results gallery layout for optimal viewing of different aspect ratios, product section headers that appear above each product's image gallery for clear organization, and removable brand logo preview with one-click deselection capability.

### Technical Implementations
The system is built on a modular architecture using Python 3.11 and Flask for the web application. It integrates GenAI for image generation (Google Gemini 2.5 Flash Image as primary, OpenAI DALL-E 3 as fallback), Pillow for image processing, and a custom RegionalTranslator for localized messages. Performance is optimized through parallel processing using ThreadPoolExecutor, enabling simultaneous generation of all products for up to 4x speed improvement. Asset management uses Azure-based incremental versioning that queries Azure Blob Storage to preserve version history across sessions (e.g., `product_16x9_v1.png`, `product_16x9_v2.png`), allowing users to build a library of creative variations over time. It supports campaign brief parsing from JSON and YAML formats.

### Feature Specifications
- **Campaign Management**: Supports multi-product campaigns (default: 4 products with character-specific descriptions emphasizing hero model consistency based on Henry Cavill: "Business Casual for a Superman" featuring Superman as Clark in newsroom environment, "Super Suit for a Superman" with Clark as Superman in metropolitan setting, "Business Casual for a Batman" showing Batman as Bruce in Wayne Enterprises corporate office, and "Bat Suit for a Dark Knight" depicting Bruce as Batman in metropolitan environment - all products specify the hero's physical appearance based on the same model, Henry Cavill) with dynamic form fields, hero image uploads from Azure with preview and delete functionality, brand color selection (applied to campaign message text), and logo integration with positioning controls and deselection capability (logos are only applied when explicitly selected for each campaign).
- **Asset Generation**: GenAI-powered image generation with multi-aspect ratio support (1:1, 9:16, 16:9), Azure-based incremental versioning (queries Azure Blob Storage for latest version number and increments, even when local outputs are cleared), and intelligent hero image workflow:
  - **With uploaded hero**: Reuses user-provided image across all outputs (only text overlay changes per region)
  - **Without uploaded hero**: Generates fresh region-specific images via GenAI for each campaign, creating culturally appropriate backgrounds (e.g., Russia scene for Russia, Japan scene for Japan)
- **Image Processing**: Optimized image resizing with smart cropping (cover/crop mode, smart crop positioning for 16:9, center for 9:16 and 1:1), campaign message text overlay with customizable brand color, and multi-script font support for multilingual text rendering (Thai, Arabic, Hebrew, Bengali, Greek, Devanagari, Ethiopic, Korean, Traditional Chinese, Japanese, Cyrillic, Latin).
- **Localization**: **Dynamic translation using Google Cloud Translation API** for campaign messages across 52 global regions:
  1. **Google Cloud Translation API** (dynamic) - Automatic translation of ANY custom message using Google Translate
  2. **English fallback** - Original message if API unavailable or region not mapped
  
  Supports major markets across Asia-Pacific (Japan, South Korea, China, Taiwan, Thailand, Vietnam, Philippines, Singapore, India, Pakistan, Bangladesh, Indonesia, Malaysia, Australia, New Zealand), Middle East & North Africa (Saudi Arabia, UAE, Egypt, Israel, Iran, Morocco, Turkey), Europe (France, Germany, Spain, Italy, UK, Netherlands, Poland, Sweden, Norway, Denmark, Finland, Portugal, Greece, Czech Republic, Romania, Hungary, Russia, Ukraine), Americas (USA, Canada, Mexico, Brazil, Argentina, Colombia, Chile, Peru), and Africa (South Africa, Nigeria, Kenya, Ethiopia). Includes intelligent font selection based on script detection for proper multilingual text rendering.
- **Output & Storage**: Organizes output by product and aspect ratio, provides real-time asset preview and download, and integrates with Azure Blob Storage for cloud uploads. Azure image selectors use intelligent filtering: "Select Logo from Azure" looks exclusively in `assets/logos/`, while "Select Hero from Azure" filters by product (shows only that product's assets if product exists in Azure, otherwise shows all non-logo assets). Generated images are uploaded to Azure under `assets/` with product subfolders, uploading only newly created files to prevent duplicates.
- **CLI**: A command-line interface provides automation capabilities, mirroring the web application's core functions.

### System Design Choices
- **Modular Architecture**: Ensures maintainability and clear separation of concerns.
- **Single Source of Truth**: The `examples/multi_product_campaign.yaml` file serves as the canonical default campaign configuration. Web UI dynamically loads defaults via JavaScript fetch to `/examples` endpoint on page load, populating all form fields (campaign message, region, audience, brand color, and products). HTML contains hardcoded fallback defaults if YAML loading fails. This architecture ensures consistency between web UI and CLI examples while enabling easy default updates through a single YAML file.
- **Parallel Processing**: Utilizes concurrent thread execution to process all products simultaneously, reducing generation time by up to 4x for multi-product campaigns without compromising quality.
- **Azure-Based Incremental Versioning**: Version numbers are determined by querying Azure Blob Storage for the highest existing version, then incrementing. Local outputs folder is cleared on each generation for clean results display, but version history persists in Azure (e.g., v1, v2, v3... continue across sessions). Includes fallback to local versioning if Azure is unavailable.
- **Intelligent Hero Image Logic**: The system distinguishes between user-uploaded hero images (stored in `/assets/input/uploads/`) and AI-generated assets (stored in `/assets/input/generated/`). User uploads are reused across all variants, while missing heroes trigger fresh GenAI generation with region-specific prompts for culturally relevant backgrounds.
- **Organized Asset Storage**: Maintains separate directories for different asset types:
  - `/assets/input/uploads/` - User-uploaded product hero images (reused if present)
  - `/assets/input/generated/` - AI-generated region-specific hero images
  - `/assets/input/logos/` - Brand logos (exclusive source for logo overlays)
  - `/outputs/` - Generated campaign creatives with version numbers
- **Fallback Mechanism**: Prioritizes Google Gemini, then OpenAI DALL-E 3, and finally placeholder images for robust image generation.
- **Extensible Format**: Supports both JSON and YAML for campaign briefs.
- **Smart Text Overlay**: Dynamically sizes and wraps text based on image dimensions for optimal readability.
- **Multi-Script Font Support**: Automatic detection of text script (Thai, Arabic/Persian/Urdu, Hebrew, Bengali, Greek, Devanagari/Hindi, Ethiopic/Ge'ez, Korean/Hangul, Traditional Chinese, Japanese/Hiragana/Katakana, Simplified Chinese/Hanzi, Cyrillic, Latin) with intelligent font selection (Noto Sans Thai 213KB, Noto Sans Arabic 824KB, Noto Sans Hebrew 110KB, Noto Sans Bengali 446KB, Noto Sans Greek 2MB, Noto Sans Devanagari 631KB, Noto Sans Ethiopic 1.1MB, Noto Sans KR 10MB, Noto Sans TC 11.3MB, Noto Sans JP 9.2MB for respective scripts).
- **Brand Logo Features**: Allows users to select, deselect, and position brand logos from Azure, applying intelligent sizing and padding. Automatically converts white backgrounds to transparent for seamless blending with images. Logos are sourced exclusively from the dedicated `/logos/` directory. The system only applies logos when explicitly selected for each campaign, preventing unwanted logo overlay from previous campaigns.
- **Browser Cache Busting**: Implements timestamp-based cache busting to ensure fresh image loading after regeneration.

## External Dependencies
- **GenAI**: Google Gemini (primary), OpenAI DALL-E 3 (fallback)
- **Cloud Storage**: Azure Blob Storage (SAS URL authentication for secure, time-limited access)
- **Web Framework**: Flask
- **Image Processing**: Pillow (PIL)
- **Data Serialization**: PyYAML
- **HTTP Requests**: Requests library
- **Environment Variables**: Python-dotenv
- **Web Server Gateway Interface**: Werkzeug

## Environment Variables
- **GEMINI_API_KEY**: Google Gemini API key for primary image generation
- **OPENAI_API_KEY**: OpenAI API key for fallback image generation and harmful content moderation
- **PERSPECTIVE_API_KEY**: Google Perspective API key for toxicity/profanity detection (optional - recommended for brand safety)
- **GOOGLE_TRANSLATE_API_KEY**: Google Cloud Translation API key for dynamic translation of custom campaign messages (optional - falls back to hardcoded translations)
- **AZURE_STORAGE_SAS_URL**: Azure Blob Storage SAS URL (format: `https://account.blob.core.windows.net/container?sp=...&sig=...`)
- **AZURE_CONTAINER_NAME**: Override container name from SAS URL (default: `campaign-assets`)
- **AZURE_UPLOAD_ENABLED**: Enable/disable Azure uploads (default: `true`)
- **SESSION_SECRET**: Flask session secret for web application security