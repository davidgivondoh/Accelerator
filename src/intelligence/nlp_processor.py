"""
NLP Processing Pipeline for Growth Engine

Provides intelligent text processing, classification, and entity extraction
for opportunities without requiring heavy ML dependencies.
"""

import re
import json
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum


class OpportunityType(Enum):
    """Opportunity type classifications"""
    JOB = "job"
    SCHOLARSHIP = "scholarship"
    GRANT = "grant"
    FELLOWSHIP = "fellowship"
    ACCELERATOR = "accelerator"
    INTERNSHIP = "internship"
    FREELANCE = "freelance"
    COMPETITION = "competition"
    CONFERENCE = "conference"
    HACKATHON = "hackathon"
    VOLUNTEER = "volunteer"
    UNKNOWN = "unknown"


@dataclass
class ExtractedEntity:
    """Extracted entity with confidence score"""
    type: str
    value: str
    confidence: float
    start_pos: int
    end_pos: int


@dataclass
class ProcessingResult:
    """Result of NLP processing"""
    opportunity_type: OpportunityType
    extracted_entities: Dict[str, List[ExtractedEntity]]
    quality_score: float
    keywords: List[str]
    summary: str
    confidence: float
    processing_time: float


class OpportunityClassifier:
    """Classify opportunities into categories using rule-based approach"""
    
    # Enhanced classification patterns
    TYPE_PATTERNS = {
        OpportunityType.JOB: [
            r'\b(?:job|position|role|career|employment|hiring|vacancy|opening)\b',
            r'\b(?:software|developer|engineer|analyst|manager|director|coordinator)\b',
            r'\b(?:full[- ]?time|part[- ]?time|contract|permanent|temporary)\b',
            r'\b(?:salary|compensation|benefits|401k|insurance)\b'
        ],
        OpportunityType.SCHOLARSHIP: [
            r'\b(?:scholarship|grant|award|funding|tuition|education)\b',
            r'\b(?:student|academic|university|college|degree|study)\b',
            r'\b(?:undergraduate|graduate|phd|masters|bachelor)\b',
            r'\b(?:merit|need[- ]?based|financial aid)\b'
        ],
        OpportunityType.FELLOWSHIP: [
            r'\b(?:fellowship|residency|postdoc|research)\b',
            r'\b(?:fellow|researcher|scientist|academic)\b',
            r'\b(?:stipend|living allowance|research funds)\b'
        ],
        OpportunityType.GRANT: [
            r'\b(?:grant|funding|award|prize|competition)\b',
            r'\b(?:research|innovation|development|project)\b',
            r'\b(?:proposal|application|submission)\b',
            r'\b(?:\$\d+|\d+k|\d+ million|funding up to)\b'
        ],
        OpportunityType.ACCELERATOR: [
            r'\b(?:accelerator|incubator|startup|program|cohort)\b',
            r'\b(?:entrepreneur|founder|business|venture)\b',
            r'\b(?:equity|investment|seed|funding|demo day)\b',
            r'\b(?:pitch|mentor|network|scale)\b'
        ],
        OpportunityType.INTERNSHIP: [
            r'\b(?:intern|internship|trainee|apprentice)\b',
            r'\b(?:entry[- ]?level|junior|graduate|student)\b',
            r'\b(?:summer|semester|12 weeks|6 months)\b',
            r'\b(?:learning|mentorship|training|experience)\b'
        ],
        OpportunityType.COMPETITION: [
            r'\b(?:competition|contest|challenge|hackathon)\b',
            r'\b(?:prize|award|winner|finalist|submission)\b',
            r'\b(?:judged|evaluated|deadline|submission)\b'
        ],
        OpportunityType.CONFERENCE: [
            r'\b(?:conference|summit|symposium|workshop)\b',
            r'\b(?:speaker|presentation|networking|attendee)\b',
            r'\b(?:registration|tickets|venue|agenda)\b'
        ]
    }
    
    def classify(self, text: str, title: str = "", description: str = "") -> Tuple[OpportunityType, float]:
        """Classify opportunity type with confidence score"""
        combined_text = f"{title} {description} {text}".lower()
        
        type_scores = {}
        
        for opp_type, patterns in self.TYPE_PATTERNS.items():
            score = 0
            matches = 0
            
            for pattern in patterns:
                pattern_matches = len(re.findall(pattern, combined_text, re.IGNORECASE))
                if pattern_matches > 0:
                    score += pattern_matches
                    matches += 1
            
            # Weight by number of different patterns matched
            if matches > 0:
                type_scores[opp_type] = score * (matches / len(patterns))
        
        if not type_scores:
            return OpportunityType.UNKNOWN, 0.0
        
        # Get the highest scoring type
        best_type = max(type_scores.items(), key=lambda x: x[1])
        max_score = best_type[1]
        
        # Normalize confidence (0-1 scale)
        confidence = min(max_score / 3.0, 1.0)  # 3+ matches = high confidence
        
        return best_type[0], confidence


