import json
import yaml
from pathlib import Path
from typing import Dict, List, Any


class CampaignBrief:
    def __init__(self, data: Dict[str, Any]):
        self.products = data.get("products", [])
        self.region = data.get("region", "Global")
        self.audience = data.get("audience", "General")
        self.message = data.get("message", "")
        self.localized_messages = data.get("localized_messages", {})
        self.raw_data = data
    
    def validate(self) -> bool:
        if not self.products:
            raise ValueError("Campaign brief must include at least one product")
        if len(self.products) < 2:
            raise ValueError("Campaign brief must include at least two products")
        if not self.message:
            raise ValueError("Campaign brief must include a message")
        return True
    
    def get_message(self, language: str = "en") -> str:
        return self.localized_messages.get(language, self.message)


class BriefParser:
    @staticmethod
    def parse_file(file_path: str) -> CampaignBrief:
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
        brief.validate()
        return brief
    
    @staticmethod
    def parse_dict(data: Dict[str, Any]) -> CampaignBrief:
        brief = CampaignBrief(data)
        brief.validate()
        return brief
