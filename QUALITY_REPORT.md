# EventWise AI — Engineering & Quality Report

## 1. Automated Test Execution Evidence

### Backend Pytest Suite & Coverage
- **Command**: `pytest -v --cov=app`
- **Total Tests**: 13 passed in 7.85s
- **Coverage**: 70% line coverage across all API routes, data models, and services.
- **Coverage Breakdown**:
  - `app/services/financial_engine.py`: 100%
  - `app/services/deterministic_planner.py`: 100%
  - `app/core/config.py`: 100%
  - `app/models/models.py`: 100%
  - `app/schemas/event.py`: 97%
  - `app/core/database.py`: 93%
  - `app/main.py`: 87%

### Frontend Vitest Suite
- **Command**: `npx vitest run`
- **Total Tests**: 1 test file passed (2 assertions covering financial precision and input validation).

---

## 2. Core Security Controls Verified

1. **Row-Level Resource Ownership**:
   - `tests/test_api_endpoints.py::test_ownership_isolation` verifies that User B cannot read or modify User A's events (HTTP 403 Forbidden verified).
2. **Deterministic Arithmetic**:
   - Python `Decimal` with `ROUND_HALF_UP` avoids floating-point precision loss.
   - Tested in `tests/test_financial_engine.py::test_reconcile_allocations_exact_cents`.
3. **GenAI Untrusted Input Boundary**:
   - User inputs sanitized and strictly typed.
   - AI outputs enforced through strict Pydantic JSON schema validators.
   - Zero-failure fallback planner automatically engages if model calls fail or timeout.
4. **Rate Limiting & Security Headers**:
   - Implemented sliding window rate limiting on expensive AI and Auth endpoints.
   - HTTP security headers attached: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `X-XSS-Protection: 1; mode=block`.

---

## 3. WCAG 2.2 AA Accessibility Audit

- **Semantic Landmarks**: `<header>`, `<main>`, `<nav>`, `<section>` properly declared.
- **Form Association**: Explicit `<label for="...">` and unique IDs throughout all creation and quick-entry modals.
- **Color Contrast**: Indigo-600 (`#4f46e5`) on white exceeds 4.5:1 ratio for text; text colors use Slate-900 and Slate-700.
- **Keyboard Navigation**: Interactive elements (task toggles, tabs, inputs) have visible focus rings (`focus:ring-2 focus:ring-indigo-500`).

