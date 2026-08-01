"""
Data models for the Expense Tracker API.

Expense.id is server-generated (UUID4 string) — the client never supplies it.
This avoids ID collisions and keeps the create endpoint idempotent-safe.
"""
import random
import re
from datetime import date

from pydantic import BaseModel, Field, field_validator


class ExpenseCreate(BaseModel):
    """Payload for creating a new expense. No 'id' field — server assigns it."""

    title: str = Field(..., min_length=1, max_length=200,)
    amount: float = Field(..., gt=0, description="Must be a positive number")
    category: str = Field(..., min_length=1, max_length=50)
    date: date

    @field_validator("title", "category")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("must not be blank")
        return v.strip()

    @field_validator("title")
    @classmethod
    def valid_title_format(cls, v: str) -> str:
        if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*", v):
            raise ValueError("must contain only letters, numbers, underscores, or hyphens")
        return v


class Expense(ExpenseCreate):
    """Full expense record as stored and returned by the API."""

    id: str = Field(default_factory=lambda: f"exp_{random.randint(1000, 9999)}")


class TotalResponse(BaseModel):
    total: float = Field(
        ...,
        description="Sum of all matching expenses included in this total."
    )
    category: str | None = Field(
        default=None,
        description="Optional category filter used for this total. When omitted, this represents the overall total."
    )
    count: int = Field(
        ...,
        description="Number of matching expenses included in this total."
    )