class EntityExtractor:
    """Extract structured information from opportunity text"""
    
    # Enhanced extraction patterns
    EXTRACTION_PATTERNS = {
        'salary': [
            r'\$\s*(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:k|thousand)?(?:\s*(?:per|\/)\s*(?:year|annum|yr))?',
            r'(\d+)k\s*(?:per|\/)\s*(?:year|annum|yr)',
            r'salary.*?(\d+(?:,\d{3})*)',
            r'compensation.*?(\d+(?:,\d{3})*)',
            r'(\d+)\s*-\s*(\d+)\s*(?:k|thousand)'
        ],
        'deadline': [
            r'deadline.*?(\d{1,2}\/\d{1,2}\/\d{2,4})',
            r'due.*?(\d{1,2}\/\d{1,2}\/\d{2,4})',
            r'apply by.*?(\d{1,2}\/\d{1,2}\/\d{2,4})',
            r'closes.*?(\d{1,2}\/\d{1,2}\/\d{2,4})',
            r'(\d{1,2}\/\d{1,2}\/\d{2,4})',
            r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{1,2}),?\s+(\d{4})'
        ],
        'location': [
            r'location:?\s*([^,\n]+(?:,\s*[^,\n]+)*)',
            r'based in\s+([^,\n]+)',
            r'located in\s+([^,\n]+)',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([A-Z]{2})\b',  # City, State
            r'\b(remote|work from home|distributed|anywhere)\b'
        ],
        'requirements': [
            r'require(?:ment)?s?:?\s*(.+?)(?:\n\n|\n[A-Z]|$)',
            r'qualifications?:?\s*(.+?)(?:\n\n|\n[A-Z]|$)',
            r'must have:?\s*(.+?)(?:\n\n|\n[A-Z]|$)',
            r'experience.*?:?\s*(.+?)(?:\n\n|\n[A-Z]|$)'
        ],
        'skills': [
            r'\b(python|javascript|react|node\.js|java|c\+\+|sql|mongodb|aws|docker|kubernetes)\b',
            r'\b(machine learning|data science|artificial intelligence|nlp|computer vision)\b',
            r'\b(frontend|backend|full[- ]?stack|devops|cloud|mobile)\b',
            r'\b(\d+\+?\s*years?\s+experience)\b'
        ],
        'company_size': [
            r'(\d+)\s*-\s*(\d+)\s*employees',
            r'(startup|small|medium|large|enterprise)\s*(?:company|organization)',
            r'(\d+)\s*person\s*(?:team|company)'
        ],
        'remote': [
            r'\b(remote|work from home|distributed|fully remote|hybrid)\b',
            r'\b(on-?site|in-?person|office based)\b'
        ]
    }
    
    def extract_entities(self, text: str, title: str = "", description: str = "") -> Dict[str, List[ExtractedEntity]]:
        """Extract structured entities from text"""
        combined_text = f"{title}\n{description}\n{text}"
        entities = {}
        
        for entity_type, patterns in self.EXTRACTION_PATTERNS.items():
            entities[entity_type] = []
            
            for pattern in patterns:
                matches = re.finditer(pattern, combined_text, re.IGNORECASE | re.MULTILINE)
                
                for match in matches:
                    entity = ExtractedEntity(
                        type=entity_type,
                        value=match.group(0).strip(),
                        confidence=0.8,  # Rule-based confidence
                        start_pos=match.start(),
                        end_pos=match.end()
                    )
                    entities[entity_type].append(entity)
        
        return entities
    
    def extract_keywords(self, text: str, top_k: int = 20) -> List[str]:
        """Extract important keywords from text"""
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'we', 'you', 'they', 'it', 'he', 'she'
        }
        
        # Extract words and phrases
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9]+\b', text.lower())
        
        # Filter out stop words and short words
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        
        # Count frequency
        word_freq = {}
        for word in keywords:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top_k
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:top_k]]


class QualityScorer:
    """Calculate quality scores for opportunities"""
    
    def calculate_quality_score(self, opportunity: Dict[str, Any], entities: Dict[str, List[ExtractedEntity]]) -> float:
        """Calculate quality score based on completeness and richness"""
        score = 0.0
        max_score = 10.0
        
        # Basic information completeness (40% of score)
        if opportunity.get('title'):
            score += 1.0
        if opportunity.get('description') and len(opportunity['description']) > 50:
            score += 1.5
        if opportunity.get('company'):
            score += 1.0
        if opportunity.get('location'):
            score += 0.5
        
        # Entity extraction richness (30% of score)
        entity_bonus = 0
        if entities.get('salary'):
            entity_bonus += 0.5
        if entities.get('deadline'):
            entity_bonus += 0.5
        if entities.get('requirements'):
            entity_bonus += 0.5
        if entities.get('skills'):
            entity_bonus += 0.3
        if entities.get('remote'):
            entity_bonus += 0.2
        
        score += min(entity_bonus, 2.0)
        
        # Content quality indicators (20% of score)
        description = opportunity.get('description', '')
        if len(description) > 200:
            score += 0.5
        if len(description) > 500:
            score += 0.5
        
        # URLs and contact information (10% of score)
        if opportunity.get('url'):
            score += 0.3
        if opportunity.get('email') or 'email' in description.lower():
            score += 0.2
        if opportunity.get('application_url'):
            score += 0.5
        
        # Normalize to 0-1 scale
        return min(score / max_score, 1.0)


