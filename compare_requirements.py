"""
CLI tool for comparing BSS requirements documents
"""
import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.comparator import FeatureComparator
from src.report_generator import ReportGenerator
from src.utils import load_config, ensure_directory

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('comparison.log')
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Main CLI entry point"""

    parser = argparse.ArgumentParser(
        description='AI-Powered BSS Requirements Comparison Tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic comparison
  python cli/compare_requirements.py --new data/requirements_sprint.md --existing data/implemented_verizon.md

  # Generate both MD and HTML
  python cli/compare_requirements.py --new data/requirements_sprint.md --existing data/implemented_verizon.md --format both

  # Custom output location
  python cli/compare_requirements.py --new requirements_att.md --existing implemented_verizon.md --output reports/att_comparison.html

  # Batch comparison against multiple existing implementations
  python cli/compare_requirements.py --new requirements_sprint.md --existing-dir data/implementations/
        """
    )

    # Required arguments
    parser.add_argument(
        '--new',
        required=True,
        help='Path to new requirements document (markdown)'
    )

    # Existing document (single or directory)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        '--existing',
        help='Path to existing implementation document (markdown)'
    )
    group.add_argument(
        '--existing-dir',
        help='Directory containing existing implementation documents (batch mode)'
    )

    # Optional arguments
    parser.add_argument(
        '--output',
        help='Output file path (default: auto-generated in outputs/comparison_reports/)'
    )

    parser.add_argument(
        '--format',
        choices=['markdown', 'html', 'both'],
        default='html',
        help='Output format (default: html)'
    )

    parser.add_argument(
        '--config',
        default='config/config.yaml',
        help='Path to configuration file (default: config/config.yaml)'
    )

    parser.add_argument(
        '--threshold',
        type=float,
        help='Similarity threshold for matching (0.0-1.0, default: from config)'
    )

    parser.add_argument(
        '--no-recommendations',
        action='store_true',
        help='Skip AI-generated recommendations (faster)'
    )

    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    # Set log level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Validate input files
    if not Path(args.new).exists():
        logger.error(f"New requirements file not found: {args.new}")
        sys.exit(1)

    if args.existing and not Path(args.existing).exists():
        logger.error(f"Existing implementation file not found: {args.existing}")
        sys.exit(1)

    if args.existing_dir and not Path(args.existing_dir).is_dir():
        logger.error(f"Existing directory not found: {args.existing_dir}")
        sys.exit(1)

    try:
        # Load config
        config = load_config(args.config)

        # Override threshold if provided
        if args.threshold:
            config['comparison']['similar_match_threshold'] = args.threshold
            logger.info(f"Using custom similarity threshold: {args.threshold}")

        # Initialize comparator
        logger.info("Initializing BSS Requirements Comparator...")
        comparator = FeatureComparator(args.config)

        # Run comparison
        if args.existing:
            # Single comparison
            logger.info(f"Comparing: {args.new} vs {args.existing}")
            result = comparator.compare_documents(args.new, args.existing)

            # Generate recommendations
            recommendations = None
            if not args.no_recommendations:
                logger.info("Generating AI recommendations...")
                try:
                    recommendations = comparator.engine.generate_recommendations(
                        result.exact_matches,
                        result.similar_features,
                        result.delta_features
                    )
                except Exception as e:
                    logger.warning(f"Could not generate recommendations: {e}")

            # Generate report
            logger.info("Generating report...")
            report_gen = ReportGenerator(config)
            output_files = report_gen.generate(
                result,
                output_format=args.format,
                output_path=args.output,
                recommendations=recommendations
            )

            # Print results
            print("\n" + "="*80)
            print("COMPARISON COMPLETE")
            print("="*80)
            print(f"\n📊 Results:")
            print(f"  ✅ Exact Matches: {len(result.exact_matches)} ({result.statistics['exact_match_percentage']:.1f}%)")
            print(f"  ⚠️  Similar Features: {len(result.similar_features)} ({result.statistics['similar_match_percentage']:.1f}%)")
            print(f"  🆕 Delta (New): {len(result.delta_features)} ({result.statistics['delta_percentage']:.1f}%)")
            print(f"  📈 Reusability Score: {result.statistics['reusability_score']:.1f}%")

            print(f"\n📄 Reports generated:")
            for format_type, file_path in output_files.items():
                print(f"  - {format_type.upper()}: {file_path}")

            print("\n" + "="*80)

        else:
            # Batch comparison
            logger.info(f"Batch comparing: {args.new} vs all in {args.existing_dir}")
            results = comparator.compare_multiple(args.new, args.existing_dir)

            if not results:
                logger.error("No comparison results generated")
                sys.exit(1)

            # Find best match
            best_result = comparator.get_best_match(results)

            logger.info("Generating reports for all comparisons...")
            report_gen = ReportGenerator(config)

            # Create batch output directory
            batch_dir = ensure_directory("outputs/comparison_reports/batch")

            print("\n" + "="*80)
            print("BATCH COMPARISON COMPLETE")
            print("="*80)

            for i, result in enumerate(results, 1):
                print(f"\n{i}. {result.existing_document}")
                print(f"   Reusability Score: {result.statistics['reusability_score']:.1f}%")
                print(f"   Exact: {len(result.exact_matches)}, Similar: {len(result.similar_features)}, Delta: {len(result.delta_features)}")

                # Generate report for each
                output_path = f"{batch_dir}/comparison_{Path(result.existing_document).stem}.html"
                report_gen.generate_html(result, output_path)
                print(f"   Report: {output_path}")

            print(f"\n🏆 Best Match: {best_result.existing_document}")
            print(f"   Reusability Score: {best_result.statistics['reusability_score']:.1f}%")

            print("\n" + "="*80)

    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"Error during comparison: {e}", exc_info=args.verbose)
        sys.exit(1)


if __name__ == "__main__":
    main()
