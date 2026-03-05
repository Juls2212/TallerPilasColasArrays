from datetime import datetime

class FixedFailedArray:
    """Fixed-size circular array to keep the last N failed transfers."""
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.data = [None] * capacity
        self.index = 0
        self.count = 0

    def add(self, tx, reason: str):
        self.data[self.index] = (tx, reason, datetime.now())
        self.index = (self.index + 1) % self.capacity
        self.count = min(self.count + 1, self.capacity)

    def recent_first(self):
        out = []
        for i in range(self.count):
            pos = (self.index - 1 - i) % self.capacity
            out.append(self.data[pos])
        return out