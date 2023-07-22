import time
from threading import Thread

from app.constants import IS_DEBUG
from sessions.exceptions import JarvisExceptions, JarvisExceptionsCode


def timeout(timeout_time_in_seconds: float = -1):
    def decorated(func):
        def wrapper(*args, **kwargs):
            if timeout_time_in_seconds != -1 and not IS_DEBUG:
                result = [Exception('timeout marker')]

                def inner_callable():
                    result[0] = func(*args, **kwargs)

                thread_to_check_time = Thread(target=inner_callable)
                thread_to_check_time.daemon = True
                start_time = time.time()
                try:
                    thread_to_check_time.start()
                    thread_to_check_time.join(timeout_time_in_seconds)
                except Exception as thread_starting_exception:
                    raise thread_starting_exception
                to_return = result[0]
                process_time = time.time() - start_time
                if process_time > timeout_time_in_seconds and isinstance(to_return, BaseException):
                    raise JarvisExceptions.create_exception_with_code(
                        JarvisExceptionsCode.TIMEOUT,
                        f"Request processing time exceed limit({timeout_time_in_seconds})."
                        f"Processing time: {process_time}. Method {func.__name__}"
                    )
                return to_return
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorated
