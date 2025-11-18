
from pydantic import BaseModel, Field
from typing import Literal, Optional, List, Dict, Any
from product_data.product_data import PRODUCT_CATEGORIES, PRODUCT_NAME

class ProductSearchSchema(BaseModel):
    query: str = Field(description="Free-text product search (REQUIRED)", required=True)
    category: Optional[Literal[*PRODUCT_CATEGORIES]] = Field(description="Filter by exact product category if and only if the user explicitly asks for it. Otherwise, always default to None.", required=False)
    product_name: Optional[Literal[*PRODUCT_NAME]] = Field(description="Filter by exact product name if and only if the user explicitly asks for it. Otherwise, always default to None.", required=False)
    price_min: Optional[int] = Field(description="Minimum price filter if and only if the user explicitly asks for it. Otherwise, always default to None.", required=False)
    price_max: Optional[int] = Field(description="Maximum price filter if and only if the user explicitly asks for it. Otherwise, always default to None.", required=False)
    size: Optional[str] = Field(description="Product size in 台尺 (e.g., '6*7') if and only if the user explicitly asks for it. Otherwise, always default to None.", required=False)

class ProductFilterSchema(BaseModel):
    category: Optional[Literal[*PRODUCT_CATEGORIES]] = Field(description="Filter by exact product category", required=False)
    product_name: Optional[Literal[*PRODUCT_NAME]] = Field(description="Filter by exact product name", required=False)
    price_min: Optional[int] = Field(description="Minimum price filter", required=False)
    price_max: Optional[int] = Field(description="Maximum price filter", required=False)
    size: Optional[str] = Field(description="Size in 台尺 (e.g., '6*7')", required=False)