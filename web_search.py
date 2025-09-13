import asyncio
import os
import sys

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
from mcp.server.fastmcp import FastMCP
import nest_asyncio

# Apply the patch to allow nested asyncio event loops
nest_asyncio.apply()

# Initialize FastMCP server
mcp = FastMCP("web-search")

# A context manager to suppress stdout and stderr
class suppress_output:
    def __enter__(self):
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        sys.stdout = open(os.devnull, 'w')
        sys.stderr = open(os.devnull, 'w')

    def __exit__(self, exc_type, exc_val, exc_tb):
        sys.stdout.close()
        sys.stderr.close()
        sys.stdout = self.stdout
        sys.stderr = self.stderr

async def async_perform_google_search(query: str, crawler: AsyncWebCrawler):
    """
    Performs a Google search asynchronously, suppressing library output.
    """
    search_url = f"https://www.google.com/search?q={query}"
    
    prune_filter = PruningContentFilter(
        # Lower → more content retained, higher → more content pruned
        threshold=0.45,           
        # "fixed" or "dynamic"
        threshold_type="dynamic",  
        # Ignore nodes with <5 words
        min_word_threshold=5      
    )
    md_generator = DefaultMarkdownGenerator(content_filter=prune_filter)

    crawl_config = CrawlerRunConfig(markdown_generator=md_generator)
    search_result = None
    # Suppress any output from the crawler
    with suppress_output():
        search_result = await crawler.arun(search_url, config=crawl_config)

    if not search_result or not search_result.success:
        error_message = "Unknown error"
        if search_result and hasattr(search_result, '_results') and search_result._results and hasattr(search_result._results[0], 'error'):
            error_message = search_result._results[0].error
        return f"Failed to retrieve Google search results: {error_message}"

    links = []
    if hasattr(search_result, '_results') and search_result._results:
        result_data = search_result._results[0]
        if hasattr(result_data, 'links'):
            all_links = result_data.links.get('external', []) + result_data.links.get('internal', [])
            seen = set()
            for link_info in all_links:
                link = link_info.get('href')
                if link and link not in seen:
                    seen.add(link)
                    links.append(link)

    skip_domains = ["google", "youtube", "linkedin", "twitter", "facebook"]
    top_5_links = [link for link in links if not any(domain in link for domain in skip_domains)][:5]
    if not top_5_links:
        return "No relevant links found in the search results."

    crawl_results = []
    # Suppress any output from the crawler
    with suppress_output():
        for link in top_5_links:
            print(f"Fetching content from: {link}")
            result = await crawler.arun(link, config=crawl_config)
            crawl_results.append(result)

    final_content = ""
    for res in crawl_results:
        if res.success and res.markdown.fit_markdown:
            final_content += res.markdown.fit_markdown + "\n\n"

    return final_content

def perform_google_search(query: str):
    """
    Synchronous wrapper for the async Google search function.
    """
    browser_config =  BrowserConfig(
        headless=True,
        use_managed_browser=True,
        user_data_dir="/Users/dtripathi/projects/mcp/web-search/.profile",

    )
    crawler = AsyncWebCrawler(config=browser_config)
    result = asyncio.run(async_perform_google_search(query, crawler))

    # close the crawler
    asyncio.run(crawler.close())
    return result


@mcp.tool(
    name="web_search",
    description="Web search tool that uses Google to find relevant information on the web. Input is a search query string, and output is the top results from the search.",
    annotations={"web_search": {"mcp": {"max_retries": 2}}},
    structured_output=False,
    title="Web Search Tool"
)
def web_search(query: str) -> str:
    """
    Perform a web search using Google and return the top results.
    """
    return perform_google_search(query)


if __name__ == "__main__":
    # Initialize and run the server, listening on stdio
    mcp.run(transport='stdio')