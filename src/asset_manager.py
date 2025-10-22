import os
from pathlib import Path
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AssetManager:
    def __init__(self, assets_dir: Path):
        self.assets_dir = Path(assets_dir)
        self.assets_dir.mkdir(parents=True, exist_ok=True)
    
    def get_asset_path(self, product_name: str, asset_type: str = "hero") -> Optional[Path]:
        normalized_name = self._normalize_name(product_name)
        
        extensions = ['.jpg', '.jpeg', '.png', '.webp']
        
        for ext in extensions:
            asset_path = self.assets_dir / f"{normalized_name}_{asset_type}{ext}"
            if asset_path.exists():
                logger.info(f"Found existing asset for {product_name}: {asset_path}")
                return asset_path
            
            asset_path = self.assets_dir / f"{normalized_name}{ext}"
            if asset_path.exists():
                logger.info(f"Found existing asset for {product_name}: {asset_path}")
                return asset_path
        
        logger.info(f"No existing asset found for {product_name}")
        return None
    
    def save_asset(self, image, product_name: str, asset_type: str = "hero") -> Path:
        normalized_name = self._normalize_name(product_name)
        asset_path = self.assets_dir / f"{normalized_name}_{asset_type}.png"
        image.save(asset_path)
        logger.info(f"Saved asset to {asset_path}")
        return asset_path
    
    @staticmethod
    def _normalize_name(name: str) -> str:
        return name.lower().replace(' ', '_').replace('-', '_')
