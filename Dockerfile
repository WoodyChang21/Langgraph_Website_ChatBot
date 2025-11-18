# Dockerfile for YiChin Chatbot System

FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv (fast Python package installer)
RUN pip install --no-cache-dir uv

# Copy requirements
COPY requirements.txt .

# Install Python dependencies using uv (much faster than pip!)
RUN uv pip install --system --no-cache -r requirements.txt

# Copy patch script
COPY fix_langchain_mongodb.py /tmp/fix_langchain_mongodb.py

# Fix langchain-mongodb imports for LangChain 1.0+ compatibility
# This patches the bug where langchain-mongodb tries to import from langchain.retrievers
# which doesn't exist in LangChain 1.0+. The imports have moved to langchain_classic.
RUN python /tmp/fix_langchain_mongodb.py && rm /tmp/fix_langchain_mongodb.py

# Copy application code
COPY . .

# Expose API port
EXPOSE 8511

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8511/health')"

# Run the FastAPI application
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8511", "--reload"]

