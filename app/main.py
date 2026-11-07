import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers.tasks import router as tasks_router

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup complete; database schema is managed by Alembic")
    yield
    logger.info("Application shutting down")


app = FastAPI(
    title="Secure Task Manager API",
    description="A learning project for secure API development.",
    version="0.1.0",
    debug=False,
    lifespan=lifespan,
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    logger.info("Health check requested")
    return {"status": "ok"}


app.include_router(tasks_router)
