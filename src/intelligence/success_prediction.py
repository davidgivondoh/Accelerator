"""
Success Prediction Model for Growth Engine

Predicts likelihood of success for opportunities based on user profile,
opportunity characteristics, market conditions, and historical patterns.
"""

import math
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict, Counter

from .user_profiles import global_profile_engine, UserProfile, InteractionType
from .data_enrichment import global_enrichment_service
from .nlp_processor import global_processor


class PredictionType(Enum):
    """Types of success predictions"""
    APPLICATION_SUCCESS = "application_success"
    INTERVIEW_SUCCESS = "interview_success" 
    OFFER_LIKELIHOOD = "offer_likelihood"
    OVERALL_FIT = "overall_fit"
    TIME_TO_OUTCOME = "time_to_outcome"


class ConfidenceLevel(Enum):
    """Confidence levels for predictions"""
    HIGH = "high"       # 85%+ confidence
    MEDIUM = "medium"   # 65-84% confidence
    LOW = "low"         # 45-64% confidence
    UNCERTAIN = "uncertain"  # <45% confidence


@dataclass
class SuccessPrediction:
    """Individual success prediction result"""
    prediction_type: PredictionType
    success_probability: float  # 0.0 to 1.0
    confidence_level: ConfidenceLevel
    contributing_factors: List[str]
    risk_factors: List[str]
    recommendations: List[str]
    timestamp: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'prediction_type': self.prediction_type.value,
            'success_probability': self.success_probability,
            'success_percentage': f"{self.success_probability * 100:.1f}%",
            'confidence_level': self.confidence_level.value,
            'contributing_factors': self.contributing_factors,
            'risk_factors': self.risk_factors,
            'recommendations': self.recommendations,
            'timestamp': self.timestamp.isoformat()
        }


@dataclass
class ComprehensivePrediction:
    """Complete success prediction analysis"""
    user_id: str
    opportunity_id: str
    predictions: List[SuccessPrediction]
    overall_score: float
    summary: str
    generated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'opportunity_id': self.opportunity_id,
            'predictions': [p.to_dict() for p in self.predictions],
            'overall_score': self.overall_score,
            'overall_percentage': f"{self.overall_score * 100:.1f}%",
            'summary': self.summary,
            'generated_at': self.generated_at.isoformat(),
            'total_predictions': len(self.predictions)
        }


