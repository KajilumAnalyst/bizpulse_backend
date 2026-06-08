from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import Optional, List
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, Sale, SaleItem, Product
from app.schemas.schemas import SaleCreate, SaleOut, DashboardStats

router = APIRouter(prefix="/sales", tags=["Sales"])

def _next_invoice_number(db: Session, user_id: int) -> str:
    count = db.query(Sale).filter(Sale.owner_id == user_id).count()
    return f"INV-{str(count + 1).zfill(4)}"

@router.post("/", response_model=SaleOut, status_code=201)
def create_sale(body: SaleCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Calculate totals
    subtotal = sum(item.quantity * item.unit_price for item in body.items)
    total = subtotal - body.discount

    sale = Sale(
        owner_id=user.id,
        store_id=body.store_id,
        invoice_number=_next_invoice_number(db, user.id),
        customer_name=body.customer_name,
        customer_phone=body.customer_phone,
        payment_method=body.payment_method,
        subtotal=subtotal,
        discount=body.discount,
        total=total,
        notes=body.notes,
    )
    db.add(sale)
    db.flush()

    for item_data in body.items:
        item = SaleItem(
            sale_id=sale.id,
            product_id=item_data.product_id,
            product_name=item_data.product_name,
            quantity=item_data.quantity,
            unit_price=item_data.unit_price,
            total=item_data.quantity * item_data.unit_price,
        )
        db.add(item)

        # Deduct from inventory if product_id is provided
        if item_data.product_id:
            product = db.query(Product).filter(Product.id == item_data.product_id, Product.owner_id == user.id).first()
            if product:
                product.quantity = max(0, product.quantity - item_data.quantity)

    db.commit()
    db.refresh(sale)
    return sale

@router.get("/", response_model=List[SaleOut])
def list_sales(
    store_id: Optional[int] = None,
    payment_method: Optional[str] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    search: Optional[str] = Query(None),
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Sale).filter(Sale.owner_id == user.id)
    if store_id:
        q = q.filter(Sale.store_id == store_id)
    if payment_method:
        q = q.filter(Sale.payment_method == payment_method)
    if from_date:
        q = q.filter(Sale.created_at >= datetime.combine(from_date, datetime.min.time()))
    if to_date:
        q = q.filter(Sale.created_at <= datetime.combine(to_date, datetime.max.time()))
    if search:
        q = q.filter(Sale.customer_name.ilike(f"%{search}%") | Sale.invoice_number.ilike(f"%{search}%"))
    return q.order_by(Sale.created_at.desc()).offset(skip).limit(limit).all()

@router.get("/dashboard", response_model=DashboardStats)
def get_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    today = date.today()
    today_start = datetime.combine(today, datetime.min.time())
    today_end = datetime.combine(today, datetime.max.time())

    # Today
    today_sales = db.query(func.sum(Sale.total), func.count(Sale.id)).filter(
        Sale.owner_id == user.id, Sale.created_at.between(today_start, today_end)
    ).first()

    # This week (Mon–Sun)
    from datetime import timedelta
    week_start = datetime.combine(today - timedelta(days=today.weekday()), datetime.min.time())
    weekly = db.query(func.sum(Sale.total)).filter(
        Sale.owner_id == user.id, Sale.created_at >= week_start
    ).scalar() or 0

    # This month
    month_start = datetime.combine(today.replace(day=1), datetime.min.time())
    monthly = db.query(func.sum(Sale.total)).filter(
        Sale.owner_id == user.id, Sale.created_at >= month_start
    ).scalar() or 0

    # Inventory
    from app.models.models import Product
    products = db.query(Product).filter(Product.owner_id == user.id, Product.is_active == True).all()
    low_stock = sum(1 for p in products if p.quantity <= p.low_stock_threshold and p.quantity > 0)
    out_of_stock = sum(1 for p in products if p.quantity == 0)

    return DashboardStats(
        today_revenue=today_sales[0] or 0,
        today_transactions=today_sales[1] or 0,
        weekly_revenue=weekly,
        monthly_revenue=monthly,
        total_products=len(products),
        low_stock_count=low_stock,
        out_of_stock_count=out_of_stock,
    )

@router.get("/{sale_id}", response_model=SaleOut)
def get_sale(sale_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sale = db.query(Sale).filter(Sale.id == sale_id, Sale.owner_id == user.id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    return sale

@router.delete("/{sale_id}", status_code=204)
def delete_sale(sale_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    sale = db.query(Sale).filter(Sale.id == sale_id, Sale.owner_id == user.id).first()
    if not sale:
        raise HTTPException(status_code=404, detail="Sale not found")
    db.delete(sale)
    db.commit()
