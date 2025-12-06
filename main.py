"""FastAPI application for Uni Pilot."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import health, example

app = FastAPI(
    title="Uni Pilot API",
    description="API for Uni Pilot - A career roadmap application for university students",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Uni Pilot API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# Include API routers
app.include_router(health.router, tags=["health"])
app.include_router(example.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

