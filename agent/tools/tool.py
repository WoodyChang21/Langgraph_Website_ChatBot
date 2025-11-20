from langchain_core.tools import tool
from typing import List, Dict, Any, Optional, Literal

from rag.search_data import search_qa_data, search_product_data, filter_products
from data.product_data.product_data import PRODUCT_CATEGORIES, PRODUCT_NAME
from agent.tools.tool_schema import ProductSearchSchema, ProductFilterSchema


@tool("search_faq_tool")
def rag_search(query: str) -> List[Dict[str, Any]]:
    """
    📚 General Knowledge & Non-Product Queries.
    
    Use this tool for ANYTHING that is NOT related to products.
    - Brand info, Store locations, ESG.
    - General Knowledge
    - Policy questions (Returns, Shipping).
    
    ⛔ HARD STOP: If user asks for prices, specs, or any product related information, DO NOT use this.
    """
    rag_data = search_qa_data(query)
    return rag_data

@tool("search_product_tool", args_schema=ProductSearchSchema)
def product_search(
    query: str,
    category: Optional[Literal[*PRODUCT_CATEGORIES]] = None,
    product_name: Optional[Literal[*PRODUCT_NAME]] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    size: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    🛍️ Product Features, Recommendations & Semantic Search.
    
    Use this for ALL product-related questions that are not strict filters.
    - **Features:** "What are the features of the Tencel quilt?"
    - **Recommendations:** "I want something for winter", "Which is good for allergies?"
    - **Subjective/Fuzzy:** "Find me a soft quilt."
    
    Args:
        query: Descriptive/subjective part of user's question about product features, recommendations, or needs.
        category, product_name, price_min, price_max, size: Only set if user EXPLICITLY mentions them.
    """
    return search_product_data(
        query=query,
        category=category,
        product_name=product_name,
        price_min=price_min,
        price_max=price_max,
        size=size
    )

@tool("filter_product_tool", args_schema=ProductFilterSchema)
def product_filter(
    category: Optional[Literal[PRODUCT_CATEGORIES]] = None,
    product_name: Optional[Literal[PRODUCT_NAME]] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    size: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    🔍 Exact Database Filtering (Strict Constraints).
    
    Use when: The user acts like a database filter, providing **rigid, objective constraints** to narrow down the list of available products.
    
    Args:
        category, product_name, price_min, price_max, size: Only set parameters that user EXPLICITLY mentions.
    """
    return filter_products(
        category=category,
        product_name=product_name,
        price_min=price_min,
        price_max=price_max,
        size=size,
        limit=100
    )
