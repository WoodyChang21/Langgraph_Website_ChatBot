""" This file uses FireCrawl to convert a url website to markdown format for RAG"""
from langchain_community.document_loaders.firecrawl import FireCrawlLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from dotenv import load_dotenv
import os
import asyncio
from typing import List
from logger import log_success, log_error, log_header, log_info, Colors, log_warning

load_dotenv()

# FireCrawl Website to Markdown
class FireCrawlWebsiteToDocs:
    def __init__(self):
        self.mode = "scrape"
    

    def split_docs(self, docs: List[Document]):
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splitted_docs = text_splitter.split_documents(docs)
        log_success(f"Split {len(docs)} documents into {len(splitted_docs)} chunks")
        return splitted_docs


    def load_url(self, url: str, source: str):
        docs = []
        loader = FireCrawlLoader(
            api_key=os.getenv("FIRECRAWL_API_KEY"),
            url=url,
            mode=self.mode
        )
        document_data = loader.load()
        for doc in document_data:
            docs.append(Document(
                page_content=doc.page_content, 
                metadata={"source": source, "url": doc.metadata["url"]}))
        log_success(f"Loaded {len(docs)} documents from {url}")
        return docs

    def load_url_to_splitted_docs(self, url, source: str):
        docs = self.load_url(url, source)
        splitted_docs = self.split_docs(docs)
        return splitted_docs


if __name__ == "__main__":
    # url = "https://www.countess.tw/v2/Official/BrandStory"
    url = "https://www.countess.tw/page/childrens_bedding"
    mode = "scrape"
    firecrawl = FireCrawlWebsiteToDocs()
    print(firecrawl.load_url_to_splitted_docs(url, "品牌故事"))
    # print(firecrawl.load_url(url, "品牌故事"))
