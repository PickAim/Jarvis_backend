from typing import Callable

from apscheduler.triggers.interval import IntervalTrigger


class SimpleTask:
    def __init__(self, function: Callable[[None], None], trigger_interval: IntervalTrigger, identifier: str = "",
                 args=None):
        self.function = function
        self.trigger_interval = trigger_interval
        if identifier == "":
            identifier = str(function)
        self.identifier = identifier
        self.args = args
