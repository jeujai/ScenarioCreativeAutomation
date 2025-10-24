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
        
        # CJK font path
        cjk_font_path = 'assets/fonts/NotoSansJP-Regular.ttf'
        
        # Auto-detect: use CJK font ONLY if text actually contains CJK characters
        # Region is ignored to avoid degrading Latin typography in CJK regions
        needs_cjk = self._detect_cjk_text(text)
        
        if needs_cjk:
            try:
                font = ImageFont.truetype(cjk_font_path, font_size)
                logger.info(f"Using CJK font (detected CJK characters in text, region={region})")
                return font
            except Exception as e:
                logger.warning(f"Failed to load CJK font {cjk_font_path}: {e}, falling back to Latin")
        
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
