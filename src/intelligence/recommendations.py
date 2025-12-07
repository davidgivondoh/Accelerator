"""
Recommendation System for Growth Engine

ML-powered opportunity recommendations based on user profiles, behavior,
and opportunity characteristics using collaborative and content-based filtering.
"""

import numpy as np
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from collections import defaultdict, Counter
import math
import json

from .user_profiles import UserProfile, global_profile_engine, InteractionType
from .data_enrichment import global_enrichment_service


@dataclass
class RecommendationScore:
    """Individual recommendation with score and explanation"""
    opportunity_id: str
    score: float
    confidence: float
    explanation: Dict[str, Any]
    recommendation_type: str  # 'collaborative', 'content', 'hybrid', 'trending'
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'opportunity_id': self.opportunity_id,
            'score': round(self.score, 4),
            'confidence': round(self.confidence, 4),
            'explanation': self.explanation,
            'recommendation_type': self.recommendation_type
        }


@dataclass
class RecommendationResult:
    """Complete recommendation result with metadata"""
    user_id: str
    recommendations: List[RecommendationScore]
    algorithm_performance: Dict[str, float]
    diversity_score: float
    personalization_strength: float
    generated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'user_id': self.user_id,
            'recommendations': [r.to_dict() for r in self.recommendations],
            'algorithm_performance': self.algorithm_performance,
            'diversity_score': round(self.diversity_score, 4),
            'personalization_strength': round(self.personalization_strength, 4),
            'generated_at': self.generated_at.isoformat(),
            'total_recommendations': len(self.recommendations)
        }


class ContentBasedRecommender:
    """Content-based filtering using opportunity features and user preferences"""
    
    def __init__(self):
        self.feature_weights = {
            'opportunity_type': 0.25,
            'location': 0.20,
            'industry': 0.20,
            'salary': 0.15,
            'remote': 0.10,
            'company_size': 0.05,
            'keywords': 0.05
        }
    
    def calculate_content_similarity(
        self, 
        user_profile: UserProfile, 
        opportunity: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """Calculate content-based similarity score"""
        
        score = 0.0
        explanation = {}
        feature_contributions = {}
        
        # Opportunity type similarity
        opp_type = opportunity.get('type', 'unknown')
        type_pref = user_profile.preferences.get('opportunity_type')
        if type_pref and type_pref.value == opp_type:
            type_score = type_pref.confidence * self.feature_weights['opportunity_type']
            score += type_score
            feature_contributions['opportunity_type'] = type_score
            explanation['opportunity_type'] = f"Matches preferred type: {opp_type}"
        
        # Location similarity
        location_data = opportunity.get('location_data', {})
        location_pref = user_profile.preferences.get('location')
        if location_pref and location_data:
            normalized_location = location_data.get('normalized', '')
            if location_pref.value.lower() in normalized_location.lower():
                location_score = location_pref.confidence * self.feature_weights['location']
                score += location_score
                feature_contributions['location'] = location_score
                explanation['location'] = f"Matches preferred location: {location_pref.value}"
        
        # Industry similarity
        company_data = opportunity.get('company_data', {})
        industry_pref = user_profile.preferences.get('industry')
        if industry_pref and company_data:
            industry = company_data.get('industry')
            if industry == industry_pref.value:
                industry_score = industry_pref.confidence * self.feature_weights['industry']
                score += industry_score
                feature_contributions['industry'] = industry_score
                explanation['industry'] = f"Matches preferred industry: {industry}"
        
        # Salary alignment
        salary_data = opportunity.get('salary_data', {})
        salary_pref = user_profile.preferences.get('salary_range')
        if salary_pref and salary_data and isinstance(salary_pref.value, dict):
            opp_salary = salary_data.get('min_amount', 0)
            pref_min = salary_pref.value.get('min', 0)
            pref_max = salary_pref.value.get('max', float('inf'))
            
            if pref_min <= opp_salary <= pref_max:
                salary_score = self.feature_weights['salary']
                score += salary_score
                feature_contributions['salary'] = salary_score
                explanation['salary'] = f"Salary ${opp_salary:,.0f} within preferred range"
        
        # Remote work preference
        remote_pref = user_profile.preferences.get('remote_preference')
        if remote_pref and location_data:
            is_remote = location_data.get('is_remote', False)
            preference_match = False
            
            if remote_pref.value == 'remote' and is_remote:
                preference_match = True
                explanation['remote'] = "Remote position matches preference"
            elif remote_pref.value == 'onsite' and not is_remote:
                preference_match = True
                explanation['remote'] = "On-site position matches preference"
            elif remote_pref.value == 'flexible':
                preference_match = True
                explanation['remote'] = "Flexible work arrangement"
            
            if preference_match:
                remote_score = remote_pref.confidence * self.feature_weights['remote']
                score += remote_score
                feature_contributions['remote'] = remote_score
        
        # Skill/keyword matching
        skills_pref = user_profile.preferences.get('skills')
        if skills_pref and isinstance(skills_pref.value, list):
            opp_text = f"{opportunity.get('title', '')} {opportunity.get('description', '')}".lower()
            matched_skills = []
            
            for skill in skills_pref.value:
                if skill.lower() in opp_text:
                    matched_skills.append(skill)
            
            if matched_skills:
                skill_score = (len(matched_skills) / len(skills_pref.value)) * self.feature_weights['keywords']
                score += skill_score
                feature_contributions['keywords'] = skill_score
                explanation['skills'] = f"Matches skills: {', '.join(matched_skills)}"
        
        return score, {
            'total_score': score,
            'feature_contributions': feature_contributions,
            'explanation': explanation
        }
    
    def get_content_recommendations(
        self, 
        user_id: str, 
        opportunities: List[Dict[str, Any]], 
        limit: int = 10
    ) -> List[RecommendationScore]:
        """Generate content-based recommendations"""
        
        user_profile = global_profile_engine.get_user_profile(user_id)
        if not user_profile:
            return []
        
        recommendations = []
        
        for opp in opportunities:
            similarity_score, explanation = self.calculate_content_similarity(user_profile, opp)
            
            if similarity_score > 0.1:  # Only recommend if some similarity
                rec_score = RecommendationScore(
                    opportunity_id=opp.get('id', ''),
                    score=similarity_score,
                    confidence=min(similarity_score * 2, 1.0),  # Convert to confidence
                    explanation=explanation,
                    recommendation_type='content'
                )
                recommendations.append(rec_score)
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]


