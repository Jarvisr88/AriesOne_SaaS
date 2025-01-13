"""
Main FastAPI application module for AriesOne SaaS.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config.database import init_db, get_engine

# Create FastAPI app
app = FastAPI(
    title="AriesOne SaaS API",
    description="Modern API for HME/DME management",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database
init_db(get_engine())

# Import and include routers
from .routers import customers, orders, inventory

app.include_router(customers.router, prefix="/api/v1/customers", tags=["customers"])
app.include_router(orders.router, prefix="/api/v1/orders", tags=["orders"])
app.include_router(inventory.router, prefix="/api/v1/inventory", tags=["inventory"])

@app.get("/")
async def root():
    """Root endpoint returning API information."""
    return {
        "name": "AriesOne SaaS API",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
