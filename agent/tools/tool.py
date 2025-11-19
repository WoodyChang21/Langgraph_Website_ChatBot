from langchain_core.tools import tool
from typing import List, Dict, Any, Optional, Literal

from rag.search_data import search_qa_data, search_product_data, filter_products
from data.product_data.product_data import PRODUCT_CATEGORIES, PRODUCT_NAME
from agent.tools.tool_schema import ProductSearchSchema, ProductFilterSchema


@tool("faq_search_tool")
def rag_search(query: str) -> List[Dict[str, Any]]:
    """
    DO NOT USE THIS TOOL FOR ANY PRODUCT-RELATED QUESTIONS.

    Use only for brand/company FAQs like brand story, ESG, bedding maintenance, etc.
    NEVER use this tool for product features, suitability, sizes, or recommendations — use `product_search_tool` instead.

    Searches the Countess (億進寢具) knowledge base for relevant info.

    Sources include:
    - 品牌故事 (Brand Story)
    - 商店簡介 (Store Introduction)
    - 寢具知識 (Bedding Q&A): kindergarten bedding, dorm life, pillow/quilt selection, maintenance
    - 企業報導 (Company Reports): ESG/sustainability

    Args:
        query: The user's question (include context only if it's a follow-up).

    Returns:
        List of matching documents:
        - source: Document source
        - url: Link to document
        - content: Text content
        - rank: Relevance rank (0–4)
    """
    rag_data = search_qa_data(query)
    return rag_data

@tool("product_search_tool", args_schema=ProductSearchSchema)
def product_search(
    query: str,
    category: Optional[Literal[*PRODUCT_CATEGORIES]] = None,
    product_name: Optional[Literal[*PRODUCT_NAME]] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    size: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    SCOPE: Use for semantic product queries — features, recommendations, or fuzzy matches.
    DO NOT use for exact filtering (e.g., "products under 2500") — use `product_filter_tool` instead.

    This tool uses natural language vector search to find relevant products based on meaning.
    Only include the filter parameters if the user explicitly asks for it. Otherwise, always default to None for all filter parameters.

    Returns:
        A list of product matches ranked by semantic similarity.
    """
    return search_product_data(
        query=query,
        category=category,
        product_name=product_name,
        price_min=price_min,
        price_max=price_max,
        size=size
    )

@tool("product_filter_tool", args_schema=ProductFilterSchema)
def product_filter(
    category: Optional[Literal[PRODUCT_CATEGORIES]] = None,
    product_name: Optional[Literal[PRODUCT_NAME]] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    size: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    SCOPE: Use for exact product filtering by category, price, or size.
    DO NOT use for fuzzy or descriptive queries — use `product_search_tool` instead.

    Returns:
        A list of all products matching the exact filter criteria.
    """
    return filter_products(
        category=category,
        product_name=product_name,
        price_min=price_min,
        price_max=price_max,
        size=size,
        limit=100
    )
