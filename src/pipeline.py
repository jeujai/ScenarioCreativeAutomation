import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from PIL import Image

from .brief_parser import CampaignBrief
from .asset_manager import AssetManager
from .image_generator import ImageGenerator
from .image_processor import ImageProcessor
from .azure_uploader import AzureUploader
from .config import ASPECT_RATIOS, ASSETS_DIR, OUTPUTS_DIR, AZURE_UPLOAD_ENABLED, AZURE_CONTAINER_NAME

logger = logging.getLogger(__name__)


class CreativeAutomationPipeline:
    def __init__(self, assets_dir: Path = ASSETS_DIR, outputs_dir: Path = OUTPUTS_DIR):
        self.asset_manager = AssetManager(assets_dir)
        self.image_generator = ImageGenerator()
        self.image_processor = ImageProcessor()
        self.azure_uploader = AzureUploader(container_name=AZURE_CONTAINER_NAME) if AZURE_UPLOAD_ENABLED else None
        self.outputs_dir = Path(outputs_dir)
        self.assets_dir = Path(assets_dir)
        self.outputs_dir.mkdir(parents=True, exist_ok=True)
    
    def _purge_all_assets(self):
        """Clear all existing outputs and generated assets before each run"""
        logger.info("Purging all existing assets and outputs...")
        
        if self.outputs_dir.exists():
            for item in self.outputs_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                elif item.is_file():
                    item.unlink()
        
        if self.assets_dir.exists():
            for item in self.assets_dir.iterdir():
                if item.is_file() and item.suffix == '.png':
                    item.unlink()
        
        logger.info("All assets purged. Starting fresh generation...")
    
    def run(self, campaign_brief: CampaignBrief) -> Dict[str, List[Path]]:
        self._purge_all_assets()
        
        logger.info(f"Starting campaign pipeline for {len(campaign_brief.products)} products")
        logger.info(f"Region: {campaign_brief.region}, Audience: {campaign_brief.audience}")
        
        results = {}
        
        for product in campaign_brief.products:
            product_name = product.get('name', 'Unknown Product')
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing product: {product_name}")
            logger.info(f"{'='*60}")
            
            product_results = self._process_product(product, campaign_brief)
            results[product_name] = product_results
        
        logger.info(f"\n{'='*60}")
        logger.info("Campaign pipeline completed successfully!")
        logger.info(f"Total creatives generated: {sum(len(v) for v in results.values())}")
        logger.info(f"{'='*60}\n")
        
        if self.azure_uploader and self.azure_uploader.enabled:
            logger.info("Uploading campaign assets to Azure Blob Storage...")
            uploaded_urls = self.azure_uploader.upload_directory(self.outputs_dir, prefix="outputs")
            logger.info(f"Successfully uploaded {len(uploaded_urls)} assets to Azure")
        
        return results
    
    def _process_product(self, product: dict, campaign_brief: CampaignBrief) -> List[Path]:
        product_name = product.get('name', 'Unknown Product')
        
        hero_image = self._get_or_generate_hero_image(product, campaign_brief)
        
        if hero_image is None:
            logger.error(f"Failed to obtain hero image for {product_name}")
            return []
        
        output_paths = []
        
        product_dir = self.outputs_dir / self.asset_manager._normalize_name(product_name)
        product_dir.mkdir(parents=True, exist_ok=True)
        
        for aspect_name, aspect_size in ASPECT_RATIOS.items():
            logger.info(f"Creating {aspect_name} variant...")
            
            resized_image = self.image_processor.resize_to_aspect_ratio(hero_image, aspect_size)
            
            message = campaign_brief.get_message()
            final_image = self.image_processor.add_text_overlay(resized_image, message)
            
            output_filename = f"{self.asset_manager._normalize_name(product_name)}_{aspect_name.replace(':', 'x')}.png"
            output_path = product_dir / output_filename
            
            final_image.save(output_path, quality=95)
            logger.info(f"Saved creative: {output_path}")
            output_paths.append(output_path)
        
        return output_paths
    
    def _get_or_generate_hero_image(self, product: dict, campaign_brief: CampaignBrief) -> Optional[Image.Image]:
        product_name = product.get('name', 'Unknown Product')
        
        existing_asset = self.asset_manager.get_asset_path(product_name)
        
        if existing_asset:
            logger.info(f"Using existing asset: {existing_asset}")
            return Image.open(existing_asset)
        
        logger.info(f"No existing asset found. Generating new image...")
        
        prompt = self.image_generator.create_product_prompt(
            product,
            campaign_brief.message,
            campaign_brief.region
        )
        
        generated_image = self.image_generator.generate_image(prompt)
        
        if generated_image:
            self.asset_manager.save_asset(generated_image, product_name)
            return generated_image
        
        return None