class CollaborativeFilteringRecommender:
    """Collaborative filtering based on user interaction patterns"""
    
    def __init__(self):
        self.user_similarity_cache = {}
        self.min_common_interactions = 3
    
    def calculate_user_similarity(
        self, 
        user1_interactions: List[str], 
        user2_interactions: List[str]
    ) -> float:
        """Calculate similarity between two users based on interaction overlap"""
        
        set1 = set(user1_interactions)
        set2 = set(user2_interactions)
        
        if len(set1) == 0 or len(set2) == 0:
            return 0.0
        
        # Jaccard similarity
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        
        if union == 0:
            return 0.0
        
        jaccard_similarity = intersection / union
        
        # Weight by common interaction count
        weight = min(intersection / self.min_common_interactions, 1.0)
        
        return jaccard_similarity * weight
    
    def find_similar_users(
        self, 
        target_user_id: str, 
        all_user_profiles: Dict[str, UserProfile],
        similarity_threshold: float = 0.1
    ) -> List[Tuple[str, float]]:
        """Find users similar to the target user"""
        
        target_profile = all_user_profiles.get(target_user_id)
        if not target_profile:
            return []
        
        # Get positive interactions (excluding dismissals)
        target_interactions = [
            i.opportunity_id for i in target_profile.interaction_history
            if i.interaction_type != InteractionType.DISMISS
        ]
        
        similar_users = []
        
        for user_id, profile in all_user_profiles.items():
            if user_id == target_user_id:
                continue
            
            user_interactions = [
                i.opportunity_id for i in profile.interaction_history
                if i.interaction_type != InteractionType.DISMISS
            ]
            
            similarity = self.calculate_user_similarity(target_interactions, user_interactions)
            
            if similarity >= similarity_threshold:
                similar_users.append((user_id, similarity))
        
        # Sort by similarity and return
        similar_users.sort(key=lambda x: x[1], reverse=True)
        return similar_users[:10]  # Top 10 similar users
    
    def get_collaborative_recommendations(
        self, 
        user_id: str, 
        opportunities: List[Dict[str, Any]], 
        all_user_profiles: Dict[str, UserProfile],
        limit: int = 10
    ) -> List[RecommendationScore]:
        """Generate collaborative filtering recommendations"""
        
        similar_users = self.find_similar_users(user_id, all_user_profiles)
        
        if not similar_users:
            return []
        
        # Get opportunities that similar users interacted with positively
        opportunity_scores = defaultdict(float)
        opportunity_evidence = defaultdict(list)
        
        target_profile = all_user_profiles.get(user_id)
        target_interactions = set(i.opportunity_id for i in target_profile.interaction_history) if target_profile else set()
        
        for similar_user_id, similarity in similar_users:
            similar_profile = all_user_profiles[similar_user_id]
            
            for interaction in similar_profile.interaction_history:
                # Skip if target user already interacted with this opportunity
                if interaction.opportunity_id in target_interactions:
                    continue
                
                # Weight positive interactions more
                interaction_weight = 1.0
                if interaction.interaction_type in [InteractionType.APPLY, InteractionType.SAVE, InteractionType.BOOKMARK]:
                    interaction_weight = 2.0
                elif interaction.interaction_type == InteractionType.DISMISS:
                    interaction_weight = -0.5
                
                weighted_score = similarity * interaction_weight
                opportunity_scores[interaction.opportunity_id] += weighted_score
                opportunity_evidence[interaction.opportunity_id].append({
                    'similar_user_similarity': similarity,
                    'interaction_type': interaction.interaction_type.value,
                    'interaction_weight': interaction_weight
                })
        
        # Convert to recommendations
        recommendations = []
        
        # Create lookup for opportunities
        opp_lookup = {opp.get('id', ''): opp for opp in opportunities}
        
        for opp_id, score in opportunity_scores.items():
            if score > 0 and opp_id in opp_lookup:
                evidence = opportunity_evidence[opp_id]
                
                rec_score = RecommendationScore(
                    opportunity_id=opp_id,
                    score=score,
                    confidence=min(score / len(similar_users), 1.0),
                    explanation={
                        'similar_users_count': len(evidence),
                        'average_similarity': sum(e['similar_user_similarity'] for e in evidence) / len(evidence),
                        'interaction_types': list(set(e['interaction_type'] for e in evidence)),
                        'total_score': score
                    },
                    recommendation_type='collaborative'
                )
                recommendations.append(rec_score)
        
        # Sort by score and return top recommendations
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]


