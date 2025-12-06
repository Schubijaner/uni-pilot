"""FastAPI application for Uni Pilot."""

import logging
import sys

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.core.config import get_settings
from api.core.exceptions import AuthenticationError, LLMError, NotFoundError, UniPilotException, ValidationError
from api.routers import auth, chat, example, health, modules, onboarding, roadmaps, users

# Configure logging before creating the app
settings = get_settings()
log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

logging.basicConfig(
    level=log_level,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)
logger.info(f"Logging configured with level: {settings.LOG_LEVEL}")

app = FastAPI(
    title="Uni Pilot API",
    description="API for Uni Pilot - A career roadmap application for university students",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
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


# Error handlers
@app.exception_handler(UniPilotException)
async def unipilot_exception_handler(request: Request, exc: UniPilotException):
    """Handle custom UniPilot exceptions."""
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    if isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
    elif isinstance(exc, ValidationError):
        status_code = status.HTTP_400_BAD_REQUEST
    elif isinstance(exc, AuthenticationError):
        status_code = status.HTTP_401_UNAUTHORIZED
    elif isinstance(exc, LLMError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(
        status_code=status_code,
        content={"detail": exc.message, "error_code": exc.error_code},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": exc.errors(), "error_code": "VALIDATION_ERROR"},
    )


# Include API routers
app.include_router(health.router, tags=["health"])
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(onboarding.router)
app.include_router(modules.router)
app.include_router(roadmaps.router)
app.include_router(chat.router)
app.include_router(example.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

