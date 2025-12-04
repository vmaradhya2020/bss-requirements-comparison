"""
Document parser for extracting BSS requirements from markdown files
"""
import re
from typing import List, Optional
from pathlib import Path
import logging

from .models import Feature
from .utils import clean_text, extract_filename

logger = logging.getLogger(__name__)


class RequirementParser:
    """Parser for extracting structured requirements from markdown documents"""

    def __init__(self):
        # Patterns for identifying features
        self.header_pattern = re.compile(r'^(#{1,3})\s+(.+)$', re.MULTILINE)
        self.numbered_pattern = re.compile(r'^(\d+)\.\s+(.+)$', re.MULTILINE)
        self.bullet_pattern = re.compile(r'^[-*]\s+(.+)$', re.MULTILINE)

    def parse_markdown(self, file_path: str, customer: str = None) -> List[Feature]:
        """
        Parse markdown file and extract features

        Args:
            file_path: Path to markdown file
            customer: Customer name (extracted from filename if not provided)

        Returns:
            List of Feature objects
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            if not customer:
                customer = extract_filename(file_path)

            logger.info(f"Parsing {file_path} for customer: {customer}")

            features = self.extract_features(content, customer)

            logger.info(f"Extracted {len(features)} features from {file_path}")

            return features

        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            raise

    def extract_features(self, content: str, customer: str) -> List[Feature]:
        """
        Extract features from markdown content

        Strategy:
        1. Look for numbered lists (most common in requirements)
        2. Fall back to headers if no numbered lists
        3. Fall back to bullet points
        """
        features = []

        # Try numbered list first
        features = self._extract_numbered_features(content, customer)

        if not features:
            # Try headers
            features = self._extract_header_features(content, customer)

        if not features:
            # Try bullet points
            features = self._extract_bullet_features(content, customer)

        return features

    def _extract_numbered_features(self, content: str, customer: str) -> List[Feature]:
        """Extract features from numbered lists"""
        features = []
        lines = content.split('\n')

        current_feature = None
        feature_counter = 0

        for i, line in enumerate(lines):
            line = line.strip()

            # Check if line starts with number
            match = re.match(r'^(\d+)\.\s+(.+)$', line)

            if match:
                # Save previous feature if exists
                if current_feature:
                    features.append(current_feature)

                # Start new feature
                number = match.group(1)
                title = match.group(2)
                feature_counter += 1

                current_feature = Feature(
                    id=f"{customer}_{number}",
                    title=clean_text(title),
                    description="",
                    customer=customer,
                    raw_text=title
                )

            elif current_feature and line and not line.startswith('#'):
                # Add to description
                current_feature.description += " " + line
                current_feature.raw_text += " " + line

        # Add last feature
        if current_feature:
            features.append(current_feature)

        # Clean up descriptions
        for feature in features:
            feature.description = clean_text(feature.description)
            feature.raw_text = clean_text(feature.raw_text)

            # If no description, use title
            if not feature.description:
                feature.description = feature.title

        return features

    def _extract_header_features(self, content: str, customer: str) -> List[Feature]:
        """Extract features from markdown headers"""
        features = []
        lines = content.split('\n')

        current_feature = None
        feature_counter = 0

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            # Check if line is a header (### or ##)
            match = re.match(r'^(#{2,3})\s+(.+)$', line_stripped)

            if match:
                # Save previous feature
                if current_feature:
                    features.append(current_feature)

                # Start new feature
                feature_counter += 1
                title = match.group(2)

                current_feature = Feature(
                    id=f"{customer}_{feature_counter}",
                    title=clean_text(title),
                    description="",
                    customer=customer,
                    raw_text=title
                )

            elif current_feature and line_stripped and not line_stripped.startswith('#'):
                # Add to description
                current_feature.description += " " + line_stripped
                current_feature.raw_text += " " + line_stripped

        # Add last feature
        if current_feature:
            features.append(current_feature)

        # Clean up
        for feature in features:
            feature.description = clean_text(feature.description)
            feature.raw_text = clean_text(feature.raw_text)
            if not feature.description:
                feature.description = feature.title

        return features

    def _extract_bullet_features(self, content: str, customer: str) -> List[Feature]:
        """Extract features from bullet points"""
        features = []
        lines = content.split('\n')

        feature_counter = 0

        for line in lines:
            line = line.strip()

            # Check if line is a bullet point
            match = re.match(r'^[-*]\s+(.+)$', line)

            if match:
                feature_counter += 1
                content_text = match.group(1)

                feature = Feature(
                    id=f"{customer}_{feature_counter}",
                    title=clean_text(content_text),
                    description=clean_text(content_text),
                    customer=customer,
                    raw_text=content_text
                )

                features.append(feature)

        return features

    def validate_features(self, features: List[Feature]) -> bool:
        """Validate extracted features"""
        if not features:
            logger.warning("No features extracted")
            return False

        for feature in features:
            if not feature.title or not feature.description:
                logger.warning(f"Invalid feature: {feature.id}")
                return False

        return True
