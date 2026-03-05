import threading
import queue
from engine import TransactionEngine

class AppController:

    def __init__(self):
        self.engine = TransactionEngine(failed_capacity=12)
        self._events = queue.Queue() 

    def emit(self, kind: str, message: str):
        self._events.put((kind, message))

    def drain_events(self):
        out = []
        while True:
            try:
                out.append(self._events.get_nowait())
            except queue.Empty:
                break
        return out

    def add_transfer(self, tx):
        self.engine.add_pending(tx)
        self.emit("info", f"Added to pending list: {tx.short()}")

    def clear_pending(self):
        self.engine.clear_pending()
        self.emit("info", "Pending list cleared.")

    def set_server_slow(self, slow: bool):
        self.engine.set_server_slow(slow)
        self.emit("info", f"Server speed simulation: {'SLOW' if slow else 'NORMAL'}")

    def set_failure_rate(self, rate: float):
        self.engine.set_failure_rate(rate)
        self.emit("info", f"Failure simulation set to {int(self.engine.failure_rate*100)}%")


    def process_next_async(self, on_done):
        def worker():
            msg = self.engine.process_next()
            self.emit("result", msg)
            on_done()
        threading.Thread(target=worker, daemon=True).start()

    def process_all_async(self, on_done):
        def worker():
            n = 0
            while self.engine.pending_count() > 0:
                msg = self.engine.process_next()
                self.emit("result", msg)
                n += 1
            self.emit("info", f"Processed {n} pending transfer(s).")
            on_done()
        threading.Thread(target=worker, daemon=True).start()