class UserProfileAnalyzer:
    """Analyzes user profile factors for success prediction"""
    
    def analyze_profile_strength(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Analyze overall profile strength and completeness"""
        
        # Profile completeness factors
        completeness_score = 0.0
        completeness_factors = []
        
        # Basic profile elements
        if user_profile.preferences:
            completeness_score += 0.2
            completeness_factors.append("Has defined preferences")
        
        if user_profile.interaction_history:
            completeness_score += 0.3
            completeness_factors.append("Active engagement history")
        
        if user_profile.skills:
            completeness_score += 0.2
            completeness_factors.append("Skills defined")
        
        # Engagement quality
        recent_interactions = [
            i for i in user_profile.interaction_history
            if i.timestamp > datetime.utcnow() - timedelta(days=30)
        ]
        
        if len(recent_interactions) > 10:
            completeness_score += 0.15
            completeness_factors.append("High recent activity")
        elif len(recent_interactions) > 5:
            completeness_score += 0.1
            completeness_factors.append("Moderate recent activity")
        
        # Interest diversity
        interaction_types = set(i.interaction_type for i in recent_interactions)
        if len(interaction_types) >= 3:
            completeness_score += 0.15
            completeness_factors.append("Diverse engagement patterns")
        
        return {
            'completeness_score': min(completeness_score, 1.0),
            'contributing_factors': completeness_factors,
            'recent_activity_count': len(recent_interactions),
            'profile_age_days': (datetime.utcnow() - user_profile.created_at).days
        }
    
    def calculate_experience_factor(self, user_profile: UserProfile) -> float:
        """Calculate user experience factor based on platform usage"""
        
        profile_age = datetime.utcnow() - user_profile.created_at
        total_interactions = len(user_profile.interaction_history)
        
        # Base experience from profile age (diminishing returns)
        age_factor = min(profile_age.days / 90, 1.0)  # Max out at 90 days
        
        # Experience from interaction volume
        interaction_factor = min(total_interactions / 50, 1.0)  # Max out at 50 interactions
        
        # Combine factors
        experience_score = (age_factor * 0.3) + (interaction_factor * 0.7)
        
        return experience_score
    
    def analyze_historical_success(self, user_profile: UserProfile) -> Dict[str, Any]:
        """Analyze user's historical success patterns"""
        
        # Count successful outcomes from interaction history
        apply_interactions = [
            i for i in user_profile.interaction_history
            if i.interaction_type == InteractionType.APPLY
        ]
        
        save_interactions = [
            i for i in user_profile.interaction_history
            if i.interaction_type == InteractionType.SAVE
        ]
        
        view_interactions = [
            i for i in user_profile.interaction_history
            if i.interaction_type == InteractionType.VIEW
        ]
        
        # Calculate success indicators
        total_views = len(view_interactions)
        total_saves = len(save_interactions)
        total_applications = len(apply_interactions)
        
        # Application conversion rate
        application_rate = (total_applications / total_views) if total_views > 0 else 0
        
        # Save rate (interest indicator)
        save_rate = (total_saves / total_views) if total_views > 0 else 0
        
        return {
            'total_applications': total_applications,
            'application_conversion_rate': application_rate,
            'save_rate': save_rate,
            'engagement_quality': (application_rate * 0.7) + (save_rate * 0.3),
            'success_indicators': {
                'active_applicant': application_rate > 0.1,
                'selective_saver': save_rate > 0.05,
                'high_engagement': total_views > 20
            }
        }


class OpportunityAnalyzer:
    """Analyzes opportunity characteristics for success prediction"""
    
    def analyze_opportunity_attractiveness(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze how attractive/competitive an opportunity is"""
        
        # Extract key characteristics
        title = opportunity.get('title', '').lower()
        description = opportunity.get('description', '').lower()
        company = opportunity.get('company', '').lower()
        
        # Competitive keywords (indicate high competition)
        competitive_keywords = [
            'senior', 'lead', 'principal', 'director', 'manager',
            'google', 'apple', 'microsoft', 'amazon', 'meta',
            'startup', 'equity', 'remote', 'flexible'
        ]
        
        # Less competitive keywords
        accessible_keywords = [
            'entry', 'junior', 'associate', 'intern', 'trainee',
            'part-time', 'contract', 'freelance', 'temporary'
        ]
        
        # Count keyword matches
        competitive_score = sum(1 for kw in competitive_keywords if kw in title + ' ' + description)
        accessible_score = sum(1 for kw in accessible_keywords if kw in title + ' ' + description)
        
        # Analyze salary data for competitiveness
        salary_data = opportunity.get('salary_data', {})
        salary_competitiveness = 0.5  # Default moderate
        
        if salary_data:
            min_salary = salary_data.get('min_amount', 0)
            if min_salary > 100000:
                salary_competitiveness = 0.8  # High competition
            elif min_salary > 60000:
                salary_competitiveness = 0.6  # Moderate-high
            elif min_salary > 30000:
                salary_competitiveness = 0.4  # Moderate-low
            else:
                salary_competitiveness = 0.2  # Lower competition
        
        # Calculate overall competitiveness
        keyword_competitiveness = (competitive_score * 0.1) / max(accessible_score * 0.05, 1)
        overall_competitiveness = min((keyword_competitiveness * 0.6) + (salary_competitiveness * 0.4), 1.0)
        
        return {
            'competitiveness_score': overall_competitiveness,
            'salary_competitiveness': salary_competitiveness,
            'competitive_keywords_found': competitive_score,
            'accessible_keywords_found': accessible_score,
            'competition_level': (
                'very_high' if overall_competitiveness > 0.8 else
                'high' if overall_competitiveness > 0.6 else
                'moderate' if overall_competitiveness > 0.4 else
                'low'
            )
        }
    
    def calculate_fit_score(
        self, 
        user_profile: UserProfile, 
        opportunity: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate how well opportunity fits user profile"""
        
        # Get opportunity intelligence
        intelligence_data = opportunity.get('intelligence', {})
        if not intelligence_data:
            # Process opportunity if not already analyzed
            intelligence_data = global_processor.classify_opportunity(opportunity.get('description', ''))
        
        # Extract key elements
        opp_type = intelligence_data.get('opportunity_type', 'unknown')
        opp_skills = intelligence_data.get('skills', [])
        opp_industry = opportunity.get('company_data', {}).get('industry', '')
        
        # Skills matching
        user_skills = set(skill.lower() for skill in user_profile.skills)
        opp_skills_set = set(skill.lower() for skill in opp_skills)
        
        skills_overlap = len(user_skills.intersection(opp_skills_set))
        skills_total = len(user_skills.union(opp_skills_set))
        skills_match_score = skills_overlap / skills_total if skills_total > 0 else 0
        
        # Preference matching
        preference_match_score = 0.0
        if user_profile.preferences:
            # Check if opportunity type matches preferences
            preferred_types = user_profile.preferences.get('opportunity_types', [])
            if opp_type in preferred_types:
                preference_match_score += 0.4
            
            # Check location preferences
            location_data = opportunity.get('location_data', {})
            if location_data:
                user_location_prefs = user_profile.preferences.get('locations', [])
                opp_location = location_data.get('country', '').lower()
                
                if opp_location in [loc.lower() for loc in user_location_prefs]:
                    preference_match_score += 0.3
                elif location_data.get('is_remote') and 'remote' in user_location_prefs:
                    preference_match_score += 0.4
            
            # Check salary preferences
            salary_data = opportunity.get('salary_data', {})
            if salary_data:
                min_salary_pref = user_profile.preferences.get('min_salary', 0)
                opp_min_salary = salary_data.get('min_amount', 0)
                
                if opp_min_salary >= min_salary_pref:
                    preference_match_score += 0.3
        
        # Historical interest alignment
        user_interactions = user_profile.interaction_history
        similar_type_interactions = [
            i for i in user_interactions
            if i.context.get('opportunity_type') == opp_type
        ]
        
        historical_interest = len(similar_type_interactions) / len(user_interactions) if user_interactions else 0
        
        # Overall fit score
        overall_fit = (
            skills_match_score * 0.4 +
            preference_match_score * 0.4 +
            historical_interest * 0.2
        )
        
        return {
            'overall_fit_score': overall_fit,
            'skills_match_score': skills_match_score,
            'preference_match_score': preference_match_score,
            'historical_interest_score': historical_interest,
            'matching_skills': list(user_skills.intersection(opp_skills_set)),
            'skills_gap': list(opp_skills_set - user_skills),
            'fit_level': (
                'excellent' if overall_fit > 0.8 else
                'good' if overall_fit > 0.6 else
                'moderate' if overall_fit > 0.4 else
                'poor'
            )
        }


class MarketAnalyzer:
    """Analyzes market conditions affecting success probability"""
    
    def analyze_market_conditions(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze current market conditions for opportunity type"""
        
        # Extract market indicators
        opp_type = opportunity.get('intelligence', {}).get('opportunity_type', 'unknown')
        industry = opportunity.get('company_data', {}).get('industry', 'unknown')
        location_data = opportunity.get('location_data', {})
        
        # Market demand indicators (simplified analysis)
        high_demand_types = [
            'software_engineering', 'data_science', 'machine_learning',
            'cybersecurity', 'product_management', 'ux_design'
        ]
        
        moderate_demand_types = [
            'marketing', 'sales', 'business_analyst', 'project_manager'
        ]
        
        # Determine demand level
        if opp_type in high_demand_types:
            demand_level = 'high'
            demand_score = 0.8
        elif opp_type in moderate_demand_types:
            demand_level = 'moderate'
            demand_score = 0.6
        else:
            demand_level = 'variable'
            demand_score = 0.5
        
        # Location market factors
        location_factor = 0.5  # Default
        if location_data:
            if location_data.get('is_remote'):
                location_factor = 0.7  # Remote work is competitive but accessible
            else:
                # Tech hubs are more competitive
                location = location_data.get('country', '').lower()
                tech_hubs = ['united states', 'canada', 'united kingdom', 'germany', 'netherlands']
                if location in tech_hubs:
                    location_factor = 0.6
        
        # Overall market favorability
        market_favorability = (demand_score * 0.7) + (location_factor * 0.3)
        
        return {
            'demand_level': demand_level,
            'demand_score': demand_score,
            'location_factor': location_factor,
            'market_favorability': market_favorability,
            'market_insights': [
                f"Opportunity type '{opp_type}' has {demand_level} market demand",
                f"Location market factor: {location_factor:.1f}",
                f"Overall market conditions: {'favorable' if market_favorability > 0.6 else 'challenging'}"
            ]
        }


class SuccessPredictionEngine:
    """Main engine for predicting success probability"""
    
    def __init__(self):
        self.profile_analyzer = UserProfileAnalyzer()
        self.opportunity_analyzer = OpportunityAnalyzer()
        self.market_analyzer = MarketAnalyzer()
    
    def predict_application_success(
        self, 
        user_id: str, 
        opportunity: Dict[str, Any]
    ) -> SuccessPrediction:
        """Predict probability of application leading to interview"""
        
        user_profile = global_profile_engine.get_profile(user_id)
        if not user_profile:
            # Return low confidence prediction for unknown user
            return SuccessPrediction(
                prediction_type=PredictionType.APPLICATION_SUCCESS,
                success_probability=0.1,
                confidence_level=ConfidenceLevel.UNCERTAIN,
                contributing_factors=[],
                risk_factors=["User profile not found"],
                recommendations=["Complete your profile setup"],
                timestamp=datetime.utcnow()
            )
        
        # Analyze various factors
        profile_strength = self.profile_analyzer.analyze_profile_strength(user_profile)
        fit_analysis = self.opportunity_analyzer.calculate_fit_score(user_profile, opportunity)
        opp_analysis = self.opportunity_analyzer.analyze_opportunity_attractiveness(opportunity)
        market_conditions = self.market_analyzer.analyze_market_conditions(opportunity)
        historical_success = self.profile_analyzer.analyze_historical_success(user_profile)
        
        # Calculate success probability
        factors = {
            'profile_completeness': profile_strength['completeness_score'] * 0.15,
            'opportunity_fit': fit_analysis['overall_fit_score'] * 0.35,
            'market_conditions': market_conditions['market_favorability'] * 0.20,
            'historical_performance': historical_success['engagement_quality'] * 0.20,
            'competition_adjustment': (1 - opp_analysis['competitiveness_score']) * 0.10
        }
        
        base_probability = sum(factors.values())
        
        # Apply experience multiplier
        experience_factor = self.profile_analyzer.calculate_experience_factor(user_profile)
        final_probability = min(base_probability * (0.8 + experience_factor * 0.4), 1.0)
        
        # Determine confidence level
        confidence_indicators = [
            profile_strength['completeness_score'] > 0.7,
            fit_analysis['overall_fit_score'] > 0.6,
            historical_success['total_applications'] > 3,
            len(user_profile.interaction_history) > 10
        ]
        
        confidence_score = sum(confidence_indicators) / len(confidence_indicators)
        
        if confidence_score >= 0.85:
            confidence_level = ConfidenceLevel.HIGH
        elif confidence_score >= 0.65:
            confidence_level = ConfidenceLevel.MEDIUM
        elif confidence_score >= 0.45:
            confidence_level = ConfidenceLevel.LOW
        else:
            confidence_level = ConfidenceLevel.UNCERTAIN
        
        # Generate contributing factors and recommendations
        contributing_factors = []
        risk_factors = []
        recommendations = []
        
        if fit_analysis['overall_fit_score'] > 0.6:
            contributing_factors.append(f"Strong profile fit ({fit_analysis['fit_level']})")
        elif fit_analysis['overall_fit_score'] < 0.4:
            risk_factors.append("Low profile-opportunity fit")
            recommendations.append("Consider developing skills: " + ", ".join(fit_analysis['skills_gap'][:3]))
        
        if profile_strength['completeness_score'] > 0.7:
            contributing_factors.append("Complete and active profile")
        else:
            risk_factors.append("Incomplete profile")
            recommendations.append("Complete your profile with more details")
        
        if opp_analysis['competitiveness_score'] > 0.7:
            risk_factors.append(f"High competition ({opp_analysis['competition_level']})")
            recommendations.append("Tailor application to stand out from competition")
        
        if market_conditions['market_favorability'] > 0.6:
            contributing_factors.append("Favorable market conditions")
        
        if not recommendations:
            recommendations.append("Application looks promising - proceed with confidence")
        
        return SuccessPrediction(
            prediction_type=PredictionType.APPLICATION_SUCCESS,
            success_probability=final_probability,
            confidence_level=confidence_level,
            contributing_factors=contributing_factors,
            risk_factors=risk_factors,
            recommendations=recommendations,
            timestamp=datetime.utcnow()
        )
    
    def predict_overall_fit(
        self, 
        user_id: str, 
        opportunity: Dict[str, Any]
    ) -> SuccessPrediction:
        """Predict overall fit and long-term success potential"""
        
        user_profile = global_profile_engine.get_profile(user_id)
        if not user_profile:
            return SuccessPrediction(
                prediction_type=PredictionType.OVERALL_FIT,
                success_probability=0.0,
                confidence_level=ConfidenceLevel.UNCERTAIN,
                contributing_factors=[],
                risk_factors=["User profile not found"],
                recommendations=["Complete profile setup first"],
                timestamp=datetime.utcnow()
            )
        
        # Comprehensive fit analysis
        fit_analysis = self.opportunity_analyzer.calculate_fit_score(user_profile, opportunity)
        market_conditions = self.market_analyzer.analyze_market_conditions(opportunity)
        
        # Long-term factors
        growth_potential = self._analyze_growth_potential(user_profile, opportunity)
        culture_fit = self._analyze_culture_fit(user_profile, opportunity)
        
        # Calculate overall fit
        fit_components = {
            'skills_alignment': fit_analysis['skills_match_score'] * 0.25,
            'preference_match': fit_analysis['preference_match_score'] * 0.25,
            'growth_potential': growth_potential * 0.25,
            'culture_fit': culture_fit * 0.15,
            'market_alignment': market_conditions['market_favorability'] * 0.10
        }
        
        overall_fit_score = sum(fit_components.values())
        
        # Generate insights
        contributing_factors = []
        risk_factors = []
        recommendations = []
        
        if fit_analysis['skills_match_score'] > 0.7:
            contributing_factors.append("Excellent skills alignment")
        elif fit_analysis['skills_match_score'] < 0.3:
            risk_factors.append("Significant skills gap")
            recommendations.append("Develop core skills before applying")
        
        if growth_potential > 0.7:
            contributing_factors.append("High growth and learning potential")
        
        if culture_fit > 0.6:
            contributing_factors.append("Good culture and value alignment")
        
        if not contributing_factors:
            risk_factors.append("Limited alignment indicators")
        
        if not recommendations:
            if overall_fit_score > 0.7:
                recommendations.append("Excellent fit - prioritize this opportunity")
            elif overall_fit_score > 0.5:
                recommendations.append("Good fit - worth pursuing")
            else:
                recommendations.append("Consider other opportunities that better match your profile")
        
        return SuccessPrediction(
            prediction_type=PredictionType.OVERALL_FIT,
            success_probability=overall_fit_score,
            confidence_level=ConfidenceLevel.HIGH if len(contributing_factors) > 2 else ConfidenceLevel.MEDIUM,
            contributing_factors=contributing_factors,
            risk_factors=risk_factors,
            recommendations=recommendations,
            timestamp=datetime.utcnow()
        )
    
    def _analyze_growth_potential(self, user_profile: UserProfile, opportunity: Dict[str, Any]) -> float:
        """Analyze potential for growth and learning"""
        
        # Check if opportunity offers learning opportunities
        title = opportunity.get('title', '').lower()
        description = opportunity.get('description', '').lower()
        
        growth_keywords = [
            'senior', 'lead', 'growth', 'development', 'learn', 'training',
            'mentor', 'career', 'advancement', 'opportunity'
        ]
        
        growth_score = min(sum(1 for kw in growth_keywords if kw in title + ' ' + description) / 5, 1.0)
        
        # Factor in user's career stage
        experience_factor = self.profile_analyzer.calculate_experience_factor(user_profile)
        
        # New users benefit more from growth opportunities
        if experience_factor < 0.3:
            growth_score *= 1.2
        
        return min(growth_score, 1.0)
    
    def _analyze_culture_fit(self, user_profile: UserProfile, opportunity: Dict[str, Any]) -> float:
        """Analyze cultural fit based on user preferences and company info"""
        
        # Simple culture fit analysis based on available data
        culture_score = 0.5  # Default neutral
        
        # Company size preference
        company_data = opportunity.get('company_data', {})
        if company_data:
            # This would be more sophisticated with real company data
            culture_score += 0.1
        
        # Location preference alignment
        location_data = opportunity.get('location_data', {})
        if location_data and user_profile.preferences:
            user_location_prefs = user_profile.preferences.get('locations', [])
            if location_data.get('is_remote') and 'remote' in user_location_prefs:
                culture_score += 0.3
        
        return min(culture_score, 1.0)
    
    def generate_comprehensive_prediction(
        self, 
        user_id: str, 
        opportunity: Dict[str, Any]
    ) -> ComprehensivePrediction:
        """Generate comprehensive success prediction analysis"""
        
        # Generate individual predictions
        application_prediction = self.predict_application_success(user_id, opportunity)
        fit_prediction = self.predict_overall_fit(user_id, opportunity)
        
        predictions = [application_prediction, fit_prediction]
        
        # Calculate overall score
        overall_score = (
            application_prediction.success_probability * 0.6 +
            fit_prediction.success_probability * 0.4
        )
        
        # Generate summary
        if overall_score > 0.7:
            summary = "Strong candidate with high success probability"
        elif overall_score > 0.5:
            summary = "Moderate fit with reasonable success chances"
        elif overall_score > 0.3:
            summary = "Challenging opportunity requiring preparation"
        else:
            summary = "Low compatibility - consider alternative opportunities"
        
        return ComprehensivePrediction(
            user_id=user_id,
            opportunity_id=opportunity.get('id', ''),
            predictions=predictions,
            overall_score=overall_score,
            summary=summary,
            generated_at=datetime.utcnow()
        )


# Global success prediction engine
global_success_predictor = SuccessPredictionEngine()