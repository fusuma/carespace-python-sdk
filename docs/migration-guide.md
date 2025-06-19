# Migration Guide - Carespace Python SDK

This guide helps you migrate to the Carespace Python SDK from other healthcare APIs, REST clients, or previous versions of Carespace integrations.

## Table of Contents

- [From REST/HTTP Libraries](#from-resthttp-libraries)
- [From Other Healthcare SDKs](#from-other-healthcare-sdks)
- [From Previous Carespace Integrations](#from-previous-carespace-integrations)
- [From Synchronous to Async](#from-synchronous-to-async)
- [Common Migration Patterns](#common-migration-patterns)
- [Breaking Changes by Version](#breaking-changes-by-version)

## From REST/HTTP Libraries

### From requests + manual JSON handling

If you're currently using `requests` or similar libraries to interact with the Carespace API:

#### Before (requests)
```python
import requests
import json

class CarespaceAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api.carespace.ai"
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})
    
    def get_users(self, page=1, limit=20):
        response = self.session.get(
            f"{self.base_url}/users",
            params={"page": page, "limit": limit}
        )
        response.raise_for_status()
        return response.json()
    
    def create_user(self, user_data):
        response = self.session.post(
            f"{self.base_url}/users",
            json=user_data
        )
        response.raise_for_status()
        return response.json()

# Usage
api = CarespaceAPI("your-api-key")
users = api.get_users(page=1, limit=50)
print(f"Found {users['total']} users")

new_user = api.create_user({
    "email": "user@example.com",
    "name": "John Doe",
    "role": "therapist"
})
```

#### After (Carespace SDK)
```python
import asyncio
from carespace_sdk import CarespaceClient, CreateUserRequest

async def main():
    async with CarespaceClient(api_key="your-api-key") as client:
        # Get users with type safety and pagination
        users = await client.users.get_users(page=1, limit=50)
        print(f"Found {users.total} users")
        
        # Create user with validated data model
        user_data = CreateUserRequest(
            email="user@example.com",
            name="John Doe",
            role="therapist",
            password="secure-password"
        )
        new_user = await client.users.create_user(user_data)
        print(f"Created user: {new_user.id}")

asyncio.run(main())
```

**Migration Benefits:**
- ✅ **Type Safety**: Pydantic models prevent runtime errors
- ✅ **Async Support**: Better performance and scalability
- ✅ **Error Handling**: Specific exceptions for different error types
- ✅ **Automatic Retries**: Built-in retry logic with exponential backoff
- ✅ **Resource Management**: Automatic connection cleanup

### From httpx

If you're already using httpx:

#### Before (httpx)
```python
import httpx
import asyncio

async def get_carespace_data():
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": "Bearer your-api-key"}
        
        # Get users
        response = await client.get(
            "https://api.carespace.ai/users",
            headers=headers,
            params={"page": 1, "limit": 20}
        )
        response.raise_for_status()
        users_data = response.json()
        
        # Manual error handling
        if response.status_code == 401:
            raise Exception("Authentication failed")
        elif response.status_code == 404:
            raise Exception("Not found")
        
        return users_data
```

#### After (Carespace SDK)
```python
from carespace_sdk import CarespaceClient, AuthenticationError, NotFoundError

async def get_carespace_data():
    try:
        async with CarespaceClient(api_key="your-api-key") as client:
            users = await client.users.get_users(page=1, limit=20)
            return users  # Typed UsersListResponse object
    except AuthenticationError:
        # Handle auth errors specifically
        print("Please check your API key")
    except NotFoundError:
        # Handle not found errors
        print("Resource not found")
```

## From Other Healthcare SDKs

### From Epic FHIR SDK

If you're migrating from Epic's FHIR SDK or similar healthcare APIs:

#### Epic FHIR Pattern
```python
from fhirclient import client
from fhirclient.models import patient

# Epic FHIR setup
settings = {
    'app_id': 'my_app',
    'api_base': 'https://fhir.epic.com/interconnect-fhir-oauth/',
}
smart = client.FHIRClient(settings=settings)

# Get patients
search = patient.Patient.where(struct={'name': 'John'})
patients = search.perform_resources(smart.server)
```

#### Carespace SDK Equivalent
```python
from carespace_sdk import CarespaceClient

async with CarespaceClient(api_key="your-api-key") as client:
    # Get clients (equivalent to patients)
    clients = await client.clients.get_clients(search="John")
    
    for client_record in clients.data:
        print(f"Client: {client_record.name} - {client_record.email}")
```

### From Cerner/Oracle Health SDK

#### Cerner Pattern
```python
# Cerner/Oracle Health typical pattern
import requests

class CernerAPI:
    def get_patients(self, name_filter=None):
        params = {}
        if name_filter:
            params['name'] = name_filter
            
        response = requests.get(
            f"{self.base_url}/Patient",
            headers=self.auth_headers,
            params=params
        )
        return response.json()
```

#### Carespace SDK Equivalent
```python
from carespace_sdk import CarespaceClient

async with CarespaceClient(api_key="your-api-key") as client:
    # More intuitive and type-safe
    clients = await client.clients.get_clients(search="John")
    
    # Access typed data
    for client_record in clients.data:
        print(f"Name: {client_record.name}")
        print(f"Email: {client_record.email}")
        print(f"DOB: {client_record.date_of_birth}")
```

## From Previous Carespace Integrations

### From V1 REST API (Hypothetical)

If you were using a previous version of Carespace API directly:

#### Before (V1 API)
```python
import requests

class CarespaceV1:
    def __init__(self, api_key):
        self.api_key = api_key
        self.base_url = "https://api-v1.carespace.ai"
    
    def login(self, username, password):
        response = requests.post(f"{self.base_url}/auth/login", json={
            "username": username,
            "password": password
        })
        return response.json()["token"]
    
    def get_patients(self, token):
        headers = {"X-Auth-Token": token}
        response = requests.get(f"{self.base_url}/patients", headers=headers)
        return response.json()
    
    def create_program(self, token, program_data):
        headers = {"X-Auth-Token": token}
        response = requests.post(
            f"{self.base_url}/programs", 
            headers=headers,
            json=program_data
        )
        return response.json()

# Usage
api = CarespaceV1("api-key")
token = api.login("user@example.com", "password")
patients = api.get_patients(token)
```

#### After (Current SDK)
```python
from carespace_sdk import CarespaceClient, CreateProgramRequest

async with CarespaceClient(api_key="your-api-key") as client:
    # Authentication is handled automatically
    login_response = await client.login_and_set_token("user@example.com", "password")
    
    # Get clients (renamed from patients for clarity)
    clients = await client.clients.get_clients()
    
    # Create program with validated data
    program_data = CreateProgramRequest(
        name="Rehabilitation Program",
        description="Post-surgery recovery",
        category="rehabilitation",
        difficulty="intermediate",
        duration=45
    )
    
    new_program = await client.programs.create_program(program_data)
```

**Key Changes:**
- 🔄 **Terminology**: "Patients" → "Clients" for broader healthcare use cases
- 🔑 **Authentication**: Simplified token management
- 📝 **Data Models**: Structured request/response objects
- 🏗️ **Architecture**: Organized into logical API modules (auth, users, clients, programs)

## From Synchronous to Async

### Converting Sync Code

If you're new to async/await in Python:

#### Synchronous Pattern
```python
def process_all_clients():
    # Synchronous, blocking operations
    client_api = CarespaceAPI()
    
    all_clients = client_api.get_clients()
    for client in all_clients:
        details = client_api.get_client_details(client.id)
        programs = client_api.get_client_programs(client.id)
        
        # Process data...
        print(f"Client {client.name} has {len(programs)} programs")

# Usage
process_all_clients()  # Blocks until complete
```

#### Async Pattern
```python
async def process_all_clients():
    # Asynchronous, non-blocking operations
    async with CarespaceClient(api_key="your-api-key") as client:
        
        all_clients = await client.clients.get_clients()
        
        # Process multiple clients concurrently
        tasks = []
        for client_record in all_clients.data:
            task = process_single_client(client, client_record.id)
            tasks.append(task)
        
        # Wait for all to complete
        results = await asyncio.gather(*tasks)
        
        for result in results:
            print(f"Processed: {result}")

async def process_single_client(client, client_id):
    # Concurrent operations for each client
    details, programs = await asyncio.gather(
        client.clients.get_client(client_id),
        client.clients.get_client_programs(client_id)
    )
    
    return f"Client {details.name} has {len(programs.data)} programs"

# Usage
import asyncio
asyncio.run(process_all_clients())  # Run async function
```

**Benefits of Async:**
- ⚡ **Performance**: Concurrent API calls
- 🔄 **Scalability**: Handle many operations simultaneously  
- 🚀 **Efficiency**: Non-blocking I/O operations

### Async Best Practices

1. **Use context managers**:
   ```python
   # ✅ Good
   async with CarespaceClient(api_key="key") as client:
       users = await client.users.get_users()
   
   # ❌ Avoid
   client = CarespaceClient(api_key="key")
   users = await client.users.get_users()
   await client.close()  # Easy to forget
   ```

2. **Batch operations with gather()**:
   ```python
   # ✅ Concurrent operations
   user, programs, clients = await asyncio.gather(
       client.users.get_user("user-123"),
       client.programs.get_programs(),
       client.clients.get_clients()
   )
   
   # ❌ Sequential operations
   user = await client.users.get_user("user-123")
   programs = await client.programs.get_programs()
   clients = await client.clients.get_clients()
   ```

3. **Handle exceptions properly**:
   ```python
   from carespace_sdk import CarespaceError
   
   try:
       users = await client.users.get_users()
   except CarespaceError as e:
       print(f"API error: {e.message}")
   ```

## Common Migration Patterns

### Pattern 1: Bulk Data Processing

#### Before (Synchronous)
```python
def sync_all_data():
    api = requests.Session()
    api.headers.update({"Authorization": "Bearer token"})
    
    # Sequential processing - slow
    all_users = []
    for page in range(1, 11):  # 10 pages
        response = api.get(f"/users?page={page}")
        users = response.json()
        all_users.extend(users['data'])
        
        # Process each user
        for user in users['data']:
            user_details = api.get(f"/users/{user['id']}")
            # More processing...
```

#### After (Async + Concurrent)
```python
async def async_all_data():
    async with CarespaceClient(api_key="token") as client:
        # Concurrent page fetching
        page_tasks = []
        for page in range(1, 11):
            task = client.users.get_users(page=page)
            page_tasks.append(task)
        
        page_results = await asyncio.gather(*page_tasks)
        
        # Flatten results
        all_users = []
        for result in page_results:
            all_users.extend(result.data)
        
        # Concurrent user processing
        user_tasks = []
        for user in all_users:
            task = process_user(client, user.id)
            user_tasks.append(task)
        
        await asyncio.gather(*user_tasks)

async def process_user(client, user_id):
    try:
        user_details = await client.users.get_user(user_id)
        # Process user...
    except Exception as e:
        print(f"Error processing user {user_id}: {e}")
```

### Pattern 2: Error Handling Migration

#### Before (Basic error handling)
```python
def create_users(user_list):
    created = []
    failed = []
    
    for user_data in user_list:
        try:
            response = requests.post("/users", json=user_data)
            if response.status_code == 201:
                created.append(response.json())
            else:
                failed.append({"data": user_data, "error": response.text})
        except Exception as e:
            failed.append({"data": user_data, "error": str(e)})
    
    return created, failed
```

#### After (Structured error handling)
```python
from carespace_sdk import (
    ValidationError, 
    AuthenticationError, 
    NotFoundError,
    CreateUserRequest
)

async def create_users(user_list):
    created = []
    failed = []
    
    async with CarespaceClient(api_key="key") as client:
        for user_data in user_list:
            try:
                # Use typed request model
                request = CreateUserRequest(**user_data)
                user = await client.users.create_user(request)
                created.append(user)
                
            except ValidationError as e:
                # Handle validation errors specifically
                failed.append({
                    "data": user_data, 
                    "error": "validation_error",
                    "details": e.response_data
                })
            except AuthenticationError:
                # Handle auth errors - maybe refresh token
                print("Authentication failed - refreshing token")
                break  # Stop processing
            except Exception as e:
                failed.append({
                    "data": user_data, 
                    "error": "unknown_error",
                    "details": str(e)
                })
    
    return created, failed
```

### Pattern 3: Configuration Migration

#### Before (Manual configuration)
```python
import os

class Config:
    API_BASE_URL = os.getenv("CARESPACE_URL", "https://api.carespace.ai")
    API_KEY = os.getenv("CARESPACE_API_KEY")
    TIMEOUT = int(os.getenv("TIMEOUT", "30"))
    
    @classmethod
    def get_headers(cls):
        return {
            "Authorization": f"Bearer {cls.API_KEY}",
            "Content-Type": "application/json"
        }
```

#### After (SDK configuration)
```python
import os
from carespace_sdk import CarespaceClient, create_production_client

# Method 1: Direct configuration
client = CarespaceClient(
    base_url=os.getenv("CARESPACE_URL", "https://api.carespace.ai"),
    api_key=os.getenv("CARESPACE_API_KEY"),
    timeout=float(os.getenv("CARESPACE_TIMEOUT", "30.0"))
)

# Method 2: Environment-specific factory
production_client = create_production_client(
    api_key=os.getenv("CARESPACE_PROD_API_KEY")
)

# Method 3: Custom configuration class
@dataclass
class CarespaceConfig:
    api_key: str
    base_url: str = "https://api.carespace.ai"
    timeout: float = 30.0
    
    @classmethod
    def from_env(cls):
        return cls(
            api_key=os.getenv("CARESPACE_API_KEY"),
            base_url=os.getenv("CARESPACE_URL", cls.base_url),
            timeout=float(os.getenv("CARESPACE_TIMEOUT", cls.timeout))
        )

# Usage
config = CarespaceConfig.from_env()
client = CarespaceClient(**config.__dict__)
```

## Breaking Changes by Version

### Version 1.0.0 (Initial Release)

**New Features:**
- ✅ Full async/await support
- ✅ Type-safe Pydantic models
- ✅ Comprehensive error handling
- ✅ Automatic retry logic
- ✅ Context manager support

**Migration Required:**
- 🔄 All API calls must be awaited
- 🔄 Use typed request/response models
- 🔄 Update error handling to use specific exceptions

### Future Version Compatibility

When upgrading between versions:

1. **Check CHANGELOG.md** for breaking changes
2. **Run tests** after upgrading
3. **Update type hints** if model signatures change
4. **Review deprecation warnings** in your IDE

### Deprecation Policy

- **Minor versions**: New features, deprecation warnings
- **Major versions**: Remove deprecated features
- **Patch versions**: Bug fixes only

## Migration Checklist

Use this checklist when migrating to the Carespace Python SDK:

### Pre-Migration
- [ ] Review current API usage patterns
- [ ] Identify all API endpoints currently used
- [ ] Document current error handling approach
- [ ] Set up development environment with SDK

### During Migration
- [ ] Install Carespace Python SDK
- [ ] Convert synchronous calls to async/await
- [ ] Replace manual JSON with typed models
- [ ] Update error handling to use SDK exceptions
- [ ] Add proper resource management (context managers)
- [ ] Update configuration management

### Post-Migration
- [ ] Run comprehensive tests
- [ ] Verify all API calls work correctly
- [ ] Check error handling scenarios
- [ ] Performance test async operations
- [ ] Update documentation
- [ ] Train team on new patterns

### Testing Migration
```python
# Create parallel implementation for testing
async def test_migration_equivalence():
    """Test that old and new implementations give same results."""
    
    # Old implementation result
    old_api = OldCarespaceAPI()
    old_users = old_api.get_users(page=1, limit=10)
    
    # New implementation result
    async with CarespaceClient(api_key="test-key") as client:
        new_users = await client.users.get_users(page=1, limit=10)
    
    # Compare results
    assert len(old_users['data']) == len(new_users.data)
    for old_user, new_user in zip(old_users['data'], new_users.data):
        assert old_user['id'] == new_user.id
        assert old_user['email'] == new_user.email
```

## Getting Help

If you encounter issues during migration:

1. **Check the documentation**: API reference and usage guide
2. **Search existing issues**: GitHub issues for similar problems
3. **Create detailed issue**: Include code samples and error messages
4. **Join discussions**: GitHub Discussions for general questions

## Next Steps

After successful migration:

1. **Explore advanced features**: Bulk operations, health monitoring
2. **Optimize for performance**: Use concurrent operations where appropriate
3. **Add comprehensive testing**: Unit and integration tests
4. **Set up monitoring**: Error tracking and performance monitoring
5. **Consider data science integration**: Pandas integration for analytics

The Carespace Python SDK provides a modern, type-safe, and efficient way to interact with healthcare data. The migration effort will result in more maintainable, reliable, and performant code.