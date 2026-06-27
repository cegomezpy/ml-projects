"""
Main FastAPI application entry point.

This file initializes the FastAPI app and includes all routers.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from presentation.api.routes import models

# ============================================================================
# Create FastAPI Application
# ============================================================================

app = FastAPI(
    title="ML Projects API",
    description="""
    Machine Learning Projects API with DDD Architecture

    This API allows you to:
    * Train various ML models (linear regression, logistic regression, decision trees, etc.)
    * Make predictions using trained models
    * Manage and view model information

    Built with:
    - **FastAPI** for the API framework
    - **scikit-learn** for machine learning
    - **DDD Architecture** for clean code organization
    - **SOLID Principles** for maintainability
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================================
# CORS Middleware
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Include Routers
# ============================================================================

app.include_router(models.router)

# ============================================================================
# Root Endpoint
# ============================================================================


@app.get("/", tags=["root"])
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "message": "Welcome to ML Projects API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
        "endpoints": {
            "train": "POST /api/models/train",
            "predict": "POST /api/models/predict",
            "get_model": "GET /api/models/{model_id}",
            "list_models": "GET /api/models",
            "delete_model": "DELETE /api/models/{model_id}",
        },
    }


# ============================================================================
# Health Check
# ============================================================================


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ml-projects-api"}


# ============================================================================
# Global Exception Handler
# ============================================================================


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Global exception handler for uncaught exceptions.
    In production, you'd want to log these properly.
    """
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
        },
    )


# ============================================================================
# Startup and Shutdown Events
# ============================================================================


@app.on_event("startup")
async def startup_event():
    """
    Run on application startup.
    Initialize any required resources here.
    """
    print("🚀 ML Projects API starting up...")
    print("📚 Documentation available at: http://localhost:8000/docs")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Run on application shutdown.
    Clean up resources here.
    """
    print("👋 ML Projects API shutting down...")


# ============================================================================
# Run Application
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Auto-reload on code changes (development only)
    )
