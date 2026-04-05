"""SMDPIS - Social Media Data Parser & Intelligence System.

FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config.settings import settings
from api.routes import analytics, forensics, dashboard

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade Social Media Intelligence Platform with AI Analytics & Digital Forensics",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(analytics.router, prefix="/api")
app.include_router(forensics.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/")
async def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational",
        "docs": "/docs",
        "modules": {
            "ai_analytics": "/api/analytics",
            "digital_forensics": "/api/forensics",
            "dashboard": "/api/dashboard",
        },
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.HOST, port=settings.PORT, reload=True)
