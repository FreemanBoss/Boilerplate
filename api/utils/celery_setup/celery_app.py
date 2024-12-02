from celery import Celery

from api.utils.settings import Config


def make_celery(app=None, broker_url=None, result_backend=None):
    """
    Sets up Celery.
    """
    name = "api.utils.celery_setup.celery_app"
    if app:
        name = app.__name__

    # Set up Celery with custom broker and result backend
    celery = Celery(
        name,
        broker=broker_url or Config.CELERY_BROKER_URL,
        backend=result_backend or Config.CELERY_RESULT_BACKEND,
    )

    # add celery configurations
    celery.config_from_object("api.utils.celery_setup.celery_config")

    # Automatically discover tasks from the specified module
    celery.autodiscover_tasks(["api.utils.celery_setup.tasks"], related_name="tasks")

    return celery


# Create a Celery app instance for production
app = make_celery()

if __name__ == "__main__":

    app.start()
