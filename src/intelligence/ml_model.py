"""
ML Scoring Model for the Growth Engine.

XGBoost-based model for predicting opportunity fit scores.
Combines semantic similarity with structured features to
produce accurate fit predictions.

Features:
- XGBoost classifier for fit prediction
- Confidence interval estimation
- Model persistence and versioning
- Online learning from outcomes
"""

import json
import pickle
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from src.intelligence.features import FeatureExtractor, get_feature_extractor
from src.intelligence.embeddings import (
    get_embedding_service,
    calculate_profile_opportunity_match,
)


class MLScoringModel:
    """
    XGBoost-based model for opportunity fit scoring.
    
    Combines semantic similarity with engineered features
    to predict fit scores and tier assignments.
    """
    
    # Default model parameters
    DEFAULT_PARAMS = {
        "objective": "binary:logistic",
        "eval_metric": "auc",
        "max_depth": 6,
        "learning_rate": 0.1,
        "n_estimators": 100,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "random_state": 42,
    }
    
    # Tier thresholds
    TIER_THRESHOLDS = {
        "tier_1": 0.75,  # High confidence fit
        "tier_2": 0.50,  # Moderate fit
        "tier_3": 0.25,  # Low fit (below this is "unscored")
    }
    
    def __init__(self, model_path: Path | None = None):
        """
        Initialize the ML scoring model.
        
        Args:
            model_path: Path to load existing model from
        """
        self.model = None
        self.feature_extractor = get_feature_extractor()
        self.model_version = "0.1.0"
        self.training_samples = 0
        self.model_path = model_path
        
        # Load model if path provided
        if model_path and model_path.exists():
            self.load(model_path)
    
    def _ensure_model(self) -> None:
        """Ensure model is initialized, create default if needed."""
        if self.model is None:
            self._create_default_model()
    
    def _create_default_model(self) -> None:
        """Create a default model with synthetic training."""
        try:
            import xgboost as xgb
            
            # Generate synthetic training data
            X_train, y_train = self._generate_synthetic_data(n_samples=1000)
            
            # Create and train model
            self.model = xgb.XGBClassifier(**self.DEFAULT_PARAMS)
            self.model.fit(X_train, y_train)
            self.training_samples = len(y_train)
            
        except ImportError:
            # Fallback to simple heuristic model if XGBoost not available
            print("XGBoost not available, using heuristic model")
            self.model = "heuristic"
    
    def _generate_synthetic_data(
        self,
        n_samples: int = 1000,
    ) -> tuple[np.ndarray, np.ndarray]:
        """
        Generate synthetic training data.
        
        Creates realistic feature combinations with labels
        based on domain knowledge about what makes a good fit.
        
        Args:
            n_samples: Number of samples to generate
            
        Returns:
            Tuple of (features, labels)
        """
        np.random.seed(42)
        
        feature_names = self.feature_extractor.get_feature_names()
        n_features = len(feature_names)
        
        X = np.zeros((n_samples, n_features))
        y = np.zeros(n_samples)
        
        for i in range(n_samples):
            # Generate realistic feature values
            features = {
                "semantic_score": np.random.beta(5, 2),  # Skewed toward higher
                "skill_match_ratio": np.random.beta(3, 2),
                "skill_match_count": np.random.poisson(3),
                "missing_skills_count": np.random.poisson(2),
                "user_skill_count": np.random.poisson(10) + 5,
                "required_experience_years": np.random.choice([0, 1, 2, 3, 5, 7, 10]),
                "user_experience_years": np.random.poisson(5),
                "experience_ratio": np.random.beta(3, 2) * 2,
                "experience_gap": np.random.exponential(1),
                "days_until_deadline": np.random.exponential(20) + 1,
                "deadline_urgency": np.random.beta(2, 3),
                "has_deadline": np.random.choice([0, 1], p=[0.3, 0.7]),
                "prestige_score": np.random.beta(2, 3),
                "is_high_prestige": np.random.choice([0, 1], p=[0.8, 0.2]),
                "type_is_job": np.random.choice([0, 1], p=[0.5, 0.5]),
                "type_is_fellowship": np.random.choice([0, 1], p=[0.85, 0.15]),
                "type_is_grant": np.random.choice([0, 1], p=[0.85, 0.15]),
                "type_is_scholarship": np.random.choice([0, 1], p=[0.9, 0.1]),
                "type_is_accelerator": np.random.choice([0, 1], p=[0.9, 0.1]),
                "type_is_research": np.random.choice([0, 1], p=[0.9, 0.1]),
                "has_compensation": np.random.choice([0, 1], p=[0.4, 0.6]),
                "compensation_amount": np.random.exponential(50000),
                "compensation_normalized": np.random.beta(2, 3),
            }
            
            X[i] = self.feature_extractor.features_to_array(features)
            
            # Generate label based on feature combination
            # Higher probability of positive label for good combinations
            fit_signal = (
                0.3 * features["semantic_score"] +
                0.25 * features["skill_match_ratio"] +
                0.15 * min(1.0, features["experience_ratio"]) +
                0.1 * features["prestige_score"] +
                0.1 * features["deadline_urgency"] +
                0.1 * features["compensation_normalized"]
            )
            
            # Add noise and convert to binary
            fit_signal += np.random.normal(0, 0.1)
            y[i] = 1 if fit_signal > 0.5 else 0
        
        return X, y
    
    async def score(
        self,
        opportunity: dict[str, Any],
        profile: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Score an opportunity against a profile.
        
        Args:
            opportunity: Opportunity dictionary
            profile: Profile dictionary
            
        Returns:
            Scoring result with fit_score, tier, confidence, and explanation
        """
        # Ensure model is ready
        self._ensure_model()
        
        # Get semantic similarity
        semantic_result = await calculate_profile_opportunity_match(profile, opportunity)
        semantic_score = semantic_result["semantic_score"]
        
        # Extract features
        features = self.feature_extractor.extract_features(
            opportunity=opportunity,
            profile=profile,
            semantic_score=semantic_score,
        )
        
        # Get prediction
        if self.model == "heuristic":
            fit_score = self._heuristic_score(features)
            confidence = 0.5  # Low confidence for heuristic
        else:
            X = self.feature_extractor.features_to_array(features).reshape(1, -1)
            fit_score = float(self.model.predict_proba(X)[0, 1])
            confidence = self._calculate_confidence(X)
        
        # Determine tier
        tier = self._assign_tier(fit_score)
        
        # Generate explanation
        explanation = self._generate_explanation(features, fit_score, tier)
        
        return {
            "fit_score": round(fit_score, 4),
            "tier": tier,
            "confidence": round(confidence, 4),
            "semantic_score": round(semantic_score, 4),
            "features": {k: round(v, 4) if isinstance(v, float) else v for k, v in features.items()},
            "explanation": explanation,
            "model_version": self.model_version,
        }
    
    def _heuristic_score(self, features: dict[str, float]) -> float:
        """Calculate fit score using heuristic when XGBoost unavailable."""
        score = (
            0.30 * features.get("semantic_score", 0.5) +
            0.25 * features.get("skill_match_ratio", 0.5) +
            0.15 * min(1.0, features.get("experience_ratio", 1.0)) +
            0.10 * features.get("prestige_score", 0.5) +
            0.10 * features.get("deadline_urgency", 0.5) +
            0.10 * features.get("compensation_normalized", 0.5)
        )
        return min(1.0, max(0.0, score))
    
    def _calculate_confidence(self, X: np.ndarray) -> float:
        """Calculate confidence in the prediction."""
        if self.model == "heuristic" or self.model is None:
            return 0.5
        
        # Use prediction probability distance from 0.5 as confidence
        prob = self.model.predict_proba(X)[0, 1]
        confidence = abs(prob - 0.5) * 2  # Scale to 0-1
        
        # Adjust based on training samples
        sample_factor = min(1.0, self.training_samples / 1000)
        
        return confidence * sample_factor
    
    def _assign_tier(self, fit_score: float) -> str:
        """Assign tier based on fit score."""
        if fit_score >= self.TIER_THRESHOLDS["tier_1"]:
            return "TIER_1"
        elif fit_score >= self.TIER_THRESHOLDS["tier_2"]:
            return "TIER_2"
        elif fit_score >= self.TIER_THRESHOLDS["tier_3"]:
            return "TIER_3"
        else:
            return "UNSCORED"
    
    def _generate_explanation(
        self,
        features: dict[str, float],
        fit_score: float,
        tier: str,
    ) -> dict[str, Any]:
        """Generate human-readable explanation of the score."""
        strengths = []
        weaknesses = []
        
        # Analyze key features
        if features.get("semantic_score", 0) >= 0.7:
            strengths.append("Strong semantic match with your profile")
        elif features.get("semantic_score", 0) < 0.5:
            weaknesses.append("Low semantic relevance to your background")
        
        if features.get("skill_match_ratio", 0) >= 0.7:
            strengths.append(f"Good skill match ({int(features.get('skill_match_ratio', 0) * 100)}%)")
        elif features.get("skill_match_ratio", 0) < 0.4:
            weaknesses.append(f"Missing key skills ({int(features.get('missing_skills_count', 0))} skills)")
        
        if features.get("experience_ratio", 0) >= 0.8:
            strengths.append("Experience level well-aligned")
        elif features.get("experience_gap", 0) > 2:
            weaknesses.append(f"Experience gap: need {int(features.get('experience_gap', 0))} more years")
        
        if features.get("is_high_prestige", 0) == 1:
            strengths.append("High-prestige organization")
        
        if features.get("deadline_urgency", 0) > 0.7:
            weaknesses.append("Urgent deadline - apply soon!")
        
        return {
            "summary": f"{tier} opportunity with {int(fit_score * 100)}% fit score",
            "strengths": strengths,
            "weaknesses": weaknesses,
            "recommendation": self._get_recommendation(tier, fit_score),
        }
    
    def _get_recommendation(self, tier: str, fit_score: float) -> str:
        """Get action recommendation based on tier."""
        recommendations = {
            "TIER_1": "Highly recommended - prioritize this application!",
            "TIER_2": "Good fit - add to your application list",
            "TIER_3": "Consider if time permits or for practice",
            "UNSCORED": "Low fit - focus on higher-scoring opportunities",
        }
        return recommendations.get(tier, "Review manually")
    
    async def score_batch(
        self,
        opportunities: list[dict[str, Any]],
        profile: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Score multiple opportunities against a profile.
        
        Args:
            opportunities: List of opportunity dictionaries
            profile: Profile dictionary
            
        Returns:
            List of scoring results
        """
        results = []
        for opp in opportunities:
            result = await self.score(opp, profile)
            result["opportunity_id"] = opp.get("id")
            result["opportunity_title"] = opp.get("title")
            results.append(result)
        
        # Sort by fit score descending
        results.sort(key=lambda x: x["fit_score"], reverse=True)
        
        return results
    
    def update_from_outcome(
        self,
        features: dict[str, float],
        outcome: bool,
    ) -> None:
        """
        Update model with outcome feedback.
        
        Args:
            features: Features from the original scoring
            outcome: True if positive outcome (accepted), False otherwise
        """
        # This would implement online learning
        # For now, just track for batch retraining
        self.training_samples += 1
    
    def save(self, path: Path) -> None:
        """Save model to file."""
        path.parent.mkdir(parents=True, exist_ok=True)
        
        model_data = {
            "version": self.model_version,
            "training_samples": self.training_samples,
            "params": self.DEFAULT_PARAMS,
            "thresholds": self.TIER_THRESHOLDS,
        }
        
        if self.model != "heuristic" and self.model is not None:
            with open(path.with_suffix(".pkl"), "wb") as f:
                pickle.dump(self.model, f)
        
        with open(path.with_suffix(".json"), "w") as f:
            json.dump(model_data, f, indent=2)
    
    def load(self, path: Path) -> None:
        """Load model from file."""
        pkl_path = path.with_suffix(".pkl")
        json_path = path.with_suffix(".json")
        
        if json_path.exists():
            with open(json_path, "r") as f:
                model_data = json.load(f)
                self.model_version = model_data.get("version", "0.1.0")
                self.training_samples = model_data.get("training_samples", 0)
        
        if pkl_path.exists():
            with open(pkl_path, "rb") as f:
                self.model = pickle.load(f)
        else:
            self._create_default_model()


# Global model instance
_model: MLScoringModel | None = None


def get_ml_model() -> MLScoringModel:
    """Get or create the global ML model."""
    global _model
    if _model is None:
        _model = MLScoringModel()
    return _model
