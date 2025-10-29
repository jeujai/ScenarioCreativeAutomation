"""AI-based content moderation using OpenAI Moderation API"""
import logging
from typing import Dict, List, Optional
from openai import OpenAI

from .config import OPENAI_API_KEY

logger = logging.getLogger(__name__)


class ContentModerator:
    """
    AI-based content moderation to detect prohibited words, offensive content,
    and inappropriate text using OpenAI's Moderation API.
    """
    
    _client: Optional[OpenAI] = None
    
    @classmethod
    def _get_client(cls) -> Optional[OpenAI]:
        """Get or create OpenAI client"""
        if cls._client is None and OPENAI_API_KEY:
            try:
                cls._client = OpenAI(api_key=OPENAI_API_KEY)
                logger.info("OpenAI Moderation API client initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize OpenAI client: {e}")
                return None
        return cls._client
    
    @classmethod
    def moderate_text(cls, text: str) -> Dict:
        """
        Check if text contains inappropriate content using OpenAI Moderation API.
        
        Args:
            text: The text content to moderate
            
        Returns:
            Dict with keys:
                - flagged: bool - True if content violates policies
                - categories: Dict - Categories that were flagged
                - category_scores: Dict - Confidence scores for each category
        """
        client = cls._get_client()
        
        if not client:
            logger.warning("OpenAI client not available, skipping moderation")
            return {
                "flagged": False,
                "categories": {},
                "category_scores": {},
                "skipped": True
            }
        
        try:
            response = client.moderations.create(input=text)
            result = response.results[0]
            
            return {
                "flagged": result.flagged,
                "categories": result.categories.model_dump(),
                "category_scores": result.category_scores.model_dump(),
                "skipped": False
            }
        except Exception as e:
            logger.error(f"Content moderation API error: {e}")
            return {
                "flagged": False,
                "categories": {},
                "category_scores": {},
                "error": str(e),
                "skipped": True
            }
    
    @classmethod
    def moderate_campaign_brief(cls, campaign_data: Dict) -> Dict:
        """
        Moderate all text fields in a campaign brief.
        
        Args:
            campaign_data: Campaign brief dictionary
            
        Returns:
            Dict with keys:
                - passed: bool - True if all content passed moderation
                - violations: List[Dict] - Details of any flagged content
        """
        violations = []
        
        # Check campaign message
        message = campaign_data.get('message', '')
        if message:
            result = cls.moderate_text(message)
            if result.get('flagged'):
                violations.append({
                    'field': 'Campaign Message',
                    'content': message,
                    'categories': cls._get_flagged_categories(result['categories'])
                })
        
        # Check product names and descriptions
        products = campaign_data.get('products', [])
        for idx, product in enumerate(products, 1):
            product_name = product.get('name', '')
            if product_name:
                result = cls.moderate_text(product_name)
                if result.get('flagged'):
                    violations.append({
                        'field': f'Product {idx} Name',
                        'content': product_name,
                        'categories': cls._get_flagged_categories(result['categories'])
                    })
            
            product_desc = product.get('description', '')
            if product_desc:
                result = cls.moderate_text(product_desc)
                if result.get('flagged'):
                    violations.append({
                        'field': f'Product {idx} Description',
                        'content': product_desc,
                        'categories': cls._get_flagged_categories(result['categories'])
                    })
        
        # Check audience
        audience = campaign_data.get('audience', '')
        if audience:
            result = cls.moderate_text(audience)
            if result.get('flagged'):
                violations.append({
                    'field': 'Target Audience',
                    'content': audience,
                    'categories': cls._get_flagged_categories(result['categories'])
                })
        
        return {
            'passed': len(violations) == 0,
            'violations': violations
        }
    
    @classmethod
    def _get_flagged_categories(cls, categories: Dict) -> List[str]:
        """Extract list of flagged category names"""
        return [category for category, flagged in categories.items() if flagged]
    
    @classmethod
    def format_violation_message(cls, violations: List[Dict]) -> str:
        """Format violation details into a user-friendly error message"""
        if not violations:
            return ""
        
        lines = ["Content moderation detected inappropriate content:"]
        for violation in violations:
            field = violation['field']
            categories = ", ".join(violation['categories'])
            lines.append(f"  • {field}: Flagged for {categories}")
        
        lines.append("\nPlease revise the flagged content and try again.")
        return "\n".join(lines)
