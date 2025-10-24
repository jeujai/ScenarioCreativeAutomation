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
            # Landscape format (16:9) - bias toward top to keep heads visible
            top = int((new_height - target_height) * 0.2)  # 20% from top instead of 50%
        else:
            # Portrait or square - center vertically
            top = (new_height - target_height) // 2
        
        right = left + target_width
        bottom = top + target_height
        
        # Crop to exact target dimensions
        cropped = resized.crop((left, top, right, bottom))
        
        logger.info(f"Resized image from {image.size} to {cropped.size} (cover mode, smart crop)")
        return cropped
    
    def add_text_overlay(self, image: Image.Image, text: str, position: str = "bottom") -> Image.Image:
        img_copy = image.copy()
        draw = ImageDraw.Draw(img_copy)
        
        width, height = img_copy.size
        
        font = self._get_font(width)
        
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
    
    def _get_font(self, image_width: int) -> Union[ImageFont.FreeTypeFont, ImageFont.ImageFont]:
        font_size = max(int(image_width * 0.05), 32)
        
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
        
        return ImageFont.load_default()
    
    def _get_line_height(self, font: Union[ImageFont.FreeTypeFont, ImageFont.ImageFont], draw: ImageDraw.ImageDraw) -> int:
        bbox = draw.textbbox((0, 0), "Ay", font=font)
        return bbox[3] - bbox[1] + 10
    
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
