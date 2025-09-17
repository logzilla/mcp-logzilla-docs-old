# MCP Docs Server — Tests & CI

This repo includes a comprehensive, self-contained test suite for:

- `index_builder_faiss.py`
- `models.py`
- `search_engine_faiss.py`
- `server.py`

The tests are fast and do **not** require heavy native libs (FAISS, PyTorch, or Hugging Face) in CI or locally: they install lightweight **stubs** for `faiss`, `tiktoken`, `sentence_transformers`, `dotenv`, and the MCP modules during test setup.

---

## Quick start

```bash
# Python 3.10–3.12 recommended
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
python -m pip install -U pip

# Minimal test dependencies
pip install pytest pydantic pydantic-settings

# (Optional) If you want server FastAPI routes available in imports:
# pip install fastapi uvicorn

# Run tests (unit + integration, excluding performance)
pytest -m "not performance"
````

> The suite automatically stubs FAISS/transformers/etc., so you don’t need to install them.

---

## Test layout

```
tests/
  conftest.py                       # installs test-time stubs for faiss/tiktoken/etc.
  test_index_builder_faiss.py       # unit & CLI tests for index builder
  test_models.py                    # models.py coverage
  test_search_engine_faiss.py       # FAISS engine init/search/cleanup tests
  test_server.py                    # MCP server tool registration & CLI smoke tests
pytest.ini                          # marks and default settings
```

---

## Useful pytest invocations

Run all (excluding perf):

```bash
pytest -m "not performance" -q
```

Only a single file:

```bash
pytest tests/test_search_engine_faiss.py -q
```

Only one test:

```bash
pytest tests/test_index_builder_faiss.py::test_build_index_e2e_writes_files -q
```

Show print/log output:

```bash
pytest -s
```

Increase verbosity:

```bash
pytest -vv
```

---

## Markers

* `@pytest.mark.integration` — multi-module flows (kept quick)
* `@pytest.mark.performance` — perf/stress; **skipped by default**. To include:

  ```bash
  pytest -m "performance"
  ```

---

## Coverage (optional)

```bash
pip install coverage
coverage run -m pytest -m "not performance"
coverage report -m
```

---

## CI with GitHub Actions

A ready-to-use workflow is provided in `.github/workflows/python-tests.yml`. It:

* Runs on Python 3.10–3.12
* Installs `pytest`, `pydantic`, and `pydantic-settings`
* (Optionally) you can enable FastAPI/uvicorn if you add tests that rely on them
* Executes `pytest -m "not performance"`

> See the full workflow file below for adjustments (e.g., add coverage upload).

---

## Notes & gotchas

* The tests import your modules **after** installing stubs, so imports are lightweight and deterministic.
* If you later want tests that *actually* hit real FAISS or real transformers, add a separate test file and **do not** use the stubs fixture there — or gate them with a marker like `@pytest.mark.realdeps`.
* `server.py` imports `pydantic`/`pydantic_settings` unconditionally. That’s why those two packages are required for the server tests to import the module cleanly.

````

---

# .github/workflows/python-tests.yml

```yaml
name: Python tests

on:
  push:
    branches: [ main, master ]
  pull_request:
    branches: [ main, master ]

permissions:
  contents: read

jobs:
  tests:
    runs-on: ubuntu-latest
    timeout-minutes: 20

    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12"]

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: "pip"

      - name: Install test dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pytest pydantic pydantic-settings
          # Optional: enable FastAPI tests if you add any that require it
          # pip install fastapi uvicorn

      - name: Run pytest (exclude performance)
        run: |
          pytest -m "not performance" -q
````
