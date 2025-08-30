"""
Simple ScienceDirect API client wrapper for searching and retrieving articles.
"""

import os
import json
from typing import List, Dict, Optional, Any
import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()


class Article(BaseModel):
    """Structured representation of a ScienceDirect article."""
    title: str
    authors: List[str] = Field(default_factory=list)
    abstract: Optional[str] = None
    doi: Optional[str] = None
    pii: Optional[str] = None
    publication_name: Optional[str] = None
    publication_date: Optional[str] = None
    url: Optional[str] = None


class ScienceDirectClient:
    """Async client for interacting with ScienceDirect API."""
    
    BASE_URL = "https://api.elsevier.com/content"
    SEARCH_URL = f"{BASE_URL}/search/sciencedirect"
    ARTICLE_URL = f"{BASE_URL}/article/pii"
    
    def __init__(self, api_key: Optional[str] = None, auth_token: Optional[str] = None, inst_token: Optional[str] = None, debug: bool = False):
        self.api_key = api_key or os.getenv("ELSEVIER_API_KEY")
        self.auth_token = auth_token or os.getenv("ELSEVIER_AUTH_TOKEN")
        self.inst_token = inst_token or os.getenv("ELSEVIER_INST_TOKEN")
        self.debug = debug or os.getenv("DEBUG", "").lower() in ("true", "1", "yes")
        
        if not self.api_key:
            raise ValueError("Elsevier API key is required. Set ELSEVIER_API_KEY in .env")
        
        self.headers = {
            "X-ELS-APIKey": self.api_key,
            "Accept": "application/json"
        }
        
        if self.auth_token:
            self.headers["X-ELS-Authtoken"] = self.auth_token
        
        if self.inst_token:
            self.headers["X-ELS-Insttoken"] = self.inst_token
    
    def _debug_log(self, message: str, data: Any = None):
        """Log debug information if debug mode is enabled."""
        if self.debug:
            print(f"[DEBUG] {message}")
            if data:
                print(f"[DEBUG DATA] {json.dumps(data, indent=2) if isinstance(data, dict) else data}")
    
    async def search_articles(self, query: str, limit: int = 10) -> List[Article]:
        """
        Search for articles on ScienceDirect.
        
        Args:
            query: Search query string
            limit: Maximum number of results (max 200 per API limit)
            
        Returns:
            List of Article objects
        """
        params = {
            "query": query,
            "count": min(limit, 200),  # API max is 200
            "httpAccept": "application/json"
        }
        
        self._debug_log(f"Searching articles with query: {query}", {"params": params, "url": self.SEARCH_URL})
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    self.SEARCH_URL,
                    headers=self.headers,
                    params=params,
                    timeout=30.0
                )
                
                self._debug_log(f"Response status: {response.status_code}")
                
                response.raise_for_status()
                data = response.json()
                
                self._debug_log("Response data received", data)
                
                return self._parse_search_results(data)
                
            except httpx.HTTPStatusError as e:
                error_detail = {
                    "status_code": e.response.status_code,
                    "response_text": e.response.text,
                    "headers": dict(e.response.headers),
                    "url": str(e.response.url)
                }
                self._debug_log("HTTP Error occurred", error_detail)
                
                if e.response.status_code == 401:
                    raise ValueError(f"Invalid API key or authentication failed. Debug: {json.dumps(error_detail) if self.debug else 'Enable debug mode for details'}")
                elif e.response.status_code == 429:
                    raise ValueError(f"Rate limit exceeded. Please try again later. Debug: {json.dumps(error_detail) if self.debug else 'Enable debug mode for details'}")
                else:
                    raise ValueError(f"API request failed: {e.response.status_code} - {e.response.text[:500] if self.debug else 'Enable debug mode for full error'}")
            except Exception as e:
                self._debug_log(f"Unexpected error: {type(e).__name__}: {str(e)}")
                raise ValueError(f"Search failed: {str(e)}")
    
    async def get_article(self, pii: str) -> Article:
        """
        Retrieve detailed article information by PII (Publisher Item Identifier).
        
        Args:
            pii: The PII of the article
            
        Returns:
            Article object with detailed information
        """
        url = f"{self.ARTICLE_URL}/{pii}"
        
        self._debug_log(f"Getting article with PII: {pii}", {"url": url})
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    url,
                    headers=self.headers,
                    timeout=30.0
                )
                
                self._debug_log(f"Response status: {response.status_code}")
                
                response.raise_for_status()
                data = response.json()
                
                self._debug_log("Article data received", data)
                
                return self._parse_article(data)
                
            except httpx.HTTPStatusError as e:
                error_detail = {
                    "status_code": e.response.status_code,
                    "response_text": e.response.text,
                    "headers": dict(e.response.headers),
                    "url": str(e.response.url)
                }
                self._debug_log("HTTP Error occurred", error_detail)
                
                if e.response.status_code == 404:
                    raise ValueError(f"Article with PII {pii} not found. Debug: {json.dumps(error_detail) if self.debug else 'Enable debug mode for details'}")
                else:
                    raise ValueError(f"Failed to retrieve article: {e.response.status_code} - {e.response.text[:500] if self.debug else 'Enable debug mode for full error'}")
            except Exception as e:
                self._debug_log(f"Unexpected error: {type(e).__name__}: {str(e)}")
                raise ValueError(f"Article retrieval failed: {str(e)}")
    
    def _parse_search_results(self, data: Dict[str, Any]) -> List[Article]:
        """Parse search results from API response."""
        articles = []
        
        search_results = data.get("search-results", {})
        entries = search_results.get("entry", [])
        
        for entry in entries:
            article = Article(
                title=entry.get("dc:title", "No title"),
                authors=self._extract_authors(entry),
                abstract=entry.get("prism:teaser", entry.get("dc:description")),
                doi=entry.get("prism:doi"),
                pii=entry.get("pii"),
                publication_name=entry.get("prism:publicationName"),
                publication_date=entry.get("prism:coverDate"),
                url=entry.get("link", [{}])[0].get("@href") if entry.get("link") else None
            )
            articles.append(article)
        
        return articles
    
    def _parse_article(self, data: Dict[str, Any]) -> Article:
        """Parse article details from API response."""
        article_data = data.get("full-text-retrieval-response", {})
        core_data = article_data.get("coredata", {})
        
        # Extract abstract from originalText if available
        original_text = article_data.get("originalText", {})
        abstract = None
        if isinstance(original_text, dict):
            abstract = original_text.get("xocs:doc", {}).get("xocs:serial-item", {}).get("xocs:raw-text", "")
        
        if not abstract:
            abstract = core_data.get("dc:description")
        
        return Article(
            title=core_data.get("dc:title", "No title"),
            authors=self._extract_authors_from_article(core_data),
            abstract=abstract,
            doi=core_data.get("prism:doi"),
            pii=core_data.get("pii"),
            publication_name=core_data.get("prism:publicationName"),
            publication_date=core_data.get("prism:coverDate"),
            url=core_data.get("link", [{}])[0].get("@href") if core_data.get("link") else None
        )
    
    def _extract_authors(self, entry: Dict[str, Any]) -> List[str]:
        """Extract author names from search result entry."""
        authors = []
        creator = entry.get("dc:creator")
        
        if creator:
            if isinstance(creator, str):
                authors.append(creator)
            elif isinstance(creator, list):
                authors.extend(creator)
        
        return authors
    
    def _extract_authors_from_article(self, core_data: Dict[str, Any]) -> List[str]:
        """Extract author names from article core data."""
        authors = []
        creator = core_data.get("dc:creator")
        
        if isinstance(creator, dict):
            authors.append(creator.get("$", ""))
        elif isinstance(creator, list):
            for c in creator:
                if isinstance(c, dict):
                    authors.append(c.get("$", ""))
                else:
                    authors.append(str(c))
        elif creator:
            authors.append(str(creator))
        
        return [a for a in authors if a]  # Filter out empty strings