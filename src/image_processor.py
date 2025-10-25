from PIL import Image, ImageDraw, ImageFont, ImageFilter
from pathlib import Path
from typing import Tuple, Optional, Union
import logging

logger = logging.getLogger(__name__)


class ImageProcessor:
    def __init__(self):
        self.default_font_size = 72
        self.text_color = (255, 255, 255)
        self.text_shadow_color = (0, 0, 0)
        self.text_padding = 50
    
    def resize_to_aspect_ratio(self, image: Image.Image, target_size: Tuple[int, int]) -> Image.Image:
        """Resize and crop image to fill target dimensions completely (cover mode with smart positioning)"""
        target_width, target_height = target_size
        original_width, original_height = image.size
        
        # Calculate scaling factor to cover entire frame
        width_ratio = target_width / original_width
        height_ratio = target_height / original_height
        scale_factor = max(width_ratio, height_ratio)  # Use max to ensure full coverage
        
        # Calculate new dimensions that will cover the target
        new_width = int(original_width * scale_factor)
        new_height = int(original_height * scale_factor)
        
        # Resize image to cover target dimensions
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Smart crop positioning based on aspect ratio
        # For landscape (16:9): bias toward top to preserve heads
        # For portrait (9:16): center horizontally
        # For square (1:1): center both ways
        
        left = (new_width - target_width) // 2  # Center horizontally by default
        
        if target_width > target_height:
            # Landscape format (16:9) - anchor at top to prevent head cropping
            top = 0  # Anchor at top edge to preserve heads/faces
        else:
            # Portrait or square - center vertically
            top = (new_height - target_height) // 2
        
        right = left + target_width
        bottom = top + target_height
        
        # Crop to exact target dimensions
        cropped = resized.crop((left, top, right, bottom))
        
        logger.info(f"Resized image from {image.size} to {cropped.size} (cover mode, smart crop)")
        return cropped
    
    def add_text_overlay(self, image: Image.Image, text: str, position: str = "bottom", region: Optional[str] = None) -> Image.Image:
        img_copy = image.copy()
        draw = ImageDraw.Draw(img_copy)
        
        width, height = img_copy.size
        
        # Auto-detect CJK from text content or region
        font = self._get_font(width, text=text, region=region)
        
        lines = self._wrap_text(text, font, width - (2 * self.text_padding), draw)
        
        line_height = self._get_line_height(font, draw)
        total_text_height = len(lines) * line_height
        
        if position == "bottom":
            y = height - total_text_height - self.text_padding
        elif position == "top":
            y = self.text_padding
        else:
            y = (height - total_text_height) // 2
        
        overlay = Image.new('RGBA', img_copy.size, (0, 0, 0, 0))
        overlay_draw = ImageDraw.Draw(overlay)
        
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (width - text_width) // 2
            
            for offset_x in [-2, 0, 2]:
                for offset_y in [-2, 0, 2]:
                    if offset_x != 0 or offset_y != 0:
                        overlay_draw.text(
                            (x + offset_x, y + offset_y),
                            line,
                            font=font,
                            fill=(*self.text_shadow_color, 180)
                        )
            
            overlay_draw.text((x, y), line, font=font, fill=(*self.text_color, 255))
            y += line_height
        
        img_copy = Image.alpha_composite(img_copy.convert('RGBA'), overlay)
        img_copy = img_copy.convert('RGB')
        
        logger.info(f"Added text overlay: {text[:30]}...")
        return img_copy
    
    def add_logo_overlay(
        self, 
        image: Image.Image, 
        logo: Image.Image, 
        position: str = "top-left",
        size_ratio: float = 0.15,
        padding: int = 30
    ) -> Image.Image:
        """
        Add brand logo overlay to image at specified corner position
        
        Args:
            image: Base image to add logo to
            logo: Logo image to overlay
            position: One of: "top-left", "top-right", "bottom-left", "bottom-right"
            size_ratio: Logo size relative to image width (default 0.15 = 15%)
            padding: Padding from edges in pixels
        """
        img_copy = image.copy().convert('RGBA')
        
        # Calculate logo dimensions (maintain aspect ratio)
        img_width, img_height = img_copy.size
        logo_max_width = int(img_width * size_ratio)
        
        # Resize logo maintaining aspect ratio
        logo_aspect = logo.width / logo.height
        logo_width = logo_max_width
        logo_height = int(logo_width / logo_aspect)
        
        # Resize logo
        logo_resized = logo.convert('RGBA').resize(
            (logo_width, logo_height),
            Image.Resampling.LANCZOS
        )
        
        # Make white/near-white pixels transparent for better blending
        logo_data = list(logo_resized.getdata())
        new_logo_data = []
        for pixel in logo_data:
            r, g, b, a = pixel
            # Check if pixel is white or very close to white (RGB values > 240)
            if r > 240 and g > 240 and b > 240:
                # Make it fully transparent
                new_logo_data.append((r, g, b, 0))
            else:
                # Keep original pixel with its alpha
                new_logo_data.append((r, g, b, a))
        
        logo_resized.putdata(new_logo_data)
        logger.info("Applied white-to-transparent conversion for logo background")
        
        # Calculate position coordinates
        if position == "top-left":
            x, y = padding, padding
        elif position == "top-right":
            x, y = img_width - logo_width - padding, padding
        elif position == "bottom-left":
            x, y = padding, img_height - logo_height - padding
        elif position == "bottom-right":
            x, y = img_width - logo_width - padding, img_height - logo_height - padding
        else:
            # Default to top-left if invalid position
            x, y = padding, padding
            logger.warning(f"Invalid logo position '{position}', using top-left")
        
        logger.info(f"Logo positioning: position={position}, image_size=({img_width}x{img_height}), logo_size=({logo_width}x{logo_height}), coordinates=({x},{y})")
        
        # Paste logo with alpha channel
        img_copy.paste(logo_resized, (x, y), logo_resized)
        
        # Convert back to RGB
        img_copy = img_copy.convert('RGB')
        
        logger.info(f"Added logo overlay at position: {position} ({logo_width}x{logo_height}px at {x},{y})")
        return img_copy
    
    def _detect_thai_text(self, text: str) -> bool:
        """Detect if text contains Thai characters"""
        if not text:
            return False
        for char in text:
            code = ord(char)
            if 0x0E00 <= code <= 0x0E7F:  # Thai
                return True
        return False
    
    def _detect_arabic_text(self, text: str) -> bool:
        """Detect if text contains Arabic/Persian/Urdu characters"""
        if not text:
            return False
        for char in text:
            code = ord(char)
            if (0x0600 <= code <= 0x06FF or   # Arabic
                0x0750 <= code <= 0x077F or   # Arabic Supplement
                0x08A0 <= code <= 0x08FF or   # Arabic Extended-A
                0xFB50 <= code <= 0xFDFF or   # Arabic Presentation Forms-A
                0xFE70 <= code <= 0xFEFF):    # Arabic Presentation Forms-B
                return True
        return False
    
    def _detect_hebrew_text(self, text: str) -> bool:
        """Detect if text contains Hebrew characters"""
        if not text:
            return False
        for char in text:
            code = ord(char)
            if (0x0590 <= code <= 0x05FF or   # Hebrew
                0xFB1D <= code <= 0xFB4F):    # Hebrew Presentation Forms
                return True
        return False
    
    def _detect_bengali_text(self, text: str) -> bool:
        """Detect if text contains Bengali characters"""
        if not text:
            return False
        for char in text:
            code = ord(char)
            if 0x0980 <= code <= 0x09FF:  # Bengali
                return True
        return False
    
    def _detect_greek_text(self, text: str) -> bool:
        """Detect if text contains Greek characters"""
        if not text:
            return False
        for char in text:
            code = ord(char)
            if (0x0370 <= code <= 0x03FF or   # Greek and Coptic
                0x1F00 <= code <= 0x1FFF):    # Greek Extended
                return True
        return False
    
    def _detect_devanagari_text(self, text: str) -> bool:
        """Detect if text contains Devanagari (Hindi) characters"""
        if not text:
            return False
        for char in text:
            code = ord(char)
            if (0x0900 <= code <= 0x097F or   # Devanagari
                0xA8E0 <= code <= 0xA8FF):    # Devanagari Extended
                return True
        return False
    
    def _detect_ethiopic_text(self, text: str) -> bool:
        """Detect if text contains Ethiopic (Ge'ez) characters"""
        if not text:
            return False
        for char in text:
            code = ord(char)
            if (0x1200 <= code <= 0x137F or   # Ethiopic
                0x1380 <= code <= 0x139F or   # Ethiopic Supplement
                0x2D80 <= code <= 0x2DDF or   # Ethiopic Extended
                0xAB00 <= code <= 0xAB2F):    # Ethiopic Extended-A
                return True
        return False
    
    def _detect_korean_text(self, text: str) -> bool:
        """Detect if text contains Korean (Hangul) characters"""
        if not text:
            return False
        for char in text:
            code = ord(char)
            if 0xAC00 <= code <= 0xD7AF:  # Hangul Syllables
                return True
        return False
    
    def _detect_cjk_text(self, text: str) -> bool:
        """Detect if text contains CJK (Chinese, Japanese, Korean) characters"""
        if not text:
            return False
        
        # Unicode ranges for CJK characters (comprehensive coverage)
        for char in text:
            code = ord(char)
            if (0x4E00 <= code <= 0x9FFF or   # CJK Unified Ideographs
                0x3400 <= code <= 0x4DBF or   # CJK Extension A
                0x20000 <= code <= 0x2A6DF or # CJK Extension B
                0x2A700 <= code <= 0x2B73F or # CJK Extension C
                0x2B740 <= code <= 0x2B81F or # CJK Extension D
                0x2B820 <= code <= 0x2CEAF or # CJK Extension E
                0x3040 <= code <= 0x309F or   # Hiragana
                0x30A0 <= code <= 0x30FF or   # Katakana
                0xFF65 <= code <= 0xFF9F or   # Halfwidth Katakana
                0x3000 <= code <= 0x303F or   # CJK Punctuation
                0xAC00 <= code <= 0xD7AF):    # Hangul
                return True
        return False
    
    def _get_font(self, image_width: int, text: str = "", region: Optional[str] = None) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
        font_size = max(int(image_width * 0.05), 32)
        
        # Font paths for different scripts
        thai_font_path = 'assets/fonts/NotoSansThai-Regular.ttf'
        arabic_font_path = 'assets/fonts/NotoSansArabic-Regular.ttf'
        hebrew_font_path = 'assets/fonts/NotoSansHebrew-Regular.ttf'
        bengali_font_path = 'assets/fonts/NotoSansBengali-Regular.ttf'
        greek_font_path = 'assets/fonts/NotoSansGreek-Regular.ttf'
        devanagari_font_path = 'assets/fonts/NotoSansDevanagari-Regular.ttf'
        ethiopic_font_path = 'assets/fonts/NotoSansEthiopic-Regular.ttf'
        korean_font_path = 'assets/fonts/NotoSansKR-Regular.ttf'
        traditional_chinese_font_path = 'assets/fonts/NotoSansTC-Regular.ttf'
        japanese_font_path = 'assets/fonts/NotoSansJP-Regular.ttf'
        
        # Auto-detect Thai (must come before others as Thai is very specific)
        if self._detect_thai_text(text):
            try:
                font = ImageFont.truetype(thai_font_path, font_size)
                logger.info(f"Using Thai font (detected Thai characters, region={region})")
                return font
            except Exception as e:
                logger.warning(f"Failed to load Thai font {thai_font_path}: {e}, falling back")
        
        # Auto-detect Arabic (for Arabic, Persian, Urdu)
        if self._detect_arabic_text(text):
            try:
                font = ImageFont.truetype(arabic_font_path, font_size)
                logger.info(f"Using Arabic font (detected Arabic/Persian/Urdu characters, region={region})")
                return font
            except Exception as e:
                logger.warning(f"Failed to load Arabic font {arabic_font_path}: {e}, falling back")
        
        # Auto-detect Hebrew
        if self._detect_hebrew_text(text):
            try:
                font = ImageFont.truetype(hebrew_font_path, font_size)
                logger.info(f"Using Hebrew font (detected Hebrew characters, region={region})")
                return font
            except Exception as e:
                logger.warning(f"Failed to load Hebrew font {hebrew_font_path}: {e}, falling back")
        
        # Auto-detect Bengali
        if self._detect_bengali_text(text):
            try:
                font = ImageFont.truetype(bengali_font_path, font_size)
                logger.info(f"Using Bengali font (detected Bengali characters, region={region})")
                return font
            except Exception as e:
                logger.warning(f"Failed to load Bengali font {bengali_font_path}: {e}, falling back")
        
        # Auto-detect Greek
        if self._detect_greek_text(text):
            try:
                font = ImageFont.truetype(greek_font_path, font_size)
                logger.info(f"Using Greek font (detected Greek characters, region={region})")
                return font
            except Exception as e:
                logger.warning(f"Failed to load Greek font {greek_font_path}: {e}, falling back")
        
        # Auto-detect Devanagari (Hindi script)
        if self._detect_devanagari_text(text):
            try:
                font = ImageFont.truetype(devanagari_font_path, font_size)
                logger.info(f"Using Devanagari font (detected Hindi characters, region={region})")
                return font
            except Exception as e:
                logger.warning(f"Failed to load Devanagari font {devanagari_font_path}: {e}, falling back")
        
        # Auto-detect Ethiopic (Ge'ez script)
        if self._detect_ethiopic_text(text):
            try:
                font = ImageFont.truetype(ethiopic_font_path, font_size)
                logger.info(f"Using Ethiopic font (detected Ge'ez characters, region={region})")
                return font
            except Exception as e:
                logger.warning(f"Failed to load Ethiopic font {ethiopic_font_path}: {e}, falling back")
        
        # Auto-detect Korean (Hangul has priority)
        if self._detect_korean_text(text):
            try:
                font = ImageFont.truetype(korean_font_path, font_size)
                logger.info(f"Using Korean font (detected Hangul characters, region={region})")
                return font
            except Exception as e:
                logger.warning(f"Failed to load Korean font {korean_font_path}: {e}, trying Japanese font")
        
        # Auto-detect: use CJK font ONLY if text actually contains CJK characters
        # Region is ignored to avoid degrading Latin typography in CJK regions
        needs_cjk = self._detect_cjk_text(text)
        
        if needs_cjk:
            # Try Traditional Chinese font first (supports both traditional and simplified)
            try:
                font = ImageFont.truetype(traditional_chinese_font_path, font_size)
                logger.info(f"Using Traditional Chinese/CJK font (detected CJK characters in text, region={region})")
                return font
            except Exception as e:
                logger.warning(f"Failed to load Traditional Chinese font {traditional_chinese_font_path}: {e}, trying Japanese font")
            
            # Fallback to Japanese font (also supports Chinese)
            try:
                font = ImageFont.truetype(japanese_font_path, font_size)
                logger.info(f"Using Japanese/CJK font (detected CJK characters in text, region={region})")
                return font
            except Exception as e:
                logger.warning(f"Failed to load Japanese font {japanese_font_path}: {e}, falling back to Latin")
        
        # Use standard Latin fonts for non-CJK text
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:\\Windows\\Fonts\\Arial.ttf"
        ]
        
        for font_path in font_paths:
            try:
                return ImageFont.truetype(font_path, font_size)
            except:
                continue
        
        logger.warning("No suitable font found, using default")
        return ImageFont.load_default()
    
    def _get_line_height(self, font: Union[ImageFont.FreeTypeFont, ImageFont.ImageFont], draw: ImageDraw.ImageDraw) -> int:
        bbox = draw.textbbox((0, 0), "Ay", font=font)
        return int(bbox[3] - bbox[1] + 10)
    
    def _wrap_text(self, text: str, font: Union[ImageFont.FreeTypeFont, ImageFont.ImageFont], max_width: int, draw: ImageDraw.ImageDraw) -> list:
        words = text.split()
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
