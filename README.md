# YiChin Chatbot System (億進寢具 Chatbot)

A RAG-powered chatbot system built with LangGraph, FastAPI, and MongoDB Atlas. Provides an intelligent customer service agent for Yi Jinn Bedding that answers product questions, provides recommendations, and maintains conversation context.

## Overview

The chatbot uses:
- **LangGraph**: Stateful conversational agent with memory
- **RAG**: Retrieval-Augmented Generation for grounding responses in product data and FAQs
- **MongoDB Atlas**: Vector storage with hybrid search
- **Redis**: Conversation state management

## How RAG Works

1. **Data Ingestion**: 
   - Product data and website content are scraped and transformed into documents
   - Documents are chunked (500 chars, 100 overlap) and embedded using `text-embedding-3-small`
   - Embeddings are stored in MongoDB Atlas with vector search indexes

2. **Query Processing**:
   - User query is embedded into the same vector space
   - Hybrid search combines vector similarity and full-text search to retrieve relevant documents
   - Top 5 most relevant documents are retrieved from either QA or product collections

3. **Response Generation**:
   - Retrieved documents are passed as context to the LLM (GPT-4o-mini)
   - Agent uses tools (`search_faq_tool`, `search_product_tool`, `filter_product_tool`) to fetch relevant information
   - LLM generates grounded responses based on retrieved context, preventing hallucinations

## Prerequisites

- Python 3.11+
- OpenAI API key
- MongoDB Atlas account with Vector Search enabled
- FireCrawl API key
- Redis (included in docker-compose.yml)

## Setup

### 1. Clone and Configure Environment

```bash
git clone <repository-url>
cd Langgraph_Website_ChatBot
cp .env.example .env
# Edit .env with your API keys and credentials
```

Required environment variables (see `.env.example` for details):
- `OPENAI_API_KEY`
- `MONGODB_URL`, `DATABASE_NAME`, collection names
- `REDIS_URL`
- `FIRECRAWL_API_KEY`

### 2. Install Dependencies

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python fix_langchain_mongodb.py
```

### 3. Set Up MongoDB

1. Create collections in MongoDB Atlas: `qa_collection` and `product_collection`
2. Create vector search index (JSON Editor):
   ```json
   {
     "mappings": {
       "dynamic": true,
       "fields": {
         "embedding": {
           "type": "knnVector",
           "dimensions": 1536,
           "similarity": "cosine"
         }
       }
     }
   }
   ```
   Name it `vector_index` (or match `ATLAS_VECTOR_SEARCH_INDEX_NAME` in `.env`)

### 4. Start Redis

```bash
docker-compose up -d redis
# Or install locally: sudo apt-get install redis-server
```

### 5. Ingest Data

```bash
python rag/add_data_to_mongo.py
```

This scrapes website content and loads product data into MongoDB.

### 6. Run Application

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8511 --reload
```

API available at `http://localhost:8511` (docs at `/docs`)

## Docker Setup

```bash
docker-compose up -d --build
docker-compose exec app python rag/add_data_to_mongo.py
```

## API Usage

**Get Answer:**
```bash
GET /chatbot/get_agent_answer/?question=我想找一件不會太熱的雙人棉被&uuid=user123
```

**Streaming Answer:**
```bash
GET /chatbot/get_agent_answer_stream/?question=棉被應該多久清洗一次？&uuid=user123
```

## Project Structure

- `agent/` - LangGraph agent with tools and memory
- `api/` - FastAPI endpoints
- `data/` - Data sources (product data, website URLs)
- `rag/` - RAG implementation (vector store, search functions, data ingestion)

## Troubleshooting

- **MongoDB connection**: Verify `MONGODB_URL` and IP whitelist
- **Redis connection**: Check `REDIS_URL` and ensure Redis is running
- **Vector index errors**: Ensure index is created and finished building in Atlas
- **Import errors**: Run `python fix_langchain_mongodb.py`