class OpportunityProcessor:
    """Main NLP processor for opportunities"""
    
    def __init__(self):
        self.classifier = OpportunityClassifier()
        self.extractor = EntityExtractor()
        self.scorer = QualityScorer()
    
    def process_opportunity(self, opportunity: Dict[str, Any]) -> ProcessingResult:
        """Process an opportunity and extract intelligence"""
        start_time = datetime.now()
        
        title = opportunity.get('title', '')
        description = opportunity.get('description', '')
        text = f"{title} {description}"
        
        # Classify opportunity type
        opp_type, type_confidence = self.classifier.classify(text, title, description)
        
        # Extract entities
        entities = self.extractor.extract_entities(text, title, description)
        
        # Extract keywords
        keywords = self.extractor.extract_keywords(text)
        
        # Calculate quality score
        quality_score = self.scorer.calculate_quality_score(opportunity, entities)
        
        # Generate summary
        summary = self._generate_summary(opportunity, entities, opp_type)
        
        # Calculate overall confidence
        confidence = (type_confidence + quality_score) / 2.0
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return ProcessingResult(
            opportunity_type=opp_type,
            extracted_entities=entities,
            quality_score=quality_score,
            keywords=keywords,
            summary=summary,
            confidence=confidence,
            processing_time=processing_time
        )
    
    def _generate_summary(self, opportunity: Dict[str, Any], entities: Dict[str, List[ExtractedEntity]], opp_type: OpportunityType) -> str:
        """Generate a concise summary of the opportunity"""
        title = opportunity.get('title', 'Opportunity')
        company = opportunity.get('company', 'Company')
        
        summary_parts = [f"{opp_type.value.title()}: {title}"]
        
        if company and company.lower() not in title.lower():
            summary_parts.append(f"at {company}")
        
        # Add location if available
        if entities.get('location') and entities['location']:
            location = entities['location'][0].value
            summary_parts.append(f"in {location}")
        
        # Add salary if available
        if entities.get('salary') and entities['salary']:
            salary = entities['salary'][0].value
            summary_parts.append(f"({salary})")
        
        # Add remote info
        if entities.get('remote') and entities['remote']:
            remote_info = entities['remote'][0].value.lower()
            if 'remote' in remote_info:
                summary_parts.append("(Remote)")
        
        return " ".join(summary_parts)
    
    def process_batch(self, opportunities: List[Dict[str, Any]]) -> List[ProcessingResult]:
        """Process multiple opportunities"""
        results = []
        for opp in opportunities:
            try:
                result = self.process_opportunity(opp)
                results.append(result)
            except Exception as e:
                # Log error and continue with next opportunity
                print(f"Error processing opportunity {opp.get('id', 'unknown')}: {e}")
                continue
        
        return results
    
    def get_processing_stats(self, results: List[ProcessingResult]) -> Dict[str, Any]:
        """Get statistics from processing results"""
        if not results:
            return {}
        
        total_results = len(results)
        avg_quality = sum(r.quality_score for r in results) / total_results
        avg_confidence = sum(r.confidence for r in results) / total_results
        avg_processing_time = sum(r.processing_time for r in results) / total_results
        
        # Type distribution
        type_counts = {}
        for result in results:
            opp_type = result.opportunity_type.value
            type_counts[opp_type] = type_counts.get(opp_type, 0) + 1
        
        return {
            'total_processed': total_results,
            'average_quality_score': round(avg_quality, 3),
            'average_confidence': round(avg_confidence, 3),
            'average_processing_time_ms': round(avg_processing_time * 1000, 2),
            'type_distribution': type_counts,
            'high_quality_count': sum(1 for r in results if r.quality_score > 0.7),
            'high_confidence_count': sum(1 for r in results if r.confidence > 0.8)
        }


# Global processor instance
global_processor = OpportunityProcessor()


def process_opportunity_text(opportunity: Dict[str, Any]) -> Dict[str, Any]:
    """Convenience function to process a single opportunity"""
    result = global_processor.process_opportunity(opportunity)
    
    return {
        'opportunity_id': opportunity.get('id'),
        'type': result.opportunity_type.value,
        'quality_score': result.quality_score,
        'confidence': result.confidence,
        'keywords': result.keywords[:10],  # Top 10 keywords
        'summary': result.summary,
        'entities': {k: [{'type': e.type, 'value': e.value, 'confidence': e.confidence} 
                        for e in v[:3]]  # Top 3 entities per type
                    for k, v in result.extracted_entities.items() if v},
        'processing_time_ms': round(result.processing_time * 1000, 2)
    }