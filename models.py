from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum, DECIMAL, Date, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, index=True)
    name       = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False)
    password   = Column(String(255), nullable=False)
    role       = Column(Enum("admin", "staff"), default="admin")
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

class Product(Base):
    __tablename__ = "products"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(150), nullable=False)
    category    = Column(String(50),  nullable=False)
    origin      = Column(String(150), nullable=False)
    description = Column(Text)
    price       = Column(String(100))
    markets     = Column(String(255))
    emoji       = Column(String(10),  default="🌿")
    status      = Column(Enum("active", "draft"), default="active")
    created_at  = Column(DateTime, server_default=func.now())
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())
    orders      = relationship("Order", back_populates="product")

class Order(Base):
    __tablename__ = "orders"
    id            = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(150), nullable=False)
    company       = Column(String(150))
    email         = Column(String(150), nullable=False)
    phone         = Column(String(30))
    country       = Column(String(100), nullable=False)
    product_id    = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    product_name  = Column(String(150), nullable=False)
    quantity_mt   = Column(DECIMAL(10, 2), nullable=False)
    delivery_date = Column(Date, nullable=True)
    special_notes = Column(Text)
    status        = Column(Enum("NEW","PROCESSING","CONFIRMED","SHIPPED","COMPLETED","CANCELLED"), default="NEW")
    created_at    = Column(DateTime, server_default=func.now())
    updated_at    = Column(DateTime, server_default=func.now(), onupdate=func.now())
    product       = relationship("Product", back_populates="orders")

class Inquiry(Base):
    __tablename__ = "inquiries"
    id                = Column(Integer, primary_key=True, index=True)
    name              = Column(String(150), nullable=False)
    company           = Column(String(150))
    email             = Column(String(150), nullable=False)
    country           = Column(String(100))
    products_interest = Column(String(255))
    message           = Column(Text)
    status            = Column(Enum("NEW","CONTACTED","QUOTATION_SENT","CLOSED"), default="NEW")
    created_at        = Column(DateTime, server_default=func.now())
    updated_at        = Column(DateTime, server_default=func.now(), onupdate=func.now())

class Setting(Base):
    __tablename__ = "settings"
    id          = Column(Integer, primary_key=True, index=True)
    setting_key = Column(String(100), unique=True, nullable=False)
    value       = Column(Text)
    updated_at  = Column(DateTime, server_default=func.now(), onupdate=func.now())
