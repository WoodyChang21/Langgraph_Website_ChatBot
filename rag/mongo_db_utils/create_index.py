from rag.mongo_db_utils.vector_store_utils import get_vector_store
from langchain_mongodb.index import create_fulltext_search_index
from rag.mongo_db_utils.vector_store_utils import get_mongo_client
import os
from dotenv import load_dotenv

load_dotenv()

QA_COLLECTION_NAME = os.getenv("QA_COLLECTION_NAME")
PRODUCT_COLLECTION_NAME = os.getenv("PRODUCT_COLLECTION_NAME")
DATABASE_NAME = os.getenv("DATABASE_NAME")
SEARCH_INDEX_NAME = os.getenv("SEARCH_INDEX_NAME")

def create_search_index(collection: str=PRODUCT_COLLECTION_NAME):
    """
    Create MongoDB Full-text search index for product search.
    
    Args:
        collection: Collection name to create index for
    """
    client = get_mongo_client()
    create_fulltext_search_index(
        collection = client[DATABASE_NAME][collection],
        field = "text",
        index_name = SEARCH_INDEX_NAME
    )

def create_index(collection: str):
    """
    Create MongoDB Vector Search index for semantic search.
    
    This creates only the vector search index (no full-text search index).
    Vector search is sufficient for most use cases and avoids compatibility issues.
    
    Args:
        collection: Collection name to create index for
    """
    vector_store = get_vector_store(collection)
    vector_store.create_vector_search_index(dimensions=1536)
    create_search_index(collection)


if __name__ == "__main__":
    # create_index(PRODUCT_COLLECTION_NAME)
    create_search_index(QA_COLLECTION_NAME)