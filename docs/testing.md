# Testing Strategy

The project will use the following testing levels:
- **Unit tests:** Verify individual functions and components in isolation. They will be the primary testing level, particularly for data processing, statistical calculations, race analysis and validation.
- **Integration tests:** Verify that multiple components work correctly together, including interactions with persistence layers and external service adapters.
- **End-to-end tests:** Deferred until complete user-facing workflows exist and justify the additional complexity.
- **AI evaluation:** Model quality will be evaluated separately from conventional automated tests, using a controlled dataset of historical races with known outcomes. Evaluation results must not leak into the information provided to the model.

## Framework and Dependencies
[pytest](https://docs.pytest.org/) is the project's testing framework.

It is included as a development dependency, managed through `uv`, rather than as a runtime dependency.

Install and synchronize project dependencies with:

`uv sync --locked`

Add future development or testing tools through `uv add --dev <package>`.

## Test Organization
Tests are located in the `tests/` directory.

The intended structure is:
- `tests/test_environment.py`: Project environment checks.
- `tests/unit/`: Isolated tests for individual functions and components.
- `tests/integration/`: Tests covering interactions between components.
- `tests/fixtures/`: Small, controlled datasets and reusable test inputs.

Test files follow the `test_*.py` naming convention, and individual test functions follow the `test_*` naming convention.

Directories will be introduced as the corresponding tests become necessary.

## Test Data and External Dependencies
Tests should use small, deterministic datasets representative of the GBGB data consumed by HoundIQ.

Expected results should be known in advance, allowing calculations and transformations to be verified reliably.

The default test suite must not depend on live GBGB requests, external APIs, database services or paid LLM calls.

External services should be isolated using controlled test doubles or simulated responses where appropriate. Tests requiring real external services must be explicitly separated from the normal test suite.

## AI Evaluation
AI analysis quality requires a separate evaluation process because model responses may vary and depend on external providers.

Evaluations will use historical races with known outcomes, kept separate from the information supplied to the model during analysis.

Results should be assessed using measurable criteria such as prediction accuracy, hit rate and confidence calibration, rather than exact natural-language output matching.

## Execution Workflow
Run the complete test suite:

`uv run --locked pytest`

Run only unit tests:

`uv run --locked pytest tests/unit`

Run only integration tests:

`uv run --locked pytest tests/integration`

Tests should be executed locally before committing changes that affect application behaviour.

Check Python syntax without executing the application:

`uv run --locked python -m compileall -q -x '(^|/)(\\.venv|\\.git)(/|$)' .`

## Initial Test Coverage
Since the application logic has not been implemented yet, the initial test suite contains an environment smoke test that verifies the active Python interpreter matches the version pinned in `.python-version`.

Functional unit and integration tests will be introduced alongside the application components they verify.