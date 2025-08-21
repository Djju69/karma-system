"""
Main application entry point for Railway deployment.
Runs both FastAPI and Telegram bot in the same process.
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

# Import bot and API components
from app.bot.main import main as bot_main
from app.api.main import app as api_app


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown."""
    # Start bot in background task
    bot_task = asyncio.create_task(bot_main())
    
    yield
    
    # Cleanup on shutdown
    bot_task.cancel()
    try:
        await bot_task
    except asyncio.CancelledError:
        pass


# Create main FastAPI app
app = FastAPI(
    title="Karma System",
    description="Telegram Bot + API for Karma System",
    version="1.0.0",
    lifespan=lifespan
)

# Mount API routes
app.mount("/api", api_app)

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for Railway."""
    return {"status": "healthy", "service": "karma-system"}


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
