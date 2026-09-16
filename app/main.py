from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import Base, engine
from app.routers import products, orders, users, analytics

# In production you'd use Alembic migrations instead of create_all().
# create_all() is fine for getting the schema up quickly during development.
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Micro-ERP API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this before deploying publicly
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(analytics.router)


@app.get("/")
def root():
    return {"status": "ok", "service": "micro-erp-api"}
