
from pydantic import BaseModel, Field
from typing import Optional
from data.product_data.product_data import PRODUCT_CATEGORIES, PRODUCT_NAME

class ProductSearchSchema(BaseModel):
    query: str = Field(description="Free-text product search (REQUIRED)")
    category: Optional[str] = Field(default=None, description="Filter by exact product category if and only if the user explicitly asks for it. Otherwise, always default to None.")
    product_name: Optional[str] = Field(default=None, description="Filter by exact product name if and only if the user explicitly asks for it. Otherwise, always default to None.")
    price_min: Optional[int] = Field(default=None, description="Minimum price filter if and only if the user explicitly asks for it. Otherwise, always default to None.")
    price_max: Optional[int] = Field(default=None, description="Maximum price filter if and only if the user explicitly asks for it. Otherwise, always default to None.")
    size: Optional[str] = Field(default=None, description="Product size in 台尺 (e.g., '6*7') if and only if the user explicitly asks for it. Otherwise, always default to None.")

class ProductFilterSchema(BaseModel):
    category: Optional[str] = Field(default=None, description="Filter by exact product category")
    product_name: Optional[str] = Field(default=None, description="Filter by exact product name")
    price_min: Optional[int] = Field(default=None, description="Minimum price filter")
    price_max: Optional[int] = Field(default=None, description="Maximum price filter")
    size: Optional[str] = Field(default=None, description="Size in 台尺 (e.g., '6*7')")