from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, func,Text
from sqlalchemy.orm import declarative_base
from .database import Base
from datetime import datetime


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    s3_key = Column(String(512), nullable=False, unique=True)
    file_size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    item_id = Column(Integer, ForeignKey("items.id"), nullable=True)
