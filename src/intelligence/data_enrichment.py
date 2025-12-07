"""
Data Enrichment Service for Growth Engine

Enhances opportunity data with additional metadata, standardization,
and intelligent processing to improve search and recommendation quality.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any, Set
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import hashlib


class LocationType(Enum):
    """Location type classifications"""
    CITY = "city"
    STATE = "state"
    COUNTRY = "country"
    REGION = "region"
    REMOTE = "remote"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


@dataclass
class LocationData:
    """Standardized location information"""
    original: str
    normalized: str
    city: Optional[str]
    state: Optional[str]
    country: Optional[str]
    region: Optional[str]
    type: LocationType
    is_remote: bool
    confidence: float


@dataclass
class SalaryData:
    """Standardized salary information"""
    original: str
    min_amount: Optional[float]
    max_amount: Optional[float]
    currency: str
    period: str  # 'annual', 'hourly', 'monthly', 'project'
    is_range: bool
    confidence: float


@dataclass
class CompanyData:
    """Enhanced company information"""
    name: str
    normalized_name: str
    industry: Optional[str]
    size_category: Optional[str]  # 'startup', 'small', 'medium', 'large', 'enterprise'
    estimated_size: Optional[Tuple[int, int]]  # employee range
    is_verified: bool
    confidence: float


class LocationEnricher:
    """Enrich and standardize location data"""
    
    # Location mappings and patterns
    COUNTRY_MAPPINGS = {
        'us': 'United States',
        'usa': 'United States', 
        'united states': 'United States',
        'uk': 'United Kingdom',
        'britain': 'United Kingdom',
        'england': 'United Kingdom',
        'canada': 'Canada',
        'australia': 'Australia',
        'germany': 'Germany',
        'france': 'France',
        'netherlands': 'Netherlands',
        'singapore': 'Singapore',
        'india': 'India',
        'china': 'China',
        'japan': 'Japan'
    }
    
    REGION_MAPPINGS = {
        'north america': ['United States', 'Canada', 'Mexico'],
        'europe': ['United Kingdom', 'Germany', 'France', 'Netherlands', 'Spain', 'Italy'],
        'asia pacific': ['Singapore', 'Australia', 'Japan', 'China', 'India'],
        'middle east': ['UAE', 'Saudi Arabia', 'Israel'],
        'africa': ['South Africa', 'Nigeria', 'Kenya', 'Egypt']
    }
    
    US_STATES = {
        'ca': 'California', 'ny': 'New York', 'tx': 'Texas', 'fl': 'Florida',
        'il': 'Illinois', 'pa': 'Pennsylvania', 'oh': 'Ohio', 'ga': 'Georgia',
        'nc': 'North Carolina', 'mi': 'Michigan', 'nj': 'New Jersey', 'va': 'Virginia',
        'wa': 'Washington', 'az': 'Arizona', 'ma': 'Massachusetts', 'tn': 'Tennessee',
        'in': 'Indiana', 'mo': 'Missouri', 'md': 'Maryland', 'wi': 'Wisconsin',
        'co': 'Colorado', 'mn': 'Minnesota', 'sc': 'South Carolina', 'al': 'Alabama'
    }
    
    REMOTE_INDICATORS = {
        'remote', 'work from home', 'distributed', 'anywhere', 'global',
        'home office', 'virtual', 'telecommute', 'wfh', 'fully remote'
    }
    
    def enrich_location(self, location_text: str) -> LocationData:
        """Enrich location data with structured information"""
        if not location_text:
            return LocationData(
                original="", normalized="", city=None, state=None, 
                country=None, region=None, type=LocationType.UNKNOWN,
                is_remote=False, confidence=0.0
            )
        
        original = location_text.strip()
        normalized = original.lower()
        
        # Check if it's remote
        is_remote = any(indicator in normalized for indicator in self.REMOTE_INDICATORS)
        
        if is_remote:
            return LocationData(
                original=original, normalized="Remote", city=None, state=None,
                country=None, region=None, type=LocationType.REMOTE,
                is_remote=True, confidence=0.9
            )
        
        # Parse location components
        city, state, country, region = self._parse_location_components(normalized)
        
        # Determine location type
        location_type = self._determine_location_type(city, state, country, region)
        
        # Calculate confidence
        confidence = self._calculate_location_confidence(city, state, country, region)
        
        # Create normalized string
        normalized_parts = []
        if city:
            normalized_parts.append(city)
        if state:
            normalized_parts.append(state)
        if country:
            normalized_parts.append(country)
        
        normalized_str = ", ".join(normalized_parts) if normalized_parts else original
        
        return LocationData(
            original=original,
            normalized=normalized_str,
            city=city,
            state=state,
            country=country,
            region=region,
            type=location_type,
            is_remote=is_remote,
            confidence=confidence
        )
    
    def _parse_location_components(self, location: str) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
        """Parse location into components"""
        city, state, country, region = None, None, None, None
        
        # Try to match country first
        for key, value in self.COUNTRY_MAPPINGS.items():
            if key in location:
                country = value
                break
        
        # Try to match US state
        if country == 'United States' or not country:
            for abbr, full_state in self.US_STATES.items():
                if f" {abbr} " in f" {location} " or location.endswith(f" {abbr}"):
                    state = full_state
                    country = 'United States'
                    break
        
        # Extract city (assumes format like "City, State" or "City, Country")
        parts = [part.strip() for part in location.split(',')]
        if len(parts) >= 2:
            potential_city = parts[0].title()
            if len(potential_city) > 1 and potential_city.replace(' ', '').replace('-', '').isalpha():
                city = potential_city
        
        # Determine region
        if country:
            for region_name, countries in self.REGION_MAPPINGS.items():
                if country in countries:
                    region = region_name.title()
                    break
        
        return city, state, country, region
    
    def _determine_location_type(self, city: str, state: str, country: str, region: str) -> LocationType:
        """Determine the primary location type"""
        if city and (state or country):
            return LocationType.CITY
        elif state and country:
            return LocationType.STATE
        elif country:
            return LocationType.COUNTRY
        elif region:
            return LocationType.REGION
        else:
            return LocationType.UNKNOWN
    
    def _calculate_location_confidence(self, city: str, state: str, country: str, region: str) -> float:
        """Calculate confidence in location parsing"""
        score = 0.0
        if city:
            score += 0.4
        if state:
            score += 0.3
        if country:
            score += 0.3
        elif region:
            score += 0.2
        
        return min(score, 1.0)


class SalaryEnricher:
    """Enrich and standardize salary data"""
    
    SALARY_PATTERNS = [
        r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*-?\s*(?:\$\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)?(?:\s*k)?(?:\s*(?:per|\/)\s*(?:year|annum|yr|hour|hr|month|mo))?',
        r'(\d+)k?\s*-\s*(\d+)k?(?:\s*(?:per|\/)\s*(?:year|annum|yr))?',
        r'up to\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*k?',
        r'starting at\s*\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*k?',
        r'salary.*?\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*k?',
        r'compensation.*?\$?\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*k?'
    ]
    
    CURRENCY_SYMBOLS = {
        '$': 'USD',
        '€': 'EUR', 
        '£': 'GBP',
        '¥': 'JPY',
        'C$': 'CAD',
        'A$': 'AUD'
    }
    
    def enrich_salary(self, text: str) -> Optional[SalaryData]:
        """Extract and standardize salary information"""
        if not text:
            return None
        
        text_lower = text.lower()
        
        # Try each salary pattern
        for pattern in self.SALARY_PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return self._process_salary_match(match, text)
        
        return None
    
    def _process_salary_match(self, match, original_text: str) -> SalaryData:
        """Process a salary regex match"""
        groups = match.groups()
        original = match.group(0).strip()
        
        # Extract currency (default to USD)
        currency = 'USD'
        for symbol, curr in self.CURRENCY_SYMBOLS.items():
            if symbol in original:
                currency = curr
                break
        
        # Extract amounts
        amounts = []
        for group in groups:
            if group:
                # Remove commas and convert to float
                clean_amount = re.sub(r'[,$]', '', group)
                try:
                    amount = float(clean_amount)
                    # Handle 'k' notation
                    if 'k' in group.lower() or (amount < 1000 and 'per' not in original_text.lower()):
                        amount *= 1000
                    amounts.append(amount)
                except ValueError:
                    continue
        
        # Determine if it's a range
        is_range = len(amounts) > 1
        min_amount = min(amounts) if amounts else None
        max_amount = max(amounts) if len(amounts) > 1 else min_amount
        
        # Determine period (annual, hourly, monthly)
        period = 'annual'
        if any(word in original_text.lower() for word in ['hour', 'hr', '/hr']):
            period = 'hourly'
        elif any(word in original_text.lower() for word in ['month', 'mo', '/mo']):
            period = 'monthly'
        elif any(word in original_text.lower() for word in ['project', 'contract', 'gig']):
            period = 'project'
        
        # Calculate confidence
        confidence = 0.8 if amounts else 0.3
        if is_range:
            confidence += 0.1
        if currency != 'USD':
            confidence -= 0.1
        
        return SalaryData(
            original=original,
            min_amount=min_amount,
            max_amount=max_amount,
            currency=currency,
            period=period,
            is_range=is_range,
            confidence=max(confidence, 0.1)
        )


class CompanyEnricher:
    """Enrich company information"""
    
    COMPANY_SIZE_INDICATORS = {
        'startup': (1, 50),
        'small': (10, 100),
        'medium': (100, 1000),
        'large': (1000, 10000),
        'enterprise': (10000, 100000)
    }
    
    INDUSTRY_KEYWORDS = {
        'technology': ['tech', 'software', 'ai', 'ml', 'data', 'cloud', 'saas', 'platform'],
        'finance': ['finance', 'fintech', 'bank', 'investment', 'trading', 'crypto'],
        'healthcare': ['health', 'medical', 'pharma', 'biotech', 'hospital', 'care'],
        'education': ['education', 'edtech', 'learning', 'university', 'school', 'academic'],
        'ecommerce': ['ecommerce', 'retail', 'marketplace', 'shopping', 'commerce'],
        'consulting': ['consulting', 'advisory', 'services', 'professional services'],
        'media': ['media', 'entertainment', 'content', 'publishing', 'streaming'],
        'nonprofit': ['nonprofit', 'ngo', 'foundation', 'charity', 'social impact']
    }
    
    def enrich_company(self, company_name: str, description: str = "") -> CompanyData:
        """Enrich company data"""
        if not company_name:
            return CompanyData(
                name="", normalized_name="", industry=None, size_category=None,
                estimated_size=None, is_verified=False, confidence=0.0
            )
        
        normalized_name = self._normalize_company_name(company_name)
        industry = self._detect_industry(company_name, description)
        size_category, estimated_size = self._estimate_company_size(company_name, description)
        
        confidence = self._calculate_company_confidence(
            company_name, industry, size_category
        )
        
        return CompanyData(
            name=company_name.strip(),
            normalized_name=normalized_name,
            industry=industry,
            size_category=size_category,
            estimated_size=estimated_size,
            is_verified=False,  # Would integrate with company database
            confidence=confidence
        )
    
    def _normalize_company_name(self, name: str) -> str:
        """Normalize company name for matching"""
        # Remove common suffixes
        suffixes = ['Inc.', 'Inc', 'LLC', 'Corp.', 'Corp', 'Ltd.', 'Ltd', 'Co.', 'Co']
        normalized = name.strip()
        
        for suffix in suffixes:
            if normalized.endswith(suffix):
                normalized = normalized[:-len(suffix)].strip()
                if normalized.endswith(','):
                    normalized = normalized[:-1].strip()
                break
        
        return normalized
    
    def _detect_industry(self, company_name: str, description: str) -> Optional[str]:
        """Detect company industry from name and description"""
        text = f"{company_name} {description}".lower()
        
        industry_scores = {}
        for industry, keywords in self.INDUSTRY_KEYWORDS.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                industry_scores[industry] = score
        
        if industry_scores:
            return max(industry_scores.items(), key=lambda x: x[1])[0]
        return None
    
    def _estimate_company_size(self, company_name: str, description: str) -> Tuple[Optional[str], Optional[Tuple[int, int]]]:
        """Estimate company size"""
        text = f"{company_name} {description}".lower()
        
        # Look for explicit size indicators
        for size_category, size_range in self.COMPANY_SIZE_INDICATORS.items():
            if size_category in text:
                return size_category, size_range
        
        # Look for employee count patterns
        employee_match = re.search(r'(\d+)\s*(?:-\s*(\d+))?\s*employees', text)
        if employee_match:
            min_emp = int(employee_match.group(1))
            max_emp = int(employee_match.group(2)) if employee_match.group(2) else min_emp
            
            # Categorize based on size
            avg_size = (min_emp + max_emp) / 2
            for category, (min_range, max_range) in self.COMPANY_SIZE_INDICATORS.items():
                if min_range <= avg_size <= max_range:
                    return category, (min_emp, max_emp)
        
        return None, None
    
    def _calculate_company_confidence(self, name: str, industry: str, size_category: str) -> float:
        """Calculate confidence in company data"""
        score = 0.5  # Base score for having a name
        
        if industry:
            score += 0.3
        if size_category:
            score += 0.2
        
        # Boost for well-known company patterns
        if any(indicator in name.lower() for indicator in ['inc', 'corp', 'ltd', 'llc']):
            score += 0.1
        
        return min(score, 1.0)


class DataEnrichmentService:
    """Main service for enriching opportunity data"""
    
    def __init__(self):
        self.location_enricher = LocationEnricher()
        self.salary_enricher = SalaryEnricher()
        self.company_enricher = CompanyEnricher()
    
    def enrich_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich a single opportunity with additional metadata"""
        enriched = opportunity.copy()
        
        # Enrich location data
        location_text = opportunity.get('location', '')
        location_data = self.location_enricher.enrich_location(location_text)
        enriched['location_data'] = {
            'original': location_data.original,
            'normalized': location_data.normalized,
            'city': location_data.city,
            'state': location_data.state,
            'country': location_data.country,
            'region': location_data.region,
            'type': location_data.type.value,
            'is_remote': location_data.is_remote,
            'confidence': location_data.confidence
        }
        
        # Enrich salary data
        description = opportunity.get('description', '')
        title = opportunity.get('title', '')
        salary_text = f"{title} {description}"
        salary_data = self.salary_enricher.enrich_salary(salary_text)
        
        if salary_data:
            enriched['salary_data'] = {
                'original': salary_data.original,
                'min_amount': salary_data.min_amount,
                'max_amount': salary_data.max_amount,
                'currency': salary_data.currency,
                'period': salary_data.period,
                'is_range': salary_data.is_range,
                'confidence': salary_data.confidence
            }
        
        # Enrich company data
        company_name = opportunity.get('company', '')
        company_data = self.company_enricher.enrich_company(company_name, description)
        enriched['company_data'] = {
            'name': company_data.name,
            'normalized_name': company_data.normalized_name,
            'industry': company_data.industry,
            'size_category': company_data.size_category,
            'estimated_size': company_data.estimated_size,
            'is_verified': company_data.is_verified,
            'confidence': company_data.confidence
        }
        
        # Add enrichment metadata
        enriched['enrichment_metadata'] = {
            'enriched_at': datetime.utcnow().isoformat(),
            'enrichment_version': '1.0',
            'fields_enriched': ['location_data', 'salary_data', 'company_data'],
            'data_quality_score': self._calculate_data_quality_score(enriched)
        }
        
        return enriched
    
    def enrich_batch(self, opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Enrich multiple opportunities"""
        return [self.enrich_opportunity(opp) for opp in opportunities]
    
    def _calculate_data_quality_score(self, enriched_opportunity: Dict[str, Any]) -> float:
        """Calculate overall data quality score"""
        score = 0.0
        max_score = 0.0
        
        # Location data quality
        location_data = enriched_opportunity.get('location_data', {})
        if location_data:
            max_score += 1.0
            score += location_data.get('confidence', 0.0)
        
        # Salary data quality
        salary_data = enriched_opportunity.get('salary_data', {})
        if salary_data:
            max_score += 1.0
            score += salary_data.get('confidence', 0.0)
        
        # Company data quality
        company_data = enriched_opportunity.get('company_data', {})
        if company_data:
            max_score += 1.0
            score += company_data.get('confidence', 0.0)
        
        # Basic completeness
        basic_fields = ['title', 'description', 'company', 'location']
        basic_score = sum(1 for field in basic_fields if enriched_opportunity.get(field))
        max_score += len(basic_fields)
        score += basic_score
        
        return score / max_score if max_score > 0 else 0.0
    
    def generate_enrichment_report(self, enriched_opportunities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate a report on enrichment quality and statistics"""
        total_opportunities = len(enriched_opportunities)
        if total_opportunities == 0:
            return {'error': 'No opportunities provided'}
        
        # Quality statistics
        quality_scores = [opp.get('enrichment_metadata', {}).get('data_quality_score', 0) 
                         for opp in enriched_opportunities]
        avg_quality = sum(quality_scores) / len(quality_scores)
        
        # Location statistics
        location_types = {}
        remote_count = 0
        for opp in enriched_opportunities:
            location_data = opp.get('location_data', {})
            loc_type = location_data.get('type', 'unknown')
            location_types[loc_type] = location_types.get(loc_type, 0) + 1
            if location_data.get('is_remote'):
                remote_count += 1
        
        # Salary statistics
        salary_count = sum(1 for opp in enriched_opportunities if opp.get('salary_data'))
        
        # Industry distribution
        industries = {}
        for opp in enriched_opportunities:
            industry = opp.get('company_data', {}).get('industry')
            if industry:
                industries[industry] = industries.get(industry, 0) + 1
        
        return {
            'total_opportunities': total_opportunities,
            'average_data_quality': round(avg_quality, 3),
            'enrichment_coverage': {
                'with_location_data': sum(1 for opp in enriched_opportunities if opp.get('location_data')),
                'with_salary_data': salary_count,
                'with_company_data': sum(1 for opp in enriched_opportunities if opp.get('company_data')),
                'remote_opportunities': remote_count
            },
            'location_distribution': location_types,
            'industry_distribution': industries,
            'quality_distribution': {
                'high_quality': sum(1 for score in quality_scores if score > 0.8),
                'medium_quality': sum(1 for score in quality_scores if 0.5 < score <= 0.8),
                'low_quality': sum(1 for score in quality_scores if score <= 0.5)
            },
            'generated_at': datetime.utcnow().isoformat()
        }


# Global enrichment service
global_enrichment_service = DataEnrichmentService()