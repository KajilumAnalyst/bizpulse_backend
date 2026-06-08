from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, date, timedelta
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.models import User, Sale, Product
from app.schemas.schemas import AIQuery, AIResponse
from app.services.ai_service import get_ai_response

router = APIRouter(prefix="/ai", tags=["AI Insights"])

@router.post("/chat", response_model=AIResponse)
async def ai_chat(body: AIQuery, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Build real business context to give AI accurate data
    today = date.today()
    month_start = datetime.combine(today.replace(day=1), datetime.min.time())
    today_start = datetime.combine(today, datetime.min.time())

    monthly_revenue = db.query(func.sum(Sale.total)).filter(
        Sale.owner_id == user.id, Sale.created_at >= month_start
    ).scalar() or 0

    today_revenue = db.query(func.sum(Sale.total)).filter(
        Sale.owner_id == user.id, Sale.created_at >= today_start
    ).scalar() or 0

    products = db.query(Product).filter(Product.owner_id == user.id, Product.is_active == True).all()
    low_stock = [p.name for p in products if p.quantity <= p.low_stock_threshold and p.quantity > 0]
    out_of_stock = [p.name for p in products if p.quantity == 0]

    context = {
        "business_name": user.business_name,
        "today_revenue": today_revenue,
        "monthly_revenue": monthly_revenue,
        "total_products": len(products),
        "low_stock": low_stock,
        "out_of_stock": out_of_stock,
    }

    reply, provider = await get_ai_response(body.message, context)
    return AIResponse(reply=reply, provider=provider)
