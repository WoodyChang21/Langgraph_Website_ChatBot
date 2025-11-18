"""
Shared utilities for MongoDB Vector Store operations.
"""
from langchain_openai import OpenAIEmbeddings
from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

# 環境變數
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MONGODB_URL = os.getenv("MONGODB_URL")
DATABASE_NAME = os.getenv("DATABASE_NAME")
QA_COLLECTION_NAME = os.getenv("QA_COLLECTION_NAME")
ATLAS_VECTOR_SEARCH_INDEX_NAME = os.getenv("ATLAS_VECTOR_SEARCH_INDEX_NAME")

# Embedding 設定
_embedding_model = OpenAIEmbeddings(model="text-embedding-3-small")

# MongoDB 連接 (單例模式)
_client = None
_collection = None


def get_mongo_client():
    """Get or create MongoDB client instance."""
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URL)
    return _client


def get_collection(collection: str):
    """Get or create MongoDB collection instance."""
    client = get_mongo_client()
    _collection = client[DATABASE_NAME][collection]
    return _collection

def get_vector_store(collection: str):
    """
    Get or create MongoDBAtlasVectorSearch instance.
    
    Returns:
        MongoDBAtlasVectorSearch: Configured vector store instance
    """
    collection = get_collection(collection=collection)
    return MongoDBAtlasVectorSearch(
        collection=collection,
        embedding=_embedding_model,
        index_name=ATLAS_VECTOR_SEARCH_INDEX_NAME,
        relevance_score_fn="cosine",
    )

