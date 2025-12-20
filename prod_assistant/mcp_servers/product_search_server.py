import sys
from mcp.server.fastmcp import FastMCP
from prod_assistant.retriever.retrieval import Retriever
from langchain_community.tools import DuckDuckGoSearchRun
import asyncio


# Initialize MCP server
mcp = FastMCP("hybrid_search")

# Load retriever once
retriever_obj = Retriever()
retriever = retriever_obj.load_retriever()

# LangChain DuckDuckGo tool
duckduckgo = DuckDuckGoSearchRun()

# ---------- Helpers ----------
def format_docs(docs) -> str:
    """Format retriever docs into readable context."""
    if not docs:
        return ""
    formatted_chunks = []
    for d in docs:
        meta = d.metadata or {}
        formatted = (
            f"Title: {meta.get('product_title', 'N/A')}\n"
            f"Price: {meta.get('price', 'N/A')}\n"
            f"Rating: {meta.get('rating', 'N/A')}\n"
            f"Reviews:\n{d.page_content.strip()}"
        )
        formatted_chunks.append(formatted)
    return "\n\n---\n\n".join(formatted_chunks)

# ---------- MCP Tools ----------
@mcp.tool()
async def get_product_info(query: str) -> str:
    try:
        product_keywords = [
            "phone","mobile","laptop","charger","price",
            "gb","ram","camera","note","pro","galaxy","samsung"
        ]
        if not any(word in query.lower() for word in product_keywords):
            return "No local results found."

        docs = retriever.invoke(query)
        if not docs or len(docs) == 0:
            return "No local results found."

        # crude relevance check: require query words in top doc
        query_words = set(query.lower().replace("?", "").split())
        top_doc_text = docs[0].page_content.lower()
        if not any(word in top_doc_text for word in query_words):
            return "No local results found."

        context = format_docs(docs)
        if not context.strip():
            return "No local results found."

        return context
    except Exception as e:
        return f"Error retrieving product info: {str(e)}"
    
@mcp.tool()
async def web_search(query: str) -> str:
    """Search the web using DuckDuckGo if retriever has no results."""
    try:
        # DuckDuckGoSearchRun.run is synchronous, wrap in thread
        return await asyncio.to_thread(duckduckgo.run, query)
    except Exception as e:
        return f"Error during web search: {str(e)}"

# ---------- Run Server ----------
if __name__ == "__main__":
    print("[DEBUG] Starting MCP server...", file=sys.stderr, flush=True)
    mcp.run(transport="stdio")
