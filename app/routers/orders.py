from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.database import get_db
from app import models, schemas

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=schemas.OrderOut, status_code=201)
def create_order(order_in: schemas.OrderCreate, db: Session = Depends(get_db)):
    """
    Creates an order and decrements stock for every line item as a single
    atomic transaction.

    Why this matters: if item 3 of 5 is out of stock, items 1 and 2 must
    NOT remain deducted. SQLAlchemy's Session gives us exactly one
    transaction per request by default -- nothing is written to the
    database until db.commit() succeeds. If anything raises before that,
    db.rollback() discards every change made so far in this function,
    including the earlier stock deductions. This is the "all or nothing"
    guarantee (atomicity + consistency from ACID).
    """
    if not order_in.items:
        raise HTTPException(status_code=400, detail="Order must contain at least one item")

    try:
        # 1. Lock and validate every product line BEFORE writing anything.
        #    with_for_update() takes a row-level lock so two simultaneous
        #    orders for the last unit of the same product can't both pass
        #    the stock check (prevents a race condition / overselling).
        line_items = []
        total_price = 0

        for item in order_in.items:
            product = (
                db.query(models.Product)
                .filter(models.Product.id == item.product_id)
                .with_for_update()
                .first()
            )
            if product is None:
                raise HTTPException(
                    status_code=404,
                    detail=f"Product {item.product_id} not found",
                )
            if product.stock_quantity < item.quantity:
                raise HTTPException(
                    status_code=409,
                    detail=(
                        f"Insufficient stock for '{product.name}': "
                        f"requested {item.quantity}, available {product.stock_quantity}"
                    ),
                )
            line_items.append((product, item.quantity))
            total_price += product.price * item.quantity

        # 2. Create the order record.
        order = models.Order(
            user_id=order_in.user_id,
            total_price=total_price,
            status=models.OrderStatus.completed,
        )
        db.add(order)
        db.flush()  # assigns order.id without committing yet

        # 3. Create order_items and deduct stock -- still uncommitted.
        for product, quantity in line_items:
            db.add(
                models.OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=quantity,
                    unit_price=product.price,
                )
            )
            product.stock_quantity -= quantity  # DB CHECK constraint also guards this

        # 4. Only now do we make it durable. Everything above happens or
        #    none of it does.
        db.commit()

    except HTTPException:
        db.rollback()
        raise
    except SQLAlchemyError:
        db.rollback()
        raise HTTPException(status_code=500, detail="Transaction failed, no changes were saved")

    db.refresh(order)
    return order


@router.get("/{order_id}", response_model=schemas.OrderOut)
def get_order(order_id: int, db: Session = Depends(get_db)):
    order = (
        db.query(models.Order)
        .options(joinedload(models.Order.items))
        .filter(models.Order.id == order_id)
        .first()
    )
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order


@router.get("/", response_model=list[schemas.OrderOut])
def list_orders(db: Session = Depends(get_db)):
    return db.query(models.Order).options(joinedload(models.Order.items)).all()
