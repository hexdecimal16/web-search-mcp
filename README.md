# Web Search MCP Tool

A Model Context Protocol (MCP) server that provides a tool for performing Google searches and retrieving the content of the top results.

## Features

-   Performs a Google search for a given query.
-   Identifies the top 5 non-social media search results.
-   Crawls the content of the top results.
-   Returns the crawled content as a single string.

## Prerequisites

-   **Python 3.13+**
-   **uv**: This project uses `uv` for package management. If you don't have it, install it with:
    ```bash
    curl -LsSf https://astral.sh/uv/install.sh | sh
    ```

## Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/hexdecimal16/web-search-mcp
    cd web-search-mcp
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    uv venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    The project's dependencies are defined in `pyproject.toml`. Install them using `uv`:
    ```bash
    uv sync
    ```

## Usage

This tool is designed to be launched by an MCP client application (e.g., Claude Desktop) using `stdio` as the transport mechanism.

### MCP Client Configuration

You must configure your MCP client to launch the tool. The following JSON configuration uses `uv` to run the `web_search.py` script.

**Note:** This configuration is based on the user's specific request. For some MCP client environments that have issues with `asyncio` event loop conflicts, a different configuration may be needed.

```json
{
  "mcpServers": {
    "web-search": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/your/project/web-search-mcp",
        "run",
        "web_search.py",
        "--timeout=15"
      ]
    }
  }
}
```
**Important:** Replace `/path/to/your/project/web-search-mcp` with the correct absolute path to this project on your filesystem.

## Testing

To verify that the script is syntactically correct and the tool is functioning, you can run the included tests using `pytest`.

1.  **Install test dependencies:**
    ```bash
    uv pip install pytest pytest-asyncio
    ```

2.  **Run the tests:**
    ```bash
    pytest
    ```