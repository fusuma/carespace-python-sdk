# Contributing to Carespace Python SDK

Thank you for your interest in contributing to the Carespace Python SDK! This guide will help you get started with development, testing, and contributing to the project.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Code Standards](#code-standards)
- [Testing](#testing)
- [Making Changes](#making-changes)
- [Submitting Pull Requests](#submitting-pull-requests)
- [Release Process](#release-process)

## Development Setup

### Prerequisites

- Python 3.8 or higher
- Git
- A virtual environment tool (venv, virtualenv, or conda)

### Getting Started

1. **Fork the repository**
   ```bash
   # Fork the repo on GitHub, then clone your fork
   git clone https://github.com/YOUR_USERNAME/carespace-python-sdk.git
   cd carespace-python-sdk
   ```

2. **Set up development environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   
   # Install in development mode with all dependencies
   pip install -e ".[dev]"
   ```

3. **Install pre-commit hooks**
   ```bash
   pre-commit install
   ```

4. **Verify installation**
   ```bash
   # Run tests to make sure everything works
   pytest
   
   # Check code quality
   black --check .
   isort --check-only .
   flake8 .
   mypy carespace_sdk
   ```

### Environment Variables

For testing and development, you may need to set up environment variables:

```bash
# .env file (create in project root)
CARESPACE_API_KEY=your-development-api-key
CARESPACE_BASE_URL=https://api-dev.carespace.ai
CARESPACE_TIMEOUT=30.0
```

## Project Structure

```
carespace-python-sdk/
├── carespace_sdk/           # Main package
│   ├── __init__.py         # Package exports
│   ├── client.py           # Main CarespaceClient class
│   ├── exceptions.py       # Exception definitions
│   ├── http_client.py      # HTTP client wrapper
│   ├── models.py           # Pydantic data models
│   └── api/                # API endpoint modules
│       ├── __init__.py
│       ├── auth.py         # Authentication API
│       ├── clients.py      # Client management API
│       ├── programs.py     # Program management API
│       └── users.py        # User management API
├── tests/                  # Test suite
│   ├── conftest.py         # Pytest configuration & fixtures
│   ├── test_*.py           # Test modules
│   └── integration/        # Integration tests
├── docs/                   # Documentation
│   ├── api-reference.md    # API reference
│   ├── usage-guide.md      # Usage examples
│   └── contributing.md     # This file
├── pyproject.toml          # Project configuration
├── pytest.ini             # Pytest configuration
└── README.md               # Main documentation
```

### Key Files

- **`carespace_sdk/__init__.py`**: Main package exports - add new public classes/functions here
- **`carespace_sdk/models.py`**: All Pydantic models for request/response data
- **`carespace_sdk/exceptions.py`**: Custom exceptions for the SDK
- **`carespace_sdk/client.py`**: Main client class and factory functions
- **`carespace_sdk/api/*.py`**: API endpoint implementations
- **`tests/conftest.py`**: Shared test fixtures and configuration

## Code Standards

We maintain high code quality standards using automated tools and manual review.

### Code Style

- **Formatter**: Black (line length: 88 characters)
- **Import sorting**: isort
- **Linting**: flake8
- **Type checking**: mypy

### Running Code Quality Checks

```bash
# Format code
black .
isort .

# Check formatting (CI uses these)
black --check .
isort --check-only .

# Lint code
flake8 .

# Type checking
mypy carespace_sdk

# Run all checks at once
pre-commit run --all-files
```

### Code Style Guidelines

1. **Type Hints**: All functions should have type hints
   ```python
   async def create_user(self, user_data: CreateUserRequest) -> User:
       """Create a new user."""
       # Implementation here
   ```

2. **Docstrings**: Use Google-style docstrings for public methods
   ```python
   async def get_users(
       self, 
       page: int = 1, 
       limit: int = 20, 
       search: Optional[str] = None
   ) -> UsersListResponse:
       """Get paginated list of users.
       
       Args:
           page: Page number (1-indexed)
           limit: Number of items per page
           search: Optional search term
           
       Returns:
           UsersListResponse with paginated user data
           
       Raises:
           AuthenticationError: If not authenticated
           ValidationError: If parameters are invalid
       """
   ```

3. **Error Handling**: Always handle exceptions appropriately
   ```python
   try:
       response = await self._http_client.get("/users")
       return UsersListResponse(**response)
   except httpx.HTTPStatusError as e:
       if e.response.status_code == 401:
           raise AuthenticationError("Authentication required")
       elif e.response.status_code == 404:
           raise NotFoundError("Users not found")
       else:
           raise CarespaceError(f"API error: {e}")
   ```

4. **Async/Await**: All API methods should be async
   ```python
   # ✅ Good
   async def get_user(self, user_id: str) -> User:
       return await self._http_client.get(f"/users/{user_id}")
   
   # ❌ Bad
   def get_user(self, user_id: str) -> User:
       return self._http_client.get(f"/users/{user_id}")
   ```

### Adding New Models

When adding new Pydantic models to `models.py`:

1. **Use proper base classes**:
   ```python
   from pydantic import BaseModel, Field
   from typing import Optional
   from datetime import datetime
   
   class NewModel(BaseModel):
       model_config = ConfigDict(extra="forbid")  # Strict validation
       
       id: str
       name: str
       optional_field: Optional[str] = None
       created_at: datetime
   ```

2. **Add proper field validation**:
   ```python
   class CreateUserRequest(BaseModel):
       email: str = Field(..., pattern=r'^[^@]+@[^@]+\.[^@]+$')
       name: str = Field(..., min_length=1, max_length=100)
       password: str = Field(..., min_length=8)
   ```

3. **Export in `__init__.py`**:
   ```python
   from .models import NewModel, CreateNewModelRequest
   
   __all__ = [
       # ... existing exports
       "NewModel",
       "CreateNewModelRequest",
   ]
   ```

## Testing

We use pytest for testing with comprehensive test coverage requirements.

### Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test API interactions end-to-end
- **Mock Tests**: Test with mocked HTTP responses

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage report
pytest --cov=carespace_sdk --cov-report=html

# Run specific test file
pytest tests/test_users.py

# Run specific test
pytest tests/test_users.py::TestUsersAPI::test_create_user

# Run with verbose output
pytest -v

# Run integration tests only
pytest tests/integration/

# Run fast tests only (exclude slow/integration tests)
pytest -m "not slow"
```

### Writing Tests

#### Unit Test Example

```python
# tests/test_users.py
import pytest
from unittest.mock import AsyncMock, patch
from carespace_sdk import CarespaceClient, CreateUserRequest, User

@pytest.mark.asyncio
async def test_create_user_success(mock_http_client):
    """Test successful user creation."""
    # Arrange
    user_data = CreateUserRequest(
        email="test@example.com",
        name="Test User",
        role="therapist",
        password="test-password"
    )
    
    expected_response = {
        "id": "user-123",
        "email": "test@example.com",
        "name": "Test User",
        "role": "therapist",
        "is_active": True,
        "is_verified": False,
        "created_at": "2024-01-01T00:00:00",
        "updated_at": "2024-01-01T00:00:00"
    }
    
    mock_http_client.post.return_value = expected_response
    
    # Act
    client = CarespaceClient(api_key="test-key")
    client._http_client = mock_http_client
    result = await client.users.create_user(user_data)
    
    # Assert
    assert isinstance(result, User)
    assert result.email == "test@example.com"
    assert result.name == "Test User"
    mock_http_client.post.assert_called_once_with("/users", json=user_data.model_dump())

@pytest.mark.asyncio
async def test_create_user_validation_error(mock_http_client):
    """Test user creation with validation error."""
    from carespace_sdk import ValidationError
    
    # Mock HTTP error response
    mock_http_client.post.side_effect = ValidationError(
        "Validation failed", 
        status_code=400,
        response_data={"email": ["Email already exists"]}
    )
    
    client = CarespaceClient(api_key="test-key")
    client._http_client = mock_http_client
    
    with pytest.raises(ValidationError) as exc_info:
        await client.users.create_user(CreateUserRequest(
            email="duplicate@example.com",
            name="Test User",
            role="therapist",
            password="password"
        ))
    
    assert exc_info.value.status_code == 400
    assert "Email already exists" in str(exc_info.value.response_data)
```

#### Integration Test Example

```python
# tests/integration/test_users_integration.py
import pytest
from carespace_sdk import CarespaceClient, CreateUserRequest

@pytest.mark.integration
@pytest.mark.asyncio
async def test_user_lifecycle_integration():
    """Test complete user lifecycle with real API."""
    async with CarespaceClient(api_key=pytest.api_key) as client:
        # Create user
        user_data = CreateUserRequest(
            email=f"test-{pytest.timestamp}@example.com",
            name="Integration Test User",
            role="therapist",
            password="test-password-123"
        )
        
        created_user = await client.users.create_user(user_data)
        assert created_user.email == user_data.email
        
        try:
            # Get user
            retrieved_user = await client.users.get_user(created_user.id)
            assert retrieved_user.id == created_user.id
            
            # Update user
            updated_user = await client.users.update_user(
                created_user.id,
                UpdateUserRequest(name="Updated Name")
            )
            assert updated_user.name == "Updated Name"
            
        finally:
            # Cleanup
            await client.users.delete_user(created_user.id)
```

### Test Configuration

Key pytest configurations in `pytest.ini`:

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    --strict-markers
    --strict-config
    --verbose
    --tb=short
    --cov=carespace_sdk
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-fail-under=85
markers =
    unit: Unit tests
    integration: Integration tests  
    slow: Slow running tests
```

### Test Fixtures

Common fixtures are defined in `tests/conftest.py`:

```python
import pytest
from unittest.mock import AsyncMock
from carespace_sdk import CarespaceClient

@pytest.fixture
def mock_http_client():
    """Mock HTTP client for unit tests."""
    mock = AsyncMock()
    mock.get.return_value = {}
    mock.post.return_value = {}
    mock.put.return_value = {}
    mock.delete.return_value = {}
    return mock

@pytest.fixture
async def client():
    """CarespaceClient with mocked HTTP client."""
    client = CarespaceClient(api_key="test-key")
    # Would set up mocked client here
    yield client
    await client.close()
```

## Making Changes

### Branch Naming

Use descriptive branch names following this pattern:
- `feature/add-new-endpoint` - for new features
- `fix/authentication-bug` - for bug fixes
- `docs/update-readme` - for documentation changes
- `refactor/reorganize-models` - for refactoring

### Commit Messages

Follow conventional commit format:
- `feat: add support for program templates`
- `fix: handle timeout errors properly`
- `docs: update API reference for new endpoints`
- `test: add integration tests for client management`
- `refactor: simplify error handling logic`

### Adding New API Endpoints

1. **Add to appropriate API module** (e.g., `carespace_sdk/api/users.py`):
   ```python
   async def new_endpoint(self, param: str) -> ResponseModel:
       """New endpoint description."""
       response = await self._http_client.get(f"/new-endpoint/{param}")
       return ResponseModel(**response)
   ```

2. **Add request/response models** to `carespace_sdk/models.py`:
   ```python
   class NewEndpointResponse(BaseModel):
       model_config = ConfigDict(extra="forbid")
       
       id: str
       data: str
       created_at: datetime
   ```

3. **Export new models** in `carespace_sdk/__init__.py`:
   ```python
   from .models import NewEndpointResponse
   
   __all__ = [
       # ... existing exports
       "NewEndpointResponse",
   ]
   ```

4. **Add comprehensive tests**:
   ```python
   # tests/test_new_endpoint.py
   @pytest.mark.asyncio
   async def test_new_endpoint():
       # Test implementation
       pass
   ```

5. **Update documentation** in relevant markdown files

### Adding New Exceptions

1. **Add to `carespace_sdk/exceptions.py`**:
   ```python
   class NewSpecificError(CarespaceError):
       """Raised when specific condition occurs."""
       
       def __init__(self, message: str, additional_info: str = None):
           super().__init__(message)
           self.additional_info = additional_info
   ```

2. **Export in `__init__.py`**:
   ```python
   from .exceptions import NewSpecificError
   ```

3. **Add tests for the new exception**

## Submitting Pull Requests

### Before Submitting

1. **Run the full test suite**:
   ```bash
   pytest
   ```

2. **Check code quality**:
   ```bash
   pre-commit run --all-files
   ```

3. **Update documentation** if needed

4. **Add/update tests** for your changes

### Pull Request Process

1. **Create a pull request** with:
   - Clear title describing the change
   - Detailed description of what was changed and why
   - Links to related issues
   - Screenshots/examples if applicable

2. **PR Template** (create `.github/pull_request_template.md`):
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update
   
   ## Testing
   - [ ] Unit tests pass
   - [ ] Integration tests pass (if applicable)
   - [ ] Added new tests for changes
   
   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Documentation updated
   - [ ] No breaking changes (or documented)
   ```

3. **Address review feedback** promptly

4. **Ensure CI passes** before requesting final review

### Review Process

- All PRs require at least one approval
- Automated checks must pass (tests, linting, type checking)
- Breaking changes require special consideration
- Documentation updates may be required

## Release Process

### Versioning

We follow [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update version** in `pyproject.toml`:
   ```toml
   [project]
   version = "1.2.0"
   ```

2. **Update CHANGELOG.md** with release notes

3. **Create release PR** with version bump and changelog

4. **Tag release** after merge:
   ```bash
   git tag v1.2.0
   git push origin v1.2.0
   ```

5. **GitHub Actions** will automatically:
   - Run full test suite
   - Build package
   - Publish to PyPI
   - Create GitHub release

### Pre-release Testing

Before major releases:
1. Run integration tests against staging environment
2. Test with multiple Python versions (3.8, 3.9, 3.10, 3.11, 3.12)
3. Verify documentation builds correctly
4. Test installation from PyPI test instance

## Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue with reproduction steps  
- **Feature Requests**: Open a GitHub Issue with detailed use case
- **Security Issues**: Email security@carespace.ai (do not open public issues)

## Code of Conduct

Be respectful, inclusive, and professional in all interactions. We want to maintain a welcoming environment for all contributors.

## Recognition

Contributors are recognized in:
- CONTRIBUTORS.md file
- Release notes for significant contributions
- GitHub contributor graphs

Thank you for contributing to the Carespace Python SDK! 🎉