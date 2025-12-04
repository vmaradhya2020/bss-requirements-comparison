"""
Main comparator orchestrating the entire comparison workflow
"""
import logging
from typing import List, Dict
from pathlib import Path

from .models import Feature, ComparisonResult
from .parser import RequirementParser
from .comparison_engine import ComparisonEngine
from .utils import load_config, extract_filename

logger = logging.getLogger(__name__)


class FeatureComparator:
    """Main orchestrator for BSS requirements comparison"""

    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = load_config(config_path)
        self.parser = RequirementParser()
        self.engine = ComparisonEngine(self.config)

        logger.info("Feature comparator initialized")

    def compare_documents(
        self,
        new_doc_path: str,
        existing_doc_path: str,
        new_customer: str = None,
        existing_customer: str = None
    ) -> ComparisonResult:
        """
        Compare two requirement documents

        Args:
            new_doc_path: Path to new requirements document
            existing_doc_path: Path to existing implementation document
            new_customer: Customer name for new requirements
            existing_customer: Customer name for existing implementation

        Returns:
            ComparisonResult object with all matches and statistics
        """
        logger.info(f"Starting comparison: {new_doc_path} vs {existing_doc_path}")

        # Parse documents
        logger.info("Parsing new requirements...")
        new_features = self.parser.parse_markdown(
            new_doc_path,
            customer=new_customer or extract_filename(new_doc_path)
        )

        logger.info("Parsing existing implementation...")
        existing_features = self.parser.parse_markdown(
            existing_doc_path,
            customer=existing_customer or extract_filename(existing_doc_path)
        )

        if not new_features:
            raise ValueError(f"No features extracted from {new_doc_path}")

        if not existing_features:
            raise ValueError(f"No features extracted from {existing_doc_path}")

        # Perform comparison
        logger.info("Running AI-powered comparison...")
        exact_matches, similar_matches, delta_features = self.engine.compare_features(
            new_features,
            existing_features
        )

        # Create result object
        result = ComparisonResult(
            new_document=Path(new_doc_path).name,
            existing_document=Path(existing_doc_path).name,
            new_features_count=len(new_features),
            existing_features_count=len(existing_features),
            exact_matches=exact_matches,
            similar_features=similar_matches,
            delta_features=delta_features
        )

        # Calculate statistics
        result.calculate_statistics()

        logger.info(f"Comparison complete: {result.statistics}")

        return result

    def compare_multiple(
        self,
        new_doc_path: str,
        existing_dir: str
    ) -> List[ComparisonResult]:
        """
        Compare new requirements against multiple existing implementations

        Args:
            new_doc_path: Path to new requirements
            existing_dir: Directory containing existing implementation docs

        Returns:
            List of ComparisonResult objects
        """
        logger.info(f"Batch comparison: {new_doc_path} vs all in {existing_dir}")

        results = []
        existing_path = Path(existing_dir)

        # Find all markdown files in directory
        for doc_path in existing_path.glob("*.md"):
            try:
                result = self.compare_documents(new_doc_path, str(doc_path))
                results.append(result)
            except Exception as e:
                logger.error(f"Error comparing with {doc_path}: {e}")

        logger.info(f"Batch comparison complete: {len(results)} comparisons")

        return results

    def get_best_match(self, results: List[ComparisonResult]) -> ComparisonResult:
        """
        Find the best matching existing implementation

        Args:
            results: List of comparison results

        Returns:
            ComparisonResult with highest reusability score
        """
        if not results:
            return None

        best_result = max(
            results,
            key=lambda r: r.statistics.get('reusability_score', 0)
        )

        return best_result
