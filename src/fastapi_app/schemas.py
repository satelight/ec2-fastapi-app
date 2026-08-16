from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    price: float

class ItemUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None

class Item(BaseModel):
    id: int
    title: str
    description: Optional[str]
    price: float
    created_at: datetime

    class Config:
        from_attributes = True


class FileCreate(BaseModel):
    filename: str
    file_size: int
    item_id: int | None = None


class File(BaseModel):
    id: int
    filename: str
    s3_key: str
    file_size: int
    uploaded_at: datetime
    item_id: int | None = None

    class Config:
        from_attributes = True
