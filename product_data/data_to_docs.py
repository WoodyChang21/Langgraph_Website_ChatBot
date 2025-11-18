from dotenv import load_dotenv
import os
import re
from typing import List, Dict
from openai import OpenAI
from product_data.product_data import PRODUCT_DATA
from langchain_core.documents import Document
from rag.mongo_db_utils.add_data import add_documents
from rag.mongo_db_utils.vector_store_utils import get_vector_store
from rag.mongo_db_utils.vector_store_utils import get_mongo_client
load_dotenv()

# Configuration

MONGODB_URI = os.getenv("MONGODB_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")
COLLECTION_NAME = os.getenv("PRODUCT_COLLECTION_NAME")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize MongoDB client
client = get_mongo_client()
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Initialize OpenAI client
openai = OpenAI(api_key=OPENAI_API_KEY)



def parse_prices(price_str: str) -> List[int]:
    """Extract numeric prices from string like '$750 / $850 / $1600'"""
    if not price_str or "未列出" in price_str or "尚未上架" in price_str:
        return []
    
    # Remove dollar signs, commas, and split by /
    prices = []
    for p in price_str.split('/'):
        # Extract numbers only
        nums = re.findall(r'\d+', p.replace(',', ''))
        if nums:
            prices.append(int(nums[0]))
    return prices


def parse_sizes(size_str: str) -> List[str]:
    """Extract sizes from string like '3*4 / 4*5 / 5*7'"""
    if not size_str:
        return []
    return [s.strip() for s in size_str.split('/')]


def parse_weight_prices(weight_price_str: str) -> List[Dict]:
    """Parse weight-based pricing like '$2550 (1.5斤) / $4250 (2.5斤)'"""
    if not weight_price_str:
        return []
    
    variants = []
    items = weight_price_str.split('/')
    for item in items:
        # Extract price and weight
        price_match = re.search(r'\$?([\d,]+)', item)
        weight_match = re.search(r'\(([\d.]+斤)\)', item)
        
        if price_match and weight_match:
            variants.append({
                "size": "custom",
                "weight": weight_match.group(1),
                "price": int(price_match.group(1).replace(',', ''))
            })
    
    return variants


def create_variants(sizes: List[str], prices: List[int]) -> List[Dict]:
    """Create variant objects from sizes and prices"""
    if not sizes or not prices:
        return []
    
    variants = []
    for i, size in enumerate(sizes):
        # If fewer prices than sizes, use last price
        price = prices[i] if i < len(prices) else prices[-1]
        variants.append({
            "size": size,
            "price": price
        })
    
    return variants


def generate_embedding(text: str) -> List[float]:
    """Generate embedding using OpenAI API"""
    response = openai.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def transform_product(product_data: List) -> Dict:
    """Transform raw product data into MongoDB schema"""
    all_docs = []
    for raw_product in product_data:
        # Parse sizes and prices
        sizes = parse_sizes(raw_product.get("sizes_prices", ""))
        prices = parse_prices(raw_product.get("prices", ""))
        
        # Create variants
        if "weight_prices" in raw_product:
            # Special case: weight-based pricing (蠶絲被)
            variants = parse_weight_prices(raw_product["weight_prices"])
            pricing_type = "by_weight"
        else:
            variants = create_variants(sizes, prices)
            pricing_type = None
        
        # Calculate price range
        if variants:
            variant_prices = [v["price"] for v in variants]
            price_range = {
                "min": min(variant_prices),
                "max": max(variant_prices)
            }
        else:
            price_range = {
                "min": None,
                "max": None
            }
        
        # Build document with enriched page_content for better search
        # Include category and product_name in embedding text to improve search accuracy
        # This helps with queries like "蠶絲被" (product name) or "透氣的棉被" (category-based)
        enriched_content = f"類別: {raw_product['category']} | 產品名稱: {raw_product['product_name']} | {raw_product['description']}"
        
        doc = Document(
            page_content=enriched_content,
            metadata={
                "product_name": raw_product["product_name"],
                "category": raw_product["category"],
                "variants": variants,
                "price_range": price_range
            }
        )

        if pricing_type:
            doc.metadata["pricing_type"] = pricing_type

        if not variants or ("未列出" in raw_product.get("prices", "") or "尚未上架" in raw_product.get("prices", "")):
            doc.metadata["availability_status"] = "coming_soon"
        
        all_docs.append(doc)

    return all_docs

if __name__ == "__main__":
    for product in PRODUCT_DATA:
        docs = transform_product(product)
        print(docs)
        break