"""
Intelligence Layer - Adaptive Learning & ML-Powered Scoring

This module provides the intelligence components for the Accelerator system:
- Embedding generation and similarity computation
- Feature engineering for ML models
- XGBoost-based fit scoring
- Outcome tracking and learning
- Adaptive weight optimization
- Analytics and performance dashboards

Components:
    EmbeddingPipeline: Generate and store embeddings for opportunities/profiles
    FeatureEngineer: Extract structured features for ML models
    MLScoringModel: XGBoost classifier for opportunity fit scoring
    LearningAgent: Outcome tracking and adaptive optimization
    AnalyticsEngine: Performance metrics and insights
"""

from src.intelligence.embeddings import (
    EmbeddingPipeline,
    EmbeddingConfig,
    EmbeddingResult,
    SimilarityResult,
)

from src.intelligence.features import (
    FeatureExtractor as FeatureEngineer,
    get_feature_extractor,
)

from src.intelligence.ml_model import (
    MLScoringModel,
)

from src.intelligence.learning import (
    LearningAgent,
    OutcomeTracker,
    PatternAnalyzer,
    WeightOptimizer,
    OutcomeType,
    OutcomeData,
    SuccessPattern,
    WeightAdjustment,
    LearningInsight,
    PerformanceReport,
    record_outcome,
    run_weekly_learning,
)

from src.intelligence.analytics import (
    AnalyticsEngine,
    AnalyticsExporter,
    MetricPeriod,
    FunnelStage,
    TimeSeriesMetric,
    FunnelMetrics,
    CohortAnalysis,
    ROIMetrics,
    DashboardData,
    get_dashboard,
    print_dashboard,
    export_analytics,
)

__all__ = [
    # Embeddings
    "EmbeddingPipeline",
    "EmbeddingConfig",
    "EmbeddingResult",
    "SimilarityResult",
    
    # Features
    "FeatureEngineer",
    "SemanticFeatures",
    "StructuralFeatures",
    "TemporalFeatures",
    "HistoricalFeatures",
    "FeatureVector",
    
    # ML Model
    "MLScoringModel",
    "ModelConfig",
    "PredictionResult",
    "PredictionWithConfidence",
    
    # Learning
    "LearningAgent",
    "OutcomeTracker",
    "PatternAnalyzer",
    "WeightOptimizer",
    "OutcomeType",
    "OutcomeData",
    "SuccessPattern",
    "WeightAdjustment",
    "LearningInsight",
    "PerformanceReport",
    "record_outcome",
    "run_weekly_learning",
    
    # Analytics
    "AnalyticsEngine",
    "AnalyticsExporter",
    "MetricPeriod",
    "FunnelStage",
    "TimeSeriesMetric",
    "FunnelMetrics",
    "CohortAnalysis",
    "ROIMetrics",
    "DashboardData",
    "get_dashboard",
    "print_dashboard",
    "export_analytics",
]
