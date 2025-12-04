"""
Data models for BSS requirements comparison
"""
from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class Feature:
    """Represents a single BSS feature requirement"""
    id: str
    title: str
    description: str
    customer: str
    category: Optional[str] = None
    raw_text: Optional[str] = None
    metadata: Dict = field(default_factory=dict)

    def __str__(self):
        return f"Feature({self.id}: {self.title})"

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "customer": self.customer,
            "category": self.category,
            "raw_text": self.raw_text,
            "metadata": self.metadata
        }


@dataclass
class MatchPair:
    """Represents a matched pair of features"""
    new_feature: Feature
    existing_feature: Feature
    similarity_score: float
    match_type: str  # "exact", "similar", "partial"
    gap_analysis: Optional[str] = None

    def to_dict(self):
        return {
            "new_feature": self.new_feature.to_dict(),
            "existing_feature": self.existing_feature.to_dict(),
            "similarity_score": self.similarity_score,
            "match_type": self.match_type,
            "gap_analysis": self.gap_analysis
        }


@dataclass
class ComparisonResult:
    """Results of comparing two requirement documents"""
    new_document: str
    existing_document: str
    new_features_count: int
    existing_features_count: int
    exact_matches: List[MatchPair] = field(default_factory=list)
    similar_features: List[MatchPair] = field(default_factory=list)
    delta_features: List[Feature] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    statistics: Dict = field(default_factory=dict)

    def calculate_statistics(self):
        """Calculate comparison statistics"""
        total_new = self.new_features_count
        matched_count = len(self.exact_matches) + len(self.similar_features)

        self.statistics = {
            "total_new_features": total_new,
            "total_existing_features": self.existing_features_count,
            "exact_matches_count": len(self.exact_matches),
            "similar_matches_count": len(self.similar_features),
            "delta_count": len(self.delta_features),
            "exact_match_percentage": (len(self.exact_matches) / total_new * 100) if total_new > 0 else 0,
            "similar_match_percentage": (len(self.similar_features) / total_new * 100) if total_new > 0 else 0,
            "delta_percentage": (len(self.delta_features) / total_new * 100) if total_new > 0 else 0,
            "reusability_score": (matched_count / total_new * 100) if total_new > 0 else 0
        }
        return self.statistics

    def to_dict(self):
        return {
            "new_document": self.new_document,
            "existing_document": self.existing_document,
            "new_features_count": self.new_features_count,
            "existing_features_count": self.existing_features_count,
            "exact_matches": [m.to_dict() for m in self.exact_matches],
            "similar_features": [m.to_dict() for m in self.similar_features],
            "delta_features": [f.to_dict() for f in self.delta_features],
            "timestamp": self.timestamp,
            "statistics": self.statistics
        }
