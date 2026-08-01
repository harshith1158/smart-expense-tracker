# AI Notes

## How I used AI in this project

I used GitHub Copilot and FastAPI/Pydantic documentation during the build. The AI was helpful for getting the first version of the API structure in place, however I made the important decisions around architecture, validation, and documentation myself.

## 1. What was AI-generated and what I changed

### AI-generated starting point

The first draft of the project included the basic structure for:
- src/models.py — request and response models
- src/storage.py — the data handling layer
- src/main.py — route definitions and FastAPI wiring
- tests/test_api.py — the initial test layout and common test cases

### What I changed myself

I then refined the implementation in a few important ways:
- I split the app into separate modules so the models, storage logic, and routes were easier to reason about and test.
- I added a welcome endpoint at / so the API has a friendly entry point with links to Swagger and the expenses route.
- I improved the Swagger/OpenAPI descriptions so the total response is clearer and the expenses endpoint is easier to understand in the docs.
- I kept the list endpoint simple and functional so it still matches the original assignment behavior while remaining easy to use.
- I removed the local expenses.json artifact from the repository root so the project did not ship with sample expense data,ensuring confidentiality.

## 2. What I validated and tested

I validated the project in a few practical ways:
- I ran the full test suite with pytest -q, and the result was 17 passed tests under 3 seconds.
- I started the server locally and checked the live endpoints at /, /expenses, /docs, and /openapi.json.
- I tested the API behavior directly for validation errors, and I confirmed that negative amounts return 422, blank titles or categories are rejected, and deleting a missing expense returns 404.
- I also checked that the app responded correctly after the server was restarted, which confirmed that the storage flow was working as intended.

## 3. AI suggestions I chose not to use

There were a few ideas that were reasonable, however I did not use them for this submission:
- I did not add a database layer because the assignment allows local JSON storage, and the simpler approach kept the setup lightweight and easy for the evaluator to run.
- I did not add a monthly summary endpoint because the Swagger/OpenAPI docs bonus added more immediate value without changing the core API contract.

## To Conclude :

The project is small, but it is structured in a way that is easy to understand. The API behavior is tested, the documentation is in place, and the implementation is aligned with the assignment requirements.
