from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import Optional, List
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, Product
from app.schemas.schemas import ProductCreate, ProductUpdate, ProductOut

router = APIRouter(prefix="/inventory", tags=["Inventory"])

@router.post("/", response_model=ProductOut, status_code=201)
def add_product(body: ProductCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = Product(owner_id=user.id, **body.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)
    return product

@router.get("/", response_model=List[ProductOut])
def list_products(
    category: Optional[str] = None,
    search: Optional[str] = Query(None),
    store_id: Optional[int] = None,
    low_stock_only: bool = False,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Product).filter(Product.owner_id == user.id, Product.is_active == True)
    if category:
        q = q.filter(Product.category == category)
    if store_id:
        q = q.filter(Product.store_id == store_id)
    if search:
        q = q.filter(Product.name.ilike(f"%{search}%") | Product.sku.ilike(f"%{search}%"))
    products = q.offset(skip).limit(limit).all()
    if low_stock_only:
        products = [p for p in products if p.quantity <= p.low_stock_threshold]
    return products

@router.get("/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id, Product.owner_id == user.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/{product_id}", response_model=ProductOut)
def update_product(product_id: int, body: ProductUpdate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id, Product.owner_id == user.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    for field, value in body.model_dump(exclude_none=True).items():
        setattr(product, field, value)
    db.commit()
    db.refresh(product)
    return product

@router.delete("/{product_id}", status_code=204)
def delete_product(product_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    product = db.query(Product).filter(Product.id == product_id, Product.owner_id == user.id).first()
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    product.is_active = False   # soft delete
    db.commit()
