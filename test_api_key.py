#!/usr/bin/env python3
"""
Test harness to verify Science Direct API key is working.
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

from src.sciencedirect import ScienceDirectClient

load_dotenv()


async def test_api_key():
    """Test the Science Direct API key with a simple search query."""
    
    print("=" * 60)
    print("Science Direct API Key Test Harness")
    print("=" * 60)
    
    api_key = os.getenv("ELSEVIER_API_KEY")
    auth_token = os.getenv("ELSEVIER_AUTH_TOKEN")
    inst_token = os.getenv("ELSEVIER_INST_TOKEN")
    
    if not api_key:
        print("\n❌ ERROR: No API key found!")
        print("Please set ELSEVIER_API_KEY in your .env file")
        return False
    
    print(f"\n✓ API Key found: {api_key[:8]}...")
    if auth_token:
        print(f"✓ Auth token found: {auth_token[:8]}...")
    else:
        print("ℹ No auth token found (optional - for user session)")
    if inst_token:
        print(f"✓ Institution token found: {inst_token[:8]}...")
    else:
        print("ℹ No institution token found (optional)")
    
    try:
        client = ScienceDirectClient(api_key=api_key, auth_token=auth_token, inst_token=inst_token)
        print("\n✓ Client initialized successfully")
        
        print("\n🔍 Testing API with search query: 'machine learning'")
        print("-" * 40)
        
        articles = await client.search_articles("machine learning", limit=3)
        
        if articles:
            print(f"\n✓ API call successful! Found {len(articles)} articles:")
            print("-" * 40)
            
            for i, article in enumerate(articles, 1):
                print(f"\n{i}. {article.title}")
                if article.authors:
                    print(f"   Authors: {', '.join(article.authors[:3])}")
                    if len(article.authors) > 3:
                        print(f"            ... and {len(article.authors) - 3} more")
                if article.publication_name:
                    print(f"   Journal: {article.publication_name}")
                if article.publication_date:
                    print(f"   Date: {article.publication_date}")
                if article.doi:
                    print(f"   DOI: {article.doi}")
            
            print("\n" + "=" * 60)
            print("✅ API KEY VERIFICATION SUCCESSFUL!")
            print("=" * 60)
            return True
        else:
            print("\n⚠ No articles found, but API call was successful")
            print("✅ API KEY IS VALID")
            return True
            
    except ValueError as e:
        error_msg = str(e)
        print(f"\n❌ ERROR: {error_msg}")
        
        if "Invalid API key" in error_msg or "authentication failed" in error_msg:
            print("\n⚠ Your API key appears to be invalid or expired.")
            print("Please check your ELSEVIER_API_KEY in the .env file")
        elif "Rate limit" in error_msg:
            print("\n⚠ Rate limit exceeded. Your API key is valid but you've hit the rate limit.")
            print("Please wait and try again later.")
        else:
            print("\n⚠ An unexpected error occurred while testing the API")
        
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {str(e)}")
        print("\nPlease check your internet connection and try again")
        return False


async def test_article_retrieval():
    """Test retrieving a specific article (optional extended test)."""
    
    print("\n" + "=" * 60)
    print("Extended Test: Article Retrieval")
    print("=" * 60)
    
    try:
        client = ScienceDirectClient()
        
        print("\n🔍 Searching for an article to test retrieval...")
        articles = await client.search_articles("COVID-19", limit=1)
        
        if articles and articles[0].pii:
            pii = articles[0].pii
            print(f"✓ Found article with PII: {pii}")
            print(f"  Title: {articles[0].title}")
            
            print(f"\n📄 Retrieving full article details...")
            article = await client.get_article(pii)
            
            print(f"\n✓ Article retrieved successfully!")
            print(f"  Title: {article.title}")
            if article.abstract:
                abstract_preview = article.abstract[:200] + "..." if len(article.abstract) > 200 else article.abstract
                print(f"  Abstract: {abstract_preview}")
            
            return True
        else:
            print("⚠ No articles with PII found for retrieval test")
            return False
            
    except Exception as e:
        print(f"\n⚠ Article retrieval test failed: {str(e)}")
        return False


async def main():
    """Run all tests."""
    
    success = await test_api_key()
    
    if success:
        print("\n" + "=" * 60)
        print("Would you like to run the extended article retrieval test? (y/n)")
        print("=" * 60)
        
        try:
            response = input("> ").strip().lower()
            if response == 'y':
                await test_article_retrieval()
        except KeyboardInterrupt:
            print("\n\nTest cancelled by user")
    
    return success


if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest cancelled by user")
        sys.exit(1)