import pytest
from web_search import web_search

@pytest.mark.asyncio
async def test_web_search():
    """
    Tests that the web_search tool returns a string.
    """
    # We can't easily mock the google search, so we'll just
    # test that the function runs without error and returns a string.
    # This is more of an integration test than a unit test.
    result = await web_search("what is the capital of France?")
    assert isinstance(result, str)
    assert result
