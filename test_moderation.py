#!/usr/bin/env python3
"""Test script for content moderation functionality"""
import logging
from src.content_moderator import ContentModerator

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

def test_clean_content():
    """Test that clean content passes moderation"""
    print("\n" + "="*60)
    print("TEST 1: Clean content should pass")
    print("="*60)
    
    result = ContentModerator.moderate_text("Dress like a superhero with our new collection")
    print(f"Flagged: {result.get('flagged')}")
    print(f"Skipped: {result.get('skipped', False)}")
    
    if result.get('flagged'):
        print(f"Categories: {ContentModerator._get_flagged_categories(result['categories'])}")
    
    assert not result.get('flagged'), "Clean content should not be flagged"
    print("✅ PASSED")


def test_inappropriate_content():
    """Test that inappropriate content is flagged"""
    print("\n" + "="*60)
    print("TEST 2: Inappropriate content should be flagged")
    print("="*60)
    
    result = ContentModerator.moderate_text("I want to kill everyone with violence")
    print(f"Flagged: {result.get('flagged')}")
    print(f"Skipped: {result.get('skipped', False)}")
    
    if result.get('flagged'):
        print(f"Categories: {ContentModerator._get_flagged_categories(result['categories'])}")
    
    if not result.get('skipped'):
        assert result.get('flagged'), "Inappropriate content should be flagged"
        print("✅ PASSED")
    else:
        print("⚠️  SKIPPED (OpenAI API not available)")


def test_campaign_brief_moderation():
    """Test campaign brief moderation"""
    print("\n" + "="*60)
    print("TEST 3: Campaign brief with clean content")
    print("="*60)
    
    clean_campaign = {
        'message': 'Dress like a superhero with our new collection',
        'products': [
            {'name': 'Superman Suit', 'description': 'Classic red and blue outfit'},
            {'name': 'Batman Suit', 'description': 'Dark knight costume'}
        ],
        'audience': 'Young professionals'
    }
    
    result = ContentModerator.moderate_campaign_brief(clean_campaign)
    print(f"Passed: {result['passed']}")
    print(f"Violations: {len(result['violations'])}")
    
    assert result['passed'], "Clean campaign should pass"
    print("✅ PASSED")
    
    print("\n" + "="*60)
    print("TEST 4: Campaign brief with inappropriate content")
    print("="*60)
    
    bad_campaign = {
        'message': 'I want to harm people with violence',
        'products': [
            {'name': 'Good Product', 'description': 'Clean description'},
            {'name': 'Bad Product', 'description': 'I will kill you'}
        ],
        'audience': 'Bad audience with violent intent'
    }
    
    result = ContentModerator.moderate_campaign_brief(bad_campaign)
    print(f"Passed: {result['passed']}")
    print(f"Violations: {len(result['violations'])}")
    
    if result['violations']:
        for violation in result['violations']:
            print(f"  - {violation['field']}: {violation['categories']}")
    
    if not result.get('skipped'):
        assert not result['passed'], "Inappropriate campaign should fail"
        assert len(result['violations']) > 0, "Should have violations"
        print("✅ PASSED")
    else:
        print("⚠️  SKIPPED (OpenAI API not available)")


if __name__ == "__main__":
    try:
        test_clean_content()
        test_inappropriate_content()
        test_campaign_brief_moderation()
        
        print("\n" + "="*60)
        print("ALL TESTS COMPLETED")
        print("="*60)
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        exit(1)
