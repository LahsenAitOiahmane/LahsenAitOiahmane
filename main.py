from fastapi import FastAPI
from app.routes.homepage_routes import router as homepage_router
from app.routes.ssl_cert_routes import router as ssl_cert_router

app = FastAPI(
    title="SSL Selling Website Backend",
    description="Backend service for selling SSL certificates",
    version="1.0.0"
)

# Include the homepage routes
app.include_router(homepage_router)
app.include_router(ssl_cert_router)

@app.get("/", tags=["Health Check"])
async def health_check():
    """
    Health check endpoint to verify that the backend is operational.
    """
    return {"status": "healthy"}

