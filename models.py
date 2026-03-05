from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Transaction:
    tx_id: str
    origin: str
    destination: str
    amount: float
    created_at: datetime = field(default_factory=datetime.now)

    def short(self) -> str:
        return f"{self.tx_id} {self.origin}->{self.destination} ${self.amount:.2f}"