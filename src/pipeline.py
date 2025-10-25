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
from .translator import RegionalTranslator
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
        """Clear outputs and AI-generated assets (preserve user uploads)"""
        logger.info("Purging previous outputs and AI-generated assets...")
        
        # Always purge outputs directory for fresh creatives
        if self.outputs_dir.exists():
            for item in self.outputs_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                elif item.is_file():
                    item.unlink()
        
        # Purge AI-generated assets (in generated/ subdirectory)
        generated_dir = self.assets_dir / 'generated'
        if generated_dir.exists():
            for item in generated_dir.iterdir():
                if item.is_dir():
                    shutil.rmtree(item)
                    logger.debug(f"Purged generated directory: {item}")
                elif item.is_file():
                    item.unlink()
                    logger.debug(f"Purged generated asset: {item}")
        
        # NOTE: User uploads in uploads/ subdirectory are preserved
        
        logger.info("Purge complete. User uploads preserved, ready for fresh generation...")
    
    def run(self, campaign_brief: CampaignBrief) -> tuple[Dict[str, List[Path]], int]:
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
        
        azure_upload_count = 0
        if self.azure_uploader and self.azure_uploader.enabled:
            logger.info("Uploading campaign assets to Azure Blob Storage...")
            uploaded_urls = self.azure_uploader.upload_directory(self.outputs_dir, prefix="outputs")
            azure_upload_count = len(uploaded_urls)
            logger.info(f"Successfully uploaded {azure_upload_count} assets to Azure")
        
        return results, azure_upload_count
    
    def _process_product(self, product: dict, campaign_brief: CampaignBrief) -> List[Path]:
        product_name = product.get('name', 'Unknown Product')
        
        hero_image = self._get_or_generate_hero_image(product, campaign_brief)
        
        if hero_image is None:
            logger.error(f"Failed to obtain hero image for {product_name}")
            return []
        
        # Get brand logo if available
        brand_logo = self._get_brand_logo()
        logo_position = campaign_brief.logo_position
        
        output_paths = []
        
        product_dir = self.outputs_dir / self.asset_manager._normalize_name(product_name)
        product_dir.mkdir(parents=True, exist_ok=True)
        
        for aspect_name, aspect_size in ASPECT_RATIOS.items():
            logger.info(f"Creating {aspect_name} variant...")
            
            resized_image = self.image_processor.resize_to_aspect_ratio(hero_image, aspect_size)
            
            # Get message and translate to regional language
            message = campaign_brief.get_message()
            translated_message = RegionalTranslator.translate(message, campaign_brief.region)
            final_image = self.image_processor.add_text_overlay(
                resized_image, 
                translated_message, 
                region=campaign_brief.region,
                text_color=campaign_brief.brand_color
            )
            
            # Add brand logo overlay if available
            if brand_logo:
                final_image = self.image_processor.add_logo_overlay(
                    final_image, 
                    brand_logo, 
                    position=logo_position
                )
                logger.info(f"Added brand logo at position: {logo_position}")
            
            output_filename = f"{self.asset_manager._normalize_name(product_name)}_{aspect_name.replace(':', 'x')}.png"
            output_path = product_dir / output_filename
            
            final_image.save(output_path, quality=95)
            logger.info(f"Saved creative: {output_path}")
            output_paths.append(output_path)
        
        return output_paths
    
    def _get_brand_logo(self) -> Optional[Image.Image]:
        """Get brand logo from uploads directory if available"""
        uploads_dir = self.assets_dir / 'uploads'
        
        # Look for brand_logo file
        for pattern in ['brand_logo.*', '*logo*']:
            matches = list(uploads_dir.glob(pattern))
            if matches:
                logo_path = matches[0]
                logger.info(f"Found brand logo: {logo_path}")
                try:
                    return Image.open(logo_path)
                except Exception as e:
                    logger.error(f"Failed to load brand logo: {e}")
        
        return None
    
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
