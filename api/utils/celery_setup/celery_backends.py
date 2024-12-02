from celery.backends.database.session import ResultModelBase

from api.database.database import sync_engine
from api.utils.task_logger import create_logger

logger = create_logger("CELERY DATABASE")


def setup_celery_results_db():
    """Create engine and create tables for celery results backend."""
    # Create tables defined by Celery's backend models
    ResultModelBase.metadata.create_all(sync_engine)
    logger.info("Celery result backend tables created successfully.")


if __name__ == "__main__":
    setup_celery_results_db()