class TrendingRecommender:
    """Recommend trending/popular opportunities"""
    
    def __init__(self):
        self.trending_window_days = 7
        self.min_interactions_for_trending = 5
    
    def calculate_trending_score(
        self, 
        opportunity_id: str, 
        all_user_profiles: Dict[str, UserProfile]
    ) -> Tuple[float, Dict[str, Any]]:
        """Calculate trending score based on recent interactions"""
        
        cutoff_date = datetime.utcnow() - timedelta(days=self.trending_window_days)
        
        recent_interactions = []
        interaction_types = defaultdict(int)
        
        for profile in all_user_profiles.values():
            for interaction in profile.interaction_history:
                if (interaction.opportunity_id == opportunity_id and 
                    interaction.timestamp > cutoff_date):
                    recent_interactions.append(interaction)
                    interaction_types[interaction.interaction_type.value] += 1
        
        if len(recent_interactions) < self.min_interactions_for_trending:
            return 0.0, {}
        
        # Calculate trending score
        total_interactions = len(recent_interactions)
        
        # Weight different interaction types
        weighted_score = 0.0
        for interaction in recent_interactions:
            if interaction.interaction_type == InteractionType.VIEW:
                weighted_score += 1.0
            elif interaction.interaction_type == InteractionType.CLICK:
                weighted_score += 2.0
            elif interaction.interaction_type in [InteractionType.APPLY, InteractionType.SAVE]:
                weighted_score += 5.0
            elif interaction.interaction_type == InteractionType.SHARE:
                weighted_score += 3.0
        
        # Normalize by time (more recent = higher score)
        time_weight = 0.0
        for interaction in recent_interactions:
            days_ago = (datetime.utcnow() - interaction.timestamp).days
            time_weight += math.exp(-0.1 * days_ago)  # Exponential decay
        
        trending_score = (weighted_score * time_weight) / (self.trending_window_days * 10)
        
        return trending_score, {
            'total_interactions': total_interactions,
            'interaction_breakdown': dict(interaction_types),
            'weighted_score': weighted_score,
            'time_weight': time_weight,
            'trending_period_days': self.trending_window_days
        }
    
    def get_trending_recommendations(
        self, 
        opportunities: List[Dict[str, Any]], 
        all_user_profiles: Dict[str, UserProfile],
        limit: int = 10
    ) -> List[RecommendationScore]:
        """Generate trending opportunity recommendations"""
        
        recommendations = []
        
        for opp in opportunities:
            opp_id = opp.get('id', '')
            trending_score, explanation = self.calculate_trending_score(opp_id, all_user_profiles)
            
            if trending_score > 0.1:  # Only recommend if significantly trending
                rec_score = RecommendationScore(
                    opportunity_id=opp_id,
                    score=trending_score,
                    confidence=min(trending_score * 2, 1.0),
                    explanation=explanation,
                    recommendation_type='trending'
                )
                recommendations.append(rec_score)
        
        # Sort by trending score
        recommendations.sort(key=lambda x: x.score, reverse=True)
        return recommendations[:limit]


