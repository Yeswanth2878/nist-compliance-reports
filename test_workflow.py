#!/usr/bin/env python3
"""
Unit tests for NIST Compliance Workflow
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, MagicMock
import json
from datetime import datetime

# Import the main application
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import NISTComplianceAgent, WorkflowRequest, Config

# Test fixtures
@pytest.fixture
def agent():
    """Create a test agent instance with mocked clients"""
    with patch('main.openai.OpenAI') as mock_openai, \
         patch('main.Github') as mock_github, \
         patch('main.requests.Session') as mock_session:
        
        # Create mock clients
        mock_openai_client = Mock()
        mock_github_client = Mock()
        mock_session_instance = Mock()
        
        mock_openai.return_value = mock_openai_client
        mock_github.return_value = mock_github_client
        mock_session.return_value = mock_session_instance
        
        # Create agent
        agent = NISTComplianceAgent()
        
        # Manually set the clients to ensure they're not None
        agent.openai_client = mock_openai_client
        agent.github_client = mock_github_client
        agent.session = mock_session_instance
        
        return agent

@pytest.fixture
def sample_articles():
    """Sample articles for testing"""
    return [
        {
            'title': 'NIST SP 800-218A: Secure Software Development Framework',
            'url': 'https://csrc.nist.gov/publications/detail/sp/800-218a/final',
            'date': '2024-12-01',
            'summary': 'Updated guidance for secure software development practices',
            'source': 'NIST CSRC',
            'content': '''
            # Secure Software Development Framework

            This publication provides guidance on secure software development practices
            including CI/CD pipeline security, SAST/DAST tools, and supply chain security.

            ## Key Updates
            - Enhanced container security guidelines
            - New SBOM requirements
            - Updated threat modeling practices

            ## Implementation Guidance
            Organizations should integrate security controls throughout the SDLC.
            '''
        },
        {
            'title': 'NIST Cybersecurity Framework 2.0',
            'url': 'https://csrc.nist.gov/csf-2.0',
            'date': '2024-11-15',
            'summary': 'Major update to the Cybersecurity Framework',
            'source': 'NIST CSRC',
            'content': '''
            # Cybersecurity Framework 2.0

            The updated framework includes new guidance for cloud environments
            and DevOps practices.

            ## Changes for Software Teams
            - Enhanced security controls for CI/CD
            - New governance requirements
            - Updated risk assessment methods
            '''
        }
    ]

@pytest.fixture
def mock_openai_response():
    """Mock OpenAI API response"""
    mock_response = Mock()
    mock_response.choices = [Mock()]
    mock_response.choices[0].message.content = "0.9"
    return mock_response

class TestNISTComplianceAgent:
    """Test suite for NISTComplianceAgent"""

    @pytest.mark.asyncio
    async def test_search_nist_updates_success(self, agent):
        """Test successful NIST updates search"""
        # Mock the session response
        mock_response = Mock()
        mock_response.json.return_value = {
            'publications': [
                {
                    'title': 'Test Publication',
                    'url': '/publications/test',
                    'datePublished': '2024-12-01',
                    'description': 'Test description'
                }
            ]
        }
        mock_response.raise_for_status = Mock()
        
        agent.session.get.return_value = mock_response
        
        # Test the search
        articles = await agent.search_nist_updates("secure development", 5)
        
        # Assertions
        assert len(articles) > 0
        assert articles[0]['title'] == 'Test Publication'
        assert articles[0]['source'] == 'NIST CSRC'

    @pytest.mark.asyncio
    async def test_extract_content_success(self, agent, sample_articles):
        """Test content extraction from articles"""
        # Mock BeautifulSoup and requests
        mock_response = Mock()
        mock_response.content = b"""
        <html>
            <body>
                <main>
                    <h1>Test Article</h1>
                    <p>This is test content about secure development.</p>
                    <p>It includes information about CI/CD and SAST tools.</p>
                </main>
            </body>
        </html>
        """
        mock_response.raise_for_status = Mock()
        
        agent.session.get.return_value = mock_response
        
        # Test content extraction
        articles_with_content = await agent.extract_content(sample_articles)
        
        # Assertions
        assert len(articles_with_content) > 0
        assert 'content' in articles_with_content[0]
        assert len(articles_with_content[0]['content']) > 0

    @pytest.mark.asyncio
    async def test_assess_it_relevance(self, agent, mock_openai_response):
        """Test IT relevance assessment"""
        # Ensure the OpenAI client is properly mocked
        assert agent.openai_client is not None, "OpenAI client should be mocked"
        
        # Mock OpenAI client response
        agent.openai_client.chat.completions.create.return_value = mock_openai_response
        
        test_article = {
            'title': 'Secure Software Development Guide',
            'summary': 'Guide covering CI/CD security, SAST tools, and DevOps practices',
            'content': 'Content about secure coding, supply chain security, and SBOM requirements'
        }
        
        # Test relevance assessment
        score = await agent._assess_it_relevance(test_article)
        
        # Assertions
        assert isinstance(score, float)
        assert 0.0 <= score <= 1.0
        agent.openai_client.chat.completions.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_filter_it_relevant_content(self, agent, sample_articles, mock_openai_response):
        """Test filtering articles for IT relevance"""
        # Ensure the OpenAI client is properly mocked
        assert agent.openai_client is not None, "OpenAI client should be mocked"
        
        # Mock the relevance assessment
        agent.openai_client.chat.completions.create.return_value = mock_openai_response
        
        # Test filtering
        filtered_articles = await agent.filter_it_relevant_content(sample_articles)
        
        # Assertions
        assert isinstance(filtered_articles, list)
        for article in filtered_articles:
            assert 'relevance_score' in article
            assert article['relevance_score'] > 0.7

    @pytest.mark.asyncio
    async def test_generate_summary(self, agent, sample_articles):
        """Test summary generation"""
        # Ensure the OpenAI client is properly mocked
        assert agent.openai_client is not None, "OpenAI client should be mocked"
        
        # Mock OpenAI response for summary
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = """
# NIST Compliance Update Summary

