# Creative Automation Pipeline

## Overview
This project is a Python-based creative automation pipeline that leverages Generative AI to produce social ad campaign assets. It functions as both a web application and a command-line tool, designed to automate the creation of localized campaign creatives across multiple products, aspect ratios, and markets. The system aims to accelerate campaign velocity, ensure brand consistency, maximize relevance and personalization, optimize marketing ROI, and provide actionable insights.

## User Preferences
Not specified.

## System Architecture

### UI/UX Decisions
The web interface features a modern, responsive design with a dark, professional theme inspired by creative tools. It utilizes a grid-based layout with a sidebar, main preview area, and a real-time process logs panel. Key UI elements include a visual color picker, Azure Blob Storage integration for image selection with previews, and a redesigned results gallery layout for optimal viewing of different aspect ratios.

### Technical Implementations
The system is built on a modular architecture using Python 3.11 and Flask for the web application. It integrates GenAI for image generation (Google Gemini as primary, OpenAI DALL-E 3 as fallback), Pillow for image processing, and a custom RegionalTranslator for localized messages. Asset management distinguishes between user uploads (preserved) and AI-generated assets (purged for fresh generation). It supports campaign brief parsing from JSON and YAML formats.

### Feature Specifications
- **Campaign Management**: Supports multi-product campaigns with dynamic form fields, including hero image uploads, brand color selection, and logo integration with positioning controls.
- **Asset Generation**: GenAI-powered image generation with multi-aspect ratio support (1:1, 9:16, 16:9) and intelligent asset management (reuse existing, generate missing).
- **Image Processing**: Optimized image resizing with smart cropping (cover/crop mode, smart crop positioning for 16:9, center for 9:16 and 1:1), text overlay, and multi-script font support for multilingual text rendering (Japanese, Korean, Ethiopic, Cyrillic, Latin).
- **Localization**: Automatic translation of campaign messages to regional languages (supporting 10 regions: Japan, South Korea, China, France, Germany, Spain, Italy, Brazil, Russia, Ethiopia) with graceful fallback and intelligent font selection based on script detection.
- **Output & Storage**: Organizes output by product and aspect ratio, provides real-time asset preview and download, and integrates with Azure Blob Storage for cloud uploads.
- **CLI**: A command-line interface provides automation capabilities, mirroring the web application's core functions.

### System Design Choices
- **Modular Architecture**: Ensures maintainability and clear separation of concerns.
- **Auto-Purge Assets**: Clears previous AI-generated assets before each new generation to ensure freshness.
- **Fallback Mechanism**: Prioritizes Google Gemini, then OpenAI DALL-E 3, and finally placeholder images for robust image generation.
- **Extensible Format**: Supports both JSON and YAML for campaign briefs.
- **Smart Text Overlay**: Dynamically sizes and wraps text based on image dimensions for optimal readability.
- **Multi-Script Font Support**: Automatic detection of text script (Ethiopic/Ge'ez, Korean/Hangul, Japanese/Hiragana/Katakana, Chinese/Hanzi, Cyrillic, Latin) with intelligent font selection (Noto Sans Ethiopic 1.1MB, Noto Sans KR 10MB, Noto Sans JP 9.2MB for respective scripts).
- **Brand Logo Features**: Allows users to select and position brand logos from Azure, applying intelligent sizing and padding.
- **Browser Cache Busting**: Implements timestamp-based cache busting to ensure fresh image loading after regeneration.

## External Dependencies
- **GenAI**: Google Gemini (primary), OpenAI DALL-E 3 (fallback)
- **Cloud Storage**: Azure Blob Storage
- **Web Framework**: Flask
- **Image Processing**: Pillow (PIL)
- **Data Serialization**: PyYAML
- **HTTP Requests**: Requests library
- **Environment Variables**: Python-dotenv
- **Web Server Gateway Interface**: Werkzeug