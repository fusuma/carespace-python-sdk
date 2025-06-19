# Carespace Python SDK Documentation

Welcome to the Carespace Python SDK documentation! This directory contains comprehensive guides and references for using the SDK effectively.

## Documentation Structure

### Core Documentation
- **[API Reference](api-reference.md)** - Complete API documentation with all classes, methods, and models
- **[Usage Guide](usage-guide.md)** - Comprehensive examples and practical patterns for common use cases
- **[Contributing Guide](contributing.md)** - Development setup, code standards, and contribution guidelines
- **[Migration Guide](migration-guide.md)** - Migrate from other SDKs or previous versions

### Quick Navigation

#### Getting Started
- [Installation](../README.md#installation)
- [Quick Start](../README.md#quick-start)
- [Authentication](usage-guide.md#authentication)

#### API Documentation
- [Client Class](api-reference.md#client)
- [Authentication API](api-reference.md#authentication-api)
- [Users API](api-reference.md#users-api)
- [Clients API](api-reference.md#clients-api)
- [Programs API](api-reference.md#programs-api)
- [Data Models](api-reference.md#data-models)
- [Exceptions](api-reference.md#exceptions)

#### Advanced Topics
- [Error Handling](usage-guide.md#error-handling)
- [Data Science Integration](usage-guide.md#data-science-integration)
- [Testing](usage-guide.md#testing)
- [Best Practices](usage-guide.md#best-practices)

#### Development
- [Development Setup](contributing.md#development-setup)
- [Code Standards](contributing.md#code-standards)
- [Testing Guidelines](contributing.md#testing)
- [Release Process](contributing.md#release-process)

## Documentation Principles

Our documentation follows these principles:

### 1. **Example-Driven**
Every feature is demonstrated with practical, copy-pasteable code examples.

### 2. **Progressive Complexity**
Documentation starts with simple examples and gradually introduces advanced concepts.

### 3. **Type-Safe**
All examples include proper type hints and demonstrate type-safe patterns.

### 4. **Error-Aware**
Examples include proper error handling and demonstrate common error scenarios.

### 5. **Real-World Focused**
Examples reflect actual healthcare workflow patterns and use cases.

## Quick Reference Cards

### Authentication
```python
# Login and auto-set token
async with CarespaceClient() as client:
    await client.login_and_set_token("user@example.com", "password")
    users = await client.users.get_users()

# Direct API key
async with CarespaceClient(api_key="your-key") as client:
    users = await client.users.get_users()
```

### CRUD Operations
```python
async with CarespaceClient(api_key="your-key") as client:
    # Create
    user = await client.users.create_user(CreateUserRequest(...))
    
    # Read
    user = await client.users.get_user("user-id")
    users = await client.users.get_users(page=1, limit=20)
    
    # Update
    user = await client.users.update_user("user-id", UpdateUserRequest(...))
    
    # Delete
    await client.users.delete_user("user-id")
```

### Error Handling
```python
from carespace_sdk import AuthenticationError, ValidationError, NotFoundError

try:
    user = await client.users.get_user("user-id")
except AuthenticationError:
    # Handle auth issues
    pass
except NotFoundError:
    # Handle missing resources
    pass
except ValidationError as e:
    # Handle validation errors
    print(f"Validation failed: {e.response_data}")
```

### Pagination
```python
# Manual pagination
page = 1
while True:
    response = await client.users.get_users(page=page, limit=50)
    process_users(response.data)
    
    if page >= response.pages:
        break
    page += 1

# Collect all pages
all_users = []
page = 1
while True:
    response = await client.users.get_users(page=page, limit=100)
    all_users.extend(response.data)
    if page >= response.pages:
        break
    page += 1
```

## Code Examples by Use Case

### Healthcare Practice Management
```python
# Patient intake workflow
async def patient_intake(patient_data):
    async with CarespaceClient(api_key="your-key") as client:
        # Create client record
        client_record = await client.clients.create_client(patient_data)
        
        # Assign initial assessment program
        await client.clients.assign_program_to_client(
            client_id=client_record.id,
            program_id="initial-assessment",
            start_date="2024-01-01",
            end_date="2024-01-15"
        )
        
        return client_record
```

### Rehabilitation Program Management
```python
# Create comprehensive rehab program
async def create_rehab_program():
    async with CarespaceClient(api_key="your-key") as client:
        # Create program
        program = await client.programs.create_program(CreateProgramRequest(
            name="Post-Surgery Knee Rehabilitation",
            category="rehabilitation",
            difficulty="intermediate",
            duration=45
        ))
        
        # Add exercises
        exercises = [
            CreateExerciseRequest(name="Range of Motion", duration=300, ...),
            CreateExerciseRequest(name="Strength Training", duration=600, ...),
            CreateExerciseRequest(name="Balance Training", duration=240, ...)
        ]
        
        for exercise_data in exercises:
            await client.programs.add_exercise_to_program(program.id, exercise_data)
        
        return program
```

### Analytics and Reporting
```python
# Generate practice analytics
async def generate_practice_report():
    async with CarespaceClient(api_key="your-key") as client:
        # Gather data
        users_response = await client.users.get_users(limit=1000)
        clients_response = await client.clients.get_clients(limit=1000) 
        programs_response = await client.programs.get_programs(limit=1000)
        
        # Generate insights
        report = {
            "total_staff": len(users_response.data),
            "total_patients": len(clients_response.data),
            "active_programs": sum(1 for p in programs_response.data if not p.is_template),
            "program_templates": sum(1 for p in programs_response.data if p.is_template)
        }
        
        return report
```

## Integration Patterns

### With FastAPI
```python
from fastapi import FastAPI, HTTPException, Depends
from carespace_sdk import CarespaceClient, NotFoundError

app = FastAPI()

async def get_carespace_client():
    async with CarespaceClient(api_key="your-key") as client:
        yield client

@app.get("/users/{user_id}")
async def get_user(user_id: str, client: CarespaceClient = Depends(get_carespace_client)):
    try:
        user = await client.users.get_user(user_id)
        return user
    except NotFoundError:
        raise HTTPException(status_code=404, detail="User not found")
```

### With Django
```python
from django.http import JsonResponse
from carespace_sdk import CarespaceClient
import asyncio

async def get_user_data(request, user_id):
    async with CarespaceClient(api_key=settings.CARESPACE_API_KEY) as client:
        try:
            user = await client.users.get_user(user_id)
            return JsonResponse(user.dict())
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

def user_view(request, user_id):
    return asyncio.run(get_user_data(request, user_id))
```

### With Pandas/Jupyter
```python
import pandas as pd
import matplotlib.pyplot as plt
from carespace_sdk import CarespaceClient

# Data analysis in Jupyter notebook
async def analyze_client_data():
    async with CarespaceClient(api_key="your-key") as client:
        # Get data
        clients = await client.clients.get_clients(limit=1000)
        
        # Convert to DataFrame
        df = pd.DataFrame([c.dict() for c in clients.data])
        
        # Visualize
        df['gender'].value_counts().plot(kind='bar')
        plt.title('Client Gender Distribution')
        plt.show()
        
        return df

# Run in Jupyter
df = await analyze_client_data()
```

## Troubleshooting Guide

### Common Issues

1. **Authentication Errors**
   - Check API key validity
   - Verify token expiration
   - Ensure proper environment configuration

2. **Timeout Issues**
   - Increase timeout settings
   - Check network connectivity
   - Consider pagination for large datasets

3. **Rate Limiting**
   - Implement exponential backoff
   - Use batch operations when possible
   - Monitor rate limit headers

4. **Type Errors**
   - Ensure proper model instantiation
   - Check field requirements
   - Validate data before API calls

### Debug Mode
```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

async with CarespaceClient(api_key="your-key") as client:
    # HTTP requests will be logged
    users = await client.users.get_users()
```

## Support and Community

- **Issues**: [GitHub Issues](https://github.com/carespace/python-sdk/issues)
- **Discussions**: [GitHub Discussions](https://github.com/carespace/python-sdk/discussions)
- **Email**: [support@carespace.ai](mailto:support@carespace.ai)
- **Documentation**: [docs.carespace.ai](https://docs.carespace.ai)

## Contributing to Documentation

We welcome improvements to our documentation! Please see our [Contributing Guide](contributing.md) for details on:

- Writing style guidelines
- Documentation structure
- Example requirements
- Review process

---

**Happy coding with the Carespace Python SDK!** 🏥✨