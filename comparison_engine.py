"""
LLM-powered comparison engine using CrewAI for intelligent feature matching
"""
import os
import logging
from typing import List, Dict, Tuple
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np

from .models import Feature, MatchPair
from .utils import get_api_key

logger = logging.getLogger(__name__)


class ComparisonEngine:
    """AI-powered engine for comparing BSS requirements using CrewAI"""

    def __init__(self, config: Dict):
        self.config = config
        self.api_key = get_api_key(config.get('llm', {}).get('provider', 'openai'))

        # Initialize LLM
        llm_config = config.get('llm', {})
        self.llm = ChatOpenAI(
            model=llm_config.get('model', 'gpt-4'),
            temperature=llm_config.get('temperature', 0.3),
            openai_api_key=self.api_key
        )

        # Initialize embeddings for semantic similarity
        self.embeddings = OpenAIEmbeddings(
            model=llm_config.get('embedding_model', 'text-embedding-ada-002'),
            openai_api_key=self.api_key
        )

        # Thresholds
        comparison_config = config.get('comparison', {})
        self.exact_threshold = comparison_config.get('exact_match_threshold', 0.95)
        self.similar_threshold = comparison_config.get('similar_match_threshold', 0.70)

        logger.info("Comparison engine initialized")

    def compare_features(
        self,
        new_features: List[Feature],
        existing_features: List[Feature]
    ) -> Tuple[List[MatchPair], List[MatchPair], List[Feature]]:
        """
        Compare new features against existing features using AI

        Returns:
            Tuple of (exact_matches, similar_matches, delta_features)
        """
        logger.info(f"Comparing {len(new_features)} new features against {len(existing_features)} existing features")

        exact_matches = []
        similar_matches = []
        delta_features = []

        # Create embeddings for all features
        new_embeddings = self._create_embeddings(new_features)
        existing_embeddings = self._create_embeddings(existing_features)

        # Track which existing features have been matched
        matched_existing_indices = set()

        # Compare each new feature
        for i, new_feature in enumerate(new_features):
            best_match = None
            best_score = 0.0
            best_index = -1

            # Find best matching existing feature
            for j, existing_feature in enumerate(existing_features):
                if j in matched_existing_indices:
                    continue

                # Calculate similarity using embeddings
                similarity = self._calculate_similarity(
                    new_embeddings[i],
                    existing_embeddings[j]
                )

                if similarity > best_score:
                    best_score = similarity
                    best_match = existing_feature
                    best_index = j

            # Categorize based on similarity score
            if best_score >= self.exact_threshold:
                # Exact match
                match_pair = MatchPair(
                    new_feature=new_feature,
                    existing_feature=best_match,
                    similarity_score=best_score,
                    match_type="exact"
                )
                exact_matches.append(match_pair)
                matched_existing_indices.add(best_index)
                logger.debug(f"Exact match: {new_feature.title} <-> {best_match.title} ({best_score:.2f})")

            elif best_score >= self.similar_threshold:
                # Similar match - needs gap analysis
                gap_analysis = self._analyze_gap(new_feature, best_match)
                match_pair = MatchPair(
                    new_feature=new_feature,
                    existing_feature=best_match,
                    similarity_score=best_score,
                    match_type="similar",
                    gap_analysis=gap_analysis
                )
                similar_matches.append(match_pair)
                matched_existing_indices.add(best_index)
                logger.debug(f"Similar match: {new_feature.title} <-> {best_match.title} ({best_score:.2f})")

            else:
                # Delta - new feature
                delta_features.append(new_feature)
                logger.debug(f"Delta feature: {new_feature.title} (best score: {best_score:.2f})")

        logger.info(f"Comparison complete: {len(exact_matches)} exact, {len(similar_matches)} similar, {len(delta_features)} delta")

        return exact_matches, similar_matches, delta_features

    def _create_embeddings(self, features: List[Feature]) -> List[np.ndarray]:
        """Create embeddings for features"""
        try:
            # Combine title and description for better context
            texts = [f"{f.title}. {f.description}" for f in features]

            # Get embeddings from OpenAI
            embeddings = self.embeddings.embed_documents(texts)

            return [np.array(emb) for emb in embeddings]

        except Exception as e:
            logger.error(f"Error creating embeddings: {e}")
            # Fallback to basic text comparison
            return [np.zeros(1536) for _ in features]  # OpenAI embedding dimension

    def _calculate_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        """Calculate cosine similarity between two embeddings"""
        try:
            # Cosine similarity
            dot_product = np.dot(emb1, emb2)
            norm1 = np.linalg.norm(emb1)
            norm2 = np.linalg.norm(emb2)

            if norm1 == 0 or norm2 == 0:
                return 0.0

            similarity = dot_product / (norm1 * norm2)

            # Convert from [-1, 1] to [0, 1]
            similarity = (similarity + 1) / 2

            return float(similarity)

        except Exception as e:
            logger.error(f"Error calculating similarity: {e}")
            return 0.0

    def _analyze_gap(self, new_feature: Feature, existing_feature: Feature) -> str:
        """
        Use LLM to analyze the gap between similar features

        Args:
            new_feature: New requirement
            existing_feature: Existing implementation

        Returns:
            Gap analysis description
        """
        try:
            prompt = f"""You are a BSS requirements analyst. Compare these two telecom features and identify the gaps.

NEW REQUIREMENT:
Title: {new_feature.title}
Description: {new_feature.description}

EXISTING IMPLEMENTATION:
Title: {existing_feature.title}
Description: {existing_feature.description}

Provide a concise gap analysis (2-3 sentences) explaining:
1. What additional capabilities the new requirement needs
2. What modifications to the existing implementation would be required

Gap Analysis:"""

            response = self.llm.invoke(prompt)
            gap_analysis = response.content.strip()

            return gap_analysis

        except Exception as e:
            logger.error(f"Error in gap analysis: {e}")
            return "Unable to perform detailed gap analysis. Manual review recommended."

    def generate_recommendations(
        self,
        exact_matches: List[MatchPair],
        similar_matches: List[MatchPair],
        delta_features: List[Feature]
    ) -> List[str]:
        """
        Generate strategic recommendations using CrewAI

        Args:
            exact_matches: List of exact matches
            similar_matches: List of similar matches
            delta_features: List of new features

        Returns:
            List of recommendation strings
        """
        try:
            # Create analysis agent
            analyst = Agent(
                role='BSS Requirements Strategist',
                goal='Analyze feature comparison results and provide actionable recommendations',
                backstory='You are an expert in telecom BSS systems with deep knowledge of feature reuse and implementation strategies.',
                verbose=True,
                llm=self.llm
            )

            # Prepare summary
            summary = f"""
Feature Comparison Results:
- Exact Matches: {len(exact_matches)} features can be reused as-is
- Similar Features: {len(similar_matches)} features need adaptation
- New Features (Delta): {len(delta_features)} features require fresh implementation

Total Reusability: {(len(exact_matches) + len(similar_matches)) / (len(exact_matches) + len(similar_matches) + len(delta_features)) * 100:.1f}%
"""

            # Create recommendation task
            task = Task(
                description=f"""Based on this feature comparison analysis:

{summary}

Provide 4-5 strategic recommendations for the implementation team. Focus on:
1. How to maximize reuse of exact matches
2. Strategy for adapting similar features
3. Prioritization approach for delta features
4. Risk mitigation and timeline considerations

Format as a numbered list.""",
                agent=analyst,
                expected_output="Numbered list of 4-5 strategic recommendations"
            )

            # Create crew and execute
            crew = Crew(
                agents=[analyst],
                tasks=[task],
                process=Process.sequential,
                verbose=self.config.get('crewai', {}).get('verbose', False)
            )

            result = crew.kickoff()

            # Parse recommendations
            recommendations = []
            if result:
                lines = str(result).split('\n')
                for line in lines:
                    line = line.strip()
                    if line and (line[0].isdigit() or line.startswith('-')):
                        recommendations.append(line)

            return recommendations if recommendations else [
                "1. Prioritize reuse of exact match features to accelerate implementation",
                "2. Create adaptation roadmap for similar features with gap analysis",
                "3. Assess delta features for complexity and dependencies",
                "4. Consider phased rollout approach for new capabilities"
            ]

        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return [
                "1. Review exact matches for immediate reuse opportunities",
                "2. Analyze similar features for required adaptations",
                "3. Plan implementation strategy for delta features",
                "4. Conduct detailed technical assessment before starting"
            ]
