import pytest
import sys
import os


from tools.search_tool import WebSearchTool
from tools.crawler_tool import WebCrawlerTool
from agent.orchestrator import AgentOrchestrator


def test_search_tool_structure() -> None:
    """Test if search tool fetches records correctly and preserves schema keys."""
    search_tool = WebSearchTool()
    results = search_tool.search("هوش مصنوعی")
    
    assert isinstance(results, list)
    
    if len(results) > 0:
        first_result = results[0]
        assert "title" in first_result
        assert "link" in first_result  
        assert "snippet" in first_result


def test_crawler_html_parser_unit() -> None:
    """Unit test for the parser layer (_clean_html) to fulfill task requirements."""
    crawler = WebCrawlerTool()
    mock_html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <nav>Ignore this navigation bar</nav>
            <header>Ignore header</header>
            <h1>Main Research Concept</h1>
            <p>Target visible content here.</p>
            <script>console.log('Ignore scripting blocks');</script>
        </body>
    </html>
    """
    cleaned = crawler._clean_html(mock_html)
    
    # Assert structural text filtering works perfectly
    assert "Main Research Concept" in cleaned
    assert "Target visible content here." in cleaned
    assert "Ignore this navigation bar" not in cleaned
    assert "console.log" not in cleaned


def test_web_scraper_execution() -> None:
    """Test live crawling response handling from standard web page endpoints."""
    crawler = WebCrawlerTool()
    test_url = "https://www.varzesh3.com"
    content = crawler.extract_text(test_url)
    
    assert isinstance(content, str)


def test_orchestrator_initialization() -> None:
    """Test orchestrator engine setup and local LLM dependency loading."""
    orchestrator = AgentOrchestrator()
    assert orchestrator.llm is not None
    assert orchestrator.search_tool is not None
    assert orchestrator.crawler_tool is not None