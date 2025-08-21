"""
FastAPI application for Karma System API.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import qr, partners, listings

# Create FastAPI app
app = FastAPI(
    title="Karma System API",
    description="REST API for Karma System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(qr.router, prefix="/qr", tags=["QR Codes"])
app.include_router(partners.router, prefix="/partners", tags=["Partners"])
app.include_router(listings.router, prefix="/listings", tags=["Listings"])

@app.get("/")
async def root():
    """API root endpoint."""
    return {"message": "Karma System API", "version": "1.0.0"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}
