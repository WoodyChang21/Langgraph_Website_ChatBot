from dotenv import load_dotenv
import os
import re
from typing import List, Dict
from openai import OpenAI
from data.product_data.product_data import PRODUCT_DATA
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



def parse_weight_prices(weight_prices: List[str]) -> List[Dict]:
    """Parse weight-based pricing from list like ['$2550 (1.5斤)', '$4250 (2.5斤)']"""
    if not weight_prices:
        return []
    
    variants = []
    for item in weight_prices:
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


def create_variants(sizes: List[str], prices: List) -> List[Dict]:
    """Create variant objects from sizes and prices lists.
    
    Args:
        sizes: List of size strings (e.g., ["3*4", "4*5"])
        prices: List of prices - can contain integers, strings, or mixed types
                (e.g., [750, 850] or ["價格未列出"] or [3980, "依斤計價"])
    """
    if not sizes:
        return []
    
    variants = []
    for i, size in enumerate(sizes):
        if prices and i < len(prices):
            # Get price for this size
            price = prices[i]
            # Convert string status messages to English equivalents
            if isinstance(price, str):
                if "未列出" in price or "價格未列出" in price:
                    price = "Price hasn't yet been listed"
                elif "尚未上架" in price or "尚位上架" in price:
                    price = "Product isn't available yet"
                elif price == "依斤計價":
                    price = None  # Indicates weight-based pricing
        elif prices and len(prices) > 0:
            # If fewer prices than sizes, use last price
            price = prices[-1]
            if isinstance(price, str):
                if "未列出" in price or "價格未列出" in price:
                    price = "Price hasn't yet been listed"
                elif "尚未上架" in price or "尚位上架" in price:
                    price = "Product isn't available yet"
                elif price == "依斤計價":
                    price = None
        else:
            # No prices available
            price = "Price hasn't yet been listed"
        
        variant = {
            "size": size,
            "price": price
        }
        
        # Add pricing_type if it's weight-based
        if price is None:
            variant["pricing_type"] = "by_weight"
        
        variants.append(variant)
    
    return variants


def transform_product(product_data: List) -> List[Document]:
    """Transform raw product data into MongoDB schema"""
    all_docs = []
    for raw_product in product_data:
        # Get sizes and prices (already lists)
        sizes = raw_product.get("sizes", [])
        prices = raw_product.get("prices", [])
        
        # Create variants
        if "weight_prices" in raw_product:
            # Special case: weight-based pricing (蠶絲被)
            variants = parse_weight_prices(raw_product["weight_prices"])
            pricing_type = "by_weight"
        else:
            # Standard format: create variants from sizes and prices lists
            variants = create_variants(sizes, prices)
            # Determine pricing_type based on variants
            has_weight_based = any(v.get("pricing_type") == "by_weight" for v in variants)
            has_numeric = any(isinstance(v.get("price"), int) for v in variants)
            if has_weight_based and has_numeric:
                pricing_type = "mixed"  # Some sizes fixed, some by weight
            elif has_weight_based:
                pricing_type = "by_weight"
            else:
                pricing_type = None
        
        # Calculate price range (only from variants with numeric prices)
        if variants:
            variant_prices = [v["price"] for v in variants if isinstance(v.get("price"), int)]
            if variant_prices:
                price_range = {
                    "min": min(variant_prices),
                    "max": max(variant_prices)
                }
            else:
                # All variants use weight-based pricing or have status messages
                price_range = {
                    "min": None,
                    "max": None
                }
        else:
            price_range = {
                "min": None,
                "max": None
            }
        
        enriched_content = f"類別: {raw_product['category']} | 產品名稱: {raw_product['product_name']} | {raw_product['description']}"
        
        # Build metadata
        metadata = {
            "product_name": raw_product["product_name"],
            "category": raw_product["category"],
            "variants": variants,
            "price_range": price_range
        }
        
        # Add product_id if available
        if "product_id" in raw_product and raw_product["product_id"] is not None:
            metadata["product_id"] = raw_product["product_id"]
        
        # Add pricing_type if needed
        if pricing_type:
            metadata["pricing_type"] = pricing_type
        
        doc = Document(
            page_content=enriched_content,
            metadata=metadata
        )
        
        all_docs.append(doc)

    return all_docs

if __name__ == "__main__":
    docs = transform_product(PRODUCT_DATA)
    for doc in docs:
        if doc.metadata.get("product_id") == "9449314":
            print(doc)
    # for product in PRODUCT_DATA:
    #     if len(product.get("sizes")) != len(product.get("prices")):
    #         print("NOT EQUAL")
