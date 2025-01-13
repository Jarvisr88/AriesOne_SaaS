"""
Search service for image discovery.
"""
from typing import Dict, Any, List, Optional
from elasticsearch import AsyncElasticsearch
import logging
from datetime import datetime
from .config import settings


class SearchService:
    """Manages image search operations."""
    
    def __init__(self):
        """Initialize search service."""
        self.logger = logging.getLogger(__name__)
        self.es = AsyncElasticsearch([settings.ELASTICSEARCH_URL])
        
    async def index_image(
        self,
        company_id: int,
        image_id: str,
        metadata: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> bool:
        """Index image data.
        
        Args:
            company_id: Company identifier
            image_id: Image identifier
            metadata: Image metadata
            analysis: AI analysis results
            
        Returns:
            True if successful
        """
        try:
            # Prepare document
            doc = {
                "company_id": company_id,
                "image_id": image_id,
                "metadata": metadata,
                "analysis": analysis,
                "indexed_at": datetime.utcnow(),
                "tags": self._extract_tags(analysis),
                "keywords": self._extract_keywords(analysis),
                "nsfw_score": analysis.get("nsfw_score", 0),
                "quality_score": analysis.get("quality_score", 0)
            }
            
            # Index document
            await self.es.index(
                index=f"images-{company_id}",
                id=image_id,
                document=doc,
                refresh=True
            )
            
            return True
            
        except Exception as e:
            self.logger.error(f"Indexing error: {str(e)}")
            return False
            
    async def search_images(
        self,
        company_id: int,
        query: str,
        filters: Optional[Dict[str, Any]] = None,
        sort: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """Search for images.
        
        Args:
            company_id: Company identifier
            query: Search query
            filters: Search filters
            sort: Sort field
            page: Page number
            size: Page size
            
        Returns:
            Search results
        """
        try:
            # Build query
            search_query = self._build_query(
                company_id,
                query,
                filters
            )
            
            # Add sorting
            if sort:
                search_query["sort"] = self._build_sort(sort)
                
            # Execute search
            result = await self.es.search(
                index=f"images-{company_id}",
                body=search_query,
                from_=(page - 1) * size,
                size=size
            )
            
            # Format results
            return self._format_results(result)
            
        except Exception as e:
            self.logger.error(f"Search error: {str(e)}")
            return {
                "total": 0,
                "hits": []
            }
            
    def _build_query(
        self,
        company_id: int,
        query: str,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Build Elasticsearch query.
        
        Args:
            company_id: Company identifier
            query: Search query
            filters: Search filters
            
        Returns:
            Query object
        """
        # Base query
        must = [
            {"term": {"company_id": company_id}}
        ]
        
        # Add text search
        if query:
            must.append({
                "multi_match": {
                    "query": query,
                    "fields": [
                        "metadata.original_filename^2",
                        "tags^1.5",
                        "keywords"
                    ]
                }
            })
            
        # Add filters
        if filters:
            for field, value in filters.items():
                if isinstance(value, (list, tuple)):
                    must.append({
                        "terms": {field: value}
                    })
                else:
                    must.append({
                        "term": {field: value}
                    })
                    
        return {
            "query": {
                "bool": {
                    "must": must
                }
            }
        }
        
    def _build_sort(
        self,
        sort: str
    ) -> List[Dict[str, Any]]:
        """Build sort configuration.
        
        Args:
            sort: Sort field
            
        Returns:
            Sort configuration
        """
        field, order = sort.split(':')
        return [{field: {"order": order}}]
        
    def _format_results(
        self,
        result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Format search results.
        
        Args:
            result: Elasticsearch response
            
        Returns:
            Formatted results
        """
        return {
            "total": result["hits"]["total"]["value"],
            "hits": [
                {
                    "id": hit["_id"],
                    "score": hit["_score"],
                    **hit["_source"]
                }
                for hit in result["hits"]["hits"]
            ]
        }
        
    def _extract_tags(
        self,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Extract searchable tags.
        
        Args:
            analysis: AI analysis results
            
        Returns:
            List of tags
        """
        tags = set()
        
        # Add classifications
        for item in analysis.get("classification", []):
            tags.add(item["label"].lower())
            
        # Add VIT results
        for item in analysis.get("analysis", {}).get("vit_results", []):
            tags.add(item["label"].lower())
            
        return list(tags)
        
    def _extract_keywords(
        self,
        analysis: Dict[str, Any]
    ) -> List[str]:
        """Extract searchable keywords.
        
        Args:
            analysis: AI analysis results
            
        Returns:
            List of keywords
        """
        keywords = set()
        
        # Process all labels
        for item in analysis.get("classification", []):
            words = item["label"].lower().split()
            keywords.update(words)
            
        for item in analysis.get("analysis", {}).get("vit_results", []):
            words = item["label"].lower().split()
            keywords.update(words)
            
        return list(keywords)
