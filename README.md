# Carespace Python SDK

A modern, async-first Python SDK for the Carespace API with full type safety using Pydantic models.

## Features

- 🚀 **Async/Await First** - Built for modern Python with async/await support
- 🔒 **Full Type Safety** - Complete type hints and Pydantic models for data validation
- 🛡️ **Robust Error Handling** - Comprehensive exception hierarchy with detailed error information
- 🔄 **Automatic Retries** - Built-in retry logic with exponential backoff
- 📦 **Zero Dependencies Bloat** - Minimal dependencies (httpx, pydantic)
- 🎯 **Developer Friendly** - Intuitive API design with excellent IDE support
- 📊 **Data Science Ready** - Perfect for healthcare analytics and research
- 🧪 **Test Coverage** - Comprehensive test suite with pytest

## Requirements

- Python 3.8+
- httpx >= 0.25.0
- pydantic >= 2.0.0

## Installation

```bash
pip install carespace-sdk
```

### Development Installation

```bash
git clone https://github.com/carespace/python-sdk.git
cd python-sdk
pip install -e ".[dev]"
```

## Quick Start

### Basic Usage

```python
import asyncio
from carespace_sdk import CarespaceClient

async def main():
    # Create client
    async with CarespaceClient(api_key="your-api-key") as client:
        # Authenticate
        login_response = await client.auth.login("user@example.com", "password")
        client.set_api_key(login_response.access_token)
        
        # Get users
        users = await client.users.get_users(limit=10, search="john")
        print(f"Found {len(users.data)} users")
        
        # Create a client
        from carespace_sdk import CreateClientRequest, Address
        
        client_data = CreateClientRequest(
            name="John Doe",
            email="john@example.com",
            phone="+1234567890",
            address=Address(
                street="123 Main St",
                city="New York",
                state="NY",
                zip_code="10001"
            )
        )
        
        new_client = await client.clients.create_client(client_data)
        print(f"Created client: {new_client.id}")

asyncio.run(main())
```

### Environment-Specific Clients

```python
from carespace_sdk import create_production_client, create_development_client

# Production client
async with create_production_client("your-api-key") as client:
    users = await client.users.get_users()

# Development client
async with create_development_client("your-dev-api-key") as client:
    users = await client.users.get_users()
```

## Authentication

### Login and Token Management

```python
async with CarespaceClient() as client:
    # Login and automatically set token
    login_response = await client.login_and_set_token("user@example.com", "password")
    print(f"Access token expires in: {login_response.expires_in} seconds")
    
    # Manual token management
    login_response = await client.auth.login("user@example.com", "password")
    client.set_api_key(login_response.access_token)
    
    # Refresh token
    new_tokens = await client.auth.refresh_token(login_response.refresh_token)
    client.set_api_key(new_tokens.access_token)
    
    # Logout
    await client.auth.logout()
```

### Password Management

```python
# Forgot password
await client.auth.forgot_password("user@example.com")

# Reset password with token
await client.auth.reset_password("reset-token", "new-password")

# Change password (requires authentication)
await client.auth.change_password("current-password", "new-password")

# Email verification
await client.auth.verify_email("verification-token")
await client.auth.resend_verification("user@example.com")
```

## Working with Users

### User Management

```python
from carespace_sdk import CreateUserRequest, UpdateUserRequest

# Get all users with pagination
users_response = await client.users.get_users(
    page=1,
    limit=20,
    search="doctor",
    sort_by="created_at",
    sort_order="desc"
)

print(f"Total users: {users_response.total}")
for user in users_response.data:
    print(f"User: {user.name} ({user.email}) - Role: {user.role}")

# Get specific user
user = await client.users.get_user("user-id-123")
print(f"User details: {user.name} - {user.email}")

# Create user
new_user_data = CreateUserRequest(
    email="newdoctor@example.com",
    name="Dr. Jane Smith",
    first_name="Jane",
    last_name="Smith",
    role="doctor",
    password="secure-password"
)

new_user = await client.users.create_user(new_user_data)
print(f"Created user: {new_user.id}")

# Update user
update_data = UpdateUserRequest(
    name="Dr. Jane Smith-Johnson",
    is_active=True
)

updated_user = await client.users.update_user("user-id-123", update_data)

# Delete user
await client.users.delete_user("user-id-123")
```

### Profile Management

