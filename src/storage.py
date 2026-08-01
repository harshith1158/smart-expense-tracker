"""
Storage layer for expenses.

Design choice: an in-memory list is the source of truth at runtime, and it is
mirrored to a JSON file on every write so data survives a server restart.
This keeps reads fast (no disk I/O) while still giving basic persistence,
which is enough for the "in-memory or local JSON file" requirement without
pulling in a real database.
"""
import json
from pathlib import Path
from threading import Lock

from src.models import Expense


class ExpenseStore:
    def __init__(self, file_path: str | Path = "expenses.json"):
        self.file_path = Path(file_path)
        self._lock = Lock()
        self._expenses: list[Expense] = []
        self._load()

    def _load(self) -> None:
        if self.file_path.exists():
            raw = json.loads(self.file_path.read_text() or "[]")
            valid_expenses: list[Expense] = []
            for item in raw:
                try:
                    valid_expenses.append(Expense(**item))
                except Exception:
                    continue
            self._expenses = valid_expenses

    def _persist(self) -> None:
        data = [json.loads(e.model_dump_json()) for e in self._expenses]
        self.file_path.write_text(json.dumps(data, indent=2, default=str))

    def add(self, expense: Expense) -> Expense:
        with self._lock:
            self._expenses.append(expense)
            self._persist()
        return expense

    def list_all(self, category: str | None = None) -> list[Expense]:
        if category is None:
            return list(self._expenses)
        return [e for e in self._expenses if e.category.lower() == category.lower()]

    def get(self, expense_id: str) -> Expense | None:
        return next((e for e in self._expenses if e.id == expense_id), None)

    def delete(self, expense_id: str) -> bool:
        with self._lock:
            before = len(self._expenses)
            self._expenses = [e for e in self._expenses if e.id != expense_id]
            deleted = len(self._expenses) != before
            if deleted:
                self._persist()
            return deleted

    def total(self, category: str | None = None) -> tuple[float, int]:
        items = self.list_all(category)
        return round(sum(e.amount for e in items), 2), len(items)
