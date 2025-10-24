"""Regional language translation for campaign messages"""
import logging

logger = logging.getLogger(__name__)


class RegionalTranslator:
    """Translates campaign messages to regional languages"""
    
    # Translation dictionary for common regions and messages
    TRANSLATIONS = {
        "Japan": {
            "Clothes that make the man": "服が人をつくる",
            "Experience the pure, natural glow. Your skin deserves it": "純粋で自然な輝きを体験してください。あなたの肌はそれに値します",
        },
        "France": {
            "Clothes that make the man": "L'habit fait le moine",
            "Experience the pure, natural glow. Your skin deserves it": "Découvrez l'éclat pur et naturel. Votre peau le mérite",
        },
        "Spain": {
            "Clothes that make the man": "El hábito hace al monje",
            "Experience the pure, natural glow. Your skin deserves it": "Experimenta el brillo puro y natural. Tu piel lo merece",
        },
        "Germany": {
            "Clothes that make the man": "Kleider machen Leute",
            "Experience the pure, natural glow. Your skin deserves it": "Erleben Sie den reinen, natürlichen Glanz. Ihre Haut verdient es",
        },
        "China": {
            "Clothes that make the man": "人靠衣装",
            "Experience the pure, natural glow. Your skin deserves it": "体验纯净自然的光泽。你的皮肤值得拥有",
        },
        "South Korea": {
            "Clothes that make the man": "옷이 날개다",
            "Experience the pure, natural glow. Your skin deserves it": "순수하고 자연스러운 빛을 경험하세요. 당신의 피부는 그럴 자격이 있습니다",
        },
        "Italy": {
            "Clothes that make the man": "L'abito fa il monaco",
            "Experience the pure, natural glow. Your skin deserves it": "Prova la luminosità pura e naturale. La tua pelle lo merita",
        },
        "Brazil": {
            "Clothes that make the man": "As roupas fazem o homem",
            "Experience the pure, natural glow. Your skin deserves it": "Experimente o brilho puro e natural. Sua pele merece",
        },
        "Russia": {
            "Clothes that make the man": "Встречают по одёжке",
            "Experience the pure, natural glow. Your skin deserves it": "Почувствуйте чистое, естественное сияние. Ваша кожа этого заслуживает",
        },
        "Ethiopia": {
            "Clothes that make the man": "ልብስ ሰውን ያደርጋል",
            "Experience the pure, natural glow. Your skin deserves it": "ንጹህ እና ተፈጥሯዊ ብሩህነትን ይለማመዱ። ቆዳዎ ይገባዋል",
        },
    }
    
    @classmethod
    def translate(cls, message: str, region: str) -> str:
        """
        Translate message to regional language
        
        Args:
            message: Original message in English
            region: Target region (e.g., "Japan", "France")
            
        Returns:
            Translated message or original if translation not available
        """
        region = region.strip()
        
        # Check if we have a translation for this region
        if region in cls.TRANSLATIONS:
            region_translations = cls.TRANSLATIONS[region]
            
            # Check if we have this specific message translated
            if message in region_translations:
                translated = region_translations[message]
                logger.info(f"Translated '{message}' to {region}: '{translated}'")
                return translated
        
        # Return original message if no translation available
        logger.info(f"No translation available for '{message}' in region '{region}', using original")
        return message
    
    @classmethod
    def get_supported_regions(cls) -> list:
        """Get list of regions with translation support"""
        return list(cls.TRANSLATIONS.keys())
