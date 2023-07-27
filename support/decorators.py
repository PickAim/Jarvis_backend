import queue
import time
from threading import Thread

from app.constants import IS_DEBUG
from sessions.exceptions import JarvisExceptions, JarvisExceptionsCode


class ExcThread(Thread):
    def __init__(self, bucket: queue.Queue, target=None):
        Thread.__init__(self)
        self.target = target
        self.bucket = bucket

    def run(self):
        try:
            return self.target()
        except Exception as e:
            self.bucket.put(e)


class ExceptionTrackedThreadExecutor:
    def __init__(self, target, timeout_time_in_seconds: float = 1000000):
        self.target = target
        self.timeout_time_in_seconds = timeout_time_in_seconds

    def run(self):
        bucket = queue.Queue()
        exc_thread = ExcThread(bucket, target=self.target)
        exc_thread.daemon = True
        try:
            exc_thread.start()
            exc_thread.join(self.timeout_time_in_seconds)
        except Exception as thread_starting_exception:
            raise thread_starting_exception
        if not bucket.empty():
            raise bucket.get()


def timeout(timeout_time_in_seconds: float = -1):
    def decorated(func):
        def wrapper(*args, **kwargs):
            if timeout_time_in_seconds != -1 and not IS_DEBUG:
                result = [Exception('timeout marker')]

                def inner_callable():
                    result[0] = func(*args, **kwargs)

                start_time = time.time()
                thread_executor = ExceptionTrackedThreadExecutor(inner_callable, timeout_time_in_seconds)
                thread_executor.run()
                to_return = result[0]
                process_time = time.time() - start_time
                if process_time > timeout_time_in_seconds and isinstance(to_return, Exception):
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
