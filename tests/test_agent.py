"""
Basic tests for the ScienceDirect research agent.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from src.sciencedirect import Article, ScienceDirectClient
from src.agent import ResearchResponse, answer_research_question


@pytest.fixture
def mock_article():
    """Create a mock article for testing."""
    return Article(
        title="Test Article Title",
        authors=["Author One", "Author Two"],
        abstract="This is a test abstract about scientific research.",
        doi="10.1234/test.doi",
        pii="S0000000000000",
        publication_name="Test Journal",
        publication_date="2024-01-01",
        url="https://example.com/article"
    )


@pytest.fixture
def mock_client(mock_article):
    """Create a mock ScienceDirectClient."""
    client = MagicMock(spec=ScienceDirectClient)
    client.search_articles = AsyncMock(return_value=[mock_article])
    client.get_article = AsyncMock(return_value=mock_article)
    return client


class TestScienceDirectClient:
    """Test the ScienceDirect API client."""
    
    def test_client_initialization_without_api_key(self):
        """Test that client raises error without API key."""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="Elsevier API key is required"):
                ScienceDirectClient()
    
    def test_client_initialization_with_api_key(self):
        """Test successful client initialization with API key."""
        client = ScienceDirectClient(api_key="test_key")
        assert client.api_key == "test_key"
        assert "X-ELS-APIKey" in client.headers
        assert client.headers["X-ELS-APIKey"] == "test_key"
    
    def test_client_with_institutional_token(self):
        """Test client initialization with institutional token."""
        client = ScienceDirectClient(api_key="test_key", inst_token="test_token")
        assert client.inst_token == "test_token"
        assert "X-ELS-Insttoken" in client.headers
        assert client.headers["X-ELS-Insttoken"] == "test_token"
    
    @pytest.mark.asyncio
    async def test_search_articles_mock(self, mock_client):
        """Test searching articles with mock client."""
        results = await mock_client.search_articles("test query", limit=5)
        assert len(results) == 1
        assert results[0].title == "Test Article Title"
        mock_client.search_articles.assert_called_once_with("test query", limit=5)
    
    @pytest.mark.asyncio
    async def test_get_article_mock(self, mock_client, mock_article):
        """Test getting article details with mock client."""
        article = await mock_client.get_article("S0000000000000")
        assert article.title == mock_article.title
        assert article.pii == mock_article.pii
        mock_client.get_article.assert_called_once_with("S0000000000000")


class TestArticleModel:
    """Test the Article Pydantic model."""
    
    def test_article_creation(self):
        """Test creating an Article instance."""
        article = Article(
            title="Test Title",
            authors=["Author 1"],
            abstract="Test abstract",
            doi="10.1234/test",
            pii="S123456",
            publication_name="Test Journal",
            publication_date="2024-01-01",
            url="https://example.com"
        )
        assert article.title == "Test Title"
        assert len(article.authors) == 1
        assert article.doi == "10.1234/test"
    
    def test_article_minimal(self):
        """Test creating Article with minimal required fields."""
        article = Article(title="Minimal Title")
        assert article.title == "Minimal Title"
        assert article.authors == []
        assert article.abstract is None
        assert article.doi is None


class TestResearchAgent:
    """Test the research agent functionality."""
    
    @pytest.mark.asyncio
    async def test_answer_research_question_with_mock(self, mock_article):
        """Test answering a research question with mocked API."""
        with patch('src.agent.ScienceDirectClient') as MockClient:
            # Setup mock client
            mock_instance = MagicMock()
            mock_instance.search_articles = AsyncMock(return_value=[mock_article])
            MockClient.return_value = mock_instance
            
            # Mock the agent run to return a simple response
            with patch('src.agent.research_agent.run') as mock_run:
                mock_result = MagicMock()
                mock_result.data = ResearchResponse(
                    answer="This is a test answer based on the research.",
                    articles=[mock_article],
                    summary="Test summary of findings."
                )
                mock_run.return_value = mock_result
                
                # Test the function
                response = await answer_research_question(
                    "What is the test question?",
                    max_articles=5,
                    api_key="test_key"
                )
                
                assert isinstance(response, ResearchResponse)
                assert "test answer" in response.answer.lower()
                assert len(response.articles) == 1
                assert response.articles[0].title == "Test Article Title"
    
    @pytest.mark.asyncio
    async def test_answer_research_question_error_handling(self):
        """Test error handling in answer_research_question."""
        with patch('src.agent.ScienceDirectClient') as MockClient:
            # Make the client raise an error
            MockClient.side_effect = ValueError("API Error")
            
            response = await answer_research_question(
                "Test question",
                api_key="test_key"
            )
            
            assert isinstance(response, ResearchResponse)
            assert "error" in response.answer.lower()
            assert len(response.articles) == 0


class TestCLI:
    """Test CLI functionality."""
    
    def test_cli_imports(self):
        """Test that CLI module can be imported."""
        from src.cli import app, main
        assert app is not None
        assert main is not None
    
    @patch('src.cli.os.getenv')
    def test_config_command(self, mock_getenv):
        """Test the config command output."""
        from src.cli import app
        from typer.testing import CliRunner
        
        runner = CliRunner()
        
        # Mock environment variables
        mock_getenv.side_effect = lambda key, default=None: {
            "ELSEVIER_API_KEY": "test_elsevier_key",
            "OPENAI_API_KEY": "test_openai_key",
            "DEFAULT_MODEL": "openai:gpt-4o-mini"
        }.get(key, default)
        
        result = runner.invoke(app, ["config"])
        assert result.exit_code == 0
        assert "Configuration Status" in result.stdout


if __name__ == "__main__":
    pytest.main([__file__, "-v"])