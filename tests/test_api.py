"""
Test suite for the Expense Tracker API.

Each test gets a fresh ExpenseStore pointed at a temp JSON file (via the
`client` fixture below), so tests never share state or touch a real
expenses.json on disk.
"""
import pytest
from fastapi.testclient import TestClient

from src import main
from src.storage import ExpenseStore


@pytest.fixture
def client(tmp_path):
    # Point the app's store at a throwaway file for this test only.
    main.store = ExpenseStore(tmp_path / "test_expenses.json")
    main.app.dependency_overrides.clear()
    return TestClient(main.app)


def make_expense(client, title="Coffee", amount=4.5, category="Food", date="2026-07-01"):
    return client.post(
        "/expenses",
        json={"title": title, "amount": amount, "category": category, "date": date},
    )


def test_add_expense_returns_201_and_generated_id(client):
    resp = make_expense(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["title"] == "Coffee"
    assert body["amount"] == 4.5
    assert "id" in body and len(body["id"]) > 0


def test_generated_id_is_short_and_readable(client):
    resp = make_expense(client)
    assert resp.status_code == 201
    body = resp.json()
    assert body["id"].startswith("exp_")
    assert len(body["id"]) <= 16


def test_add_expense_rejects_negative_amount(client):
    resp = make_expense(client, amount=-5)
    assert resp.status_code == 422


def test_add_expense_rejects_blank_title(client):
    resp = make_expense(client, title="   ")
    assert resp.status_code == 422


def test_add_expense_accepts_alphanumeric_with_underscore_and_hyphen(client):
    resp = make_expense(client, title="food_expense")
    assert resp.status_code == 201
    assert resp.json()["title"] == "food_expense"


def test_add_expense_rejects_symbol_only_title(client):
    resp = make_expense(client, title="@#$")
    assert resp.status_code == 422


def test_list_all_expenses(client):
    make_expense(client, title="Coffee", category="Food")
    make_expense(client, title="Bus_ticket", category="Transport")
    resp = client.get("/expenses")
    assert resp.status_code == 200
    assert len(resp.json()) == 2


def test_filter_expenses_by_category_case_insensitive(client):
    make_expense(client, title="Coffee", category="Food")
    make_expense(client, title="Bus ticket", category="Transport")
    resp = client.get("/expenses", params={"category": "food"})
    assert resp.status_code == 200
    results = resp.json()
    assert len(results) == 1
    assert results[0]["title"] == "Coffee"


def test_total_overall(client):
    make_expense(client, amount=10.0, category="Food")
    make_expense(client, amount=20.0, category="Transport")
    resp = client.get("/expenses/total")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 30.0
    assert body["count"] == 2
    assert body["category"] is None


def test_total_overall_endpoint(client):
    make_expense(client, amount=10.0, category="Food")
    make_expense(client, amount=20.0, category="Transport")
    resp = client.get("/expenses/total/overall")
    assert resp.status_code == 200
    body = resp.json()
    assert body["total"] == 30.0
    assert body["count"] == 2
    assert body["category"] is None


def test_total_response_schema_documents_count_and_total():
    schema = main.app.openapi()
    total_fields = schema["components"]["schemas"]["TotalResponse"]["properties"]
    assert "Sum of all matching expenses included in this total." in total_fields["total"]["description"]
    assert "Number of matching expenses included in this total." in total_fields["count"]["description"]


def test_swagger_docs_are_available(client):
    docs_response = client.get("/docs")
    assert docs_response.status_code == 200

    schema = main.app.openapi()
    assert any(tag["name"] == "expenses" for tag in schema.get("tags", []))
    assert schema["paths"]["/expenses"]["get"]["tags"] == ["expenses"]
    assert schema["paths"]["/"]["get"]["summary"] == "Welcome"


def test_total_by_category(client):
    make_expense(client, amount=10.0, category="Food")
    make_expense(client, amount=5.0, category="Food")
    make_expense(client, amount=20.0, category="Transport")
    resp = client.get("/expenses/total", params={"category": "Food"})
    body = resp.json()
    assert body["total"] == 15.0
    assert body["count"] == 2


def test_total_with_no_expenses_is_zero(client):
    resp = client.get("/expenses/total")
    body = resp.json()
    assert body["total"] == 0
    assert body["count"] == 0


def test_delete_expense_success(client):
    created = make_expense(client).json()
    resp = client.delete(f"/expenses/{created['id']}")
    assert resp.status_code == 200
    assert client.get("/expenses").json() == []


def test_delete_nonexistent_expense_returns_404(client):
    resp = client.delete("/expenses/does-not-exist")
    assert resp.status_code == 404


def test_data_persists_to_json_file(tmp_path):
    file_path = tmp_path / "persist_test.json"
    store = ExpenseStore(file_path)
    from src.models import Expense

    store.add(Expense(title="Rent", amount=500, category="Housing", date="2026-07-01"))

    # A brand-new store instance reading the same file should see the data.
    reloaded = ExpenseStore(file_path)
    assert len(reloaded.list_all()) == 1
    assert reloaded.list_all()[0].title == "Rent"
