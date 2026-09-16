# Micro-ERP: Inventory & Sales

A small ERP system for managing products, staff, and sales orders, built to
demonstrate professional backend practices: a normalized relational schema,
an ORM layer, and atomic (ACID-safe) transaction handling for stock
deductions.

## Stack
- **Backend:** FastAPI + SQLAlchemy
- **Database:** PostgreSQL (Neon)
- **Validation:** Pydantic

## Schema
See `schema.png` / the ER diagram in this README. Four tables:
`users`, `products`, `orders`, `order_items`. `order_items` is the junction
table linking orders to products, storing a `unit_price` snapshot so
historical orders aren't affected by later price changes.

## Why this project is more than CRUD

The order-creation endpoint (`POST /orders/`, see `app/routers/orders.py`)
is the core engineering piece: creating an order and deducting stock happen
in a single database transaction. If any line item is out of stock, the
**entire** order is rolled back -- no partial stock deduction, no orphaned
order record. Row-level locking (`with_for_update()`) also prevents two
simultaneous orders from overselling the last unit of a product.

## Local setup

1. Create a free Postgres database at [neon.tech](https://neon.tech) and
   copy the connection string.
2. `cp .env.example .env` and paste your connection string into `.env`.
3. Create a virtual environment and install dependencies:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```
4. Run the API:
   ```bash
   uvicorn app.main:app --reload
   ```
5. Open `http://127.0.0.1:8000/docs` for the interactive Swagger UI --
   tables are created automatically on first run.

## API overview

| Method | Endpoint                  | Purpose                              |
|--------|----------------------------|---------------------------------------|
| POST   | `/users/`                 | Create a user                         |
| POST   | `/products/`               | Create a product                      |
| GET    | `/products/low-stock`      | Products at or below threshold        |
| POST   | `/orders/`                 | Place an order (atomic transaction)   |
| GET    | `/analytics/summary`       | Total sales, order count, low stock   |
| GET    | `/analytics/sales-by-day`  | Daily sales totals for charting       |

## Roadmap
- [ ] Frontend (Inventory grid, Checkout screen, Admin dashboard)
- [ ] Auth (JWT-based login, role-gated admin routes)
- [ ] Deploy backend + Postgres to the cloud, add screenshots below

## Screenshots
_(added after frontend is built)_
