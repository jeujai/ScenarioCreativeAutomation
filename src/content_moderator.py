"""AI-based content moderation using OpenAI Moderation API and Google Perspective API"""
import logging
from typing import Dict, List, Optional
from openai import OpenAI
import requests

from .config import OPENAI_API_KEY, PERSPECTIVE_API_KEY

logger = logging.getLogger(__name__)


class ContentModerator:
    """
    AI-based content moderation using dual-layer approach:
    1. OpenAI Moderation API - Detects harmful content (violence, hate, etc.)
    2. Google Perspective API - Detects toxicity, profanity, and insults
    """
    
    _client: Optional[OpenAI] = None
    
    # Toxicity threshold (0.0 - 1.0) - Content above this is flagged
    TOXICITY_THRESHOLD = 0.7
    
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
    def _check_perspective_toxicity(cls, text: str) -> Dict:
        """
        Check text toxicity using Google Perspective API.
        
        Returns:
            Dict with keys:
                - flagged: bool
                - toxicity_score: float (0.0 - 1.0)
                - attributes: Dict of all attribute scores
        """
        if not PERSPECTIVE_API_KEY:
            return {
                "flagged": False,
                "toxicity_score": 0.0,
                "attributes": {},
                "skipped": True
            }
        
        try:
            url = f"https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze?key={PERSPECTIVE_API_KEY}"
            
            data = {
                "comment": {"text": text},
                "requestedAttributes": {
                    "TOXICITY": {},
                    "SEVERE_TOXICITY": {},
                    "IDENTITY_ATTACK": {},
                    "INSULT": {},
                    "PROFANITY": {},
                    "THREAT": {}
                },
                "languages": ["en"]
            }
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            attributes = result.get("attributeScores", {})
            
            # Extract scores
            scores = {
                attr: attributes.get(attr, {}).get("summaryScore", {}).get("value", 0.0)
                for attr in ["TOXICITY", "SEVERE_TOXICITY", "IDENTITY_ATTACK", "INSULT", "PROFANITY", "THREAT"]
            }
            
            toxicity_score = scores.get("TOXICITY", 0.0)
            flagged = toxicity_score >= cls.TOXICITY_THRESHOLD
            
            if flagged:
                logger.warning(f"Perspective API flagged text (toxicity={toxicity_score:.2f}): '{text[:50]}...'")
            
            return {
                "flagged": flagged,
                "toxicity_score": toxicity_score,
                "attributes": scores,
                "skipped": False
            }
            
        except Exception as e:
            logger.error(f"Perspective API error: {e}")
            return {
                "flagged": False,
                "toxicity_score": 0.0,
                "attributes": {},
                "error": str(e),
                "skipped": True
            }
    
    @classmethod
    def moderate_text(cls, text: str) -> Dict:
        """
        Check if text contains inappropriate content using dual-layer moderation:
        1. OpenAI Moderation API (harmful content)
        2. Google Perspective API (toxicity, profanity)
        
        Args:
            text: The text content to moderate
            
        Returns:
            Dict with keys:
                - flagged: bool - True if either API flags the content
                - openai_result: Dict - OpenAI moderation result
                - perspective_result: Dict - Perspective API result
                - flagged_by: List[str] - Which APIs flagged the content
        """
        openai_result = cls._check_openai_moderation(text)
        perspective_result = cls._check_perspective_toxicity(text)
        
        # Content is flagged if either API flags it
        flagged_by = []
        if openai_result.get('flagged'):
            flagged_by.append('OpenAI')
        if perspective_result.get('flagged'):
            flagged_by.append('Perspective')
        
        return {
            "flagged": len(flagged_by) > 0,
            "openai_result": openai_result,
            "perspective_result": perspective_result,
            "flagged_by": flagged_by
        }
    
    @classmethod
    def _check_openai_moderation(cls, text: str) -> Dict:
        """
        Check text using OpenAI Moderation API.
        
        Returns:
            Dict with moderation results from OpenAI
        """
        client = cls._get_client()
        
        if not client:
            logger.warning("OpenAI client not available, skipping OpenAI moderation")
            return {
                "flagged": False,
                "categories": {},
                "category_scores": {},
                "skipped": True
            }
        
        try:
            response = client.moderations.create(
                input=text,
                model="omni-moderation-latest"
            )
            result = response.results[0]
            
            return {
                "flagged": result.flagged,
                "categories": result.categories.model_dump(),
                "category_scores": result.category_scores.model_dump(),
                "skipped": False
            }
        except Exception as e:
            logger.error(f"OpenAI moderation API error: {e}")
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
                    'categories': cls._extract_violation_categories(result)
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
                        'categories': cls._extract_violation_categories(result)
                    })
            
            product_desc = product.get('description', '')
            if product_desc:
                result = cls.moderate_text(product_desc)
                if result.get('flagged'):
                    violations.append({
                        'field': f'Product {idx} Description',
                        'content': product_desc,
                        'categories': cls._extract_violation_categories(result)
                    })
        
        # Check audience
        audience = campaign_data.get('audience', '')
        if audience:
            result = cls.moderate_text(audience)
            if result.get('flagged'):
                violations.append({
                    'field': 'Target Audience',
                    'content': audience,
                    'categories': cls._extract_violation_categories(result)
                })
        
        return {
            'passed': len(violations) == 0,
            'violations': violations
        }
    
    @classmethod
    def _extract_violation_categories(cls, result: Dict) -> List[str]:
        """Extract list of flagged categories from combined moderation result"""
        categories = []
        
        # OpenAI categories
        openai_result = result.get('openai_result', {})
        if openai_result.get('categories'):
            openai_cats = [cat for cat, flagged in openai_result['categories'].items() if flagged]
            categories.extend([f"OpenAI:{cat}" for cat in openai_cats])
        
        # Perspective attributes
        perspective_result = result.get('perspective_result', {})
        if perspective_result.get('flagged'):
            attributes = perspective_result.get('attributes', {})
            for attr, score in attributes.items():
                if score >= cls.TOXICITY_THRESHOLD:
                    categories.append(f"Perspective:{attr.lower()}")
        
        return categories if categories else ["inappropriate_content"]
    
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
