from datetime import datetime
from pydantic import BaseModel, EmailStr
from typing import Optional, List

# ── Auth ───────────────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    business_name: str
    business_type: Optional[str] = None
    country: Optional[str] = "NG"
    phone: Optional[str] = None
    plan: Optional[str] = "basic"

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    business_name: str
    plan: str

# ── User ───────────────────────────────────────────────────────────────────
class UserOut(BaseModel):
    id: int
    email: str
    business_name: str
    owner_name: Optional[str]
    business_type: Optional[str]
    country: str
    currency: str
    phone: Optional[str]
    plan: str
    created_at: datetime
    model_config = {"from_attributes": True}

class UserUpdate(BaseModel):
    business_name: Optional[str] = None
    owner_name: Optional[str] = None
    phone: Optional[str] = None
    business_type: Optional[str] = None
    country: Optional[str] = None
    currency: Optional[str] = None

# ── Store ──────────────────────────────────────────────────────────────────
class StoreCreate(BaseModel):
    name: str
    type: Optional[str] = None
    city: Optional[str] = None
    address: Optional[str] = None

class StoreOut(BaseModel):
    id: int
    name: str
    type: Optional[str]
    city: Optional[str]
    address: Optional[str]
    is_active: bool
    created_at: datetime
    model_config = {"from_attributes": True}

# ── Product ────────────────────────────────────────────────────────────────
class ProductCreate(BaseModel):
    name: str
    sku: Optional[str] = None
    category: Optional[str] = None
    quantity: int = 0
    selling_price: float = 0.0
    cost_price: float = 0.0
    supplier: Optional[str] = None
    low_stock_threshold: int = 10
    store_id: Optional[int] = None

class ProductUpdate(BaseModel):
    name: Optional[str] = None
    quantity: Optional[int] = None
    selling_price: Optional[float] = None
    cost_price: Optional[float] = None
    supplier: Optional[str] = None
    low_stock_threshold: Optional[int] = None
    category: Optional[str] = None

class ProductOut(BaseModel):
    id: int
    name: str
    sku: Optional[str]
    category: Optional[str]
    quantity: int
    selling_price: float
    cost_price: float
    supplier: Optional[str]
    low_stock_threshold: int
    stock_status: str
    store_id: Optional[int]
    created_at: datetime
    model_config = {"from_attributes": True}

# ── Sale ───────────────────────────────────────────────────────────────────
class SaleItemCreate(BaseModel):
    product_id: Optional[int] = None
    product_name: str
    quantity: int = 1
    unit_price: float

class SaleCreate(BaseModel):
    customer_name: Optional[str] = None
    customer_phone: Optional[str] = None
    payment_method: str = "Cash"
    discount: float = 0.0
    notes: Optional[str] = None
    store_id: Optional[int] = None
    items: List[SaleItemCreate]

class SaleItemOut(BaseModel):
    id: int
    product_name: str
    quantity: int
    unit_price: float
    total: float
    model_config = {"from_attributes": True}

class SaleOut(BaseModel):
    id: int
    invoice_number: str
    customer_name: Optional[str]
    customer_phone: Optional[str]
    payment_method: str
    subtotal: float
    discount: float
    total: float
    status: str
    created_at: datetime
    items: List[SaleItemOut] = []
    model_config = {"from_attributes": True}

# ── AI ─────────────────────────────────────────────────────────────────────
class AIQuery(BaseModel):
    message: str
    store_id: Optional[int] = None

class AIResponse(BaseModel):
    reply: str
    provider: str

# ── Dashboard ──────────────────────────────────────────────────────────────
class DashboardStats(BaseModel):
    today_revenue: float
    today_transactions: int
    weekly_revenue: float
    monthly_revenue: float
    total_products: int
    low_stock_count: int
    out_of_stock_count: int
