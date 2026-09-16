from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.database import get_db
from app import models

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def sales_summary(db: Session = Depends(get_db)):
    total_sales = (
        db.query(func.coalesce(func.sum(models.Order.total_price), 0))
        .filter(models.Order.status == models.OrderStatus.completed)
        .scalar()
    )
    order_count = (
        db.query(func.count(models.Order.id))
        .filter(models.Order.status == models.OrderStatus.completed)
        .scalar()
    )
    low_stock_count = (
        db.query(func.count(models.Product.id))
        .filter(models.Product.stock_quantity <= 10)
        .scalar()
    )
    return {
        "total_sales": float(total_sales),
        "completed_orders": order_count,
        "low_stock_products": low_stock_count,
    }


@router.get("/sales-by-day")
def sales_by_day(db: Session = Depends(get_db)):
    rows = (
        db.query(
            func.date(models.Order.created_at).label("day"),
            func.sum(models.Order.total_price).label("total"),
        )
        .filter(models.Order.status == models.OrderStatus.completed)
        .group_by(func.date(models.Order.created_at))
        .order_by(func.date(models.Order.created_at))
        .all()
    )
    return [{"day": str(r.day), "total": float(r.total)} for r in rows]