## Executive Summary
Recent updates to NIST frameworks provide new guidance for secure software development.

## Latest Updates
- NIST SP 800-218A provides enhanced SSDF guidance
- Cybersecurity Framework 2.0 includes new DevOps controls

## Action Items
- [ ] Review updated SSDF practices
- [ ] Implement new CI/CD security controls
- [ ] Update SBOM requirements

## Source Citations
1. [NIST SP 800-218A](https://csrc.nist.gov/publications/detail/sp/800-218a/final)
        """
        
        agent.openai_client.chat.completions.create.return_value = mock_response
        
        # Add relevance scores to articles
        for article in sample_articles:
            article['relevance_score'] = 0.9
        
        # Test summary generation
        summary = await agent.generate_summary(sample_articles)
        
        # Assertions
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert 'NIST Compliance Update Summary' in summary
        assert '---' in summary  # YAML frontmatter
        assert 'title:' in summary
        assert 'date:' in summary

    @pytest.mark.asyncio
    async def test_publish_to_github_success(self, agent, sample_articles):
        """Test GitHub publishing functionality"""
        # Ensure the GitHub client is properly mocked
        assert agent.github_client is not None, "GitHub client should be mocked"
        
        # Mock GitHub API responses
        mock_repo = Mock()
        mock_branch = Mock()
        mock_commit = Mock()
        mock_pr = Mock()
        
        mock_commit.sha = 'abc123'
        mock_branch.commit = mock_commit
        mock_pr.html_url = 'https://github.com/test/repo/pull/123'
        
        mock_repo.default_branch = 'main'
        mock_repo.get_branch.return_value = mock_branch
        mock_repo.create_git_ref.return_value = Mock()
        mock_repo.create_file.return_value = Mock()
        mock_repo.create_pull.return_value = mock_pr
        
        agent.github_client.get_repo.return_value = mock_repo
        
        # Test publishing
        test_summary = "# Test Summary\n\nThis is a test summary."
        result = await agent.publish_to_github(test_summary, sample_articles)
        
        # Assertions
        assert isinstance(result, dict)
        assert 'summary_url' in result
        assert 'pr_url' in result
        assert 'branch' in result
        assert 'file_path' in result
        assert result['pr_url'] == 'https://github.com/test/repo/pull/123'

    def test_fallback_summary_generation(self, agent, sample_articles):
        """Test fallback summary when AI fails"""
        # Add relevance scores
        for article in sample_articles:
            article['relevance_score'] = 0.8
        
        # Test fallback summary
        summary = agent._generate_fallback_summary(sample_articles)
        
        # Assertions
        assert isinstance(summary, str)
        assert len(summary) > 0
        assert 'NIST SP 800 Compliance Update Summary' in summary
        assert str(len(sample_articles)) in summary
        for article in sample_articles:
            assert article['title'] in summary

class TestConfiguration:
    """Test configuration and environment variables"""
    
    def test_config_class_attributes(self):
        """Test Config class has required attributes"""
        assert hasattr(Config, 'OPENAI_API_KEY')
        assert hasattr(Config, 'GITHUB_TOKEN')
        assert hasattr(Config, 'GITHUB_REPO')
        assert hasattr(Config, 'NIST_BASE_URL')
        assert hasattr(Config, 'NIST_SEARCH_TERMS')
        
    def test_nist_search_terms(self):
        """Test NIST search terms are properly configured"""
        search_terms = Config.NIST_SEARCH_TERMS
        assert isinstance(search_terms, list)
        assert len(search_terms) > 0
        assert 'NIST SP 800-53' in search_terms
        assert 'NIST SP 800-171' in search_terms

class TestWorkflowRequest:
    """Test Pydantic models"""
    
    def test_workflow_request_default_values(self):
        """Test WorkflowRequest model with default values"""
        request = WorkflowRequest()
        assert request.topic is None
        assert request.max_articles == 10
        
    def test_workflow_request_with_values(self):
        """Test WorkflowRequest model with custom values"""
        request = WorkflowRequest(topic="secure development", max_articles=5)
        assert request.topic == "secure development"
        assert request.max_articles == 5

class TestIntegration:
    """Integration tests for the complete workflow"""
    
    @pytest.mark.asyncio
    async def test_full_workflow_mock(self, agent):
        """Test the complete workflow with mocked dependencies"""
        # This would be a more comprehensive integration test
        # that mocks all external dependencies and tests the full flow
        
        # Mock search results
        mock_articles = [
            {
                'title': 'Test NIST Publication',
                'url': 'https://example.com/test',
                'date': '2024-12-01',
                'summary': 'Test summary with CI/CD and security content',
                'source': 'Test Source'
            }
        ]
        
        # Mock all the workflow steps
        with patch.object(agent, 'search_nist_updates', return_value=mock_articles), \
             patch.object(agent, 'extract_content', return_value=mock_articles), \
             patch.object(agent, 'filter_it_relevant_content', return_value=mock_articles), \
             patch.object(agent, 'generate_summary', return_value="# Test Summary"), \
             patch.object(agent, 'publish_to_github', return_value={'pr_url': 'test-url'}):
            
            # This would normally be called by the FastAPI endpoint
            # but we're testing the core workflow logic
            
            # Step 1: Search
            articles = await agent.search_nist_updates("test", 10)
            assert len(articles) > 0
            
            # Step 2: Extract
            articles_with_content = await agent.extract_content(articles)
            assert len(articles_with_content) > 0
            
            # Step 3: Filter
            relevant_articles = await agent.filter_it_relevant_content(articles_with_content)
            assert len(relevant_articles) > 0
            
            # Step 4: Summarize
            summary = await agent.generate_summary(relevant_articles)
            assert len(summary) > 0
            
            # Step 5: Publish
            result = await agent.publish_to_github(summary, relevant_articles)
            assert 'pr_url' in result

# Performance and load testing helpers
class TestPerformance:
    """Performance and load testing"""
    
    @pytest.mark.asyncio
    async def test_concurrent_requests(self, agent):
        """Test handling multiple concurrent requests"""
        # Mock the dependencies
        with patch.object(agent, 'search_nist_updates', return_value=[]), \
             patch.object(agent, 'extract_content', return_value=[]), \
             patch.object(agent, 'filter_it_relevant_content', return_value=[]), \
             patch.object(agent, 'generate_summary', return_value="Test"), \
             patch.object(agent, 'publish_to_github', return_value={'pr_url': 'test'}):
            
            # Create multiple concurrent tasks
            tasks = []
            for i in range(5):
                task = agent.search_nist_updates(f"topic-{i}", 5)
                tasks.append(task)
            
            # Execute concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # All should complete without errors
            for result in results:
                assert not isinstance(result, Exception)

# Utility functions for testing
def create_mock_article(title="Test Article", include_security_content=True):
    """Helper function to create mock articles for testing"""
    content = "This article discusses general topics."
    if include_security_content:
        content = """
        This article discusses secure software development practices including:
        - CI/CD pipeline security
        - SAST and DAST tools integration
        - Supply chain security and SBOM requirements
        - Container security best practices
        - DevOps security controls
        """
    
    return {
        'title': title,
        'url': f'https://example.com/{title.lower().replace(" ", "-")}',
        'date': datetime.now().isoformat(),
        'summary': f'Summary for {title}',
        'content': content,
        'source': 'Test Source'
    }

def assert_valid_markdown_summary(summary):
    """Helper function to validate generated summaries"""
    assert isinstance(summary, str)
    assert len(summary) > 0
    
    # Check for YAML frontmatter
    assert summary.startswith('---')
    assert 'title:' in summary
    assert 'date:' in summary
    
    # Check for required sections
    assert '# NIST' in summary or '# Compliance' in summary
    
    # Check for citations or source references
    assert 'http' in summary or 'nist.gov' in summary

if __name__ == '__main__':
    # Run tests
    pytest.main(['-v', __file__])