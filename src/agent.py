"""
Pydantic-AI agent for interacting with ScienceDirect API to answer scientific questions.
"""

import os
from typing import List, Optional
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent, RunContext
from .sciencedirect import ScienceDirectClient, Article

load_dotenv()


class ResearchQuery(BaseModel):
    """Input model for research queries."""
    question: str = Field(description="The scientific question to research")
    max_articles: int = Field(default=5, description="Maximum number of articles to search")


class ResearchResponse(BaseModel):
    """Structured response from the research agent."""
    answer: str = Field(description="The synthesized answer to the question")
    articles: List[Article] = Field(description="Relevant articles found")
    summary: str = Field(description="Brief summary of the findings")


# Dependencies type for the agent
class ResearchDependencies(BaseModel):
    """Dependencies for the research agent."""
    client: ScienceDirectClient
    
    class Config:
        arbitrary_types_allowed = True


# Create the research agent
research_agent = Agent[ResearchDependencies, ResearchResponse](
    model=os.getenv("DEFAULT_MODEL", "openai:gpt-4o-mini"),
    deps_type=ResearchDependencies,
    retries=2,
    system_prompt=(
        "You are a scientific research assistant specializing in analyzing academic literature. "
        "Your role is to search for relevant scientific articles using the ScienceDirect database "
        "and provide comprehensive, evidence-based answers to research questions. "
        "Always cite the specific articles you reference and provide a balanced view of the findings. "
        "Focus on recent, peer-reviewed research when possible."
    )
)


@research_agent.tool
async def search_articles(
    ctx: RunContext[ResearchDependencies],
    query: str,
    limit: int = 5
) -> List[Article]:
    """
    Search for scientific articles on ScienceDirect.
    
    Args:
        query: Search query for finding articles
        limit: Maximum number of articles to return
        
    Returns:
        List of relevant articles
    """
    try:
        articles = await ctx.deps.client.search_articles(query, limit)
        return articles
    except Exception as e:
        print(f"Error searching articles: {e}")
        return []


@research_agent.tool  
async def get_article_details(
    ctx: RunContext[ResearchDependencies],
    pii: str
) -> Optional[Article]:
    """
    Get detailed information about a specific article.
    
    Args:
        pii: Publisher Item Identifier of the article
        
    Returns:
        Detailed article information or None if not found
    """
    try:
        article = await ctx.deps.client.get_article(pii)
        return article
    except Exception as e:
        print(f"Error getting article details: {e}")
        return None


async def answer_research_question(
    question: str,
    max_articles: int = 5,
    api_key: Optional[str] = None,
    inst_token: Optional[str] = None,
    debug: bool = False
) -> ResearchResponse:
    """
    Main function to answer a research question using the agent.
    
    Args:
        question: The research question to answer
        max_articles: Maximum number of articles to search
        api_key: Elsevier API key (optional, uses env if not provided)
        inst_token: Institutional token (optional)
        debug: Enable debug mode for detailed error information
        
    Returns:
        ResearchResponse with answer and supporting articles
    """
    # Initialize the ScienceDirect client
    client = ScienceDirectClient(api_key=api_key, inst_token=inst_token, debug=debug)
    
    # Create dependencies
    deps = ResearchDependencies(client=client)
    
    # Run the agent with a structured prompt
    prompt = (
        f"Please research the following scientific question: '{question}'. "
        f"Search for up to {max_articles} relevant articles, analyze their findings, "
        "and provide a comprehensive answer with citations."
    )
    
    try:
        result = await research_agent.run(
            prompt,
            deps=deps
        )
        return result.data
    except Exception as e:
        # Fallback response on error
        return ResearchResponse(
            answer=f"I encountered an error while researching: {str(e)}",
            articles=[],
            summary="Unable to complete the research due to an error."
        )


# Simple conversational interface
async def chat_with_agent(
    api_key: Optional[str] = None,
    inst_token: Optional[str] = None
):
    """
    Simple chat interface for the research agent.
    
    Args:
        api_key: Elsevier API key
        inst_token: Institutional token
    """
    debug = os.getenv("DEBUG", "").lower() in ("true", "1", "yes")
    client = ScienceDirectClient(api_key=api_key, inst_token=inst_token, debug=debug)
    deps = ResearchDependencies(client=client)
    
    print("Scientific Research Assistant")
    print("=" * 50)
    print("Ask me any scientific question, and I'll search the literature for you.")
    print("Type 'quit' or 'exit' to end the session.\n")
    
    while True:
        question = input("Your question: ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        if not question:
            continue
        
        print("\nSearching scientific literature...")
        
        try:
            result = await research_agent.run(
                f"Research this question: {question}",
                deps=deps
            )
            
            response = result.data
            
            print("\n" + "=" * 50)
            print("ANSWER:")
            print(response.answer)
            
            if response.articles:
                print("\n" + "=" * 50)
                print("REFERENCES:")
                for i, article in enumerate(response.articles, 1):
                    print(f"\n{i}. {article.title}")
                    if article.authors:
                        print(f"   Authors: {', '.join(article.authors[:3])}")
                    if article.publication_name:
                        print(f"   Journal: {article.publication_name}")
                    if article.publication_date:
                        print(f"   Date: {article.publication_date}")
                    if article.doi:
                        print(f"   DOI: {article.doi}")
            
            print("\n" + "=" * 50)
            print("SUMMARY:")
            print(response.summary)
            print("\n" + "=" * 50 + "\n")
            
        except Exception as e:
            print(f"\nError: {e}\n")
            print("Please check your API credentials and try again.\n")