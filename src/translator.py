"""Regional language translation for campaign messages"""
import logging
from typing import Optional
from google.cloud import translate_v2 as translate
import google.auth.api_key

from .config import GOOGLE_TRANSLATE_API_KEY

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
        "Ukraine": {
            "Clothes that make the man": "Одяг робить людину",
            "Experience the pure, natural glow. Your skin deserves it": "Відчуйте чисте, природне сяйво. Ваша шкіра на це заслуговує",
        },
        "Ethiopia": {
            "Clothes that make the man": "ልብስ ሰውን ያደርጋል",
            "Experience the pure, natural glow. Your skin deserves it": "ንጹህ እና ተፈጥሯዊ ብሩህነትን ይለማመዱ። ቆዳዎ ይገባዋል",
        },
        "India": {
            "Clothes that make the man": "कपड़े आदमी बनाते हैं",
            "Experience the pure, natural glow. Your skin deserves it": "शुद्ध, प्राकृतिक चमक का अनुभव करें। आपकी त्वचा इसकी हकदार है",
        },
        "Indonesia": {
            "Clothes that make the man": "Pakaian membuat orang",
            "Experience the pure, natural glow. Your skin deserves it": "Rasakan cahaya alami yang murni. Kulit Anda layak mendapatkannya",
        },
        "Malaysia": {
            "Clothes that make the man": "Pakaian membentuk seseorang",
            "Experience the pure, natural glow. Your skin deserves it": "Rasai cahaya semula jadi yang tulen. Kulit anda layak mendapatnya",
        },
        "Taiwan": {
            "Clothes that make the man": "人要衣裝",
            "Experience the pure, natural glow. Your skin deserves it": "體驗純淨自然的光澤。你的肌膚值得擁有",
        },
        "Thailand": {
            "Clothes that make the man": "เสื้อผ้าทำให้คน",
            "Experience the pure, natural glow. Your skin deserves it": "สัมผัสความเปล่งประกายบริสุทธิ์ตามธรรมชาติ ผิวของคุณสมควรได้รับมัน",
        },
        "Vietnam": {
            "Clothes that make the man": "Quần áo làm nên con người",
            "Experience the pure, natural glow. Your skin deserves it": "Trải nghiệm vẻ rạng ngời thuần khiết tự nhiên. Làn da của bạn xứng đáng có nó",
        },
        "Philippines": {
            "Clothes that make the man": "Ang damit ay gumagawa ng tao",
            "Experience the pure, natural glow. Your skin deserves it": "Maranasan ang purong, natural na kinang. Nararapat ito sa iyong balat",
        },
        "Singapore": {
            "Clothes that make the man": "Clothes make the man",
            "Experience the pure, natural glow. Your skin deserves it": "Experience the pure, natural glow. Your skin deserves it",
        },
        "Pakistan": {
            "Clothes that make the man": "لباس آدمی بناتا ہے",
            "Experience the pure, natural glow. Your skin deserves it": "خالص، قدرتی چمک کا تجربہ کریں۔ آپ کی جلد اس کی مستحق ہے",
        },
        "Bangladesh": {
            "Clothes that make the man": "পোশাক মানুষকে তৈরি করে",
            "Experience the pure, natural glow. Your skin deserves it": "বিশুদ্ধ, প্রাকৃতিক উজ্জ্বলতা অনুভব করুন। আপনার ত্বক এটি প্রাপ্য",
        },
        "Egypt": {
            "Clothes that make the man": "الملابس تصنع الرجل",
            "Experience the pure, natural glow. Your skin deserves it": "اختبر التوهج النقي والطبيعي. بشرتك تستحق ذلك",
        },
        "Saudi Arabia": {
            "Clothes that make the man": "الملابس تصنع الرجل",
            "Experience the pure, natural glow. Your skin deserves it": "اختبر التوهج النقي والطبيعي. بشرتك تستحق ذلك",
        },
        "UAE": {
            "Clothes that make the man": "الملابس تصنع الرجل",
            "Experience the pure, natural glow. Your skin deserves it": "اختبر التوهج النقي والطبيعي. بشرتك تستحق ذلك",
        },
        "Turkey": {
            "Clothes that make the man": "İnsan kıyafetinden belli olur",
            "Experience the pure, natural glow. Your skin deserves it": "Saf, doğal parlaklığı deneyimleyin. Cildiniz bunu hak ediyor",
        },
        "Israel": {
            "Clothes that make the man": "הבגדים עושים את האדם",
            "Experience the pure, natural glow. Your skin deserves it": "חוו את הזוהר הטהור והטבעי. העור שלכם ראוי לכך",
        },
        "Iran": {
            "Clothes that make the man": "لباس آدم را می‌سازد",
            "Experience the pure, natural glow. Your skin deserves it": "درخشش خالص و طبیعی را تجربه کنید. پوست شما شایسته آن است",
        },
        "Mexico": {
            "Clothes that make the man": "El hábito hace al monje",
            "Experience the pure, natural glow. Your skin deserves it": "Experimenta el brillo puro y natural. Tu piel lo merece",
        },
        "Argentina": {
            "Clothes that make the man": "La ropa hace al hombre",
            "Experience the pure, natural glow. Your skin deserves it": "Experimentá el brillo puro y natural. Tu piel lo merece",
        },
        "Colombia": {
            "Clothes that make the man": "El hábito hace al monje",
            "Experience the pure, natural glow. Your skin deserves it": "Experimenta el brillo puro y natural. Tu piel lo merece",
        },
        "Chile": {
            "Clothes that make the man": "El hábito hace al monje",
            "Experience the pure, natural glow. Your skin deserves it": "Experimenta el brillo puro y natural. Tu piel lo merece",
        },
        "Peru": {
            "Clothes that make the man": "El hábito hace al monje",
            "Experience the pure, natural glow. Your skin deserves it": "Experimenta el brillo puro y natural. Tu piel lo merece",
        },
        "Netherlands": {
            "Clothes that make the man": "Kleren maken de man",
            "Experience the pure, natural glow. Your skin deserves it": "Ervaar de pure, natuurlijke gloed. Je huid verdient het",
        },
        "Poland": {
            "Clothes that make the man": "Ubiór czyni człowieka",
            "Experience the pure, natural glow. Your skin deserves it": "Doświadcz czystego, naturalnego blasku. Twoja skóra na to zasługuje",
        },
        "Sweden": {
            "Clothes that make the man": "Kläder gör mannen",
            "Experience the pure, natural glow. Your skin deserves it": "Upplev den rena, naturliga glöden. Din hud förtjänar det",
        },
        "Norway": {
            "Clothes that make the man": "Klær skaper mannen",
            "Experience the pure, natural glow. Your skin deserves it": "Opplev den rene, naturlige glansen. Huden din fortjener det",
        },
        "Denmark": {
            "Clothes that make the man": "Klæder gør manden",
            "Experience the pure, natural glow. Your skin deserves it": "Oplev den rene, naturlige glød. Din hud fortjener det",
        },
        "Finland": {
            "Clothes that make the man": "Vaatteet tekevät miehen",
            "Experience the pure, natural glow. Your skin deserves it": "Koe puhdas, luonnollinen hehku. Ihosi ansaitsee sen",
        },
        "Portugal": {
            "Clothes that make the man": "O hábito faz o monge",
            "Experience the pure, natural glow. Your skin deserves it": "Experimente o brilho puro e natural. A sua pele merece",
        },
        "Greece": {
            "Clothes that make the man": "Τα ρούχα κάνουν τον άνθρωπο",
            "Experience the pure, natural glow. Your skin deserves it": "Ζήστε την καθαρή, φυσική λάμψη. Το δέρμα σας το αξίζει",
        },
        "Czech Republic": {
            "Clothes that make the man": "Šaty dělají člověka",
            "Experience the pure, natural glow. Your skin deserves it": "Zažijte čistou, přírodní záři. Vaše pokožka si to zaslouží",
        },
        "Romania": {
            "Clothes that make the man": "Haina îl face pe om",
            "Experience the pure, natural glow. Your skin deserves it": "Experimentează strălucirea pură și naturală. Pielea ta merită",
        },
        "Hungary": {
            "Clothes that make the man": "A ruha teszi az embert",
            "Experience the pure, natural glow. Your skin deserves it": "Tapasztald meg a tiszta, természetes ragyogást. A bőröd megérdemli",
        },
        "South Africa": {
            "Clothes that make the man": "Clothes make the man",
            "Experience the pure, natural glow. Your skin deserves it": "Experience the pure, natural glow. Your skin deserves it",
        },
        "Nigeria": {
            "Clothes that make the man": "Clothes make the man",
            "Experience the pure, natural glow. Your skin deserves it": "Experience the pure, natural glow. Your skin deserves it",
        },
        "Kenya": {
            "Clothes that make the man": "Clothes make the man",
            "Experience the pure, natural glow. Your skin deserves it": "Experience the pure, natural glow. Your skin deserves it",
        },
        "Morocco": {
            "Clothes that make the man": "الملابس تصنع الرجل",
            "Experience the pure, natural glow. Your skin deserves it": "اختبر التوهج النقي والطبيعي. بشرتك تستحق ذلك",
        },
        "Australia": {
            "Clothes that make the man": "Clothes make the man",
            "Experience the pure, natural glow. Your skin deserves it": "Experience the pure, natural glow. Your skin deserves it",
        },
        "New Zealand": {
            "Clothes that make the man": "Clothes make the man",
            "Experience the pure, natural glow. Your skin deserves it": "Experience the pure, natural glow. Your skin deserves it",
        },
        "Canada": {
            "Clothes that make the man": "Clothes make the man",
            "Experience the pure, natural glow. Your skin deserves it": "Experience the pure, natural glow. Your skin deserves it",
        },
        "USA": {
            "Clothes that make the man": "Clothes make the man",
            "Experience the pure, natural glow. Your skin deserves it": "Experience the pure, natural glow. Your skin deserves it",
        },
        "UK": {
            "Clothes that make the man": "Clothes make the man",
            "Experience the pure, natural glow. Your skin deserves it": "Experience the pure, natural glow. Your skin deserves it",
        },
    }
    
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
        with fallback to hardcoded translations
        
        Translation strategy:
        1. Try hardcoded translations (instant, high-quality for known messages)
        2. Try Google Cloud Translation API (dynamic, works for any message)
        3. Fallback to English (if API unavailable or region not mapped)
        
        Args:
            message: Original message in English
            region: Target region (e.g., "Japan", "France")
            
        Returns:
            Translated message or original if translation not available
        """
        region = region.strip()
        
        # Strategy 1: Check hardcoded translations first (instant, no API cost)
        if region in cls.TRANSLATIONS:
            region_translations = cls.TRANSLATIONS[region]
            if message in region_translations:
                translated = region_translations[message]
                logger.info(f"[Hardcoded] Translated '{message}' to {region}: '{translated}'")
                return translated
        
        # Strategy 2: Try Google Cloud Translation API for dynamic translation
        if region in cls.REGION_TO_LANGUAGE:
            target_language = cls.REGION_TO_LANGUAGE[region]
            
            # Skip API call if target language is English
            if target_language == "en":
                logger.info(f"[English region] No translation needed for {region}")
                return message
            
            api_translation = cls._translate_with_api(message, target_language)
            if api_translation:
                return api_translation
        
        # Strategy 3: Fallback to English
        logger.info(f"No translation available for '{message}' in region '{region}', using original")
        return message
    
    @classmethod
    def get_supported_regions(cls) -> list:
        """Get list of regions with translation support"""
        return list(cls.TRANSLATIONS.keys())
