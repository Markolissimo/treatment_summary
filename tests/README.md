# Test Suite Documentation

## Overview

Comprehensive test suite for the BiteSoft AI Treatment Summary Generator, covering all system components.

## Test Structure

```
tests/
├── conftest.py                 # Shared fixtures and test configuration
├── test_core_config.py         # Configuration module tests
├── test_core_utils.py          # Utility functions tests (age threshold)
├── test_core_prompts.py        # System prompts tests
├── test_core_security.py       # Authentication/security tests
├── test_schemas.py             # Schema validation tests
├── test_database.py            # Database and audit logging tests
├── test_api.py                 # API endpoint tests
├── test_services.py            # OpenAI service integration tests
└── test_streamlit_demo.py      # Streamlit demo tests
```

## Running Tests

### Install Test Dependencies

```bash
# Install main dependencies
pip install -r requirements.txt

# Install test dependencies
pip install pytest pytest-asyncio pytest-cov httpx
```

### Run All Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_api.py

# Run specific test class
pytest tests/test_api.py::TestTreatmentSummaryEndpoint

# Run specific test
pytest tests/test_api.py::TestTreatmentSummaryEndpoint::test_generate_treatment_summary_success
```

### Run Tests by Category

```bash
# Core module tests
pytest tests/test_core_*.py

# Schema tests
pytest tests/test_schemas.py

# Database tests
pytest tests/test_database.py

# API tests
pytest tests/test_api.py

# Service tests
pytest tests/test_services.py

# Demo tests
pytest tests/test_streamlit_demo.py
```

## Test Coverage

### Core Module Tests (`test_core_*.py`)

**`test_core_config.py`**
- Settings singleton pattern
- Required configuration fields
- Default values
- Type validation

**`test_core_utils.py`**
- Age threshold logic (adolescent <18, adult ≥18)
- Boundary value testing
- Edge cases (None, 0, 120)

**`test_core_prompts.py`**
- System prompt existence
- Guardrail keywords (diagnosis, guarantees, financials)
- Tone and audience guidance
- No harmful content

**`test_core_security.py`**
- Authentication with/without credentials
- Dev user fallback
- Token processing

### Schema Tests (`test_schemas.py`)

**Request Schema:**
- Default values for all optional fields
- Full request with patient details
- Invalid enum values rejection
- Field validation (age, lengths, etc.)

**Output Schema:**
- Valid output creation
- Optional care instructions
- List length validation (key_points, next_steps)

**Response Wrapper:**
- Success flag defaults
- Metadata handling

**Enums:**
- All enum value verification

### Database Tests (`test_database.py`)

**AuditLog Model:**
- Create audit log entries
- Error logging
- Query by user_id
- Query by document_type

**log_generation() Function:**
- Successful generation logging
- Failed generation logging
- Default parameters
- Database persistence

### API Tests (`test_api.py`)

**Health Endpoint:**
- Health check returns 200
- Response structure

**Treatment Summary Endpoint:**
- Successful generation
- Minimal request (defaults)
- Invalid input validation (422 errors)
- Error logging on failure

**Placeholder Endpoints:**
- Insurance summary placeholder
- Progress notes placeholder

**Documentation:**
- OpenAPI schema availability
- Swagger UI accessibility
- ReDoc accessibility

### Service Tests (`test_services.py`)

**Prompt Building:**
- Minimal request prompts
- Patient details inclusion
- Age category (adolescent/adult)
- Dentist note inclusion
- Proper formatting

**Generation:**
- Successful generation
- Custom API key usage
- Correct OpenAI parameters
- Time measurement
- Missing usage data handling

**GenerationResult:**
- Model creation
- Type validation

### Streamlit Demo Tests (`test_streamlit_demo.py`)

**File Structure:**
- Demo file exists
- Required imports
- API base URL configuration

**UI Components:**
- Page configuration
- Input fields
- Generate button
- Error handling

**Documentation:**
- Optional/demo status
- Separate requirements file

## Test Fixtures

### Shared Fixtures (conftest.py)

**`event_loop`**
- Async event loop for async tests

**`test_db_engine`**
- In-memory SQLite database for testing

**`test_session`**
- Database session for tests

**`test_client`**
- FastAPI test client with overridden dependencies

**`mock_openai_response`**
- Mock OpenAI API response

**`sample_treatment_request`**
- Full treatment request with all fields

**`minimal_treatment_request`**
- Empty request to test defaults

**`settings`**
- Application settings

## Mocking Strategy

### OpenAI API Mocking

Tests use `unittest.mock` to mock OpenAI API calls:

```python
@patch("app.services.openai_service.AsyncOpenAI")
async def test_generate(mock_openai_class):
    mock_client = AsyncMock()
    mock_openai_class.return_value = mock_client
    # ... configure mock response
```

### Database Mocking

Tests use in-memory SQLite database:

```python
@pytest.fixture
async def test_db_engine():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    # ... setup and teardown
```

## Best Practices

### Test Naming

- `test_<function>_<scenario>` format
- Descriptive names explaining what is tested
- Example: `test_generate_with_minimal_request`

### Test Structure

1. **Arrange** - Set up test data and mocks
2. **Act** - Execute the function/endpoint
3. **Assert** - Verify expected behavior

### Async Tests

Use `@pytest.mark.asyncio` for async tests:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result is not None
```

### Parametrized Tests

Use `@pytest.mark.parametrize` for multiple test cases:

```python
@pytest.mark.parametrize("age,expected", [
    (0, "adolescent"),
    (17, "adolescent"),
    (18, "adult"),
    (100, "adult"),
])
def test_age_categories(age, expected):
    assert get_patient_category(age) == expected
```

## Continuous Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-asyncio pytest-cov
      - run: pytest --cov=app --cov-report=xml
      - uses: codecov/codecov-action@v2
```

## Coverage Goals

- **Overall:** >80% code coverage
- **Core modules:** >90% coverage
- **API endpoints:** >85% coverage
- **Services:** >80% coverage (excluding external API calls)

## Known Limitations

### Not Tested

1. **Actual OpenAI API calls** - Mocked to avoid API costs and rate limits
2. **Full Streamlit UI interaction** - Would require Streamlit testing framework
3. **Production database** - Tests use in-memory SQLite
4. **Email integration** - Out of scope for v1 (portal team handles)

### Future Test Enhancements

1. Integration tests with real OpenAI API (optional, gated)
2. Load/performance testing
3. Security penetration testing
4. End-to-end workflow tests
5. Streamlit UI automation tests

## Troubleshooting

### Common Issues

**Import Errors:**
```bash
# Ensure app package is in Python path
export PYTHONPATH="${PYTHONPATH}:${PWD}"
```

**Async Test Failures:**
```bash
# Install pytest-asyncio
pip install pytest-asyncio
```

**Database Lock Errors:**
```bash
# Use in-memory database (already configured)
# Or ensure proper session cleanup
```

**Mock Not Working:**
```bash
# Verify patch path matches actual import
# Use full module path: "app.services.openai_service.AsyncOpenAI"
```

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure >80% coverage for new code
3. Update this README if adding new test categories
4. Run full test suite before committing

## Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [SQLModel Testing](https://sqlmodel.tiangolo.com/tutorial/testing/)
- [Async Testing](https://pytest-asyncio.readthedocs.io/)
