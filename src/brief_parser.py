import json
import yaml
from pathlib import Path
from typing import Dict, List, Any
import logging

from .content_moderator import ContentModerator

logger = logging.getLogger(__name__)


class CampaignBrief:
    def __init__(self, data: Dict[str, Any]):
        self.products = data.get("products", [])
        self.region = data.get("region", "Global")
        self.audience = data.get("audience", "General")
        self.message = data.get("message", "")
        self.localized_messages = data.get("localized_messages", {})
        self.raw_data = data
    
    @property
    def logo_position(self) -> str:
        """Get logo position, handling both camelCase (from frontend) and snake_case formats"""
        # Check for camelCase first (from web form), then snake_case, then default
        return self.raw_data.get('logoPosition') or self.raw_data.get('logo_position', 'top-left')
    
    @property
    def brand_color(self) -> str:
        """Get brand color from campaign data (hex color code)"""
        # Handle both camelCase (from frontend) and snake_case formats
        return self.raw_data.get('brandColor') or self.raw_data.get('brand_color', '#FFFFFF')
    
    @property
    def logo_selected(self) -> bool:
        """Check if a logo was explicitly selected for this campaign"""
        # Handle both camelCase (from frontend) and snake_case formats
        return self.raw_data.get('logoSelected') or self.raw_data.get('logo_selected', False)
    
    def validate(self, skip_moderation: bool = False) -> bool:
        if not self.products:
            raise ValueError("Campaign brief must include at least one product")
        if len(self.products) < 2:
            raise ValueError("Campaign brief must include at least two products")
        if not self.message:
            raise ValueError("Campaign brief must include a message")
        
        # AI-based content moderation (can be skipped if needed)
        if not skip_moderation:
            logger.info("Running AI-based content moderation...")
            moderation_result = ContentModerator.moderate_campaign_brief(self.raw_data)
            
            if not moderation_result['passed']:
                violations = moderation_result['violations']
                error_message = ContentModerator.format_violation_message(violations)
                logger.warning(f"Content moderation failed: {len(violations)} violations found")
                raise ValueError(error_message)
            
            logger.info("Content moderation passed - all content is appropriate")
        
        return True
    
    def get_message(self, language: str = "en") -> str:
        """Get message in specified language, falling back to default message"""
        return self.localized_messages.get(language, self.message)


class BriefParser:
    @staticmethod
    def parse_file(file_path: str, skip_moderation: bool = False) -> CampaignBrief:
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Campaign brief file not found: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            if path.suffix in ['.yaml', '.yml']:
                data = yaml.safe_load(f)
            elif path.suffix == '.json':
                data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {path.suffix}. Use .json, .yaml, or .yml")
        
        brief = CampaignBrief(data)
        brief.validate(skip_moderation=skip_moderation)
        return brief
    
    @staticmethod
    def parse_dict(data: Dict[str, Any], skip_moderation: bool = False) -> CampaignBrief:
        brief = CampaignBrief(data)
        brief.validate(skip_moderation=skip_moderation)
        return brief
