import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
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
        # Versioning enabled - no purge, incremental versions instead
        logger.info(f"Starting campaign pipeline for {len(campaign_brief.products)} products")
        logger.info(f"Region: {campaign_brief.region}, Audience: {campaign_brief.audience}")
        logger.info("⚡ Using parallel processing for faster generation")
        
        results = {}
        
        # Process all products in parallel while preserving order
        with ThreadPoolExecutor(max_workers=len(campaign_brief.products)) as executor:
            # Submit all tasks and maintain product order
            futures = [
                (product, executor.submit(self._process_product, product, campaign_brief))
                for product in campaign_brief.products
            ]
            
            # Collect results in original product order
            for product, future in futures:
                product_name = product.get('name', 'Unknown Product')
                
                try:
                    product_results = future.result()
                    results[product_name] = product_results
                    logger.info(f"✓ Completed: {product_name}")
                except Exception as e:
                    logger.error(f"Error processing {product_name}: {e}", exc_info=True)
                    results[product_name] = []
        
        logger.info(f"\n{'='*60}")
        logger.info("Campaign pipeline completed successfully!")
        logger.info(f"Total creatives generated: {sum(len(v) for v in results.values())}")
        logger.info(f"{'='*60}\n")
        
        azure_upload_count = 0
        if self.azure_uploader and self.azure_uploader.enabled:
            logger.info("Uploading campaign assets to Azure Blob Storage...")
            uploaded_urls = []
            
            for product_name, paths in results.items():
                for path in paths:
                    relative_path = path.relative_to(self.outputs_dir)
                    blob_name = f"assets/{relative_path}"
                    url = self.azure_uploader.upload_file(path, blob_name)
                    if url:
                        uploaded_urls.append(url)
            
            azure_upload_count = len(uploaded_urls)
            logger.info(f"Successfully uploaded {azure_upload_count} assets to Azure")
        
        return results, azure_upload_count
    
    def _get_next_version_number(self, product_dir: Path, base_filename: str) -> int:
        """Find the next available version number by scanning Azure Blob Storage"""
        import re
        
        # If Azure is enabled, check Azure for the latest version
        if self.azure_uploader and self.azure_uploader.enabled:
            try:
                product_name = product_dir.name
                prefix = f"assets/{product_name}/"
                
                # List all blobs for this product
                blobs = self.azure_uploader.list_blobs(prefix=prefix, only_images=True)
                
                max_version = 0
                pattern = re.compile(rf"{re.escape(base_filename)}_v(\d+)\.png")
                
                for blob in blobs:
                    blob_filename = Path(blob['name']).name
                    match = pattern.match(blob_filename)
                    if match:
                        version = int(match.group(1))
                        max_version = max(max_version, version)
                
                logger.info(f"Azure check: Found max version {max_version} for {base_filename}")
                return max_version + 1
            
            except Exception as e:
                logger.warning(f"Failed to check Azure for version number: {e}. Falling back to local check.")
        
        # Fallback to local check if Azure is not available
        if not product_dir.exists():
            return 1
        
        max_version = 0
        pattern = re.compile(rf"{re.escape(base_filename)}_v(\d+)\.png")
        
        for file in product_dir.glob(f"{base_filename}_v*.png"):
            match = pattern.match(file.name)
            if match:
                version = int(match.group(1))
                max_version = max(max_version, version)
        
        return max_version + 1
    
    def _process_product(self, product: dict, campaign_brief: CampaignBrief) -> List[Path]:
        product_name = product.get('name', 'Unknown Product')
        
        hero_image = self._get_or_generate_hero_image(product, campaign_brief)
        
        if hero_image is None:
            logger.error(f"Failed to obtain hero image for {product_name}")
            return []
        
        # Get brand logo only if explicitly selected for this campaign
        brand_logo = None
        if campaign_brief.logo_selected:
            brand_logo = self._get_brand_logo()
            if brand_logo:
                logger.info("Brand logo will be applied to all outputs")
            else:
                logger.warning("Logo was selected but could not be loaded from logos directory")
        else:
            logger.info("No logo selected for this campaign - skipping logo overlay")
        
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
            
            # Add brand logo overlay if selected and available
            if brand_logo:
                final_image = self.image_processor.add_logo_overlay(
                    final_image, 
                    brand_logo, 
                    position=logo_position
                )
                logger.info(f"Added brand logo at position: {logo_position}")
            
            # Generate versioned filename
            base_filename = f"{self.asset_manager._normalize_name(product_name)}_{aspect_name.replace(':', 'x')}"
            version_number = self._get_next_version_number(product_dir, base_filename)
            output_filename = f"{base_filename}_v{version_number}.png"
            output_path = product_dir / output_filename
            
            final_image.save(output_path, quality=95)
            logger.info(f"Saved creative: {output_path} (version {version_number})")
            output_paths.append(output_path)
        
        return output_paths
    
    def _get_brand_logo(self) -> Optional[Image.Image]:
        """Get brand logo from dedicated logos directory"""
        logos_dir = self.assets_dir / 'logos'
        logos_dir.mkdir(parents=True, exist_ok=True)
        
        # Look for any image file in logos directory
        for ext in ['*.png', '*.jpg', '*.jpeg', '*.webp']:
            matches = list(logos_dir.glob(ext))
            if matches:
                # Use the first logo found (or most recently modified)
                logo_path = sorted(matches, key=lambda p: p.stat().st_mtime, reverse=True)[0]
                logger.info(f"Found brand logo: {logo_path}")
                try:
                    return Image.open(logo_path)
                except Exception as e:
                    logger.error(f"Failed to load brand logo: {e}")
        
        logger.info("No brand logo found in logos directory")
        return None
    
    def _get_or_generate_hero_image(self, product: dict, campaign_brief: CampaignBrief) -> Optional[Image.Image]:
        product_name = product.get('name', 'Unknown Product')
        description = product.get('description', '')
        
        # Check if hero image was explicitly uploaded by user
        uploaded_asset = self.asset_manager.get_uploaded_asset_path(product_name)
        
        if uploaded_asset:
            logger.info(f"Using user-uploaded hero image: {uploaded_asset}")
            return Image.open(uploaded_asset)
        
        # Otherwise, always generate fresh region-specific image via GenAI
        logger.info(f"Generating region-specific image for {campaign_brief.region}...")
        
        prompt = self.image_generator.create_product_prompt(
            product,
            campaign_brief.message,
            campaign_brief.region
        )
        
        generated_image = self.image_generator.generate_image(prompt)
        
        if generated_image:
            # Save to generated folder (not uploads) for reference
            self.asset_manager.save_generated_asset(generated_image, product_name, campaign_brief.region)
            return generated_image
        
        return None
