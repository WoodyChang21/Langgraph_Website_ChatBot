from rag.mongo_db_utils.vector_store_utils import get_vector_store, get_collection
from langchain_mongodb.retrievers import MongoDBAtlasHybridSearchRetriever
import os
from typing import Optional, Literal
import logger
from dotenv import load_dotenv

from data.product_data.product_data import PRODUCT_CATEGORIES, PRODUCT_NAME

load_dotenv()

QA_COLLECTION_NAME = os.getenv("QA_COLLECTION_NAME")
PRODUCT_COLLECTION_NAME = os.getenv("PRODUCT_COLLECTION_NAME")
qa_store = get_vector_store(QA_COLLECTION_NAME)
product_store = get_vector_store(PRODUCT_COLLECTION_NAME)


def search_qa_data(query, k: int = 5):
    """
    Search QA collection using vector search.
    
    Args:
        query: Search query string
        k: Number of results to return
        score_threshold: Minimum similarity score threshold
    
    Returns:
        List of formatted search results
    """
    retriever = MongoDBAtlasHybridSearchRetriever(
        vectorstore = qa_store,
        search_index_name = "search_index",
        top_k = k,
        fulltext_penalty = 50,
        vector_penalty = 50)

    results = retriever.invoke(query)

    # Format results into structured dictionaries
    formatted_results = []

    for document in results:
        formatted_result = {
            "source": document.metadata.get("source", ""),
            "url": document.metadata.get("url", ""),
            "content": document.page_content,
            "rank": document.metadata.get("rank", 0),
        }
        formatted_results.append(formatted_result)

    formatted_results.sort(key=lambda x: x["rank"])

    # If no relevant results found, provide a helpful fallback
    if not formatted_results:
        formatted_results = [
            {
                "source": "系統預設",
                "url": "",
                "content": "很抱歉，我無法在現有的資料中找到與您問題相關的資訊。建議您直接聯繫我們的客服部門，他們將為您提供更詳細的協助。",
                "rank": 0,
            }
        ]

    return formatted_results


def filter_products(
    category: Optional[Literal[PRODUCT_CATEGORIES]] = None,
    product_name: Optional[Literal[PRODUCT_NAME]] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    size: Optional[str] = None,
    limit: int = 100
):
    """
    Pure MongoDB filtering without vector search.
    Returns ALL products matching the exact filter criteria.
    """    
    collection = get_collection(PRODUCT_COLLECTION_NAME)
    
    # Build MongoDB query filter
    query_filter = {}
    
    if category:
        query_filter["category"] = category
    
    if product_name:
        query_filter["product_name"] = product_name
    
    if price_min is not None or price_max is not None:
        price_filter = {}
        if price_min is not None:
            price_filter["price_range.min"] = {"$gte": price_min}
        if price_max is not None:
            price_filter["price_range.max"] = {"$lte": price_max}
        if price_filter:
            query_filter.update(price_filter)
    
    if size:
        query_filter["variants.size"] = size
    
    # Query MongoDB directly
    cursor = collection.find(query_filter).limit(limit)
    
    formatted_results = []
    for doc in cursor:
        ret = {
            "product_name": doc.get("product_name", ""),
            "description": doc.get("text", ""),
            "category": doc.get("category", ""),
            "variants": doc.get("variants", []),
            "price_range": doc.get("price_range", {}),
            "score": 1.0,  # Pure filtering doesn't have similarity scores
        }
        formatted_results.append(ret)
    
    if not formatted_results:
        formatted_results = [
            {
                "product_name": "很抱歉，我無法在現有的資料中找到符合條件的產品。建議您直接聯繫我們的客服部門，他們將為您提供更詳細的協助。",
                "description": "",
                "category": "",
                "variants": [],
                "price_range": {},
                "score": 0.0,
            }
        ]
    
    return formatted_results


def search_product_data(
    query: str,
    category: Optional[str] = None,
    product_name: Optional[str] = None,
    price_min: Optional[int] = None,
    price_max: Optional[int] = None,
    size: Optional[str] = None
):
    """
    Semantic vector search for products based on natural language queries.
    
    Use this for semantic queries about product features, attributes, or recommendations:
    """
    # Build filter conditions for metadata filtering
    filter_conditions = []
    
    if category:
        filter_conditions.append({"category": category})
    
    if product_name:
        filter_conditions.append({"product_name": product_name})
    
    if price_min is not None or price_max is not None:
        price_filter = {}
        if price_min is not None:
            price_filter["price_range.min"] = {"$gte": price_min}
        if price_max is not None:
            price_filter["price_range.max"] = {"$lte": price_max}
        if price_filter:
            filter_conditions.append(price_filter)
    
    if size:
        filter_conditions.append({"variants.size": size})
    
    # Build post_filter pipeline only if we have metadata filters
    # Note: No score_threshold for hybrid search (RRF uses rank-based scoring, not similarity scores)
    post_filter_pipeline = None
    
    if filter_conditions:
        metadata_filter = {"$and": filter_conditions} if len(filter_conditions) > 1 else filter_conditions[0]
        post_filter_pipeline = [{"$match": metadata_filter}]
    
    retriever = MongoDBAtlasHybridSearchRetriever(
        vectorstore = product_store,
        search_index_name = "search_index",
        top_k = 5,
        fulltext_penalty = 50,
        vector_penalty = 50,
        post_filter=post_filter_pipeline)

    results = retriever.invoke(query)

    formatted_results = []
    for document in results:
        ret = {
            "product_name": document.metadata.get("product_name", ""),
            "description": document.page_content,
            "category": document.metadata.get("category", ""),
            "variants": document.metadata.get("variants", []),
            "price_range": document.metadata.get("price_range", {}),
            "rank": document.metadata.get("rank", 0),
        }
        formatted_results.append(ret)
    
    formatted_results.sort(key=lambda x: x["rank"])
    
    if not formatted_results:
        formatted_results = [
            {
                "product_name": "很抱歉，我無法在現有的資料中找到與您問題相關的產品。建議您直接聯繫我們的客服部門，他們將為您提供更詳細的協助。",
                "description": "",
                "category": "",
                "variants": [],
                "price_range": {},
                "rank": 0.0,
            }
        ]
    return formatted_results

if __name__ == "__main__":
    # Check the accuracy of get_background_infos function
    query = "康適四孔棉抗菌被有哪些尺寸？"
    # print(search_data(query, score_threshold=0.7))
    print(search_product_data(query))
