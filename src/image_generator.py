import os
import logging
from pathlib import Path
from typing import Optional
from PIL import Image
import requests
from io import BytesIO

logger = logging.getLogger(__name__)


class ImageGenerator:
    def __init__(self, api_key: Optional[str] = None):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = api_key or os.getenv("OPENAI_API_KEY")
        
        self.use_gemini = False
        self.use_openai = False
        self.gemini_client = None
        self.openai_client = None
        
        if self.gemini_key:
            try:
                from google import genai
                from google.genai import types
                self.genai = genai
                self.genai_types = types
                self.gemini_client = genai.Client(api_key=self.gemini_key)
                self.use_gemini = True
                logger.info("Gemini client initialized for image generation")
            except Exception as e:
                logger.warning(f"Failed to initialize Gemini client: {e}")
                self.use_gemini = False
        
        if not self.use_gemini and self.openai_key:
            try:
                from openai import OpenAI
                self.openai_client = OpenAI(api_key=self.openai_key)
                self.use_openai = True
                logger.info("OpenAI client initialized for image generation")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                self.use_openai = False
    
    def generate_image(self, prompt: str, size: str = "1024x1024") -> Optional[Image.Image]:
        if self.use_gemini:
            return self._generate_with_gemini(prompt, size)
        elif self.use_openai:
            return self._generate_with_openai(prompt, size)
        else:
            return self._generate_placeholder(prompt)
    
    def _generate_with_gemini(self, prompt: str, size: str = "1024x1024") -> Optional[Image.Image]:
        try:
            logger.info(f"Generating image with Google Gemini: {prompt[:50]}...")
            
            response = self.gemini_client.models.generate_content(
                model="gemini-2.0-flash-preview-image-generation",
                contents=prompt,
                config=self.genai_types.GenerateContentConfig(
                    response_modalities=['TEXT', 'IMAGE']
                )
            )
            
            if not response.candidates:
                raise ValueError("No image generated from Gemini")
            
            content = response.candidates[0].content
            if not content or not content.parts:
                raise ValueError("No content parts in Gemini response")
            
            for part in content.parts:
                if part.inline_data and part.inline_data.data:
                    image = Image.open(BytesIO(part.inline_data.data))
                    logger.info("Successfully generated image with Gemini")
                    return image
            
            raise ValueError("No image data found in Gemini response")
            
        except Exception as e:
            logger.error(f"Error generating image with Gemini: {e}")
            if self.use_openai:
                logger.info("Falling back to OpenAI DALL-E")
                return self._generate_with_openai(prompt, size)
            else:
                return self._generate_placeholder(prompt)
    
    def _generate_with_openai(self, prompt: str, size: str = "1024x1024") -> Optional[Image.Image]:
        try:
            logger.info(f"Generating image with OpenAI DALL-E: {prompt[:50]}...")
            
            valid_size = "1024x1024" if size not in ["1024x1024", "1792x1024", "1024x1792"] else size
            
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=valid_size,
                quality="standard",
                n=1,
            )
            
            image_url = response.data[0].url if response.data and len(response.data) > 0 else None
            
            if not image_url:
                raise ValueError("No image URL returned from OpenAI")
            
            img_response = requests.get(image_url)
            img_response.raise_for_status()
            
            image = Image.open(BytesIO(img_response.content))
            logger.info("Successfully generated image with OpenAI")
            return image
            
        except Exception as e:
            logger.error(f"Error generating image with OpenAI: {e}")
            return self._generate_placeholder(prompt)
    
    def _generate_placeholder(self, prompt: str) -> Image.Image:
        logger.info(f"Generating placeholder image for: {prompt[:50]}...")
        
        from PIL import ImageDraw, ImageFont
        
        width, height = 1024, 1024
        colors = [
            (255, 99, 71),
            (70, 130, 180),
            (144, 238, 144),
            (255, 215, 0),
            (218, 112, 214)
        ]
        
        color = colors[hash(prompt) % len(colors)]
        
        image = Image.new('RGB', (width, height), color=color)
        draw = ImageDraw.Draw(image)
        
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()
        
        text = "PLACEHOLDER"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (width - text_width) // 2
        y = (height - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255), font=font)
        
        logger.info("Generated placeholder image")
        return image
    
    def create_product_prompt(self, product: dict, campaign_message: str, region: str) -> str:
        product_name = product.get('name', 'Product')
        description = product.get('description', '')
        
        prompt = f"Professional product photography of {product_name}"
        
        if description:
            prompt += f", {description}"
        
        prompt += f", high quality, commercial advertising style, clean background"
        
        if region and region != "Global":
            prompt += f", targeting {region} market"
        
        return prompt
