import time
import random
from collections import deque
from fixedArray import FixedFailedArray

class TransactionEngine:
    """
    Core:
      - Pending transfers list uses FIFO queue
      - Rollback uses LIFO stack
      - Failed transfers stored in a fixed-size array
    """
    def __init__(self, failed_capacity: int = 10):
        self.pending = deque()
        self.failed = FixedFailedArray(failed_capacity)

        self.balances = {
            "ACC-1001": 5000.0,
            "ACC-2002": 1500.0,
            "ACC-3003": 800.0,
            "ACC-4004": 12000.0,
        }

        self.server_slow = False
        self.failure_rate = 0.20
        self._tx_counter = 1

    
    def pending_snapshot(self):
        return list(self.pending)

    def failed_snapshot(self):
        return self.failed.recent_first()

    def balances_snapshot(self):
        return dict(self.balances)

    
    def set_server_slow(self, slow: bool):
        self.server_slow = slow

    def set_failure_rate(self, rate: float):
        self.failure_rate = max(0.0, min(0.9, float(rate)))

    def next_tx_id(self) -> str:
        tx_id = f"TX-{self._tx_counter:05d}"
        self._tx_counter += 1
        return tx_id

    def add_pending(self, tx):
        self.pending.append(tx)

    def clear_pending(self):
        self.pending.clear()

    def pending_count(self) -> int:
        return len(self.pending)

    def process_next(self) -> str:
        if not self.pending:
            return "There are no pending transfers."

        tx = self.pending.popleft()

        rollback_stack = []  

        time.sleep(0.8 if self.server_slow else 0.2)

        try:
            self._debit(tx, rollback_stack)
            self._validate(tx)
            self._credit(tx, rollback_stack)
            return f"Transfer completed: {tx.short()}"

        except Exception as e:
            self._rollback(rollback_stack)
            reason = str(e)
            self.failed.add(tx, reason)
            return f"Transfer failed: {tx.short()} | {reason}"

    def _maybe_fail(self, step: str):
        if random.random() < self.failure_rate:
            raise RuntimeError(f"Unexpected error during {step}")

    def _debit(self, tx, stack):
        if tx.origin not in self.balances:
            raise RuntimeError("Origin account not found")
        if self.balances[tx.origin] < tx.amount:
            raise RuntimeError("Insufficient funds")

        self.balances[tx.origin] -= tx.amount

        def undo():
            self.balances[tx.origin] += tx.amount
        stack.append(undo)

        self._maybe_fail("debit")

    def _validate(self, tx):
        if tx.destination not in self.balances:
            raise RuntimeError("Destination account not found")
        if tx.amount <= 0:
            raise RuntimeError("Invalid amount")

        self._maybe_fail("validation")

    def _credit(self, tx, stack):
        self.balances[tx.destination] += tx.amount

        def undo():
            self.balances[tx.destination] -= tx.amount
        stack.append(undo)

        self._maybe_fail("credit")

    def _rollback(self, stack):
        while stack:
            undo = stack.pop()
            try:
                undo()
            except Exception:
                pass
    def queue_snapshot(self):
        return self.pending_snapshot()