"""
User Profile Engine for Growth Engine

Builds dynamic user profiles based on behavior, preferences, and interactions
to enable personalized opportunity recommendations and experiences.
"""

import json
import hashlib
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, Counter
import math


class InteractionType(Enum):
    """Types of user interactions"""
    VIEW = "view"
    CLICK = "click"
    APPLY = "apply"
    SAVE = "save"
    DISMISS = "dismiss"
    SHARE = "share"
    SEARCH = "search"
    FILTER = "filter"
    BOOKMARK = "bookmark"
    RATE = "rate"


class PreferenceType(Enum):
    """Types of user preferences"""
    OPPORTUNITY_TYPE = "opportunity_type"
    LOCATION = "location"
    SALARY_RANGE = "salary_range"
    COMPANY_SIZE = "company_size"
    INDUSTRY = "industry"
    REMOTE_PREFERENCE = "remote_preference"
    EXPERIENCE_LEVEL = "experience_level"
    SKILLS = "skills"
    KEYWORDS = "keywords"


@dataclass
class UserInteraction:
    """Represents a single user interaction"""
    user_id: str
    interaction_type: InteractionType
    opportunity_id: str
    timestamp: datetime
    context: Dict[str, Any]  # Additional context data
    weight: float = 1.0  # Importance weight
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'user_id': self.user_id,
            'interaction_type': self.interaction_type.value,
            'opportunity_id': self.opportunity_id,
            'timestamp': self.timestamp.isoformat(),
            'context': self.context,
            'weight': self.weight
        }


@dataclass
class UserPreference:
    """Represents a user preference"""
    preference_type: PreferenceType
    value: Any
    confidence: float
    source: str  # 'explicit', 'inferred', 'learned'
    updated_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            'preference_type': self.preference_type.value,
            'value': self.value,
            'confidence': self.confidence,
            'source': self.source,
            'updated_at': self.updated_at.isoformat()
        }


@dataclass
class UserProfile:
    """Complete user profile with preferences and behavior"""
    user_id: str
    preferences: Dict[str, UserPreference]
    interaction_history: List[UserInteraction]
    computed_scores: Dict[str, float]
    profile_completeness: float
    last_updated: datetime
    created_at: datetime
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage/API response"""
        return {
            'user_id': self.user_id,
            'preferences': {k: v.to_dict() for k, v in self.preferences.items()},
            'interaction_summary': {
                'total_interactions': len(self.interaction_history),
                'recent_interactions': len([i for i in self.interaction_history 
                                          if (datetime.utcnow() - i.timestamp).days <= 7]),
                'interaction_types': dict(Counter([i.interaction_type.value 
                                                 for i in self.interaction_history]))
            },
            'computed_scores': self.computed_scores,
            'profile_completeness': self.profile_completeness,
            'last_updated': self.last_updated.isoformat(),
            'created_at': self.created_at.isoformat()
        }


class InteractionWeights:
    """Weights for different interaction types"""
    
    WEIGHTS = {
        InteractionType.VIEW: 1.0,
        InteractionType.CLICK: 2.0,
        InteractionType.APPLY: 10.0,
        InteractionType.SAVE: 5.0,
        InteractionType.DISMISS: -2.0,
        InteractionType.SHARE: 7.0,
        InteractionType.SEARCH: 1.5,
        InteractionType.FILTER: 1.0,
        InteractionType.BOOKMARK: 6.0,
        InteractionType.RATE: 8.0
    }
    
    # Time decay factors (how much interactions lose weight over time)
    TIME_DECAY = {
        InteractionType.VIEW: 0.1,      # Views decay quickly
        InteractionType.CLICK: 0.05,    # Clicks decay moderately
        InteractionType.APPLY: 0.01,    # Applications decay slowly
        InteractionType.SAVE: 0.02,     # Saves decay slowly
        InteractionType.DISMISS: 0.2,   # Dismissals decay quickly
        InteractionType.SHARE: 0.02,    # Shares decay slowly
        InteractionType.SEARCH: 0.15,   # Searches decay moderately
        InteractionType.FILTER: 0.1,    # Filters decay moderately
        InteractionType.BOOKMARK: 0.01, # Bookmarks decay very slowly
        InteractionType.RATE: 0.01      # Ratings decay very slowly
    }
    
    @classmethod
    def get_weighted_score(cls, interaction: UserInteraction, current_time: datetime = None) -> float:
        """Calculate weighted score for an interaction with time decay"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        base_weight = cls.WEIGHTS.get(interaction.interaction_type, 1.0)
        interaction_weight = interaction.weight
        
        # Calculate time decay
        days_ago = (current_time - interaction.timestamp).days
        decay_factor = cls.TIME_DECAY.get(interaction.interaction_type, 0.05)
        time_weight = math.exp(-decay_factor * days_ago)
        
        return base_weight * interaction_weight * time_weight


