import time
import random
import asyncio
import logging
from functools import wraps

logger = logging.getLogger(__name__)


def autowait(_func=None, *, wait_time: int = 10):
    try:
        _wait_time = float(wait_time)
    except:
        _wait_time = 10
    clock = {"value": time.perf_counter() - (_wait_time + 1)}

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            t = time.perf_counter()
            if t - clock["value"] < _wait_time:
                interval = _wait_time - t + clock["value"]
                logger.info("Wait {}s before calling...".format(interval))
                await asyncio.sleep(interval)
            clock["value"] = time.perf_counter()
            return await func(*args, **kwargs)

        return wrapper

    if _func is None:
        return decorator
    return decorator(_func)


def autoretry(_func=None, *, max_retries: int = 3):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                _max_retries = int(max_retries)
            except:
                _max_retries = 3
            num_retries = 0
            while True:
                try:
                    return await func(*args, **kwargs)
                except:
                    logger.error("Unexpected error", exc_info=True)
                    if num_retries >= _max_retries:
                        raise
                    num_retries += 1
                    logger.info("Autoretry (#{} attempt)".format(num_retries))

        return wrapper

    if _func is None:
        return decorator
    return decorator(_func)


def autoretry_with_exponential_backoff(
    _func=None,
    initial_delay: float = 1,
    exponential_base: float = 2,
    jitter: bool = True,
    max_retries: int = 3,
    errors: tuple = (Exception,),
):
    """Autoretry a function exponential backoff. This function is borrowed from OpenAI docs."""

    try:
        _max_retries = int(max_retries)
    except:
        _max_retries = 3

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            num_retries = 0
            delay = initial_delay

            # Loop until a successful response or max_retries is hit or a specific exception is raised
            while True:
                try:
                    return await func(*args, **kwargs)
                except errors as exc:
                    logger.error(
                        "Caught exception of type {}".format(type(exc)), exc_info=True
                    )
                    if num_retries >= _max_retries:
                        logger.error("Max retries ({}) exceeded.".format(_max_retries))
                        raise
                    num_retries += 1

                    delay *= exponential_base * (1 + jitter * random.random())
                    logger.info("Delay {}s before retrying...".format(delay))
                    await asyncio.sleep(delay)
                    logger.info("Autoretry (#{} attempt)".format(num_retries))
                except Exception as exc:
                    raise

        return wrapper

    if _func is None:
        return decorator
    return decorator(_func)
