import pytest
from src.tools.web_tools import web_search, open_web_resource


@pytest.mark.asyncio
async def test_web_search_success():
    """Validates real-time external web search execution."""
    result = await web_search.ainvoke({"query": "Python programming language"})

    assert "Sir" in result
    assert (
        "according to real-time web results" in result
        or "returned no relevant" in result
    )


@pytest.mark.asyncio
async def test_open_web_resource_facebook():
    """Validates simple platform navigation without queries."""
    result = await open_web_resource.ainvoke({"target": "facebook"})
    assert "opened facebook" in result or "accessed facebook" in result


@pytest.mark.asyncio
async def test_open_web_resource_youtube_search():
    """Validates platform navigation with search parameters."""
    result = await open_web_resource.ainvoke(
        {"target": "youtube", "action_query": "synthwave music"}
    )
    assert "synthwave music" in result
