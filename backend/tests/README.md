# RAG System Tests

This directory contains comprehensive tests for the RAG chatbot system.

## Test Structure

- `conftest.py` - Shared pytest fixtures and test configuration
- `test_api_endpoints.py` - API endpoint tests for FastAPI application
- `__init__.py` - Test package marker

## Running Tests

### Install Test Dependencies

```bash
uv sync --group test
```

Or install specific test dependencies:

```bash
pip install pytest pytest-asyncio httpx pytest-mock
```

### Run All Tests

```bash
# From project root
pytest

# From backend directory
cd backend && pytest tests/
```

### Run Specific Test Categories

```bash
# Run only API tests
pytest -m api

# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration
```

### Run Specific Test Files

```bash
# Run API endpoint tests
pytest backend/tests/test_api_endpoints.py

# Run with verbose output
pytest -v backend/tests/test_api_endpoints.py
```

### Run Tests with Coverage

```bash
pytest --cov=backend --cov-report=html
```

## Test Categories

Tests are marked with the following categories:

- `@pytest.mark.api` - API endpoint tests
- `@pytest.mark.unit` - Unit tests for individual components
- `@pytest.mark.integration` - Integration tests across components

## Test Fixtures

The `conftest.py` file provides several useful fixtures:

### Core Fixtures
- `test_config` - Test configuration with temporary directories
- `temp_dir` - Temporary directory for test data
- `test_client` - FastAPI TestClient for API testing

### Mock Fixtures
- `mock_anthropic_client` - Mocked Anthropic API client
- `mock_vector_store` - Mocked vector store operations
- `mock_ai_generator` - Mocked AI response generation
- `mock_session_manager` - Mocked session management
- `mock_rag_system` - Fully mocked RAG system

### Sample Data Fixtures
- `sample_courses` - Sample course objects for testing
- `sample_chunks` - Sample course chunks for vector store
- `sample_query_request` - Example API request data
- `expected_query_response` - Expected API response format

## API Testing Notes

The API tests use a separate test application (`test_app_without_static`) to avoid issues with static file mounting during testing. This ensures tests run reliably without requiring the frontend files to exist.

## Mocking Strategy

Tests extensively use mocking to isolate components and avoid external dependencies:

- Anthropic API calls are mocked to prevent actual API usage
- Vector database operations are mocked for speed and consistency  
- File system operations use temporary directories
- All external services are mocked at the boundary

## Test Data

Sample test data includes:
- Python programming course with 2 lessons
- Corresponding course chunks for vector search
- Realistic query/response pairs
- Edge cases for validation testing