# Carespace Python SDK - API Reference

This comprehensive API reference covers all classes, methods, and models available in the Carespace Python SDK.

## Table of Contents

- [Client](#client)
- [Authentication API](#authentication-api)
- [Users API](#users-api)
- [Clients API](#clients-api)
- [Programs API](#programs-api)
- [Data Models](#data-models)
- [Exceptions](#exceptions)

## Client

### CarespaceClient

The main client class for interacting with the Carespace API.

```python
from carespace_sdk import CarespaceClient

client = CarespaceClient(
    base_url="https://api-dev.carespace.ai",
    api_key="your-api-key",
    timeout=30.0,
    max_retries=3
)
```

#### Constructor Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `base_url` | `str` | `"https://api-dev.carespace.ai"` | Base URL for the Carespace API |
| `api_key` | `Optional[str]` | `None` | API key for authentication |
| `timeout` | `float` | `30.0` | Request timeout in seconds |
| `max_retries` | `int` | `3` | Maximum number of retry attempts |

#### Properties

| Property | Type | Description |
|----------|------|-------------|
| `auth` | `AuthAPI` | Authentication API endpoints |
| `users` | `UsersAPI` | User management endpoints |
| `clients` | `ClientsAPI` | Client management endpoints |
| `programs` | `ProgramsAPI` | Program and exercise endpoints |

#### Methods

##### `set_api_key(api_key: str) -> None`

Set or update the API key for authentication.

```python
client.set_api_key("new-api-key")
```

##### `async login_and_set_token(email: str, password: str) -> LoginResponse`

Login with credentials and automatically set the access token.

```python
login_response = await client.login_and_set_token("user@example.com", "password")
```

##### `async health_check() -> bool`

Check API connectivity and health status.

```python
is_healthy = await client.health_check()
```

##### `async close() -> None`

Clean up resources and close HTTP connections.

```python
await client.close()
```

#### Quick Access Methods

##### `async quick_get_users(limit: int = 20, search: Optional[str] = None) -> UsersListResponse`

Quick method to get users with minimal parameters.

##### `async quick_get_clients(limit: int = 20, search: Optional[str] = None) -> ClientsListResponse`

Quick method to get clients with minimal parameters.

##### `async quick_get_programs(limit: int = 20, category: Optional[str] = None) -> ProgramsListResponse`

Quick method to get programs with minimal parameters.

#### Context Manager Usage

```python
async with CarespaceClient(api_key="your-key") as client:
    users = await client.users.get_users()
    # Client automatically closes when exiting context
```

### Factory Functions

#### `create_production_client(api_key: str) -> CarespaceClient`

Create a client configured for production environment.

```python
from carespace_sdk import create_production_client

client = create_production_client("your-production-api-key")
```

#### `create_development_client(api_key: Optional[str] = None) -> CarespaceClient`

Create a client configured for development environment.

```python
from carespace_sdk import create_development_client

client = create_development_client("your-dev-api-key")
```

## Authentication API

The `AuthAPI` provides authentication and password management functionality.

### Methods

#### `async login(email: str, password: str) -> LoginResponse`

Authenticate with email and password.

```python
login_response = await client.auth.login("user@example.com", "password")
access_token = login_response.access_token
```

**Parameters:**
- `email` (str): User's email address
- `password` (str): User's password

**Returns:** `LoginResponse` with access token, refresh token, and metadata

#### `async logout() -> MessageResponse`

Logout the current user session.

```python
await client.auth.logout()
```

#### `async refresh_token(refresh_token: str) -> LoginResponse`

Refresh the access token using a refresh token.

```python
new_tokens = await client.auth.refresh_token(login_response.refresh_token)
client.set_api_key(new_tokens.access_token)
```

**Parameters:**
- `refresh_token` (str): Valid refresh token

**Returns:** `LoginResponse` with new tokens

#### `async forgot_password(email: str) -> MessageResponse`

Send password reset email to user.

```python
await client.auth.forgot_password("user@example.com")
```

**Parameters:**
- `email` (str): User's email address

#### `async reset_password(token: str, password: str) -> MessageResponse`

Reset password using reset token.

```python
await client.auth.reset_password("reset-token-123", "new-secure-password")
```

**Parameters:**
- `token` (str): Password reset token from email
- `password` (str): New password

#### `async change_password(current_password: str, new_password: str) -> MessageResponse`

Change password for authenticated user.

```python
await client.auth.change_password("current-password", "new-password")
```

**Parameters:**
- `current_password` (str): Current password
- `new_password` (str): New password

#### `async verify_email(token: str) -> MessageResponse`

Verify email address using verification token.

```python
await client.auth.verify_email("verification-token-123")
```

**Parameters:**
- `token` (str): Email verification token

#### `async resend_verification(email: str) -> MessageResponse`

Resend email verification to user.

```python
await client.auth.resend_verification("user@example.com")
```

**Parameters:**
- `email` (str): User's email address

## Users API

The `UsersAPI` provides user management functionality.

### Methods

#### `async get_users(page: int = 1, limit: int = 20, search: Optional[str] = None, sort_by: Optional[str] = None, sort_order: Optional[str] = None) -> UsersListResponse`

Get paginated list of users with optional filtering and sorting.

```python
users_response = await client.users.get_users(
    page=1,
    limit=50,
    search="doctor",
    sort_by="created_at",
    sort_order="desc"
)

for user in users_response.data:
    print(f"User: {user.name} ({user.email})")
```

**Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `search` (str, optional): Search term for filtering
- `sort_by` (str, optional): Field to sort by
- `sort_order` (str, optional): Sort order ("asc" or "desc")

**Returns:** `UsersListResponse` with paginated user data

#### `async get_user(user_id: str) -> User`

Get specific user by ID.

```python
user = await client.users.get_user("user-id-123")
print(f"User: {user.name} - {user.email}")
```

**Parameters:**
- `user_id` (str): Unique user identifier

**Returns:** `User` object

#### `async create_user(user_data: CreateUserRequest) -> User`

Create a new user.

```python
from carespace_sdk import CreateUserRequest

user_data = CreateUserRequest(
    email="newuser@example.com",
    name="John Doe",
    first_name="John",
    last_name="Doe",
    role="therapist",
    password="secure-password"
)

new_user = await client.users.create_user(user_data)
```

**Parameters:**
- `user_data` (CreateUserRequest): User creation data

**Returns:** `User` object for created user

#### `async update_user(user_id: str, user_data: UpdateUserRequest) -> User`

Update existing user.

```python
from carespace_sdk import UpdateUserRequest

update_data = UpdateUserRequest(
    name="John Smith",
    is_active=True
)

updated_user = await client.users.update_user("user-id-123", update_data)
```

**Parameters:**
- `user_id` (str): User ID to update
- `user_data` (UpdateUserRequest): Updated user data

**Returns:** `User` object with updated information

#### `async delete_user(user_id: str) -> MessageResponse`

Delete a user.

```python
await client.users.delete_user("user-id-123")
```

**Parameters:**
- `user_id` (str): User ID to delete

#### `async get_user_profile() -> User`

Get current authenticated user's profile.

```python
profile = await client.users.get_user_profile()
print(f"Current user: {profile.name}")
```

**Returns:** `User` object for current user

#### `async update_user_profile(user_data: UpdateUserRequest) -> User`

Update current user's profile.

```python
profile_update = UpdateUserRequest(name="New Name")
updated_profile = await client.users.update_user_profile(profile_update)
```

**Parameters:**
- `user_data` (UpdateUserRequest): Profile update data

**Returns:** `User` object with updated profile

#### `async get_user_settings(user_id: str) -> dict`

Get user settings.

```python
settings = await client.users.get_user_settings("user-id-123")
```

**Parameters:**
- `user_id` (str): User ID

**Returns:** Dictionary of user settings

#### `async update_user_settings(user_id: str, settings: dict) -> dict`

Update user settings.

```python
new_settings = {
    "notifications": True,
    "theme": "dark",
    "language": "en"
}

updated_settings = await client.users.update_user_settings("user-id-123", new_settings)
```

**Parameters:**
- `user_id` (str): User ID
- `settings` (dict): Settings to update

**Returns:** Dictionary of updated settings

## Clients API

The `ClientsAPI` provides client management functionality.

### Methods

#### `async get_clients(page: int = 1, limit: int = 20, search: Optional[str] = None, sort_by: Optional[str] = None, sort_order: Optional[str] = None) -> ClientsListResponse`

Get paginated list of clients.

```python
clients_response = await client.clients.get_clients(
    page=1,
    limit=50,
    search="john",
    sort_by="name"
)

for client_record in clients_response.data:
    print(f"Client: {client_record.name} - {client_record.email}")
```

**Parameters:**
- `page` (int): Page number (default: 1)
- `limit` (int): Items per page (default: 20)
- `search` (str, optional): Search term
- `sort_by` (str, optional): Field to sort by
- `sort_order` (str, optional): Sort order

**Returns:** `ClientsListResponse` with paginated client data

#### `async get_client(client_id: str) -> Client`

Get specific client by ID.

```python
client_record = await client.clients.get_client("client-id-123")
print(f"Client: {client_record.name}")
```

**Parameters:**
- `client_id` (str): Client ID

**Returns:** `Client` object

#### `async create_client(client_data: CreateClientRequest) -> Client`

Create a new client.

```python
from carespace_sdk import CreateClientRequest, Address
from datetime import datetime

address = Address(
    street="123 Main St",
    city="New York",
    state="NY",
    zip_code="10001"
)

client_data = CreateClientRequest(
    name="John Smith",
    email="john@example.com",
    phone="+1234567890",
    date_of_birth=datetime(1985, 6, 15),
    gender="male",
    address=address,
    medical_history="Previous knee surgery",
    notes="Prefers morning appointments"
)

new_client = await client.clients.create_client(client_data)
```

**Parameters:**
- `client_data` (CreateClientRequest): Client creation data

**Returns:** `Client` object

#### `async update_client(client_id: str, client_data: UpdateClientRequest) -> Client`

Update existing client.

```python
from carespace_sdk import UpdateClientRequest

update_data = UpdateClientRequest(
    phone="+1987654321",
    notes="Updated contact information"
)

updated_client = await client.clients.update_client("client-id-123", update_data)
```

**Parameters:**
- `client_id` (str): Client ID
- `client_data` (UpdateClientRequest): Update data

**Returns:** `Client` object

#### `async delete_client(client_id: str) -> MessageResponse`

Delete a client.

```python
await client.clients.delete_client("client-id-123")
```

**Parameters:**
- `client_id` (str): Client ID to delete

#### `async get_client_stats(client_id: str) -> ClientStats`

Get client statistics and analytics.

```python
stats = await client.clients.get_client_stats("client-id-123")
print(f"Total sessions: {stats.total_sessions}")
print(f"Completed exercises: {stats.completed_exercises}")
print(f"Average score: {stats.average_score}")
```

**Parameters:**
- `client_id` (str): Client ID

**Returns:** `ClientStats` object

#### `async get_client_programs(client_id: str, page: int = 1, limit: int = 20, search: Optional[str] = None) -> ProgramsListResponse`

Get programs assigned to a client.

```python
client_programs = await client.clients.get_client_programs(
    "client-id-123",
    page=1,
    limit=10
)

for program in client_programs.data:
    print(f"Assigned program: {program.name}")
```

**Parameters:**
- `client_id` (str): Client ID
- `page` (int): Page number
- `limit` (int): Items per page
- `search` (str, optional): Search term

**Returns:** `ProgramsListResponse`

#### `async assign_program_to_client(client_id: str, program_id: str, start_date: str, end_date: str, notes: Optional[str] = None) -> SuccessResponse`

Assign a program to a client.

```python
await client.clients.assign_program_to_client(
    client_id="client-id-123",
    program_id="program-id-456",
    start_date="2024-01-01",
    end_date="2024-04-01",
    notes="Post-surgery rehabilitation"
)
```

**Parameters:**
- `client_id` (str): Client ID
- `program_id` (str): Program ID
- `start_date` (str): Program start date
- `end_date` (str): Program end date
- `notes` (str, optional): Assignment notes

#### `async remove_client_program(client_id: str, program_id: str) -> MessageResponse`

Remove program assignment from client.

```python
await client.clients.remove_client_program("client-id-123", "program-id-456")
```

**Parameters:**
- `client_id` (str): Client ID
- `program_id` (str): Program ID

## Programs API

The `ProgramsAPI` provides program and exercise management functionality.

### Methods

#### `async get_programs(page: int = 1, limit: int = 20, search: Optional[str] = None, category: Optional[str] = None, difficulty: Optional[str] = None, is_template: Optional[bool] = None, sort_by: Optional[str] = None, sort_order: Optional[str] = None) -> ProgramsListResponse`

Get paginated list of programs with filtering options.

```python
programs_response = await client.programs.get_programs(
    page=1,
    limit=20,
    search="rehabilitation",
    category="physical-therapy",
    difficulty="beginner"
)

for program in programs_response.data:
    print(f"Program: {program.name} - Category: {program.category}")
```

**Parameters:**
- `page` (int): Page number
- `limit` (int): Items per page
- `search` (str, optional): Search term
- `category` (str, optional): Filter by category
- `difficulty` (str, optional): Filter by difficulty
- `is_template` (bool, optional): Filter templates
- `sort_by` (str, optional): Sort field
- `sort_order` (str, optional): Sort order

**Returns:** `ProgramsListResponse`

#### `async get_program(program_id: str) -> Program`

Get specific program by ID.

```python
program = await client.programs.get_program("program-id-123")
print(f"Program: {program.name}")
print(f"Exercises: {len(program.exercises)}")
```

**Parameters:**
- `program_id` (str): Program ID

**Returns:** `Program` object

#### `async create_program(program_data: CreateProgramRequest) -> Program`

Create a new program.

```python
from carespace_sdk import CreateProgramRequest

program_data = CreateProgramRequest(
    name="Post-Surgery Knee Rehabilitation",
    description="Comprehensive knee recovery program",
    category="rehabilitation",
    difficulty="intermediate",
    duration=45,
    is_template=False
)

new_program = await client.programs.create_program(program_data)
```

**Parameters:**
- `program_data` (CreateProgramRequest): Program creation data

**Returns:** `Program` object

#### `async update_program(program_id: str, program_data: UpdateProgramRequest) -> Program`

Update existing program.

```python
from carespace_sdk import UpdateProgramRequest

update_data = UpdateProgramRequest(
    description="Updated program description",
    duration=60,
    difficulty="advanced"
)

updated_program = await client.programs.update_program("program-id-123", update_data)
```

**Parameters:**
- `program_id` (str): Program ID
- `program_data` (UpdateProgramRequest): Update data

**Returns:** `Program` object

#### `async delete_program(program_id: str) -> MessageResponse`

Delete a program.

```python
await client.programs.delete_program("program-id-123")
```

**Parameters:**
- `program_id` (str): Program ID

#### `async get_program_exercises(program_id: str, page: int = 1, limit: int = 50, search: Optional[str] = None) -> ExercisesListResponse`

Get exercises in a program.

```python
exercises_response = await client.programs.get_program_exercises(
    "program-id-123",
    page=1,
    limit=50
)

for exercise in exercises_response.data:
    print(f"Exercise: {exercise.name}")
    print(f"Duration: {exercise.duration}s, Reps: {exercise.repetitions}")
```

**Parameters:**
- `program_id` (str): Program ID
- `page` (int): Page number
- `limit` (int): Items per page
- `search` (str, optional): Search term

**Returns:** `ExercisesListResponse`

#### `async add_exercise_to_program(program_id: str, exercise_data: CreateExerciseRequest) -> Exercise`

Add exercise to program.

```python
from carespace_sdk import CreateExerciseRequest

exercise_data = CreateExerciseRequest(
    name="Knee Flexion Exercise",
    description="Gentle knee bending exercise",
    instructions="Slowly bend knee to 90 degrees",
    video_url="https://example.com/video.mp4",
    duration=30,
    repetitions=10,
    sets=3,
    rest_time=60,
    order=1
)

new_exercise = await client.programs.add_exercise_to_program("program-id-123", exercise_data)
```

**Parameters:**
- `program_id` (str): Program ID
- `exercise_data` (CreateExerciseRequest): Exercise data

**Returns:** `Exercise` object

#### `async update_program_exercise(program_id: str, exercise_id: str, exercise_data: CreateExerciseRequest) -> Exercise`

Update exercise in program.

```python
updated_exercise = await client.programs.update_program_exercise(
    "program-id-123",
    "exercise-id-456",
    exercise_data
)
```

**Parameters:**
- `program_id` (str): Program ID
- `exercise_id` (str): Exercise ID
- `exercise_data` (CreateExerciseRequest): Updated exercise data

**Returns:** `Exercise` object

#### `async remove_program_exercise(program_id: str, exercise_id: str) -> MessageResponse`

Remove exercise from program.

```python
await client.programs.remove_program_exercise("program-id-123", "exercise-id-456")
```

**Parameters:**
- `program_id` (str): Program ID
- `exercise_id` (str): Exercise ID

#### `async duplicate_program(program_id: str, duplicate_data: Optional[DuplicateProgramRequest] = None) -> Program`

Duplicate an existing program.

```python
from carespace_sdk import DuplicateProgramRequest

duplicate_data = DuplicateProgramRequest(
    name="Advanced Knee Rehabilitation",
    description="Advanced version of the program",
    copy_exercises=True
)

duplicated_program = await client.programs.duplicate_program("program-id-123", duplicate_data)
```

**Parameters:**
- `program_id` (str): Program ID to duplicate
- `duplicate_data` (DuplicateProgramRequest, optional): Duplication options

**Returns:** `Program` object

#### `async get_program_templates(page: int = 1, limit: int = 20, search: Optional[str] = None, category: Optional[str] = None, difficulty: Optional[str] = None) -> ProgramsListResponse`

Get program templates.

```python
templates = await client.programs.get_program_templates(
    page=1,
    limit=10,
    category="rehabilitation"
)
```

**Parameters:**
- `page` (int): Page number
- `limit` (int): Items per page
- `search` (str, optional): Search term
- `category` (str, optional): Filter by category
- `difficulty` (str, optional): Filter by difficulty

**Returns:** `ProgramsListResponse`

## Data Models

### Authentication Models

#### `LoginRequest`
```python
class LoginRequest(BaseModel):
    email: str
    password: str
```

#### `LoginResponse`
```python
class LoginResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: str
    user_role: str
```

#### `RefreshTokenRequest`
```python
class RefreshTokenRequest(BaseModel):
    refresh_token: str
```

### User Models

#### `User`
```python
class User(BaseModel):
    id: str
    email: str
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime
    updated_at: datetime
```

#### `CreateUserRequest`
```python
class CreateUserRequest(BaseModel):
    email: str
    name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: str
    password: str
    is_active: bool = True
```

#### `UpdateUserRequest`
```python
class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None
```

#### `UsersListResponse`
```python
class UsersListResponse(PaginatedResponse):
    data: List[User]
```

### Client Models

#### `Address`
```python
class Address(BaseModel):
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"
```

#### `Client`
```python
class Client(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[Address] = None
    medical_history: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
```

#### `CreateClientRequest`
```python
class CreateClientRequest(BaseModel):
    name: str
    email: str
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[Address] = None
    medical_history: Optional[str] = None
    notes: Optional[str] = None
    is_active: bool = True
```

#### `UpdateClientRequest`
```python
class UpdateClientRequest(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    address: Optional[Address] = None
    medical_history: Optional[str] = None
    notes: Optional[str] = None
    is_active: Optional[bool] = None
```

#### `ClientStats`
```python
class ClientStats(BaseModel):
    total_sessions: int
    completed_exercises: int
    average_score: float
    last_session_date: Optional[datetime] = None
    total_program_time: int  # in minutes
    compliance_rate: float  # percentage
```

#### `ClientsListResponse`
```python
class ClientsListResponse(PaginatedResponse):
    data: List[Client]
```

### Program Models

#### `Exercise`
```python
class Exercise(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    duration: Optional[int] = None  # seconds
    repetitions: Optional[int] = None
    sets: Optional[int] = None
    rest_time: Optional[int] = None  # seconds
    order: int = 0
    created_at: datetime
    updated_at: datetime
```

#### `Program`
```python
class Program(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    duration: Optional[int] = None  # minutes
    is_template: bool = False
    exercises: List[Exercise] = []
    created_at: datetime
    updated_at: datetime
```

#### `CreateProgramRequest`
```python
class CreateProgramRequest(BaseModel):
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    duration: Optional[int] = None
    is_template: bool = False
```

#### `UpdateProgramRequest`
```python
class UpdateProgramRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None
    duration: Optional[int] = None
    is_template: Optional[bool] = None
```

#### `CreateExerciseRequest`
```python
class CreateExerciseRequest(BaseModel):
    name: str
    description: Optional[str] = None
    instructions: Optional[str] = None
    video_url: Optional[str] = None
    image_url: Optional[str] = None
    duration: Optional[int] = None
    repetitions: Optional[int] = None
    sets: Optional[int] = None
    rest_time: Optional[int] = None
    order: int = 0
```

#### `DuplicateProgramRequest`
```python
class DuplicateProgramRequest(BaseModel):
    name: str
    description: Optional[str] = None
    copy_exercises: bool = True
```

#### `ProgramsListResponse`
```python
class ProgramsListResponse(PaginatedResponse):
    data: List[Program]
```

#### `ExercisesListResponse`
```python
class ExercisesListResponse(PaginatedResponse):
    data: List[Exercise]
```

### Utility Models

#### `PaginationParams`
```python
class PaginationParams(BaseModel):
    page: int = 1
    limit: int = 20
```

#### `PaginatedResponse`
```python
class PaginatedResponse(BaseModel):
    total: int
    page: int
    limit: int
    pages: int
```

#### `MessageResponse`
```python
class MessageResponse(BaseModel):
    message: str
```

#### `SuccessResponse`
```python
class SuccessResponse(BaseModel):
    success: bool = True
    message: Optional[str] = None
```

## Exceptions

### Exception Hierarchy

All SDK exceptions inherit from `CarespaceError`.

#### `CarespaceError`
Base exception class for all Carespace SDK errors.

```python
class CarespaceError(Exception):
    def __init__(self, message: str, status_code: Optional[int] = None, response_data: Optional[dict] = None):
        self.message = message
        self.status_code = status_code
        self.response_data = response_data
```

**Attributes:**
- `message` (str): Error message
- `status_code` (int, optional): HTTP status code
- `response_data` (dict, optional): Response data from API

#### `AuthenticationError`
Raised when authentication fails (HTTP 401).

```python
try:
    await client.users.get_users()
except AuthenticationError as e:
    print(f"Authentication failed: {e.message}")
```

#### `ValidationError`
Raised when request validation fails (HTTP 400).

```python
try:
    await client.users.create_user(invalid_data)
except ValidationError as e:
    print(f"Validation error: {e.message}")
    print(f"Response data: {e.response_data}")
```

#### `NotFoundError`
Raised when a resource is not found (HTTP 404).

```python
try:
    user = await client.users.get_user("invalid-id")
except NotFoundError as e:
    print(f"User not found: {e.message}")
```

#### `RateLimitError`
Raised when rate limit is exceeded (HTTP 429).

```python
try:
    await client.users.get_users()
except RateLimitError as e:
    print(f"Rate limit exceeded: {e.message}")
    if e.retry_after:
        print(f"Retry after {e.retry_after} seconds")
```

**Additional Attributes:**
- `retry_after` (int, optional): Seconds to wait before retrying

#### `ServerError`
Raised for server-side errors (HTTP 5xx).

```python
try:
    await client.users.get_users()
except ServerError as e:
    print(f"Server error: {e.message}")
    print(f"Status code: {e.status_code}")
```

#### `NetworkError`
Raised for network connectivity issues.

```python
try:
    await client.users.get_users()
except NetworkError as e:
    print(f"Network error: {e.message}")
    if e.original_exception:
        print(f"Original error: {e.original_exception}")
```

**Additional Attributes:**
- `original_exception` (Exception, optional): Original network exception

#### `TimeoutError`
Raised when request times out.

```python
try:
    await client.users.get_users()
except TimeoutError as e:
    print(f"Request timed out: {e.message}")
    print(f"Timeout duration: {e.timeout_duration}s")
```

**Additional Attributes:**
- `timeout_duration` (float): Timeout duration in seconds

### Error Handling Best Practices

```python
from carespace_sdk import (
    CarespaceError,
    AuthenticationError,
    ValidationError,
    NotFoundError,
    RateLimitError,
    NetworkError,
    TimeoutError,
    ServerError
)

async def robust_api_call():
    try:
        return await client.users.get_user("user-id")
    except AuthenticationError:
        # Handle authentication - maybe refresh token
        pass
    except NotFoundError:
        # Handle missing resource
        pass
    except ValidationError as e:
        # Handle validation errors
        print(f"Validation failed: {e.response_data}")
    except RateLimitError as e:
        # Handle rate limiting
        if e.retry_after:
            await asyncio.sleep(e.retry_after)
            # Retry the request
    except (NetworkError, TimeoutError):
        # Handle connectivity issues
        # Implement retry logic
        pass
    except ServerError:
        # Handle server errors
        # Maybe retry or fallback
        pass
    except CarespaceError as e:
        # Handle any other API errors
        print(f"API error: {e.message}")
```