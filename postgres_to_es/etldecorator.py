import random
from functools import wraps
from time import sleep

from loguru import logger


def coroutine(coro):
    @wraps(coro)
    def coroinit(*args, **kwargs):
        fn = coro(*args, **kwargs)
        next(fn)
        return fn
    return coroinit

def _sleep_time(start_sleep_time: float, border_sleep_time: float, factor: int, attempt: int) -> float:
    try:
        sleep_time = random.uniform(start_sleep_time, start_sleep_time * factor) * factor ** attempt
    except OverflowError:
        logger.debug('Overflow in factor ** attemt, sleep_time = border_sleep_time')
        sleep_time = border_sleep_time
    return min(border_sleep_time, sleep_time)

def backoff(start_sleep_time=0.1, border_sleep_time=30, factor=2):
    if start_sleep_time < 0.001:
        logger.debug('start_sleep_time fewer than 0.001 set to 0.001')
        start_sleep_time = 0.001
    def decorator(target):
        @wraps(target)
        def retry(*args, **kwargs):
            attempt = 0
            while True:
                sleep_time = _sleep_time(start_sleep_time, border_sleep_time, factor, attempt)
                try:
                    attempt += 1
                    service_name = target.__name__
                    logger.debug(service_name)
                    logger.debug(f'This is call number {attempt}')
                    logger.debug(f'I am in backoff decorator and I will sleep {sleep_time} second')
                    #logger.debug(*args)
                    sleep(sleep_time)
                    ret = target(*args, **kwargs)
                except Exception as e:
                    logger.debug(f'OH NO EXEPTION!!!! I WILL WAIT  {sleep_time} seconds and try again')
                    logger.debug(e)
                    #sleep(sleep_time * 2)
                    #return target(*args, **kwargs)
                else:
                    return ret
        return retry
    return decorator
    
z ='''
def on_exception(wait_gen,
                 exception,
                 max_tries=None,
                 max_time=None,
                 jitter=full_jitter,
                 giveup=lambda e: False,
                 on_success=None,
                 on_backoff=None,
                 on_giveup=None,
                 logger='backoff',
                 backoff_log_level=logging.INFO,
                 giveup_log_level=logging.ERROR,
                 **wait_gen_kwargs):
 
    def decorate(target):
        # change names because python 2.x doesn't have nonlocal
        logger_ = _prepare_logger(logger)

        on_success_ = _config_handlers(on_success)
        on_backoff_ = _config_handlers(
            on_backoff, _log_backoff, logger_, backoff_log_level
        )
        on_giveup_ = _config_handlers(
            on_giveup, _log_giveup, logger_, giveup_log_level
        )

        retry = retry_exception

        return retry(target, wait_gen, exception,
                     max_tries, max_time, jitter, giveup,
                     on_success_, on_backoff_, on_giveup_,
                     wait_gen_kwargs)

    # Return a function which decorates a target with a retry loop.
    return decorate

def retry_exception(target, wait_gen, exception,
                    max_tries, max_time, jitter, giveup,
                    on_success, on_backoff, on_giveup,
                    wait_gen_kwargs):

    @functools.wraps(target)
    def retry(*args, **kwargs):

        # change names because python 2.x doesn't have nonlocal
        max_tries_ = _maybe_call(max_tries)
        max_time_ = _maybe_call(max_time)

        tries = 0
        start = datetime.datetime.now()
        wait = _init_wait_gen(wait_gen, wait_gen_kwargs)
        while True:
            tries += 1
            elapsed = timedelta.total_seconds(datetime.datetime.now() - start)
            details = (target, args, kwargs, tries, elapsed)

            try:
                ret = target(*args, **kwargs)
            except exception as e:
                max_tries_exceeded = (tries == max_tries_)
                max_time_exceeded = (max_time_ is not None and
                                     elapsed >= max_time_)

                if giveup(e) or max_tries_exceeded or max_time_exceeded:
                    _call_handlers(on_giveup, *details)
                    raise

                try:
                    seconds = _next_wait(wait, jitter, elapsed, max_time_)
                except StopIteration:
                    _call_handlers(on_giveup, *details)
                    raise e

                _call_handlers(on_backoff, *details, wait=seconds)

                time.sleep(seconds)
            else:
                _call_handlers(on_success, *details)

                return ret
    return retry
'''