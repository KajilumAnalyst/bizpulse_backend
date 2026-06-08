from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum

# ── Enums ──────────────────────────────────────────────────────────────────
class PlanEnum(str, enum.Enum):
    basic = "basic"
    pro = "pro"
    business = "business"

class StockStatus(str, enum.Enum):
    in_stock = "In Stock"
    low_stock = "Low Stock"
    out_of_stock = "Out of Stock"

class PaymentMethod(str, enum.Enum):
    cash = "Cash"
    transfer = "Transfer"
    pos = "POS"
    ussd = "USSD"
    mobile_money = "Mobile Money"

class SaleStatus(str, enum.Enum):
    paid = "Paid"
    pending = "Pending"
    cancelled = "Cancelled"

# ── User ───────────────────────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    email           = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=True)   # nullable for Google auth
    business_name   = Column(String(255), nullable=False)
    owner_name      = Column(String(255), nullable=True)
    business_type   = Column(String(100), nullable=True)
    country         = Column(String(10), default="NG")
    currency        = Column(String(10), default="₦")
    phone           = Column(String(30), nullable=True)
    plan            = Column(String(20), default="basic")
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    stores      = relationship("Store", back_populates="owner", cascade="all, delete-orphan")
    sales       = relationship("Sale", back_populates="owner", cascade="all, delete-orphan")
    products    = relationship("Product", back_populates="owner", cascade="all, delete-orphan")

# ── Store ──────────────────────────────────────────────────────────────────
class Store(Base):
    __tablename__ = "stores"

    id          = Column(Integer, primary_key=True, index=True)
    owner_id    = Column(Integer, ForeignKey("users.id"), nullable=False)
    name        = Column(String(255), nullable=False)
    type        = Column(String(100), nullable=True)
    city        = Column(String(100), nullable=True)
    address     = Column(Text, nullable=True)
    is_active   = Column(Boolean, default=True)
    created_at  = Column(DateTime, default=datetime.utcnow)

    owner       = relationship("User", back_populates="stores")
    sales       = relationship("Sale", back_populates="store", cascade="all, delete-orphan")
    products    = relationship("Product", back_populates="store", cascade="all, delete-orphan")

# ── Product ────────────────────────────────────────────────────────────────
class Product(Base):
    __tablename__ = "products"

    id              = Column(Integer, primary_key=True, index=True)
    owner_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    store_id        = Column(Integer, ForeignKey("stores.id"), nullable=True)
    name            = Column(String(255), nullable=False)
    sku             = Column(String(100), nullable=True)
    category        = Column(String(100), nullable=True)
    quantity        = Column(Integer, default=0)
    selling_price   = Column(Float, default=0.0)
    cost_price      = Column(Float, default=0.0)
    supplier        = Column(String(255), nullable=True)
    low_stock_threshold = Column(Integer, default=10)
    is_active       = Column(Boolean, default=True)
    created_at      = Column(DateTime, default=datetime.utcnow)
    updated_at      = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    owner       = relationship("User", back_populates="products")
    store       = relationship("Store", back_populates="products")
    sale_items  = relationship("SaleItem", back_populates="product")

    @property
    def stock_status(self) -> str:
        if self.quantity == 0:
            return "Out of Stock"
        if self.quantity <= self.low_stock_threshold:
            return "Low Stock"
        return "In Stock"

# ── Sale ───────────────────────────────────────────────────────────────────
class Sale(Base):
    __tablename__ = "sales"

    id              = Column(Integer, primary_key=True, index=True)
    owner_id        = Column(Integer, ForeignKey("users.id"), nullable=False)
    store_id        = Column(Integer, ForeignKey("stores.id"), nullable=True)
    invoice_number  = Column(String(50), unique=True, nullable=False)
    customer_name   = Column(String(255), nullable=True)
    customer_phone  = Column(String(30), nullable=True)
    payment_method  = Column(String(50), default="Cash")
    subtotal        = Column(Float, default=0.0)
    discount        = Column(Float, default=0.0)
    total           = Column(Float, default=0.0)
    status          = Column(String(20), default="Paid")
    notes           = Column(Text, nullable=True)
    created_at      = Column(DateTime, default=datetime.utcnow)

    owner   = relationship("User", back_populates="sales")
    store   = relationship("Store", back_populates="sales")
    items   = relationship("SaleItem", back_populates="sale", cascade="all, delete-orphan")

# ── SaleItem ───────────────────────────────────────────────────────────────
class SaleItem(Base):
    __tablename__ = "sale_items"

    id          = Column(Integer, primary_key=True, index=True)
    sale_id     = Column(Integer, ForeignKey("sales.id"), nullable=False)
    product_id  = Column(Integer, ForeignKey("products.id"), nullable=True)
    product_name = Column(String(255), nullable=False)   # snapshot at time of sale
    quantity    = Column(Integer, default=1)
    unit_price  = Column(Float, default=0.0)
    total       = Column(Float, default=0.0)

    sale    = relationship("Sale", back_populates="items")
    product = relationship("Product", back_populates="sale_items")
