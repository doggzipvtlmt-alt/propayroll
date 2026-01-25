import logging
import sys
from app.core.config import settings

def setup_logging() -> None:
    level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    root = logging.getLogger()
    root.setLevel(level)

    handler = logging.StreamHandler(sys.stdout)
    fmt = logging.Formatter(
        fmt="%(asctime)s %(levelname)s %(name)s request_id=%(request_id)s %(message)s"
    )
    handler.setFormatter(fmt)

    # remove default handlers to avoid duplicates
    root.handlers = []
    root.addHandler(handler)

class RequestIdFilter(logging.Filter):
    def __init__(self):
        super().__init__()
        self.request_id = "-"

    def filter(self, record):
        if not hasattr(record, "request_id"):
            record.request_id = self.request_id
        return True

request_id_filter = RequestIdFilter()

def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if not any(isinstance(f, RequestIdFilter) for f in logger.filters):
        logger.addFilter(request_id_filter)
    return logger
