import logging

from fastapi import FastAPI, Response, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.database import engine
from app.routers.tasks import router as tasks_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Secure Task Manager API",
    description="A secure, containerized task API with an AWS DevSecOps delivery pipeline.",
    version="1.0.0",
    debug=False,
)


@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
    """Liveness probe: confirms that the API process is responding."""
    return {"status": "ok"}


@app.get("/ready", tags=["Health"])
def readiness_check(response: Response) -> dict[str, str]:
    """Readiness probe: confirms that the application can reach its database."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except SQLAlchemyError:
        logger.exception("Database readiness check failed")
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return {"status": "not_ready", "dependency": "database"}
    return {"status": "ready"}


app.include_router(tasks_router)