class PreferenceInferrer:
    """Infers user preferences from interactions and opportunity data"""
    
    def __init__(self):
        self.min_interactions_for_inference = 3
        self.confidence_threshold = 0.6
    
    def infer_preferences_from_interactions(
        self, 
        interactions: List[UserInteraction], 
        opportunity_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, UserPreference]:
        """Infer preferences from user interactions"""
        
        preferences = {}
        
        # Get positive interactions (not dismissals)
        positive_interactions = [
            i for i in interactions 
            if i.interaction_type != InteractionType.DISMISS
        ]
        
        if len(positive_interactions) < self.min_interactions_for_inference:
            return preferences
        
        # Infer opportunity type preferences
        type_prefs = self._infer_opportunity_type_preference(positive_interactions, opportunity_data)
        if type_prefs:
            preferences[PreferenceType.OPPORTUNITY_TYPE.value] = type_prefs
        
        # Infer location preferences
        location_prefs = self._infer_location_preference(positive_interactions, opportunity_data)
        if location_prefs:
            preferences[PreferenceType.LOCATION.value] = location_prefs
        
        # Infer salary preferences
        salary_prefs = self._infer_salary_preference(positive_interactions, opportunity_data)
        if salary_prefs:
            preferences[PreferenceType.SALARY_RANGE.value] = salary_prefs
        
        # Infer remote work preference
        remote_prefs = self._infer_remote_preference(positive_interactions, opportunity_data)
        if remote_prefs:
            preferences[PreferenceType.REMOTE_PREFERENCE.value] = remote_prefs
        
        # Infer industry preferences
        industry_prefs = self._infer_industry_preference(positive_interactions, opportunity_data)
        if industry_prefs:
            preferences[PreferenceType.INDUSTRY.value] = industry_prefs
        
        # Infer skill preferences
        skill_prefs = self._infer_skill_preference(positive_interactions, opportunity_data)
        if skill_prefs:
            preferences[PreferenceType.SKILLS.value] = skill_prefs
        
        return preferences
    
    def _infer_opportunity_type_preference(
        self, 
        interactions: List[UserInteraction], 
        opportunity_data: Dict[str, Dict[str, Any]]
    ) -> Optional[UserPreference]:
        """Infer opportunity type preferences"""
        
        type_scores = defaultdict(float)
        
        for interaction in interactions:
            opp_data = opportunity_data.get(interaction.opportunity_id)
            if not opp_data:
                continue
            
            opp_type = opp_data.get('type', 'unknown')
            weight = InteractionWeights.get_weighted_score(interaction)
            type_scores[opp_type] += weight
        
        if not type_scores:
            return None
        
        # Get top preference
        top_type = max(type_scores.items(), key=lambda x: x[1])
        total_score = sum(type_scores.values())
        confidence = top_type[1] / total_score
        
        if confidence >= self.confidence_threshold:
            return UserPreference(
                preference_type=PreferenceType.OPPORTUNITY_TYPE,
                value=top_type[0],
                confidence=confidence,
                source='inferred',
                updated_at=datetime.utcnow()
            )
        
        return None
    
    def _infer_location_preference(
        self, 
        interactions: List[UserInteraction], 
        opportunity_data: Dict[str, Dict[str, Any]]
    ) -> Optional[UserPreference]:
        """Infer location preferences"""
        
        location_scores = defaultdict(float)
        
        for interaction in interactions:
            opp_data = opportunity_data.get(interaction.opportunity_id)
            if not opp_data:
                continue
            
            location_data = opp_data.get('location_data', {})
            if location_data:
                # Prefer normalized location
                location = location_data.get('normalized', location_data.get('original', ''))
                if location:
                    weight = InteractionWeights.get_weighted_score(interaction)
                    location_scores[location] += weight
        
        if not location_scores:
            return None
        
        # Get top preference
        top_location = max(location_scores.items(), key=lambda x: x[1])
        total_score = sum(location_scores.values())
        confidence = top_location[1] / total_score
        
        if confidence >= self.confidence_threshold:
            return UserPreference(
                preference_type=PreferenceType.LOCATION,
                value=top_location[0],
                confidence=confidence,
                source='inferred',
                updated_at=datetime.utcnow()
            )
        
        return None
    
    def _infer_salary_preference(
        self, 
        interactions: List[UserInteraction], 
        opportunity_data: Dict[str, Dict[str, Any]]
    ) -> Optional[UserPreference]:
        """Infer salary range preferences"""
        
        salaries = []
        
        for interaction in interactions:
            opp_data = opportunity_data.get(interaction.opportunity_id)
            if not opp_data:
                continue
            
            salary_data = opp_data.get('salary_data', {})
            if salary_data and salary_data.get('min_amount'):
                weight = InteractionWeights.get_weighted_score(interaction)
                # Use average of min and max if available
                min_sal = salary_data['min_amount']
                max_sal = salary_data.get('max_amount', min_sal)
                avg_salary = (min_sal + max_sal) / 2
                
                # Add weighted salary multiple times based on interaction strength
                for _ in range(int(weight)):
                    salaries.append(avg_salary)
        
        if len(salaries) < 3:
            return None
        
        # Calculate preferred salary range (25th to 75th percentile)
        salaries.sort()
        q25_idx = len(salaries) // 4
        q75_idx = (3 * len(salaries)) // 4
        
        preferred_range = {
            'min': salaries[q25_idx],
            'max': salaries[q75_idx],
            'median': salaries[len(salaries) // 2]
        }
        
        return UserPreference(
            preference_type=PreferenceType.SALARY_RANGE,
            value=preferred_range,
            confidence=0.7,  # Moderate confidence for salary inference
            source='inferred',
            updated_at=datetime.utcnow()
        )
    
    def _infer_remote_preference(
        self, 
        interactions: List[UserInteraction], 
        opportunity_data: Dict[str, Dict[str, Any]]
    ) -> Optional[UserPreference]:
        """Infer remote work preferences"""
        
        remote_score = 0.0
        onsite_score = 0.0
        
        for interaction in interactions:
            opp_data = opportunity_data.get(interaction.opportunity_id)
            if not opp_data:
                continue
            
            location_data = opp_data.get('location_data', {})
            weight = InteractionWeights.get_weighted_score(interaction)
            
            if location_data.get('is_remote'):
                remote_score += weight
            else:
                onsite_score += weight
        
        total_score = remote_score + onsite_score
        if total_score == 0:
            return None
        
        remote_ratio = remote_score / total_score
        
        # Strong preference if > 70% or < 30%
        if remote_ratio > 0.7:
            return UserPreference(
                preference_type=PreferenceType.REMOTE_PREFERENCE,
                value='remote',
                confidence=remote_ratio,
                source='inferred',
                updated_at=datetime.utcnow()
            )
        elif remote_ratio < 0.3:
            return UserPreference(
                preference_type=PreferenceType.REMOTE_PREFERENCE,
                value='onsite',
                confidence=1.0 - remote_ratio,
                source='inferred',
                updated_at=datetime.utcnow()
            )
        else:
            return UserPreference(
                preference_type=PreferenceType.REMOTE_PREFERENCE,
                value='flexible',
                confidence=0.6,
                source='inferred',
                updated_at=datetime.utcnow()
            )
    
    def _infer_industry_preference(
        self, 
        interactions: List[UserInteraction], 
        opportunity_data: Dict[str, Dict[str, Any]]
    ) -> Optional[UserPreference]:
        """Infer industry preferences"""
        
        industry_scores = defaultdict(float)
        
        for interaction in interactions:
            opp_data = opportunity_data.get(interaction.opportunity_id)
            if not opp_data:
                continue
            
            company_data = opp_data.get('company_data', {})
            industry = company_data.get('industry')
            
            if industry:
                weight = InteractionWeights.get_weighted_score(interaction)
                industry_scores[industry] += weight
        
        if not industry_scores:
            return None
        
        # Get top industry
        top_industry = max(industry_scores.items(), key=lambda x: x[1])
        total_score = sum(industry_scores.values())
        confidence = top_industry[1] / total_score
        
        if confidence >= self.confidence_threshold:
            return UserPreference(
                preference_type=PreferenceType.INDUSTRY,
                value=top_industry[0],
                confidence=confidence,
                source='inferred',
                updated_at=datetime.utcnow()
            )
        
        return None
    
    def _infer_skill_preference(
        self, 
        interactions: List[UserInteraction], 
        opportunity_data: Dict[str, Dict[str, Any]]
    ) -> Optional[UserPreference]:
        """Infer skill preferences from opportunity keywords"""
        
        skill_scores = defaultdict(float)
        
        for interaction in interactions:
            opp_data = opportunity_data.get(interaction.opportunity_id)
            if not opp_data:
                continue
            
            # Look for skills in title and description
            title = opp_data.get('title', '').lower()
            description = opp_data.get('description', '').lower()
            keywords = opp_data.get('keywords', [])
            
            weight = InteractionWeights.get_weighted_score(interaction)
            
            # Common tech skills to look for
            tech_skills = [
                'python', 'javascript', 'react', 'node', 'java', 'sql', 'aws', 'docker',
                'machine learning', 'data science', 'ai', 'analytics', 'cloud', 'devops'
            ]
            
            for skill in tech_skills:
                if skill in title or skill in description or skill in keywords:
                    skill_scores[skill] += weight
        
        if not skill_scores:
            return None
        
        # Get top skills
        top_skills = sorted(skill_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        if top_skills and top_skills[0][1] > 0:
            return UserPreference(
                preference_type=PreferenceType.SKILLS,
                value=[skill for skill, score in top_skills],
                confidence=0.6,
                source='inferred',
                updated_at=datetime.utcnow()
            )
        
        return None


class UserProfileEngine:
    """Main engine for managing user profiles"""
    
    def __init__(self):
        self.preference_inferrer = PreferenceInferrer()
        self.profiles: Dict[str, UserProfile] = {}
    
    def create_user_profile(self, user_id: str) -> UserProfile:
        """Create a new user profile"""
        profile = UserProfile(
            user_id=user_id,
            preferences={},
            interaction_history=[],
            computed_scores={},
            profile_completeness=0.0,
            last_updated=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        
        self.profiles[user_id] = profile
        return profile
    
    def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by ID"""
        return self.profiles.get(user_id)
    
    def add_interaction(self, user_id: str, interaction: UserInteraction) -> None:
        """Add a user interaction to their profile"""
        if user_id not in self.profiles:
            self.create_user_profile(user_id)
        
        profile = self.profiles[user_id]
        profile.interaction_history.append(interaction)
        profile.last_updated = datetime.utcnow()
        
        # Keep only recent interactions (last 1000 or 90 days)
        cutoff_date = datetime.utcnow() - timedelta(days=90)
        profile.interaction_history = [
            i for i in profile.interaction_history
            if i.timestamp > cutoff_date
        ][-1000:]  # Keep last 1000 interactions
    
    def update_explicit_preference(
        self, 
        user_id: str, 
        preference_type: PreferenceType, 
        value: Any, 
        confidence: float = 1.0
    ) -> None:
        """Update explicit user preference"""
        if user_id not in self.profiles:
            self.create_user_profile(user_id)
        
        profile = self.profiles[user_id]
        preference = UserPreference(
            preference_type=preference_type,
            value=value,
            confidence=confidence,
            source='explicit',
            updated_at=datetime.utcnow()
        )
        
        profile.preferences[preference_type.value] = preference
        profile.last_updated = datetime.utcnow()
        
        # Recalculate profile completeness
        profile.profile_completeness = self._calculate_profile_completeness(profile)
    
    def infer_preferences(
        self, 
        user_id: str, 
        opportunity_data: Dict[str, Dict[str, Any]]
    ) -> Dict[str, UserPreference]:
        """Infer user preferences from their interactions"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return {}
        
        inferred_prefs = self.preference_inferrer.infer_preferences_from_interactions(
            profile.interaction_history, 
            opportunity_data
        )
        
        # Update profile with inferred preferences (only if not explicitly set)
        for pref_type, preference in inferred_prefs.items():
            if pref_type not in profile.preferences or profile.preferences[pref_type].source == 'inferred':
                profile.preferences[pref_type] = preference
        
        profile.last_updated = datetime.utcnow()
        profile.profile_completeness = self._calculate_profile_completeness(profile)
        
        return inferred_prefs
    
    def calculate_interest_score(
        self, 
        user_id: str, 
        opportunity: Dict[str, Any]
    ) -> float:
        """Calculate user's predicted interest score for an opportunity"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return 0.5  # Neutral score for unknown users
        
        score = 0.0
        total_weight = 0.0
        
        # Score based on opportunity type preference
        opp_type = opportunity.get('type', 'unknown')
        type_pref = profile.preferences.get(PreferenceType.OPPORTUNITY_TYPE.value)
        if type_pref and type_pref.value == opp_type:
            score += type_pref.confidence * 0.3
        total_weight += 0.3
        
        # Score based on location preference
        location_data = opportunity.get('location_data', {})
        location_pref = profile.preferences.get(PreferenceType.LOCATION.value)
        if location_pref and location_data:
            normalized_location = location_data.get('normalized', '')
            if location_pref.value in normalized_location:
                score += location_pref.confidence * 0.2
        total_weight += 0.2
        
        # Score based on remote preference
        remote_pref = profile.preferences.get(PreferenceType.REMOTE_PREFERENCE.value)
        if remote_pref and location_data:
            is_remote = location_data.get('is_remote', False)
            if (remote_pref.value == 'remote' and is_remote) or \
               (remote_pref.value == 'onsite' and not is_remote):
                score += remote_pref.confidence * 0.15
        total_weight += 0.15
        
        # Score based on industry preference
        company_data = opportunity.get('company_data', {})
        industry_pref = profile.preferences.get(PreferenceType.INDUSTRY.value)
        if industry_pref and company_data:
            industry = company_data.get('industry')
            if industry == industry_pref.value:
                score += industry_pref.confidence * 0.2
        total_weight += 0.2
        
        # Score based on salary preference
        salary_data = opportunity.get('salary_data', {})
        salary_pref = profile.preferences.get(PreferenceType.SALARY_RANGE.value)
        if salary_pref and salary_data and isinstance(salary_pref.value, dict):
            opp_salary = salary_data.get('min_amount', 0)
            pref_min = salary_pref.value.get('min', 0)
            pref_max = salary_pref.value.get('max', float('inf'))
            
            if pref_min <= opp_salary <= pref_max:
                score += 0.15
        total_weight += 0.15
        
        # Normalize score
        if total_weight > 0:
            normalized_score = score / total_weight
        else:
            normalized_score = 0.5
        
        # Add baseline for new users or opportunities
        return max(0.1, min(0.9, normalized_score))
    
    def _calculate_profile_completeness(self, profile: UserProfile) -> float:
        """Calculate profile completeness score"""
        total_preferences = len(PreferenceType)
        set_preferences = len(profile.preferences)
        
        # Base completeness from explicit preferences
        preference_score = set_preferences / total_preferences
        
        # Bonus for interaction history
        interaction_bonus = min(len(profile.interaction_history) / 50.0, 0.3)  # Max 30% bonus
        
        return min(preference_score + interaction_bonus, 1.0)
    
    def get_profile_insights(self, user_id: str) -> Dict[str, Any]:
        """Get insights about user profile and behavior"""
        profile = self.get_user_profile(user_id)
        if not profile:
            return {'error': 'Profile not found'}
        
        # Interaction patterns
        interaction_counts = Counter([i.interaction_type.value for i in profile.interaction_history])
        
        # Recent activity (last 30 days)
        recent_cutoff = datetime.utcnow() - timedelta(days=30)
        recent_interactions = [i for i in profile.interaction_history if i.timestamp > recent_cutoff]
        
        # Most active days/times (simplified)
        activity_by_day = defaultdict(int)
        for interaction in recent_interactions:
            day_name = interaction.timestamp.strftime('%A')
            activity_by_day[day_name] += 1
        
        return {
            'profile_completeness': profile.profile_completeness,
            'total_interactions': len(profile.interaction_history),
            'recent_activity': len(recent_interactions),
            'interaction_breakdown': dict(interaction_counts),
            'most_active_day': max(activity_by_day.items(), key=lambda x: x[1])[0] if activity_by_day else None,
            'preferences_set': len(profile.preferences),
            'explicit_preferences': sum(1 for p in profile.preferences.values() if p.source == 'explicit'),
            'inferred_preferences': sum(1 for p in profile.preferences.values() if p.source == 'inferred'),
            'profile_age_days': (datetime.utcnow() - profile.created_at).days,
            'last_activity': profile.last_updated.isoformat()
        }


# Global profile engine instance
global_profile_engine = UserProfileEngine()


def track_user_interaction(
    user_id: str, 
    interaction_type: str, 
    opportunity_id: str, 
    context: Dict[str, Any] = None
) -> None:
    """Convenience function to track user interactions"""
    interaction = UserInteraction(
        user_id=user_id,
        interaction_type=InteractionType(interaction_type),
        opportunity_id=opportunity_id,
        timestamp=datetime.utcnow(),
        context=context or {},
        weight=1.0
    )
    
    global_profile_engine.add_interaction(user_id, interaction)