```python
# Get current user profile
profile = await client.users.get_user_profile()
print(f"Current user: {profile.name}")

# Update profile
from carespace_sdk import UpdateUserRequest

profile_update = UpdateUserRequest(
    name="Updated Name",
    first_name="Updated",
    last_name="Name"
)

updated_profile = await client.users.update_user_profile(profile_update)

# User settings
settings = await client.users.get_user_settings("user-id")
updated_settings = await client.users.update_user_settings("user-id", {
    "notifications": True,
    "theme": "dark",
    "language": "en"
})
```

## Working with Clients

### Client Management

```python
from carespace_sdk import CreateClientRequest, UpdateClientRequest, Address
from datetime import datetime

# Get all clients
clients_response = await client.clients.get_clients(
    page=1,
    limit=20,
    search="john",
    sort_by="name"
)

for client_record in clients_response.data:
    print(f"Client: {client_record.name} - Email: {client_record.email}")

# Get specific client
client_record = await client.clients.get_client("client-id-123")
print(f"Client: {client_record.name}")

# Create client with full details
address = Address(
    street="123 Main Street",
    city="New York",
    state="NY",
    zip_code="10001",
    country="USA"
)

client_data = CreateClientRequest(
    name="John Smith",
    email="john.smith@example.com",
    phone="+1234567890",
    date_of_birth=datetime(1985, 6, 15),
    gender="male",
    address=address,
    medical_history="Previous knee injury in 2020",
    notes="Prefers morning appointments"
)

new_client = await client.clients.create_client(client_data)
print(f"Created client: {new_client.id}")

# Update client
update_data = UpdateClientRequest(
    phone="+1987654321",
    notes="Updated notes - now prefers afternoon appointments"
)

updated_client = await client.clients.update_client("client-id-123", update_data)

# Get client statistics
stats = await client.clients.get_client_stats("client-id-123")
print(f"Client stats:")
print(f"  Total sessions: {stats.total_sessions}")
print(f"  Completed exercises: {stats.completed_exercises}")
print(f"  Average score: {stats.average_score}")
print(f"  Last session: {stats.last_session_date}")
```

### Client Program Management

```python
# Get programs assigned to client
client_programs = await client.clients.get_client_programs(
    "client-id-123",
    page=1,
    limit=10
)

for program in client_programs.data:
    print(f"Assigned program: {program.name}")

# Assign program to client
await client.clients.assign_program_to_client(
    client_id="client-id-123",
    program_id="program-id-456",
    start_date="2024-01-01",
    end_date="2024-04-01",
    notes="Post-surgery rehabilitation program"
)

# Remove program assignment
await client.clients.remove_client_program("client-id-123", "program-id-456")
```

## Working with Programs

### Program Management

```python
from carespace_sdk import CreateProgramRequest, UpdateProgramRequest

# Get all programs with filtering
programs_response = await client.programs.get_programs(
    page=1,
    limit=20,
    search="rehabilitation",
    category="physical-therapy",
    difficulty="beginner",
    is_template=False
)

for program in programs_response.data:
    print(f"Program: {program.name} - Category: {program.category}")
    print(f"  Duration: {program.duration} minutes")
    print(f"  Exercises: {len(program.exercises)}")

# Get specific program
program = await client.programs.get_program("program-id-123")
print(f"Program: {program.name}")

# Create program
program_data = CreateProgramRequest(
    name="Post-Surgery Knee Rehabilitation",
    description="Comprehensive rehabilitation program for post-surgical knee recovery",
    category="rehabilitation",
    difficulty="intermediate",
    duration=45,
    is_template=False
)

new_program = await client.programs.create_program(program_data)
print(f"Created program: {new_program.id}")

# Update program
update_data = UpdateProgramRequest(
    description="Updated program description",
    duration=60,
    difficulty="advanced"
)

updated_program = await client.programs.update_program("program-id-123", update_data)

# Duplicate program
from carespace_sdk import DuplicateProgramRequest

duplicate_data = DuplicateProgramRequest(
    name="Advanced Knee Rehabilitation",
    description="Advanced version of the rehabilitation program",
    copy_exercises=True
)

duplicated_program = await client.programs.duplicate_program("program-id-123", duplicate_data)
```

### Exercise Management

