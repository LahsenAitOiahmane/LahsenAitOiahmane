from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel
from typing import List

# SQLAlchemy Base
Base = declarative_base()

# SQLAlchemy Models (Database Models)

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    price = Column(Integer, nullable=False)
    is_featured = Column(Boolean, default=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "price": self.price,
            "is_featured": self.is_featured,
        }

class Promotion(Base):
    __tablename__ = "promotions"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    valid_until = Column(DateTime, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "valid_until": self.valid_until.isoformat(),
        }

class FAQ(Base):
    __tablename__ = "faqs"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "answer": self.answer,
        }

class SSLCertificate(Base):
    __tablename__ = 'ssl_certificates'
    
    id = Column(Integer, primary_key=True, index=True)
    domain_name = Column(String, unique=True, index=True)
    cert_type = Column(String)  # Type of certificate: Basic, Wildcard, EV, etc.
    price = Column(Float)  # Price of the certificate
    expiration_date = Column(Date)  # Expiration date of the certificate
    
    def __repr__(self):
        return f"<SSLCertificate(id={self.id}, domain_name={self.domain_name}, cert_type={self.cert_type})>"

# Pydantic Models (Request/Response Models)

class ProductBase(BaseModel):
    name: str
    description: str
    price: int
    is_featured: bool = False

    class Config:
        orm_mode = True  # Tells Pydantic to treat SQLAlchemy models as dict-like objects

class ProductCreate(ProductBase):
    pass

class ProductResponse(ProductBase):
    id: int

class PromotionBase(BaseModel):
    title: str
    description: str
    valid_until: datetime

    class Config:
        orm_mode = True

class PromotionCreate(PromotionBase):
    pass

class PromotionResponse(PromotionBase):
    id: int

class FAQBase(BaseModel):
    question: str
    answer: str

    class Config:
        orm_mode = True

class FAQCreate(FAQBase):
    pass

class FAQResponse(FAQBase):
    id: int

class SSLCertificateBase(BaseModel):
    domain_name: str
    cert_type: str
    price: float
    expiration_date: datetime

    class Config:
        orm_mode = True

class SSLCertificateCreate(SSLCertificateBase):
    pass

class SSLCertificateResponse(SSLCertificateBase):
    id: int

    class Config:
        orm_mode = True

# Example of Usage:
# For FastAPI routes, you will use these Pydantic models to handle validation and serialization.
# For example:
# - SSLCertificateCreate will be used for creating new SSL certificates (in POST requests).
# - SSLCertificateResponse will be used for serializing the response data (in GET requests).
