from pydantic import BaseModel, HttpUrl
from typing import Optional

class Item(BaseModel):
  name: str
  description: Optional[str] = None
  price: float