```python
from carespace_sdk import CreateExerciseRequest

# Get exercises in program
exercises_response = await client.programs.get_program_exercises(
    "program-id-123",
    page=1,
    limit=50
)

for exercise in exercises_response.data:
    print(f"Exercise: {exercise.name}")
    print(f"  Duration: {exercise.duration}s")
    print(f"  Reps: {exercise.repetitions}, Sets: {exercise.sets}")

# Add exercise to program
exercise_data = CreateExerciseRequest(
    name="Knee Flexion Exercise",
    description="Gentle knee bending exercise for flexibility",
    instructions="Slowly bend your knee to 90 degrees and hold for 5 seconds",
    video_url="https://example.com/exercise-video.mp4",
    duration=30,
    repetitions=10,
    sets=3,
    rest_time=60,
    order=1
)

new_exercise = await client.programs.add_exercise_to_program("program-id-123", exercise_data)

# Update exercise
updated_exercise = await client.programs.update_program_exercise(
    "program-id-123",
    "exercise-id-456",
    exercise_data
)

# Remove exercise
await client.programs.remove_program_exercise("program-id-123", "exercise-id-456")

# Get program templates
templates = await client.programs.get_program_templates(
    page=1,
    limit=10,
    category="rehabilitation"
)
```

## Error Handling

### Exception Hierarchy

```python
from carespace_sdk import (
    CarespaceError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    ServerError,
    NetworkError,
    RateLimitError,
    TimeoutError,
)

try:
    user = await client.users.get_user("invalid-id")
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
    # Redirect to login or refresh token
except NotFoundError as e:
    print(f"User not found: {e.message}")
except ValidationError as e:
    print(f"Invalid data: {e.message}")
    print(f"Response data: {e.response_data}")
except RateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
    if e.retry_after:
        print(f"Retry after {e.retry_after} seconds")
except NetworkError as e:
    print(f"Network error: {e.message}")
    if e.original_exception:
        print(f"Original error: {e.original_exception}")
except TimeoutError as e:
    print(f"Request timed out: {e.message}")
    print(f"Timeout duration: {e.timeout_duration}s")
except ServerError as e:
    print(f"Server error: {e.message}")
    print(f"Status code: {e.status_code}")
except CarespaceError as e:
    print(f"API error: {e.message}")
    print(f"Status code: {e.status_code}")
    print(f"Response data: {e.response_data}")
```

### Retry Configuration

```python
# Configure retries and timeout
client = CarespaceClient(
    api_key="your-api-key",
    timeout=60.0,  # 60 second timeout
    max_retries=5,  # Retry up to 5 times
)

# Custom retry logic for specific operations
import asyncio

async def robust_get_users():
    max_attempts = 3
    for attempt in range(max_attempts):
        try:
            return await client.users.get_users()
        except (NetworkError, TimeoutError) as e:
            if attempt == max_attempts - 1:
                raise
            wait_time = 2 ** attempt  # Exponential backoff
            await asyncio.sleep(wait_time)
```

## Data Science and Analytics

### Pandas Integration

```python
import pandas as pd
from datetime import datetime, timedelta

async def get_client_analytics():
    # Get all clients
    all_clients = []
    page = 1
    
    while True:
        response = await client.clients.get_clients(page=page, limit=100)
        all_clients.extend(response.data)
        
        if page >= response.pages:
            break
        page += 1
    
    # Convert to DataFrame
    client_data = []
    for client_record in all_clients:
        client_data.append({
            'id': client_record.id,
            'name': client_record.name,
            'email': client_record.email,
            'gender': client_record.gender,
            'created_at': client_record.created_at,
            'is_active': client_record.is_active,
        })
    
    df = pd.DataFrame(client_data)
    
    # Analytics
    print(f"Total clients: {len(df)}")
    print(f"Active clients: {df['is_active'].sum()}")
    print(f"Gender distribution:\\n{df['gender'].value_counts()}")
    
    # Recent registrations
    recent_date = datetime.now() - timedelta(days=30)
    recent_clients = df[df['created_at'] > recent_date]
    print(f"New clients in last 30 days: {len(recent_clients)}")
    
    return df

# Usage
df = await get_client_analytics()
```

### Bulk Operations

```python
async def bulk_create_clients(client_data_list):
    """Create multiple clients with progress tracking."""
    created_clients = []
    errors = []
    
    for i, client_data in enumerate(client_data_list):
        try:
            client_record = await client.clients.create_client(client_data)
            created_clients.append(client_record)
            print(f"Created client {i+1}/{len(client_data_list)}: {client_record.name}")
        except CarespaceError as e:
            errors.append({"index": i, "data": client_data, "error": str(e)})
            print(f"Failed to create client {i+1}: {e.message}")
    
    print(f"Successfully created {len(created_clients)} clients")
    print(f"Failed to create {len(errors)} clients")
    
    return created_clients, errors

# Usage
client_data_list = [
    CreateClientRequest(name="Client 1", email="client1@example.com"),
    CreateClientRequest(name="Client 2", email="client2@example.com"),
    # ... more clients
]

created, errors = await bulk_create_clients(client_data_list)
```