class HybridRecommendationEngine:
    """Combines multiple recommendation approaches for optimal results"""
    
    def __init__(self):
        self.content_recommender = ContentBasedRecommender()
        self.collaborative_recommender = CollaborativeFilteringRecommender()
        self.trending_recommender = TrendingRecommender()
        
        # Algorithm weights (can be tuned based on A/B testing)
        self.algorithm_weights = {
            'content': 0.4,
            'collaborative': 0.35,
            'trending': 0.15,
            'diversity_bonus': 0.1
        }
    
    def calculate_diversity_score(self, recommendations: List[RecommendationScore]) -> float:
        """Calculate diversity of recommendations"""
        if len(recommendations) <= 1:
            return 1.0
        
        rec_types = [r.recommendation_type for r in recommendations]
        unique_types = len(set(rec_types))
        max_possible_types = len(self.algorithm_weights) - 1  # Exclude diversity_bonus
        
        return unique_types / max_possible_types
    
    def calculate_personalization_strength(
        self, 
        user_id: str, 
        recommendations: List[RecommendationScore]
    ) -> float:
        """Calculate how personalized the recommendations are"""
        user_profile = global_profile_engine.get_user_profile(user_id)
        if not user_profile:
            return 0.0
        
        # Base personalization on profile completeness and interaction history
        profile_strength = user_profile.profile_completeness
        interaction_strength = min(len(user_profile.interaction_history) / 50.0, 1.0)
        
        # Factor in content-based recommendations (more personal)
        content_recs = [r for r in recommendations if r.recommendation_type == 'content']
        content_ratio = len(content_recs) / len(recommendations) if recommendations else 0
        
        return (profile_strength + interaction_strength + content_ratio) / 3
    
    def merge_recommendations(
        self,
        content_recs: List[RecommendationScore],
        collaborative_recs: List[RecommendationScore],
        trending_recs: List[RecommendationScore],
        limit: int = 20
    ) -> List[RecommendationScore]:
        """Merge and rank recommendations from different algorithms"""
        
        # Create a combined scoring system
        all_recs = {}
        
        # Add content-based recommendations
        for rec in content_recs:
            weighted_score = rec.score * self.algorithm_weights['content']
            rec.score = weighted_score
            all_recs[rec.opportunity_id] = rec
        
        # Add collaborative recommendations
        for rec in collaborative_recs:
            weighted_score = rec.score * self.algorithm_weights['collaborative']
            
            if rec.opportunity_id in all_recs:
                # Boost score for opportunities recommended by multiple algorithms
                all_recs[rec.opportunity_id].score += weighted_score
                all_recs[rec.opportunity_id].explanation['hybrid_boost'] = 'Multiple algorithm agreement'
                all_recs[rec.opportunity_id].recommendation_type = 'hybrid'
            else:
                rec.score = weighted_score
                all_recs[rec.opportunity_id] = rec
        
        # Add trending recommendations
        for rec in trending_recs:
            weighted_score = rec.score * self.algorithm_weights['trending']
            
            if rec.opportunity_id in all_recs:
                all_recs[rec.opportunity_id].score += weighted_score
                all_recs[rec.opportunity_id].explanation['trending_boost'] = 'Currently trending'
                if all_recs[rec.opportunity_id].recommendation_type != 'hybrid':
                    all_recs[rec.opportunity_id].recommendation_type = 'hybrid'
            else:
                rec.score = weighted_score
                all_recs[rec.opportunity_id] = rec
        
        # Convert to list and sort
        final_recs = list(all_recs.values())
        final_recs.sort(key=lambda x: x.score, reverse=True)
        
        return final_recs[:limit]
    
    def generate_recommendations(
        self, 
        user_id: str, 
        opportunities: List[Dict[str, Any]],
        limit: int = 20
    ) -> RecommendationResult:
        """Generate hybrid recommendations for a user"""
        
        start_time = datetime.utcnow()
        
        # Get all user profiles for collaborative filtering
        all_profiles = global_profile_engine.profiles
        
        # Generate recommendations from each algorithm
        content_recs = self.content_recommender.get_content_recommendations(
            user_id, opportunities, limit
        )
        
        collaborative_recs = self.collaborative_recommender.get_collaborative_recommendations(
            user_id, opportunities, all_profiles, limit
        )
        
        trending_recs = self.trending_recommender.get_trending_recommendations(
            opportunities, all_profiles, limit
        )
        
        # Merge recommendations
        final_recommendations = self.merge_recommendations(
            content_recs, collaborative_recs, trending_recs, limit
        )
        
        # Calculate performance metrics
        algorithm_performance = {
            'content_recommendations': len(content_recs),
            'collaborative_recommendations': len(collaborative_recs),
            'trending_recommendations': len(trending_recs),
            'final_recommendations': len(final_recommendations),
            'generation_time_ms': (datetime.utcnow() - start_time).total_seconds() * 1000
        }
        
        # Calculate quality metrics
        diversity_score = self.calculate_diversity_score(final_recommendations)
        personalization_strength = self.calculate_personalization_strength(user_id, final_recommendations)
        
        return RecommendationResult(
            user_id=user_id,
            recommendations=final_recommendations,
            algorithm_performance=algorithm_performance,
            diversity_score=diversity_score,
            personalization_strength=personalization_strength,
            generated_at=datetime.utcnow()
        )
    
    def explain_recommendation(
        self, 
        user_id: str, 
        opportunity_id: str
    ) -> Dict[str, Any]:
        """Provide detailed explanation for why an opportunity was recommended"""
        
        user_profile = global_profile_engine.get_user_profile(user_id)
        if not user_profile:
            return {'error': 'User profile not found'}
        
        # This would typically be called after a recommendation was generated
        # For now, return a template explanation
        return {
            'user_id': user_id,
            'opportunity_id': opportunity_id,
            'explanation_type': 'post_hoc',
            'factors': [
                'Based on your interaction history with similar opportunities',
                'Matches your stated preferences for opportunity type and location',
                'Similar users with comparable profiles also engaged with this opportunity',
                'Currently trending among users in your profile category'
            ],
            'confidence': 0.85,
            'recommendation_strength': 'high',
            'generated_at': datetime.utcnow().isoformat()
        }


# Global recommendation engine
global_recommendation_engine = HybridRecommendationEngine()