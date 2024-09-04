import logging.config
import logging.handlers
from functools import wraps

from app.core.logs.config import LOGGING_CONFIG_RESULT

logging.config.dictConfig(LOGGING_CONFIG_RESULT)

debug_logger = logging.getLogger('default_debug_logger')
info_logger = logging.getLogger('default_info_logger')
error_logger = logging.getLogger('default_error_logger')


def error_log(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            error_logger.error(
                f"Can't do this operation in DB in method {func.__name__}. Error: {e}"
            )
            raise e

    return wrapper


def no_log():
    def decorator(func):
        setattr(func, '_no_log', True)
        return func

    return decorator
