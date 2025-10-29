#!/usr/bin/env python3
import argparse
import logging
import sys
from pathlib import Path

from src.brief_parser import BriefParser
from src.pipeline import CreativeAutomationPipeline
from src.config import ASSETS_DIR, OUTPUTS_DIR


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('pipeline.log')
        ]
    )


def main():
    parser = argparse.ArgumentParser(
        description='Creative Automation Pipeline for Social Ad Campaigns',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py examples/campaign_brief.yaml
  python main.py examples/campaign_brief.json --verbose
  python main.py examples/campaign_brief.yaml --assets-dir ./my_assets --outputs-dir ./my_outputs
        """
    )
    
    parser.add_argument(
        'brief',
        type=str,
        help='Path to campaign brief file (JSON or YAML)'
    )
    
    parser.add_argument(
        '--assets-dir',
        type=str,
        default=str(ASSETS_DIR),
        help=f'Directory containing input assets (default: {ASSETS_DIR})'
    )
    
    parser.add_argument(
        '--outputs-dir',
        type=str,
        default=str(OUTPUTS_DIR),
        help=f'Directory for output creatives (default: {OUTPUTS_DIR})'
    )
    
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose logging'
    )
    
    parser.add_argument(
        '--skip-moderation',
        action='store_true',
        help='Skip AI-based content moderation checks'
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    try:
        logger.info("="*80)
        logger.info("CREATIVE AUTOMATION PIPELINE")
        logger.info("="*80)
        
        logger.info(f"\nParsing campaign brief: {args.brief}")
        campaign_brief = BriefParser.parse_file(args.brief, skip_moderation=args.skip_moderation)
        
        logger.info(f"Campaign Details:")
        logger.info(f"  Products: {len(campaign_brief.products)}")
        logger.info(f"  Region: {campaign_brief.region}")
        logger.info(f"  Audience: {campaign_brief.audience}")
        logger.info(f"  Message: {campaign_brief.message}")
        
        pipeline = CreativeAutomationPipeline(
            assets_dir=Path(args.assets_dir),
            outputs_dir=Path(args.outputs_dir)
        )
        
        results, azure_upload_count = pipeline.run(campaign_brief)
        
        logger.info("\n" + "="*80)
        logger.info("PIPELINE SUMMARY")
        logger.info("="*80)
        
        for product_name, output_paths in results.items():
            logger.info(f"\n{product_name}:")
            for path in output_paths:
                logger.info(f"  ✓ {path}")
        
        logger.info(f"\nTotal creatives generated: {sum(len(v) for v in results.values())}")
        logger.info(f"Azure uploads: {azure_upload_count}")
        logger.info(f"Output directory: {args.outputs_dir}")
        logger.info("\n" + "="*80)
        logger.info("PIPELINE COMPLETED SUCCESSFULLY!")
        logger.info("="*80 + "\n")
        
        return 0
        
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        return 1
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
