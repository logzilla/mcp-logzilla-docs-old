# MCP Docs Server — Tests & CI

This repo includes a comprehensive, real implementation test suite for:

- `index_builder_faiss.py`
- `models.py`
- `search_engine_faiss.py`
- `server.py`

The tests use real libraries (sentence-transformers, FAISS, tiktoken, etc.) for higher confidence.

---

## Quick start

```bash
# Python 3.10–3.12 recommended
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
python -m pip install -U pip

# Test dependencies
pip install pytest pydantic pydantic-settings sentence-transformers faiss-cpu tiktoken beautifulsoup4

# Optional for HTTP tests
# pip install fastapi uvicorn httpx

# Run tests (unit + integration)
pytest -q
````

> Some tests are marked slow; set `SKIP_SLOW_TESTS=true` to skip.

---

## Test layout

```
tests/
  conftest.py                       # real fixtures and sample data setup
  test_index_builder.py             # index builder tests (real libraries)
  test_models.py                    # models.py coverage
  test_search_engine.py             # FAISS engine init/search/cleanup tests (real)
  test_server.py                    # MCP server tests (real)
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
pytest tests/test_search_engine.py -q
```

Only one test:

```bash
pytest tests/test_index_builder.py::test_build_index_e2e_with_real_libraries -q
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

## Environment

`server.py` imports `pydantic`/`pydantic_settings` unconditionally. Ensure those packages are installed.

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
