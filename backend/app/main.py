from fastapi import FastAPI

from app.api.v1.router import api_router
from app.core.config import settings


def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )
    app.include_router(api_router, prefix=settings.API_V1_STR)
    return app


app = create_application()
"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.database import Base, engine
from app.api import (
    countries_router,
    divisions_router,
    cities_router,
    search_router,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan event handler for app startup and shutdown."""
    # Startup
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created/verified")
    
    yield
    
    # Shutdown
    await engine.dispose()
    print("✅ Database connection closed")


# Create FastAPI app
app = FastAPI(
    title=settings.api_title,
    version=settings.api_version,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(countries_router, prefix="/api/v1/geo")
app.include_router(divisions_router, prefix="/api/v1/geo")
app.include_router(cities_router, prefix="/api/v1/geo")
app.include_router(search_router, prefix="/api/v1/geo")


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.api_title,
        "version": settings.api_version,
    }


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": settings.api_title,
        "version": settings.api_version,
        "docs": "/api/docs",
    }


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
    )
