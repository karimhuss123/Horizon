# Horizon

## Run from top level (Horizon folder, above "app")

### Run app
uvicorn app.main:app --reload

### Run Celery
celery -A app.core.celery_app.celery_app worker --loglevel=info