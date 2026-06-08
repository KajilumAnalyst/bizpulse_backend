"""
reports.py — Summary report generation
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date
from typing import Optional
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, Sale, SaleItem, Product

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/summary")
def get_report(
    from_date: date = Query(...),
    to_date: date = Query(...),
    store_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    start = datetime.combine(from_date, datetime.min.time())
    end = datetime.combine(to_date, datetime.max.time())

    q = db.query(Sale).filter(Sale.owner_id == user.id, Sale.created_at.between(start, end))
    if store_id:
        q = q.filter(Sale.store_id == store_id)

    sales = q.all()
    total_revenue = sum(s.total for s in sales)
    total_transactions = len(sales)
    avg_sale = total_revenue / total_transactions if total_transactions else 0

    # Top products from sale items
    item_totals: dict = {}
    for sale in sales:
        for item in sale.items:
            item_totals[item.product_name] = item_totals.get(item.product_name, 0) + item.total
    top_products = sorted(item_totals.items(), key=lambda x: x[1], reverse=True)[:5]

    # Payment method breakdown
    method_totals: dict = {}
    for sale in sales:
        method_totals[sale.payment_method] = method_totals.get(sale.payment_method, 0) + sale.total

    return {
        "from_date": str(from_date),
        "to_date": str(to_date),
        "total_revenue": total_revenue,
        "total_transactions": total_transactions,
        "average_sale_value": round(avg_sale, 2),
        "top_products": [{"name": n, "revenue": r} for n, r in top_products],
        "payment_methods": method_totals,
    }
