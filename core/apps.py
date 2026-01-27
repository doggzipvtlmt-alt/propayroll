import logging
from django.apps import AppConfig


logger = logging.getLogger(__name__)


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        from core.db import ensure_indexes, ping_mongo, ensure_maker_user

        logger.info('Initializing MongoDB connection...')
        ping_mongo()
        ensure_indexes()
        ensure_maker_user()