## Advanced Usage

### Custom HTTP Client Configuration

```python
import httpx

# Custom HTTP client with specific configuration
custom_http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(60.0),
    limits=httpx.Limits(max_keepalive_connections=10, max_connections=20),
    headers={"User-Agent": "MyApp/1.0"},
)

client = CarespaceClient(
    api_key="your-api-key",
    # Pass custom httpx client
    httpx_client=custom_http_client
)
```

### Connection Pooling and Session Management

```python
class CarespaceService:
    def __init__(self, api_key: str):
        self.client = CarespaceClient(api_key=api_key)
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.close()
    
    async def get_user_summary(self, user_id: str):
        user = await self.client.users.get_user(user_id)
        # Additional processing...
        return user

# Usage
async with CarespaceService("your-api-key") as service:
    user = await service.get_user_summary("user-id")
```

### Health Monitoring

```python
async def monitor_api_health():
    """Monitor API health and connectivity."""
    try:
        is_healthy = await client.health_check()
        if is_healthy:
            print("✅ API is healthy and accessible")
        else:
            print("❌ API health check failed")
        return is_healthy
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

# Periodic health checks
import asyncio

async def periodic_health_check(interval=300):  # 5 minutes
    while True:
        await monitor_api_health()
        await asyncio.sleep(interval)
```

## Testing

### Unit Tests with pytest

```python
import pytest
from carespace_sdk import CarespaceClient, CreateUserRequest

@pytest.mark.asyncio
async def test_create_user():
    async with CarespaceClient(api_key="test-key") as client:
        user_data = CreateUserRequest(
            email="test@example.com",
            name="Test User"
        )
        
        user = await client.users.create_user(user_data)
        assert user.email == "test@example.com"
        assert user.name == "Test User"

@pytest.mark.asyncio
async def test_authentication_error():
    async with CarespaceClient(api_key="invalid-key") as client:
        with pytest.raises(AuthenticationError):
            await client.users.get_users()
```

### Mock Testing

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_users_with_mock():
    with patch('carespace_sdk.HTTPClient') as mock_http:
        mock_http.return_value.get = AsyncMock(return_value={
            "data": [{"id": "1", "email": "test@example.com", "name": "Test"}],
            "total": 1,
            "page": 1,
            "limit": 20,
            "pages": 1
        })
        
        client = CarespaceClient(api_key="test-key")
        users = await client.users.get_users()
        
        assert len(users.data) == 1
        assert users.data[0].email == "test@example.com"
```

## Configuration

### Environment Variables

```python
import os
from carespace_sdk import CarespaceClient

# Use environment variables
client = CarespaceClient(
    base_url=os.getenv("CARESPACE_BASE_URL", "https://api-dev.carespace.ai"),
    api_key=os.getenv("CARESPACE_API_KEY"),
    timeout=float(os.getenv("CARESPACE_TIMEOUT", "30.0")),
)
```

### Configuration File

```python
# config.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class CarespaceConfig:
    base_url: str = "https://api-dev.carespace.ai"
    api_key: Optional[str] = None
    timeout: float = 30.0
    max_retries: int = 3

# Usage
from config import CarespaceConfig

config = CarespaceConfig(
    base_url="https://api.carespace.ai",
    api_key="your-production-key",
    timeout=60.0
)

client = CarespaceClient(**config.__dict__)
```

## Performance Tips

1. **Use Connection Pooling**: The SDK automatically manages connection pooling
2. **Batch Operations**: Use pagination effectively for large datasets
3. **Async Context Managers**: Always use `async with` for proper resource cleanup
4. **Configure Timeouts**: Set appropriate timeouts for your use case
5. **Handle Rate Limits**: Implement proper retry logic for rate-limited operations

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes with tests
4. Run the test suite (`pytest`)
5. Check code quality (`black`, `isort`, `flake8`, `mypy`)
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- 📧 Email: [support@carespace.ai](mailto:support@carespace.ai)
- 🐛 Issues: [GitHub Issues](https://github.com/carespace/python-sdk/issues)
- 📖 Documentation: [docs.carespace.ai/python](https://docs.carespace.ai/python)
- 💬 Discord: [Carespace Developer Community](https://discord.gg/carespace)

---

**Built with ❤️ for the Python community by the Carespace Team**