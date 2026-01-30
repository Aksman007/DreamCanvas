"""
Celery Application Configuration

This module configures Celery for background task processing.
"""

import logging
from celery import Celery

from app.config import settings

logger = logging.getLogger(__name__)

# Create Celery app
celery_app = Celery(
    "dreamcanvas",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.tasks.generation_tasks"],
)

# Celery configuration
celery_app.conf.update(
    # Task settings
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    # Task execution settings
    task_time_limit=settings.celery_task_time_limit,
    task_soft_time_limit=settings.celery_task_soft_time_limit,
    task_acks_late=True,  # Acknowledge after task completes
    task_reject_on_worker_lost=True,
    # Worker settings
    worker_prefetch_multiplier=1,  # One task at a time per worker
    worker_concurrency=4,  # Number of concurrent workers
    # Result settings
    result_expires=3600,  # Results expire after 1 hour
    # Retry settings
    task_default_retry_delay=60,  # 1 minute
    task_max_retries=3,
    # Task routing
    task_routes={
        "app.tasks.generation_tasks.process_generation_task": {"queue": "generations"},
        "app.tasks.generation_tasks.cleanup_failed_generations": {"queue": "maintenance"},
    },
    # Beat schedule (periodic tasks)
    beat_schedule={
        "cleanup-failed-generations": {
            "task": "app.tasks.generation_tasks.cleanup_failed_generations",
            "schedule": 3600.0,  # Every hour
        },
    },
)

# For testing/development - run tasks synchronously
if settings.celery_task_always_eager:
    celery_app.conf.task_always_eager = True
    celery_app.conf.task_eager_propagates = True
    logger.warning("Celery running in EAGER mode (synchronous)")
