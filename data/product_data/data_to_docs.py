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



def parse_prices(price_str: str) -> List[int]:
    """Extract numeric prices from string like '$750 / $850 / $1600'"""
    if not price_str or "未列出" in price_str or "尚未上架" in price_str:
        return []
    
    # Check if it's pure weight-based pricing
    if price_str.strip() == "依斤計價":
        return []
    
    # Remove dollar signs, commas, and split by /
    prices = []
    for p in price_str.split('/'):
        p = p.strip()
        # Skip if contains weight-based pricing indicators (but allow mixed format)
        if p == "依斤計價":
            continue
        # Extract price number (first number in the string, before any parentheses)
        # Handle cases like "$3980 (5*7)" - extract only 3980
        price_match = re.search(r'\$?([\d,]+)', p)
        if price_match:
            price = int(price_match.group(1).replace(',', ''))
            prices.append(price)
    return prices


def parse_mixed_pricing(price_str: str, sizes: List[str]) -> List[Dict]:
    """
    Parse mixed pricing format like "$3980 (5*7)/依斤計價"
    Returns list of variants with size-specific prices or weight-based pricing indicator.
    """
    if not price_str or "未列出" in price_str or "尚未上架" in price_str:
        return []
    
    variants = []
    has_weight_pricing = "依斤計價" in price_str
    
    # Split by / to get individual price items
    price_items = [p.strip() for p in price_str.split('/')]
    
    # Extract fixed prices with their sizes
    fixed_price_map = {}  # {size: price}
    for item in price_items:
        if item == "依斤計價":
            continue
        # Match pattern like "$3980 (5*7)" or "$3980"
        price_match = re.search(r'\$?([\d,]+)', item)
        size_match = re.search(r'\(([\d*]+)\)', item)  # Match (5*7)
        
        if price_match:
            price = int(price_match.group(1).replace(',', ''))
            if size_match:
                # Price is tied to a specific size
                size = size_match.group(1)
                fixed_price_map[size] = price
            else:
                # No size specified, will be matched by order
                fixed_price_map[None] = price
    
    # Create variants for each size
    for i, size in enumerate(sizes):
        if size in fixed_price_map:
            # This size has a fixed price
            variants.append({
                "size": size,
                "price": fixed_price_map[size]
            })
        elif has_weight_pricing:
            # This size uses weight-based pricing
            variants.append({
                "size": size,
                "price": None,  # Indicates weight-based pricing
                "pricing_type": "by_weight"
            })
        elif None in fixed_price_map:
            # Use the price without size specification (by order)
            variants.append({
                "size": size,
                "price": fixed_price_map[None]
            })
    
    return variants


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


def create_variants(sizes: List[str], prices: List[int], price_status: str = None) -> List[Dict]:
    """Create variant objects from sizes and prices.
    If prices are empty, creates variants with sizes and price_status message in price field.
    
    Args:
        sizes: List of size strings
        prices: List of price integers
        price_status: Status message if prices unavailable (e.g., "Price hasn't yet been listed")
    """
    if not sizes:
        return []
    
    variants = []
    for i, size in enumerate(sizes):
        if prices and len(prices) > 0:
            # If fewer prices than sizes, use last price
            price = prices[i] if i < len(prices) else prices[-1]
        else:
            # No prices available - use status message
            price = price_status
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
        prices_str = raw_product.get("prices", "")
        
        # Determine price status message if needed
        price_status = None
        if "未列出" in prices_str or "尚未列出" in prices_str or "價格未列出" in prices_str:
            price_status = "Price hasn't yet been listed"
        elif "尚未上架" in prices_str or "尚位上架" in prices_str:
            price_status = "Product isn't available yet"
        
        # Create variants
        if "weight_prices" in raw_product:
            # Special case: weight-based pricing (蠶絲被)
            variants = parse_weight_prices(raw_product["weight_prices"])
            pricing_type = "by_weight"
        elif "依斤計價" in prices_str and any("(" in p and ")" in p for p in prices_str.split("/")):
            # Mixed format: fixed price for some sizes + weight-based for others
            # Example: "$3980 (5*7)/依斤計價"
            variants = parse_mixed_pricing(prices_str, sizes)
            pricing_type = "mixed"  # Some sizes fixed, some by weight
        else:
            # Standard format: simple price list
            prices = parse_prices(prices_str)
            variants = create_variants(sizes, prices, price_status)
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
        
        all_docs.append(doc)

    return all_docs

if __name__ == "__main__":
    for product in PRODUCT_DATA:
        docs = transform_product(product)
        print(docs)
        break