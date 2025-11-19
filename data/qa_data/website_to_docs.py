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
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
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
    import time
    from firecrawl.v2.utils.error_handler import InternalServerError
    
    firecrawl = FireCrawlWebsiteToDocs()
    from data.qa_data.data_sources import URLS_CONFIG
    
    # Create the markdown directory if it doesn't exist
    markdown_dir = "data/qa_data/markdown"
    os.makedirs(markdown_dir, exist_ok=True)
    
    failed_urls = []
    successful_urls = []
    
    for source, url in URLS_CONFIG.items():
        try:
            log_info(f"Processing {source} from {url}...")
            docs = firecrawl.load_url(url, source)
            
            if not docs:
                log_warning(f"No documents retrieved for {source}")
                failed_urls.append((source, url, "No documents retrieved"))
                continue
            
            for doc in docs:
                markdown_content = doc.page_content
                markdown_file = f"{markdown_dir}/{source}.md"
                with open(markdown_file, "w", encoding="utf-8") as f:
                    f.write(markdown_content)
                log_success(f"Saved {source} to {markdown_file}")
                successful_urls.append(source)
            
            # Add a small delay between requests to avoid rate limiting
            time.sleep(2)
            
        except InternalServerError as e:
            error_msg = str(e)
            log_error(f"FireCrawl error for {source} ({url}): {error_msg}")
            failed_urls.append((source, url, "FireCrawl Internal Server Error"))
            # Continue with next URL
            continue
        except Exception as e:
            error_msg = str(e)
            log_error(f"Failed to process {source} ({url}): {error_msg}")
            failed_urls.append((source, url, error_msg))
            # Continue with next URL
            continue
    
    # Report summary
    log_header("Processing Summary")
    log_success(f"Successfully processed: {len(successful_urls)} URLs")
    if successful_urls:
        for source in successful_urls:
            log_success(f"  ✓ {source}")
    
    if failed_urls:
        log_warning(f"Failed to process: {len(failed_urls)} URLs")
        for source, url, error in failed_urls:
            log_error(f"  ✗ {source}: {url}")
            log_error(f"    Error: {error[:150]}")
    else:
        log_success("All URLs processed successfully!")
