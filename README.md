# Smart Expense Tracker API

A small REST API for managing personal expenses. It supports creating expenses, listing and filtering them, calculating totals, deleting records, and exposing Swagger documentation for easy testing.

## What this project does

- Add a new expense with title, amount, category, and date
- View and filter expenses by category
- Calculate totals for all expenses or for one category
- Delete an expense by its generated id
- Expose a simple welcome endpoint and interactive Swagger docs

## Project structure

- src/main.py — FastAPI routes, root welcome endpoint, and Swagger metadata
- src/models.py — Pydantic request and response models with validation rules
- src/storage.py — storage layer with in-memory state and local JSON persistence
- tests/test_api.py — automated API tests for the main behaviors

## Bonus implemented

- OpenAPI / Swagger docs are enabled and available at /docs

## Requirements

- Python 3.10+

## Install dependencies

```bash
pip install -r requirements.txt
```

## Start the server

```bash
uvicorn src.main:app --host 127.0.0.1 --port 8000
```

The API will be available at:
- http://127.0.0.1:8000/
- http://127.0.0.1:8000/expenses
- http://127.0.0.1:8000/docs

## Run the tests

```bash
pytest -q
```

## API reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /expenses | Create a new expense |
| GET | /expenses | Filter or list expenses |
| GET | /expenses/total | Get total for all expenses or one category |
| GET | /expenses/total/overall | Get the overall total across all expenses |
| DELETE | /expenses/{expense_id} | Delete an expense |

## Example requests

### Create an expense

```bash
curl -X POST http://127.0.0.1:8000/expenses \
  -H "Content-Type: application/json" \
  -d '{"title": "Groceries", "amount": 45.5, "category": "Food", "date": "2026-07-30"}'
```

### List expenses

```bash
curl "http://127.0.0.1:8000/expenses"
```

### Get category total

```bash
curl "http://127.0.0.1:8000/expenses/total?category=Food"
```

## Design notes

- Expense ids are server-generated and returned in a short readable format such as exp_1234.
- The app keeps expenses in memory while the server is running, and it writes changes to a local JSON file when needed so the data survives a restart.
- Validation rejects blank titles and categories and requires positive amounts.
- Category filtering is case-insensitive.
