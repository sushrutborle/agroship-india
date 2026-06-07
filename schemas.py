from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
from decimal import Decimal

# ── Auth ──────────────────────────────────────────────────────
class LoginRequest(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user_name: str
    role: str

# ── Product ───────────────────────────────────────────────────
class ProductBase(BaseModel):
    name: str
    category: str
    origin: str
    description: Optional[str] = None
    price: Optional[str] = None
    markets: Optional[str] = None
    emoji: Optional[str] = "🌿"
    status: Optional[str] = "active"

class ProductCreate(ProductBase):
    pass

class ProductUpdate(ProductBase):
    pass

class ProductOut(ProductBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    class Config:
        from_attributes = True

# ── Order ─────────────────────────────────────────────────────
class OrderCreate(BaseModel):
    customer_name: str
    company: Optional[str] = None
    email: str
    phone: Optional[str] = None
    country: str
    product_id: Optional[int] = None
    product_name: str
    quantity_mt: Decimal
    delivery_date: Optional[date] = None
    special_notes: Optional[str] = None

class OrderStatusUpdate(BaseModel):
    status: str

class OrderOut(OrderCreate):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

# ── Inquiry ───────────────────────────────────────────────────
class InquiryCreate(BaseModel):
    name: str
    company: Optional[str] = None
    email: str
    country: Optional[str] = None
    products_interest: Optional[str] = None
    message: Optional[str] = None

class InquiryStatusUpdate(BaseModel):
    status: str

class InquiryOut(InquiryCreate):
    id: int
    status: str
    created_at: datetime
    class Config:
        from_attributes = True

# ── Settings ──────────────────────────────────────────────────
class SettingUpdate(BaseModel):
    company_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    tagline: Optional[str] = None

class SettingsOut(BaseModel):
    company_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    tagline: Optional[str]

# ── Dashboard Stats ───────────────────────────────────────────
class DashboardStats(BaseModel):
    total_products: int
    active_products: int
    total_orders: int
    new_orders: int
    total_inquiries: int
    new_inquiries: int
