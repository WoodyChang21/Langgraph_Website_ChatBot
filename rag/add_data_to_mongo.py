""" This file loads the data from the data source through web crawling and add the data to MongoDB"""
from data.qa_data.website_to_docs import FireCrawlWebsiteToDocs
from data.qa_data.data_sources import URLS_CONFIG
from data.product_data.product_data import PRODUCT_DATA
from data.product_data.data_to_docs import transform_product
from rag.mongo_db_utils.add_data import add_documents
from rag.mongo_db_utils.create_index import create_index
from rag.mongo_db_utils.vector_store_utils import get_vector_store
from dotenv import load_dotenv
import os
load_dotenv()

QA_COLLECTION_NAME = os.getenv("QA_COLLECTION_NAME")
PRODUCT_COLLECTION_NAME = os.getenv("PRODUCT_COLLECTION_NAME")

qa_vectorstore = get_vector_store(QA_COLLECTION_NAME)
product_vectorstore = get_vector_store(PRODUCT_COLLECTION_NAME)

def qa_data_processing():
    data = URLS_CONFIG
    firecrawl = FireCrawlWebsiteToDocs()
    create_index(QA_COLLECTION_NAME)
    for source, url in data.items():
        docs = firecrawl.load_url_to_splitted_docs(url, source)
        add_documents(docs, qa_vectorstore)

def product_data_processing():
    create_index(PRODUCT_COLLECTION_NAME)
    docs = transform_product(PRODUCT_DATA)
    add_documents(docs, product_vectorstore)

if __name__ == "__main__":
    qa_data_processing()
    product_data_processing()