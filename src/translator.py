"""Regional language translation for campaign messages"""
import logging
from typing import Optional
from google.cloud import translate_v2 as translate
import google.auth.api_key

from .config import GOOGLE_TRANSLATE_API_KEY

logger = logging.getLogger(__name__)


class RegionalTranslator:
    """Translates campaign messages to regional languages using Google Cloud Translation API"""
    
    # Region to ISO 639-1 language code mapping
    REGION_TO_LANGUAGE = {
        "Japan": "ja",
        "France": "fr",
        "Spain": "es",
        "Germany": "de",
        "China": "zh-CN",
        "South Korea": "ko",
        "Italy": "it",
        "Brazil": "pt",
        "Russia": "ru",
        "Ukraine": "uk",
        "Ethiopia": "am",
        "India": "hi",
        "Indonesia": "id",
        "Malaysia": "ms",
        "Taiwan": "zh-TW",
        "Thailand": "th",
        "Vietnam": "vi",
        "Philippines": "tl",
        "Singapore": "en",
        "Pakistan": "ur",
        "Bangladesh": "bn",
        "Egypt": "ar",
        "Saudi Arabia": "ar",
        "UAE": "ar",
        "Turkey": "tr",
        "Israel": "he",
        "Iran": "fa",
        "Mexico": "es",
        "Argentina": "es",
        "Colombia": "es",
        "Chile": "es",
        "Peru": "es",
        "Netherlands": "nl",
        "Poland": "pl",
        "Sweden": "sv",
        "Norway": "no",
        "Denmark": "da",
        "Finland": "fi",
        "Portugal": "pt",
        "Greece": "el",
        "Czech Republic": "cs",
        "Romania": "ro",
        "Hungary": "hu",
        "South Africa": "en",
        "Nigeria": "en",
        "Kenya": "en",
        "Morocco": "ar",
        "Australia": "en",
        "New Zealand": "en",
        "Canada": "en",
        "USA": "en",
        "UK": "en",
    }
    
    _translate_client: Optional[translate.Client] = None
    
    @classmethod
    def _get_translate_client(cls) -> Optional[translate.Client]:
        """Get or create Google Translate API client"""
        if cls._translate_client is None and GOOGLE_TRANSLATE_API_KEY:
            try:
                credentials = google.auth.api_key.Credentials(GOOGLE_TRANSLATE_API_KEY)
                cls._translate_client = translate.Client(credentials=credentials)
                logger.info("Google Cloud Translation API client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Translate client: {e}")
                return None
        return cls._translate_client
    
    @classmethod
    def _translate_with_api(cls, message: str, target_language: str) -> Optional[str]:
        """Translate message using Google Cloud Translation API"""
        client = cls._get_translate_client()
        if not client:
            return None
        
        try:
            result = client.translate(message, target_language=target_language, source_language='en')
            translated_text = result['translatedText']
            logger.info(f"API translated '{message}' to {target_language}: '{translated_text}'")
            return translated_text
        except Exception as e:
            logger.warning(f"Google Translate API error for {target_language}: {e}")
            return None
    
    @classmethod
    def translate(cls, message: str, region: str) -> str:
        """
        Translate message to regional language using Google Cloud Translation API
        
        Translation strategy:
        1. Try Google Cloud Translation API (dynamic translation for any message)
        2. Fallback to English (if API unavailable or region not mapped)
        
        Args:
            message: Original message in English
            region: Target region (e.g., "Japan", "France")
            
        Returns:
            Translated message or original if translation not available
        """
        region = region.strip()
        
        # Check if region has language mapping
        if region in cls.REGION_TO_LANGUAGE:
            target_language = cls.REGION_TO_LANGUAGE[region]
            
            # Skip API call if target language is English
            if target_language == "en":
                logger.info(f"[English region] No translation needed for {region}")
                return message
            
            # Try Google Cloud Translation API
            api_translation = cls._translate_with_api(message, target_language)
            if api_translation:
                return api_translation
        
        # Fallback to English
        logger.info(f"No translation available for '{message}' in region '{region}', using original")
        return message
    
    @classmethod
    def get_supported_regions(cls) -> list:
        """Get list of regions with translation support"""
        return list(cls.REGION_TO_LANGUAGE.keys())
