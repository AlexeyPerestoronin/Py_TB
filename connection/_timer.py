import time
import datetime

# brief: implements timer-logic
class Wait:
    # brief: class-constructor
    # param: wait_time_sec - number of seconds for waiting in one wait-round
    def __init__(self, wait_time_sec):
        self._last_timestamp = time.time_ns()
        self._wait_time = wait_time_sec * 1e+9

    # brief: waits for the remaining number of seconds since the last wait-round
    def Waiting(self):
        current_timestamp = time.time_ns()
        slipped_time = current_timestamp - self._last_timestamp
        slipped_time = self._wait_time - slipped_time
        if slipped_time > 0:
            slipped_time = slipped_time / 1e+9
            time.sleep(slipped_time)
        self._last_timestamp = current_timestamp
