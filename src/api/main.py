"""
FastAPI application for restaurant analytics dashboard.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import metrics, products, locations, orders, payments, time_analysis

app = FastAPI(
    title="Restaurant Analytics API",
    description="API for restaurant analytics dashboard with natural language queries",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(metrics.router, prefix="/api/metrics", tags=["Metrics"])
app.include_router(products.router, prefix="/api/products", tags=["Products"])
app.include_router(locations.router, prefix="/api/locations", tags=["Locations"])
app.include_router(orders.router, prefix="/api/orders", tags=["Orders"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(time_analysis.router, prefix="/api/time", tags=["Time Analysis"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Restaurant Analytics API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

