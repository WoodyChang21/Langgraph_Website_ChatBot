from langchain_core.documents import Document
from typing import List
import os

from langchain_mongodb.vectorstores import MongoDBAtlasVectorSearch

from logger import log_success

# Process all batches concurrently
def add_documents(
    documents: List[Document],
    vectorstore: MongoDBAtlasVectorSearch
):
    """Process documents in batches asynchronously.
    
    Args:
        documents: List of documents to add
        batch_size: Number of documents per batch
        vectorstore: Vector store instance
    """
    vectorstore.add_documents(documents)
    log_success(f"Added {len(documents)} documents to vector store")
