from app.core.celery_app import celery_app

@celery_app.task(name="test_task")
def print_name(name):
    print(name)