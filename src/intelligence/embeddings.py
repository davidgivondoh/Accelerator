"""
Embedding Pipeline for the Growth Engine.

Generates and manages embeddings for:
- Opportunity descriptions (for semantic search and matching)
- User profiles (for personalized scoring)
- Application content (for quality assessment)

Uses Google's text-embedding-004 model for high-quality embeddings.
Stores vectors in Pinecone for fast similarity search.
"""

import asyncio
import hashlib
from typing import Any, List, Optional
from dataclasses import dataclass

import numpy as np

from config.settings import settings

@dataclass
class EmbeddingConfig:
    """Configuration for embedding generation."""
    model: str = "text-embedding-004"
    dimensions: int = 768
    batch_size: int = 100

@dataclass
class EmbeddingResult:
    """Result of embedding generation."""
    text: str
    embedding: List[float]
    model: str
    token_count: int = 0

@dataclass
class SimilarityResult:
    """Result of similarity search."""
    text: str
    score: float
    metadata: dict = None


class EmbeddingPipeline:
    """
    Service for generating and managing text embeddings.
    
    Uses Google's text-embedding-004 for embeddings and
    optionally Pinecone for vector storage.
    """
    
    def __init__(self):
        """Initialize the embedding service."""
        self._client = None
        self._pinecone = None
        self._cache: dict[str, list[float]] = {}
    
    @property
    def client(self):
        """Lazy-load the Google GenAI client."""
        if self._client is None:
            import google.generativeai as genai
            genai.configure(api_key=settings.google_api_key.get_secret_value())
            self._client = genai
        return self._client
    
    @property
    def pinecone_index(self):
        """Lazy-load the Pinecone index."""
        if self._pinecone is None and settings.pinecone_api_key:
            try:
                from pinecone import Pinecone
                pc = Pinecone(api_key=settings.pinecone_api_key.get_secret_value())
                self._pinecone = pc.Index(settings.pinecone_index)
            except Exception as e:
                print(f"Pinecone initialization failed: {e}")
                self._pinecone = None
        return self._pinecone
    
    def _cache_key(self, text: str) -> str:
        """Generate a cache key for text."""
        return hashlib.md5(text.encode()).hexdigest()
    
    async def embed_text(
        self,
        text: str,
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            task_type: Embedding task type:
                - RETRIEVAL_DOCUMENT: For documents to be retrieved
                - RETRIEVAL_QUERY: For search queries
                - SEMANTIC_SIMILARITY: For similarity comparison
                - CLASSIFICATION: For classification tasks
                
        Returns:
            List of floats representing the embedding vector
        """
        # Check cache
        cache_key = self._cache_key(text)
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Truncate if too long (model limit ~8k tokens)
        if len(text) > 25000:
            text = text[:25000]
        
        # Generate embedding
        result = self.client.embed_content(
            model="models/text-embedding-004",
            content=text,
            task_type=task_type,
        )
        
        embedding = result['embedding']
        
        # Cache the result
        self._cache[cache_key] = embedding
        
        return embedding
    
    async def embed_batch(
        self,
        texts: list[str],
        task_type: str = "RETRIEVAL_DOCUMENT",
    ) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            task_type: Embedding task type
            
        Returns:
            List of embedding vectors
        """
        # Check cache for existing embeddings
        results = []
        texts_to_embed = []
        indices_to_embed = []
        
        for i, text in enumerate(texts):
            cache_key = self._cache_key(text)
            if cache_key in self._cache:
                results.append((i, self._cache[cache_key]))
            else:
                texts_to_embed.append(text[:25000] if len(text) > 25000 else text)
                indices_to_embed.append(i)
        
        # Generate embeddings for uncached texts
        if texts_to_embed:
            # Batch embed (up to 100 at a time)
            batch_size = 100
            for batch_start in range(0, len(texts_to_embed), batch_size):
                batch = texts_to_embed[batch_start:batch_start + batch_size]
                batch_indices = indices_to_embed[batch_start:batch_start + batch_size]
                
                result = self.client.embed_content(
                    model="models/text-embedding-004",
                    content=batch,
                    task_type=task_type,
                )
                
                for j, embedding in enumerate(result['embedding']):
                    idx = batch_indices[j]
                    results.append((idx, embedding))
                    # Cache the result
                    cache_key = self._cache_key(texts[idx])
                    self._cache[cache_key] = embedding
        
        # Sort by original index and return just embeddings
        results.sort(key=lambda x: x[0])
        return [r[1] for r in results]
    
    def cosine_similarity(
        self,
        embedding1: list[float],
        embedding2: list[float],
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between -1 and 1
        """
        a = np.array(embedding1)
        b = np.array(embedding2)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    
    async def similarity_score(
        self,
        text1: str,
        text2: str,
    ) -> float:
        """
        Calculate semantic similarity between two texts.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score between 0 and 1
        """
        embeddings = await self.embed_batch(
            [text1, text2],
            task_type="SEMANTIC_SIMILARITY",
        )
        similarity = self.cosine_similarity(embeddings[0], embeddings[1])
        # Normalize to 0-1 range
        return (similarity + 1) / 2
    
    async def store_embedding(
        self,
        id: str,
        embedding: list[float],
        metadata: dict[str, Any],
        namespace: str = "opportunities",
    ) -> bool:
        """
        Store an embedding in Pinecone.
        
        Args:
            id: Unique identifier for the vector
            embedding: The embedding vector
            metadata: Metadata to store with the vector
            namespace: Pinecone namespace
            
        Returns:
            True if successful
        """
        if self.pinecone_index is None:
            return False
        
        try:
            self.pinecone_index.upsert(
                vectors=[{
                    "id": id,
                    "values": embedding,
                    "metadata": metadata,
                }],
                namespace=namespace,
            )
            return True
        except Exception as e:
            print(f"Failed to store embedding: {e}")
            return False
    
    async def search_similar(
        self,
        query_embedding: list[float],
        top_k: int = 10,
        namespace: str = "opportunities",
        filter: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """
        Search for similar vectors in Pinecone.
        
        Args:
            query_embedding: Query vector
            top_k: Number of results to return
            namespace: Pinecone namespace
            filter: Optional metadata filter
            
        Returns:
            List of matches with id, score, and metadata
        """
        if self.pinecone_index is None:
            return []
        
        try:
            results = self.pinecone_index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter=filter,
                include_metadata=True,
            )
            
            return [
                {
                    "id": match.id,
                    "score": match.score,
                    "metadata": match.metadata,
                }
                for match in results.matches
            ]
        except Exception as e:
            print(f"Search failed: {e}")
            return []


# Global embedding service instance
_embedding_service: EmbeddingPipeline | None = None


def get_embedding_service() -> EmbeddingPipeline:
    """Get or create the global embedding service."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingPipeline()
    return _embedding_service


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

async def embed_opportunity(opportunity: dict[str, Any]) -> list[float]:
    """
    Generate embedding for an opportunity.
    
    Combines title, organization, description, and requirements
    into a comprehensive text representation.
    
    Args:
        opportunity: Opportunity dictionary
        
    Returns:
        Embedding vector
    """
    # Build comprehensive text from opportunity
    parts = [
        f"Title: {opportunity.get('title', '')}",
        f"Organization: {opportunity.get('organization', '')}",
        f"Type: {opportunity.get('opportunity_type', '')}",
        f"Description: {opportunity.get('description', '')}",
    ]
    
    if opportunity.get('requirements'):
        reqs = opportunity['requirements']
        if isinstance(reqs, dict):
            if reqs.get('skills_required'):
                parts.append(f"Required Skills: {', '.join(reqs['skills_required'])}")
            if reqs.get('experience_years'):
                parts.append(f"Experience: {reqs['experience_years']} years")
    
    if opportunity.get('tags'):
        parts.append(f"Tags: {', '.join(opportunity['tags'])}")
    
    text = "\n".join(parts)
    
    service = get_embedding_service()
    return await service.embed_text(text, task_type="RETRIEVAL_DOCUMENT")


async def embed_profile(profile: dict[str, Any]) -> list[float]:
    """
    Generate embedding for a user profile.
    
    Combines summary, skills, experience, and preferences
    into a comprehensive text representation.
    
    Args:
        profile: Profile dictionary
        
    Returns:
        Embedding vector
    """
    parts = [
        f"Name: {profile.get('name', '')}",
        f"Role: {profile.get('current_role', '')}",
        f"Summary: {profile.get('summary', '')}",
    ]
    
    if profile.get('skills'):
        skills = profile['skills']
        if isinstance(skills, list):
            parts.append(f"Skills: {', '.join(skills[:20])}")
    
    if profile.get('experience'):
        exp_parts = []
        for exp in profile['experience'][:5]:
            if isinstance(exp, dict):
                exp_parts.append(f"{exp.get('title', '')} at {exp.get('organization', '')}")
        if exp_parts:
            parts.append(f"Experience: {'; '.join(exp_parts)}")
    
    if profile.get('preferences'):
        prefs = profile['preferences']
        if isinstance(prefs, dict):
            if prefs.get('target_roles'):
                parts.append(f"Target Roles: {', '.join(prefs['target_roles'])}")
            if prefs.get('industries'):
                parts.append(f"Industries: {', '.join(prefs['industries'])}")
    
    text = "\n".join(parts)
    
    service = get_embedding_service()
    return await service.embed_text(text, task_type="RETRIEVAL_DOCUMENT")


async def calculate_profile_opportunity_match(
    profile: dict[str, Any],
    opportunity: dict[str, Any],
) -> dict[str, Any]:
    """
    Calculate semantic match score between profile and opportunity.
    
    Args:
        profile: User profile dictionary
        opportunity: Opportunity dictionary
        
    Returns:
        Match result with score and details
    """
    # Generate embeddings
    profile_embedding = await embed_profile(profile)
    opportunity_embedding = await embed_opportunity(opportunity)
    
    # Calculate similarity
    service = get_embedding_service()
    similarity = service.cosine_similarity(profile_embedding, opportunity_embedding)
    
    # Normalize to 0-1 range
    normalized_score = (similarity + 1) / 2
    
    return {
        "semantic_score": normalized_score,
        "similarity_raw": similarity,
        "interpretation": _interpret_score(normalized_score),
    }


def _interpret_score(score: float) -> str:
    """Interpret a semantic match score."""
    if score >= 0.85:
        return "Excellent match - highly relevant"
    elif score >= 0.75:
        return "Strong match - good fit"
    elif score >= 0.65:
        return "Moderate match - worth considering"
    elif score >= 0.55:
        return "Weak match - review carefully"
    else:
        return "Poor match - likely not relevant"
