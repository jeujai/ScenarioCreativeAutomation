import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AssetManager:
    def __init__(self, assets_dir: Path):
        self.assets_dir = Path(assets_dir)
        self.uploads_dir = self.assets_dir / 'uploads'
        self.generated_dir = self.assets_dir / 'generated'
        
        self.assets_dir.mkdir(parents=True, exist_ok=True)
        self.uploads_dir.mkdir(parents=True, exist_ok=True)
        self.generated_dir.mkdir(parents=True, exist_ok=True)
    
    def get_asset_path(self, product_name: str, asset_type: str = "hero") -> Optional[Path]:
        normalized_name = self._normalize_name(product_name)
        extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        # First check uploads directory (user-provided assets)
        for ext in extensions:
            asset_path = self.uploads_dir / f"{normalized_name}_{asset_type}{ext}"
            if asset_path.exists():
                logger.info(f"Found uploaded asset for {product_name}: {asset_path}")
                return asset_path
            
            asset_path = self.uploads_dir / f"{normalized_name}{ext}"
            if asset_path.exists():
                logger.info(f"Found uploaded asset for {product_name}: {asset_path}")
                return asset_path
        
        # Then check generated directory (AI-generated assets from previous runs)
        for ext in extensions:
            asset_path = self.generated_dir / f"{normalized_name}_{asset_type}{ext}"
            if asset_path.exists():
                logger.info(f"Found generated asset for {product_name}: {asset_path}")
                return asset_path
            
            asset_path = self.generated_dir / f"{normalized_name}{ext}"
            if asset_path.exists():
                logger.info(f"Found generated asset for {product_name}: {asset_path}")
                return asset_path
        
        logger.info(f"No existing asset found for {product_name}")
        return None
    
    def get_uploaded_asset_path(self, product_name: str, asset_type: str = "hero") -> Optional[Path]:
        """Check only uploads directory for user-uploaded hero images"""
        normalized_name = self._normalize_name(product_name)
        extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        for ext in extensions:
            asset_path = self.uploads_dir / f"{normalized_name}_{asset_type}{ext}"
            if asset_path.exists():
                logger.info(f"Found uploaded asset for {product_name}: {asset_path}")
                return asset_path
            
            asset_path = self.uploads_dir / f"{normalized_name}{ext}"
            if asset_path.exists():
                logger.info(f"Found uploaded asset for {product_name}: {asset_path}")
                return asset_path
        
        return None
    
    def save_asset(self, image, product_name: str, asset_type: str = "hero") -> Path:
        """Save AI-generated asset to generated directory"""
        normalized_name = self._normalize_name(product_name)
        asset_path = self.generated_dir / f"{normalized_name}_{asset_type}.png"
        image.save(asset_path)
        logger.info(f"Saved generated asset to {asset_path}")
        return asset_path
    
    def save_generated_asset(self, image, product_name: str, region: str = "Global") -> Path:
        """Save region-specific AI-generated asset"""
        normalized_name = self._normalize_name(product_name)
        normalized_region = self._normalize_name(region)
        asset_path = self.generated_dir / f"{normalized_name}_{normalized_region}_hero.png"
        image.save(asset_path)
        logger.info(f"Saved region-specific generated asset to {asset_path}")
        return asset_path
    
    @staticmethod
    def _normalize_name(name: str) -> str:
        return name.lower().replace(' ', '_').replace('-', '_')
