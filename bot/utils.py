import os
import threading
from typing import Callable, Optional, Any


class ThreadTimer:
    thread = None

    def start(self, fun: Callable, time: int, *args: Any) -> Optional[str]:
        if self.thread and self.thread.is_alive():
            return self.thread.name
        ThreadTimer.thread = threading.Timer(time*60, fun, [*args])
        ThreadTimer.thread.name = fun.__name__ + "_t"
        ThreadTimer.thread.start()

    def stop(self) -> Optional[str]:
        if self.thread and self.thread.is_alive():
            self.thread.cancel()
            return self.thread.name


def current_path() -> str:
    return os.path.abspath(os.path.dirname(__file__))

