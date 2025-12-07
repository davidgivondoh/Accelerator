"""
Advanced Filtering System for Growth Engine

Provides sophisticated filtering capabilities for opportunities across
multiple dimensions including type, location, industry, size, etc.
"""

import re
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from dataclasses import dataclass
from enum import Enum


class FilterOperation(Enum):
    """Supported filter operations"""
    EQUALS = "eq"
    NOT_EQUALS = "ne" 
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    IN = "in"
    NOT_IN = "not_in"
    GREATER_THAN = "gt"
    LESS_THAN = "lt"
    GREATER_EQUAL = "gte"
    LESS_EQUAL = "lte"
    REGEX = "regex"
    EXISTS = "exists"
    NOT_EXISTS = "not_exists"


@dataclass
class FilterCriterion:
    """A single filter criterion"""
    field: str
    operation: FilterOperation
    value: Any
    case_sensitive: bool = False


class OpportunityFilter:
    """Advanced filtering system for opportunities"""
    
    # Predefined filter categories for easy access
    CATEGORIES = {
        "scholarships": [
            "scholarship", "fellowship", "grant", "award", 
            "education", "academic", "student", "university"
        ],
        "jobs": [
            "job", "position", "role", "career", "employment", 
            "hiring", "remote", "developer", "engineer"
        ],
        "accelerators": [
            "accelerator", "incubator", "startup", "program", 
            "cohort", "venture", "entrepreneur"
        ],
        "grants": [
            "grant", "funding", "award", "prize", "competition",
            "innovation", "research", "development"
        ],
        "events": [
            "conference", "event", "summit", "workshop", 
            "meetup", "hackathon", "competition"
        ],
        "internships": [
            "intern", "internship", "trainee", "entry-level",
            "graduate", "junior", "apprentice"
        ]
    }
    
    # Location mappings for flexible location filtering
    LOCATION_MAPPINGS = {
        "remote": ["remote", "anywhere", "distributed", "virtual"],
        "us": ["usa", "united states", "america", "us"],
        "uk": ["united kingdom", "britain", "england", "uk"],
        "europe": ["eu", "european", "europe"],
        "africa": ["african", "africa"],
        "asia": ["asian", "asia", "apac"],
        "global": ["worldwide", "international", "global", "any location"]
    }
    
    def __init__(self):
        self.criteria: List[FilterCriterion] = []
    
    def add_criterion(self, field: str, operation: FilterOperation, 
                     value: Any, case_sensitive: bool = False):
        """Add a filter criterion"""
        criterion = FilterCriterion(field, operation, value, case_sensitive)
        self.criteria.append(criterion)
        return self
    
    def clear(self):
        """Clear all filter criteria"""
        self.criteria.clear()
        return self
    
    def filter_text(self, text: str, query: str, operation: FilterOperation = FilterOperation.CONTAINS, 
                   case_sensitive: bool = False) -> bool:
        """Filter text field based on operation"""
        if not text or not query:
            return operation in [FilterOperation.NOT_EXISTS, FilterOperation.NOT_EQUALS]
        
        if not case_sensitive:
            text = text.lower()
            query = str(query).lower()
        
        if operation == FilterOperation.EQUALS:
            return text == query
        elif operation == FilterOperation.NOT_EQUALS:
            return text != query
        elif operation == FilterOperation.CONTAINS:
            return query in text
        elif operation == FilterOperation.NOT_CONTAINS:
            return query not in text
        elif operation == FilterOperation.STARTS_WITH:
            return text.startswith(query)
        elif operation == FilterOperation.ENDS_WITH:
            return text.endswith(query)
        elif operation == FilterOperation.REGEX:
            try:
                return bool(re.search(query, text, re.IGNORECASE if not case_sensitive else 0))
            except re.error:
                return False
        elif operation == FilterOperation.EXISTS:
            return bool(text.strip())
        elif operation == FilterOperation.NOT_EXISTS:
            return not bool(text.strip())
        
        return False
    
    def filter_list(self, items: List[str], query: Union[str, List[str]], 
                   operation: FilterOperation) -> bool:
        """Filter list fields"""
        if not items:
            return operation in [FilterOperation.NOT_EXISTS, FilterOperation.NOT_IN]
        
        if operation == FilterOperation.IN:
            query_list = query if isinstance(query, list) else [query]
            return any(item in query_list for item in items)
        elif operation == FilterOperation.NOT_IN:
            query_list = query if isinstance(query, list) else [query]
            return not any(item in query_list for item in items)
        elif operation == FilterOperation.CONTAINS:
            query_str = str(query).lower()
            return any(query_str in str(item).lower() for item in items)
        
        return False
    
    def filter_numeric(self, value: Union[int, float], query: Union[int, float], 
                      operation: FilterOperation) -> bool:
        """Filter numeric fields"""
        if value is None:
            return operation in [FilterOperation.NOT_EXISTS]
        
        if operation == FilterOperation.EQUALS:
            return value == query
        elif operation == FilterOperation.NOT_EQUALS:
            return value != query
        elif operation == FilterOperation.GREATER_THAN:
            return value > query
        elif operation == FilterOperation.LESS_THAN:
            return value < query
        elif operation == FilterOperation.GREATER_EQUAL:
            return value >= query
        elif operation == FilterOperation.LESS_EQUAL:
            return value <= query
        
        return False
    
    def apply_filters(self, opportunities: List[Dict]) -> List[Dict]:
        """Apply all filter criteria to a list of opportunities"""
        if not self.criteria:
            return opportunities
        
        filtered = []
        
        for opp in opportunities:
            matches = True
            
            for criterion in self.criteria:
                field_value = opp.get(criterion.field)
                
                if isinstance(field_value, str):
                    if not self.filter_text(field_value, criterion.value, 
                                          criterion.operation, criterion.case_sensitive):
                        matches = False
                        break
                        
                elif isinstance(field_value, list):
                    if not self.filter_list(field_value, criterion.value, criterion.operation):
                        matches = False
                        break
                        
                elif isinstance(field_value, (int, float)):
                    if not self.filter_numeric(field_value, criterion.value, criterion.operation):
                        matches = False
                        break
                        
                else:
                    # Handle None or other types
                    if criterion.operation == FilterOperation.EXISTS:
                        if not field_value:
                            matches = False
                            break
                    elif criterion.operation == FilterOperation.NOT_EXISTS:
                        if field_value:
                            matches = False
                            break
            
            if matches:
                filtered.append(opp)
        
        return filtered
    
    def quick_category_filter(self, opportunities: List[Dict], category: str) -> List[Dict]:
        """Quick filter by predefined category"""
        if category not in self.CATEGORIES:
            return opportunities
        
        keywords = self.CATEGORIES[category]
        filtered = []
        
        for opp in opportunities:
            title = opp.get("title", "").lower()
            description = opp.get("description", "").lower()
            company = opp.get("company", "").lower()
            tags = [tag.lower() for tag in opp.get("tags", [])]
            
            # Check if any keyword matches in title, description, company, or tags
            if any(keyword in title or keyword in description or 
                   keyword in company or keyword in " ".join(tags) 
                   for keyword in keywords):
                filtered.append(opp)
        
        return filtered
    
    def quick_location_filter(self, opportunities: List[Dict], location: str) -> List[Dict]:
        """Quick filter by location with smart matching"""
        location_lower = location.lower()
        
        # Check if it's a mapped location
        location_keywords = [location_lower]
        for key, values in self.LOCATION_MAPPINGS.items():
            if location_lower in values:
                location_keywords.extend(values)
                break
        
        filtered = []
        
        for opp in opportunities:
            opp_location = opp.get("location", "").lower()
            opp_remote = opp.get("remote", False)
            
            # Check location field
            if any(keyword in opp_location for keyword in location_keywords):
                filtered.append(opp)
            # Check remote flag for remote searches
            elif "remote" in location_keywords and opp_remote:
                filtered.append(opp)
        
        return filtered
    
    def smart_search(self, opportunities: List[Dict], query: str, 
                    filters: Optional[Dict] = None) -> List[Dict]:
        """Intelligent search with multiple criteria"""
        if not query and not filters:
            return opportunities
        
        results = opportunities
        
        # Apply text search if query provided
        if query:
            query_lower = query.lower()
            text_filtered = []
            
            for opp in results:
                # Search in multiple fields
                searchable_text = " ".join([
                    opp.get("title", ""),
                    opp.get("description", ""),
                    opp.get("company", ""),
                    " ".join(opp.get("tags", [])),
                    opp.get("location", "")
                ]).lower()
                
                if query_lower in searchable_text:
                    text_filtered.append(opp)
            
            results = text_filtered
        
        # Apply additional filters
        if filters:
            if filters.get("type"):
                results = self.quick_category_filter(results, filters["type"])
            
            if filters.get("location"):
                results = self.quick_location_filter(results, filters["location"])
            
            if filters.get("remote") is not None:
                results = [opp for opp in results 
                          if opp.get("remote", False) == filters["remote"]]
            
            if filters.get("min_salary"):
                results = [opp for opp in results 
                          if opp.get("salary", 0) >= filters["min_salary"]]
            
            if filters.get("max_salary"):
                results = [opp for opp in results 
                          if opp.get("salary", float('inf')) <= filters["max_salary"]]
        
        return results


def create_sample_opportunities() -> List[Dict]:
    """Create sample opportunities for testing"""
    return [
        {
            "id": "1",
            "title": "Software Engineer - Remote",
            "company": "TechCorp",
            "description": "Remote software development position for experienced developers",
            "location": "Remote",
            "remote": True,
            "salary": 85000,
            "tags": ["software", "remote", "python", "javascript"],
            "type": "job"
        },
        {
            "id": "2", 
            "title": "Gates Foundation Scholarship",
            "company": "Bill & Melinda Gates Foundation",
            "description": "Full scholarship for African students pursuing STEM degrees",
            "location": "Global",
            "remote": False,
            "salary": 0,
            "tags": ["scholarship", "education", "african", "stem"],
            "type": "scholarship"
        },
        {
            "id": "3",
            "title": "Y Combinator W24",
            "company": "Y Combinator", 
            "description": "Premier startup accelerator program",
            "location": "San Francisco, CA",
            "remote": False,
            "salary": 0,
            "tags": ["accelerator", "startup", "venture"],
            "type": "accelerator"
        }
    ]


# Global filter instance
global_filter = OpportunityFilter()