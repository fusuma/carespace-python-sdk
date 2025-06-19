# Carespace Python SDK - Usage Guide

A comprehensive guide to using the Carespace Python SDK with practical examples and best practices.

## Table of Contents

- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [User Management](#user-management)
- [Client Management](#client-management)
- [Program Management](#program-management)
- [Error Handling](#error-handling)
- [Advanced Usage](#advanced-usage)
- [Data Science Integration](#data-science-integration)
- [Testing](#testing)
- [Best Practices](#best-practices)

## Getting Started

### Installation

```bash
pip install carespace-sdk
```

### Basic Setup

```python
import asyncio
from carespace_sdk import CarespaceClient

async def main():
    # Create client with API key
    async with CarespaceClient(api_key="your-api-key") as client:
        # Check API health
        is_healthy = await client.health_check()
        if is_healthy:
            print("✅ Connected to Carespace API")
        else:
            print("❌ API connection failed")

asyncio.run(main())
```

### Environment-Specific Clients

```python
from carespace_sdk import create_production_client, create_development_client

# Production environment
async with create_production_client("your-prod-api-key") as client:
    users = await client.users.get_users()

# Development environment
async with create_development_client("your-dev-api-key") as client:
    users = await client.users.get_users()
```

## Authentication

### Login and Token Management

The SDK provides multiple ways to handle authentication:

#### Option 1: Login and Auto-Set Token

```python
async with CarespaceClient() as client:
    # Login and automatically set the access token
    login_response = await client.login_and_set_token("user@example.com", "password")
    print(f"Logged in! Token expires in {login_response.expires_in} seconds")
    
    # Now you can make authenticated requests
    users = await client.users.get_users()
```

#### Option 2: Manual Token Management

```python
async with CarespaceClient() as client:
    # Step 1: Login to get tokens
    login_response = await client.auth.login("user@example.com", "password")
    
    # Step 2: Set the access token
    client.set_api_key(login_response.access_token)
    
    # Step 3: Make authenticated requests
    users = await client.users.get_users()
    
    # Step 4: Refresh token when needed
    if is_token_expired(login_response.expires_in):
        new_tokens = await client.auth.refresh_token(login_response.refresh_token)
        client.set_api_key(new_tokens.access_token)
```

#### Option 3: Direct API Key

```python
# If you already have an API key
async with CarespaceClient(api_key="your-long-lived-api-key") as client:
    users = await client.users.get_users()
```

### Password Management

```python
async def handle_password_operations():
    async with CarespaceClient() as client:
        # Forgot password - sends reset email
        await client.auth.forgot_password("user@example.com")
        print("Password reset email sent")
        
        # Reset password with token from email
        await client.auth.reset_password("reset-token-from-email", "new-secure-password")
        print("Password reset successful")
        
        # Change password (requires authentication)
        await client.auth.change_password("current-password", "new-password")
        print("Password changed successfully")
```

### Email Verification

```python
async def handle_email_verification():
    async with CarespaceClient() as client:
        # Verify email with token
        await client.auth.verify_email("verification-token-from-email")
        print("Email verified")
        
        # Resend verification email
        await client.auth.resend_verification("user@example.com")
        print("Verification email resent")
```

## User Management

### Creating and Managing Users

```python
from carespace_sdk import CreateUserRequest, UpdateUserRequest

async def user_management_example():
    async with CarespaceClient(api_key="your-api-key") as client:
        # Create a new user
        user_data = CreateUserRequest(
            email="newtherapist@clinic.com",
            name="Dr. Sarah Johnson",
            first_name="Sarah",
            last_name="Johnson",
            role="therapist",
            password="secure-password-123"
        )
        
        new_user = await client.users.create_user(user_data)
        print(f"Created user: {new_user.id} - {new_user.name}")
        
        # Update user information
        update_data = UpdateUserRequest(
            name="Dr. Sarah Johnson-Smith",
            is_active=True
        )
        
        updated_user = await client.users.update_user(new_user.id, update_data)
        print(f"Updated user: {updated_user.name}")
        
        # Get user details
        user_details = await client.users.get_user(new_user.id)
        print(f"User role: {user_details.role}")
        print(f"User created: {user_details.created_at}")
        print(f"User verified: {user_details.is_verified}")
```

### User Listing and Search

```python
async def search_users_example():
    async with CarespaceClient(api_key="your-api-key") as client:
        # Get all users with pagination
        all_users = await client.users.get_users(
            page=1,
            limit=50,
            search="doctor",  # Search for users with "doctor" in name/email
            sort_by="created_at",
            sort_order="desc"
        )
        
        print(f"Found {len(all_users.data)} users out of {all_users.total} total")
        print(f"Page {all_users.page} of {all_users.pages}")
        
        for user in all_users.data:
            print(f"👤 {user.name} ({user.email}) - {user.role}")
            print(f"   Created: {user.created_at.strftime('%Y-%m-%d')}")
            print(f"   Active: {'✅' if user.is_active else '❌'}")
            print(f"   Verified: {'✅' if user.is_verified else '❌'}")
```

### Profile Management

```python
async def profile_management_example():
    async with CarespaceClient(api_key="your-api-key") as client:
        # Login first
        await client.login_and_set_token("user@example.com", "password")
        
        # Get current user profile
        profile = await client.users.get_user_profile()
        print(f"Current user: {profile.name}")
        print(f"Role: {profile.role}")
        
        # Update profile
        profile_update = UpdateUserRequest(
            name="Updated Display Name",
            first_name="Updated",
            last_name="Name"
        )
        
        updated_profile = await client.users.update_user_profile(profile_update)
        print(f"Profile updated: {updated_profile.name}")
        
        # Manage user settings
        user_settings = await client.users.get_user_settings(profile.id)
        print(f"Current settings: {user_settings}")
        
        new_settings = {
            "notifications": True,
            "theme": "dark",
            "language": "en",
            "timezone": "UTC"
        }
        
        updated_settings = await client.users.update_user_settings(profile.id, new_settings)
        print(f"Settings updated: {updated_settings}")
```

## Client Management

### Creating and Managing Clients

```python
from carespace_sdk import CreateClientRequest, UpdateClientRequest, Address
from datetime import datetime

async def client_management_example():
    async with CarespaceClient(api_key="your-api-key") as client:
        # Create a complete client record
        client_address = Address(
            street="123 Healthcare Avenue",
            city="Medical City",
            state="CA",
            zip_code="90210",
            country="USA"
        )
        
        client_data = CreateClientRequest(
            name="John Smith",
            email="john.smith@email.com",
            phone="+1-555-0123",
            date_of_birth=datetime(1980, 5, 15),
            gender="male",
            address=client_address,
            medical_history="Previous ACL surgery in 2018, no current medications",
            notes="Prefers morning appointments, responds well to positive reinforcement"
        )
        
        new_client = await client.clients.create_client(client_data)
        print(f"Created client: {new_client.id} - {new_client.name}")
        
        # Update client information
        update_data = UpdateClientRequest(
            phone="+1-555-0199",  # Updated phone number
            notes="Updated notes: Now prefers afternoon appointments",
            medical_history="Previous ACL surgery in 2018, currently taking vitamin D supplements"
        )
        
        updated_client = await client.clients.update_client(new_client.id, update_data)
        print(f"Updated client: {updated_client.name}")
```

### Client Search and Analytics

```python
async def client_analytics_example():
    async with CarespaceClient(api_key="your-api-key") as client:
        # Search for clients
        clients_response = await client.clients.get_clients(
            page=1,
            limit=25,
            search="john",  # Search by name or email
            sort_by="name",
            sort_order="asc"
        )
        
        print(f"Found {len(clients_response.data)} clients")
        
        for client_record in clients_response.data:
            print(f"👤 {client_record.name}")
            print(f"   📧 {client_record.email}")
            print(f"   📞 {client_record.phone or 'No phone'}")
            print(f"   🎂 {client_record.date_of_birth.strftime('%Y-%m-%d') if client_record.date_of_birth else 'No DOB'}")
            
            # Get detailed statistics for each client
            stats = await client.clients.get_client_stats(client_record.id)
            print(f"   📊 Stats:")
            print(f"      Sessions: {stats.total_sessions}")
            print(f"      Exercises: {stats.completed_exercises}")
            print(f"      Avg Score: {stats.average_score:.1f}")
            print(f"      Compliance: {stats.compliance_rate:.1f}%")
            print(f"      Last Session: {stats.last_session_date or 'Never'}")
            print()
```

### Client Program Management

```python
async def client_program_management():
    async with CarespaceClient(api_key="your-api-key") as client:
        client_id = "client-123"
        program_id = "program-456"
        
        # Get programs assigned to client
        assigned_programs = await client.clients.get_client_programs(
            client_id,
            page=1,
            limit=10
        )
        
        print(f"Client has {len(assigned_programs.data)} assigned programs:")
        for program in assigned_programs.data:
            print(f"📋 {program.name} - {program.category}")
        
        # Assign a new program to client
        await client.clients.assign_program_to_client(
            client_id=client_id,
            program_id=program_id,
            start_date="2024-01-15",
            end_date="2024-04-15",
            notes="Post-injury rehabilitation program - focus on range of motion"
        )
        print("Program assigned successfully")
        
        # Remove program assignment
        await client.clients.remove_client_program(client_id, program_id)
        print("Program assignment removed")
```

## Program Management

### Creating and Managing Programs

```python
from carespace_sdk import CreateProgramRequest, UpdateProgramRequest, CreateExerciseRequest

async def program_management_example():
    async with CarespaceClient(api_key="your-api-key") as client:
        # Create a new rehabilitation program
        program_data = CreateProgramRequest(
            name="Post-Surgery Knee Rehabilitation",
            description="Comprehensive 12-week rehabilitation program for post-surgical knee recovery",
            category="rehabilitation",
            difficulty="intermediate",
            duration=45,  # 45 minutes per session
            is_template=False
        )
        
        new_program = await client.programs.create_program(program_data)
        print(f"Created program: {new_program.id} - {new_program.name}")
        
        # Add exercises to the program
        exercises = [
            CreateExerciseRequest(
                name="Gentle Knee Flexion",
                description="Passive knee bending to improve range of motion",
                instructions="Lie on your back, slowly bend knee to comfortable position, hold for 5 seconds",
                video_url="https://example.com/videos/knee-flexion.mp4",
                duration=120,  # 2 minutes
                repetitions=10,
                sets=2,
                rest_time=30,
                order=1
            ),
            CreateExerciseRequest(
                name="Quad Sets",
                description="Isometric quadriceps strengthening",
                instructions="Tighten thigh muscle, press knee down into surface, hold for 5 seconds",
                duration=90,
                repetitions=15,
                sets=3,
                rest_time=45,
                order=2
            ),
            CreateExerciseRequest(
                name="Ankle Pumps",
                description="Improve circulation and prevent stiffness",
                instructions="Point toes up toward shin, then point down, repeat rhythmically",
                duration=60,
                repetitions=20,
                sets=2,
                rest_time=15,
                order=3
            )
        ]
        
        # Add each exercise to the program
        for exercise_data in exercises:
            exercise = await client.programs.add_exercise_to_program(new_program.id, exercise_data)
            print(f"Added exercise: {exercise.name}")
        
        # Update program details
        update_data = UpdateProgramRequest(
            description="Comprehensive 12-week rehabilitation program for post-surgical knee recovery - Updated with latest protocols",
            duration=50  # Increased to 50 minutes
        )
        
        updated_program = await client.programs.update_program(new_program.id, update_data)
        print(f"Updated program duration to {updated_program.duration} minutes")
```

### Program Search and Templates

```python
async def program_search_example():
    async with CarespaceClient(api_key="your-api-key") as client:
        # Search for programs with filtering
        programs_response = await client.programs.get_programs(
            page=1,
            limit=20,
            search="knee",
            category="rehabilitation",
            difficulty="beginner",
            sort_by="name"
        )
        
        print(f"Found {len(programs_response.data)} rehabilitation programs:")
        
        for program in programs_response.data:
            print(f"📋 {program.name}")
            print(f"   Category: {program.category}")
            print(f"   Difficulty: {program.difficulty}")
            print(f"   Duration: {program.duration} minutes")
            print(f"   Exercises: {len(program.exercises)}")
            print(f"   Template: {'Yes' if program.is_template else 'No'}")
            print()
        
        # Get program templates specifically
        templates = await client.programs.get_program_templates(
            page=1,
            limit=10,
            category="rehabilitation",
            difficulty="intermediate"
        )
        
        print(f"Available templates: {len(templates.data)}")
        for template in templates.data:
            print(f"📋 Template: {template.name}")
```

### Exercise Management

```python
async def exercise_management_example():
    async with CarespaceClient(api_key="your-api-key") as client:
        program_id = "program-123"
        
        # Get all exercises in a program
        exercises_response = await client.programs.get_program_exercises(
            program_id,
            page=1,
            limit=50
        )
        
        print(f"Program has {len(exercises_response.data)} exercises:")
        
        for exercise in exercises_response.data:
            print(f"🏃 {exercise.name}")
            print(f"   Order: {exercise.order}")
            print(f"   Duration: {exercise.duration}s")
            print(f"   Reps: {exercise.repetitions}, Sets: {exercise.sets}")
            print(f"   Rest: {exercise.rest_time}s")
            print(f"   Instructions: {exercise.instructions[:100]}...")
            print()
        
        # Update an exercise
        if exercises_response.data:
            first_exercise = exercises_response.data[0]
            updated_exercise_data = CreateExerciseRequest(
                name=first_exercise.name,
                description=first_exercise.description,
                instructions=f"{first_exercise.instructions} - Updated with additional safety notes",
                video_url=first_exercise.video_url,
                duration=first_exercise.duration,
                repetitions=first_exercise.repetitions + 2,  # Increase reps
                sets=first_exercise.sets,
                rest_time=first_exercise.rest_time,
                order=first_exercise.order
            )
            
            updated_exercise = await client.programs.update_program_exercise(
                program_id,
                first_exercise.id,
                updated_exercise_data
            )
            print(f"Updated exercise: {updated_exercise.name}")
```

### Program Duplication

```python
from carespace_sdk import DuplicateProgramRequest

async def program_duplication_example():
    async with CarespaceClient(api_key="your-api-key") as client:
        original_program_id = "program-123"
        
        # Simple duplication
        duplicate_data = DuplicateProgramRequest(
            name="Advanced Knee Rehabilitation",
            description="Advanced version of the knee rehabilitation program",
            copy_exercises=True
        )
        
        duplicated_program = await client.programs.duplicate_program(
            original_program_id,
            duplicate_data
        )
        
        print(f"Duplicated program: {duplicated_program.name}")
        print(f"New program ID: {duplicated_program.id}")
        print(f"Exercises copied: {len(duplicated_program.exercises)}")
        
        # Now customize the duplicated program
        update_data = UpdateProgramRequest(
            difficulty="advanced",
            duration=60  # Longer sessions for advanced program
        )
        
        customized_program = await client.programs.update_program(
            duplicated_program.id,
            update_data
        )
        print(f"Customized duplicate: {customized_program.difficulty} difficulty")
```

## Error Handling

### Comprehensive Error Handling

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
import asyncio

async def robust_api_operations():
    async with CarespaceClient(api_key="your-api-key") as client:
        try:
            # Attempt to get a user
            user = await client.users.get_user("user-123")
            print(f"Retrieved user: {user.name}")
            
        except AuthenticationError as e:
            print(f"🔐 Authentication failed: {e.message}")
            # Try to refresh token or redirect to login
            
        except NotFoundError as e:
            print(f"🔍 Resource not found: {e.message}")
            # Handle missing resource gracefully
            
        except ValidationError as e:
            print(f"❌ Validation error: {e.message}")
            if e.response_data:
                print(f"Details: {e.response_data}")
            # Fix the data and retry
            
        except RateLimitError as e:
            print(f"⏱️ Rate limit exceeded: {e.message}")
            if e.retry_after:
                print(f"Waiting {e.retry_after} seconds before retry...")
                await asyncio.sleep(e.retry_after)
                # Retry the operation
            
        except NetworkError as e:
            print(f"🌐 Network error: {e.message}")
            if e.original_exception:
                print(f"Original error: {e.original_exception}")
            # Implement retry logic with exponential backoff
            
        except TimeoutError as e:
            print(f"⏰ Request timed out: {e.message}")
            print(f"Timeout was: {e.timeout_duration}s")
            # Maybe increase timeout and retry
            
        except ServerError as e:
            print(f"🔥 Server error: {e.message}")
            print(f"Status code: {e.status_code}")
            # Log the error and maybe retry later
            
        except CarespaceError as e:
            print(f"🚨 Generic API error: {e.message}")
            print(f"Status code: {e.status_code}")
            if e.response_data:
                print(f"Response: {e.response_data}")
```

### Retry Logic Implementation

```python
import asyncio
import random

async def retry_with_exponential_backoff(operation, max_retries=3, base_delay=1):
    """
    Retry an async operation with exponential backoff.
    """
    for attempt in range(max_retries):
        try:
            return await operation()
        except (NetworkError, TimeoutError, ServerError) as e:
            if attempt == max_retries - 1:
                # Last attempt, re-raise the exception
                raise
            
            # Calculate delay with jitter
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Attempt {attempt + 1} failed: {e.message}")
            print(f"Retrying in {delay:.2f} seconds...")
            await asyncio.sleep(delay)
        except (AuthenticationError, ValidationError, NotFoundError):
            # Don't retry these errors
            raise

# Usage example
async def robust_get_users():
    async with CarespaceClient(api_key="your-api-key") as client:
        async def get_users_operation():
            return await client.users.get_users(limit=50)
        
        try:
            users = await retry_with_exponential_backoff(get_users_operation)
            return users
        except Exception as e:
            print(f"All retry attempts failed: {e}")
            return None
```

## Advanced Usage

### Custom HTTP Client Configuration

```python
import httpx
from carespace_sdk import CarespaceClient

async def custom_http_client_example():
    # Create custom HTTP client with specific settings
    custom_http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(
            connect=10.0,  # Connection timeout
            read=60.0,     # Read timeout
            write=30.0,    # Write timeout
            pool=120.0     # Pool timeout
        ),
        limits=httpx.Limits(
            max_keepalive_connections=20,
            max_connections=100
        ),
        headers={
            "User-Agent": "MyHealthcareApp/1.0.0",
            "X-Custom-Header": "custom-value"
        },
        follow_redirects=True
    )
    
    # Pass custom client to Carespace client
    client = CarespaceClient(
        api_key="your-api-key",
        base_url="https://api.carespace.ai",
        httpx_client=custom_http_client
    )
    
    async with client:
        users = await client.users.get_users()
        print(f"Retrieved {len(users.data)} users with custom HTTP client")
```

### Connection Pooling and Resource Management

```python
class CarespaceService:
    """
    Service class for managing Carespace API interactions with proper resource management.
    """
    
    def __init__(self, api_key: str, base_url: str = None):
        self.api_key = api_key
        self.base_url = base_url or "https://api-dev.carespace.ai"
        self.client = None
    
    async def __aenter__(self):
        self.client = CarespaceClient(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=60.0,
            max_retries=5
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.close()
    
    async def get_user_summary(self, user_id: str) -> dict:
        """Get comprehensive user summary with error handling."""
        try:
            user = await self.client.users.get_user(user_id)
            settings = await self.client.users.get_user_settings(user_id)
            
            return {
                "user": user,
                "settings": settings,
                "summary": f"{user.name} ({user.role}) - Active: {user.is_active}"
            }
        except NotFoundError:
            return {"error": "User not found"}
        except Exception as e:
            return {"error": f"Failed to get user summary: {e}"}
    
    async def bulk_create_users(self, users_data: list) -> dict:
        """Create multiple users with progress tracking."""
        results = {"created": [], "failed": []}
        
        for i, user_data in enumerate(users_data):
            try:
                user = await self.client.users.create_user(user_data)
                results["created"].append(user)
                print(f"Created user {i+1}/{len(users_data)}: {user.name}")
            except Exception as e:
                results["failed"].append({"data": user_data, "error": str(e)})
                print(f"Failed to create user {i+1}: {e}")
        
        return results

# Usage
async def service_example():
    async with CarespaceService("your-api-key") as service:
        # Get user summary
        summary = await service.get_user_summary("user-123")
        print(summary)
        
        # Bulk create users
        users_to_create = [
            CreateUserRequest(email="user1@example.com", name="User 1", role="patient"),
            CreateUserRequest(email="user2@example.com", name="User 2", role="therapist"),
        ]
        
        results = await service.bulk_create_users(users_to_create)
        print(f"Created: {len(results['created'])}, Failed: {len(results['failed'])}")
```

### Health Monitoring and Circuit Breaker

```python
import asyncio
from datetime import datetime, timedelta

class HealthMonitor:
    """
    Monitor API health and implement circuit breaker pattern.
    """
    
    def __init__(self, client: CarespaceClient, failure_threshold=5, recovery_timeout=300):
        self.client = client
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failures = 0
        self.last_failure_time = None
        self.circuit_open = False
    
    async def check_health(self) -> bool:
        """Check API health status."""
        try:
            is_healthy = await self.client.health_check()
            if is_healthy:
                self.reset_circuit()
                return True
            else:
                self.record_failure()
                return False
        except Exception as e:
            print(f"Health check failed: {e}")
            self.record_failure()
            return False
    
    def record_failure(self):
        """Record a failure and potentially open circuit."""
        self.failures += 1
        self.last_failure_time = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.circuit_open = True
            print(f"🔴 Circuit breaker opened after {self.failures} failures")
    
    def reset_circuit(self):
        """Reset circuit breaker on successful operation."""
        if self.circuit_open or self.failures > 0:
            print("🟢 Circuit breaker reset - API is healthy")
        self.failures = 0
        self.circuit_open = False
        self.last_failure_time = None
    
    def should_allow_request(self) -> bool:
        """Check if requests should be allowed through."""
        if not self.circuit_open:
            return True
        
        # Check if recovery timeout has passed
        if self.last_failure_time:
            recovery_time = self.last_failure_time + timedelta(seconds=self.recovery_timeout)
            if datetime.now() > recovery_time:
                print("🟡 Circuit breaker half-open - testing recovery")
                return True
        
        return False
    
    async def execute_with_circuit_breaker(self, operation):
        """Execute operation with circuit breaker protection."""
        if not self.should_allow_request():
            raise Exception("Circuit breaker is open - API unavailable")
        
        try:
            result = await operation()
            self.reset_circuit()
            return result
        except Exception as e:
            self.record_failure()
            raise

# Usage example
async def monitored_api_usage():
    async with CarespaceClient(api_key="your-api-key") as client:
        monitor = HealthMonitor(client)
        
        # Periodic health checks
        async def periodic_health_check():
            while True:
                is_healthy = await monitor.check_health()
                status = "✅ Healthy" if is_healthy else "❌ Unhealthy"
                print(f"API Status: {status}")
                await asyncio.sleep(60)  # Check every minute
        
        # Start health monitoring in background
        health_task = asyncio.create_task(periodic_health_check())
        
        try:
            # Use circuit breaker for API calls
            async def get_users_safely():
                return await client.users.get_users()
            
            users = await monitor.execute_with_circuit_breaker(get_users_safely)
            print(f"Retrieved {len(users.data)} users")
            
        finally:
            health_task.cancel()
```

## Data Science Integration

### Pandas Integration for Analytics

```python
import pandas as pd
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

async def healthcare_analytics_example():
    async with CarespaceClient(api_key="your-api-key") as client:
        # Get all clients data
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
                'date_of_birth': client_record.date_of_birth,
                'created_at': client_record.created_at,
                'is_active': client_record.is_active,
                'has_medical_history': bool(client_record.medical_history),
                'age': calculate_age(client_record.date_of_birth) if client_record.date_of_birth else None
            })
        
        df = pd.DataFrame(client_data)
        
        # Basic analytics
        print("📊 Client Analytics Report")
        print("=" * 50)
        print(f"Total clients: {len(df)}")
        print(f"Active clients: {df['is_active'].sum()}")
        print(f"Inactive clients: {(~df['is_active']).sum()}")
        print()
        
        # Gender distribution
        print("Gender Distribution:")
        gender_dist = df['gender'].value_counts()
        print(gender_dist)
        print()
        
        # Age analytics
        if 'age' in df.columns and df['age'].notna().any():
            print("Age Statistics:")
            print(f"Average age: {df['age'].mean():.1f} years")
            print(f"Median age: {df['age'].median():.1f} years")
            print(f"Age range: {df['age'].min():.0f} - {df['age'].max():.0f} years")
            print()
        
        # Registration trends
        df['registration_month'] = df['created_at'].dt.to_period('M')
        monthly_registrations = df.groupby('registration_month').size()
        print("Monthly Registration Trends:")
        print(monthly_registrations.tail(6))
        print()
        
        # Get detailed stats for active clients
        active_clients = df[df['is_active'] == True]['id'].tolist()
        client_stats = []
        
        for client_id in active_clients[:10]:  # Sample first 10 for demo
            try:
                stats = await client.clients.get_client_stats(client_id)
                client_stats.append({
                    'client_id': client_id,
                    'total_sessions': stats.total_sessions,
                    'completed_exercises': stats.completed_exercises,
                    'average_score': stats.average_score,
                    'compliance_rate': stats.compliance_rate,
                    'total_program_time': stats.total_program_time
                })
            except Exception as e:
                print(f"Could not get stats for client {client_id}: {e}")
        
        if client_stats:
            stats_df = pd.DataFrame(client_stats)
            print("Client Performance Analytics:")
            print(f"Average sessions per client: {stats_df['total_sessions'].mean():.1f}")
            print(f"Average exercises completed: {stats_df['completed_exercises'].mean():.1f}")
            print(f"Average compliance rate: {stats_df['compliance_rate'].mean():.1f}%")
            print(f"Average program time: {stats_df['total_program_time'].mean():.0f} minutes")
        
        return df

def calculate_age(birth_date):
    """Calculate age from birth date."""
    if not birth_date:
        return None
    today = datetime.now().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))

# Run analytics
# df = await healthcare_analytics_example()
```

### Export and Reporting

```python
async def generate_comprehensive_report():
    """Generate comprehensive healthcare data report."""
    async with CarespaceClient(api_key="your-api-key") as client:
        report_data = {
            'generated_at': datetime.now(),
            'users': [],
            'clients': [],
            'programs': [],
            'summary': {}
        }
        
        # Get users data
        users_response = await client.users.get_users(limit=1000)
        report_data['users'] = [user.dict() for user in users_response.data]
        
        # Get clients data
        clients_response = await client.clients.get_clients(limit=1000)
        report_data['clients'] = [client_record.dict() for client_record in clients_response.data]
        
        # Get programs data
        programs_response = await client.programs.get_programs(limit=1000)
        report_data['programs'] = [program.dict() for program in programs_response.data]
        
        # Generate summary
        report_data['summary'] = {
            'total_users': len(report_data['users']),
            'total_clients': len(report_data['clients']),
            'total_programs': len(report_data['programs']),
            'active_users': sum(1 for u in report_data['users'] if u['is_active']),
            'active_clients': sum(1 for c in report_data['clients'] if c['is_active']),
            'template_programs': sum(1 for p in report_data['programs'] if p['is_template'])
        }
        
        # Export to multiple formats
        import json
        import csv
        
        # JSON export
        with open('carespace_report.json', 'w') as f:
            json.dump(report_data, f, default=str, indent=2)
        
        # CSV exports
        pd.DataFrame(report_data['users']).to_csv('users_export.csv', index=False)
        pd.DataFrame(report_data['clients']).to_csv('clients_export.csv', index=False)
        pd.DataFrame(report_data['programs']).to_csv('programs_export.csv', index=False)
        
        print("📊 Report generated successfully!")
        print(f"Summary: {report_data['summary']}")
        
        return report_data
```

## Testing

### Unit Testing with pytest

```python
# test_carespace_integration.py
import pytest
from carespace_sdk import CarespaceClient, CreateUserRequest, CreateClientRequest

@pytest.mark.asyncio
async def test_user_lifecycle():
    """Test complete user lifecycle."""
    async with CarespaceClient(api_key="test-api-key") as client:
        # Create user
        user_data = CreateUserRequest(
            email="test@example.com",
            name="Test User",
            role="therapist",
            password="test-password"
        )
        
        created_user = await client.users.create_user(user_data)
        assert created_user.email == "test@example.com"
        assert created_user.name == "Test User"
        
        # Get user
        retrieved_user = await client.users.get_user(created_user.id)
        assert retrieved_user.id == created_user.id
        
        # Update user
        update_data = UpdateUserRequest(name="Updated Test User")
        updated_user = await client.users.update_user(created_user.id, update_data)
        assert updated_user.name == "Updated Test User"
        
        # Delete user
        await client.users.delete_user(created_user.id)

@pytest.mark.asyncio
async def test_error_handling():
    """Test error handling scenarios."""
    async with CarespaceClient(api_key="invalid-key") as client:
        with pytest.raises(AuthenticationError):
            await client.users.get_users()

@pytest.mark.asyncio
async def test_pagination():
    """Test pagination functionality."""
    async with CarespaceClient(api_key="test-api-key") as client:
        # Get first page
        page1 = await client.users.get_users(page=1, limit=5)
        assert len(page1.data) <= 5
        assert page1.page == 1
        
        # Get second page if available
        if page1.pages > 1:
            page2 = await client.users.get_users(page=2, limit=5)
            assert page2.page == 2
```

### Mock Testing

```python
# test_carespace_mocked.py
import pytest
from unittest.mock import AsyncMock, patch
from carespace_sdk import CarespaceClient, User

@pytest.mark.asyncio
async def test_get_users_with_mock():
    """Test getting users with mocked HTTP client."""
    with patch('carespace_sdk.HTTPClient') as mock_http:
        # Mock the HTTP response
        mock_http.return_value.get = AsyncMock(return_value={
            "data": [
                {
                    "id": "1",
                    "email": "test@example.com",
                    "name": "Test User",
                    "role": "therapist",
                    "is_active": True,
                    "is_verified": True,
                    "created_at": "2024-01-01T00:00:00",
                    "updated_at": "2024-01-01T00:00:00"
                }
            ],
            "total": 1,
            "page": 1,
            "limit": 20,
            "pages": 1
        })
        
        client = CarespaceClient(api_key="test-key")
        users = await client.users.get_users()
        
        assert len(users.data) == 1
        assert users.data[0].email == "test@example.com"
        assert isinstance(users.data[0], User)

@pytest.mark.asyncio
async def test_client_with_fixtures():
    """Test using pytest fixtures."""
    # This would use fixtures defined in conftest.py
    pass
```

## Best Practices

### 1. Resource Management

```python
# ✅ Good: Always use async context managers
async with CarespaceClient(api_key="your-key") as client:
    users = await client.users.get_users()
# Connection automatically closed

# ❌ Bad: Manual resource management
client = CarespaceClient(api_key="your-key")
users = await client.users.get_users()
await client.close()  # Easy to forget!
```

### 2. Error Handling Strategy

```python
# ✅ Good: Specific exception handling
try:
    user = await client.users.get_user(user_id)
except NotFoundError:
    # Handle missing user specifically
    return None
except AuthenticationError:
    # Re-authenticate or redirect to login
    await refresh_authentication()
except ValidationError as e:
    # Log validation details and fix data
    logger.error(f"Validation failed: {e.response_data}")
    raise

# ❌ Bad: Catching all exceptions
try:
    user = await client.users.get_user(user_id)
except Exception as e:
    # Too broad - might hide important errors
    logger.error(f"Something went wrong: {e}")
```

### 3. Efficient Data Fetching

```python
# ✅ Good: Use pagination for large datasets
async def get_all_clients():
    all_clients = []
    page = 1
    
    while True:
        response = await client.clients.get_clients(page=page, limit=100)
        all_clients.extend(response.data)
        
        if page >= response.pages:
            break
        page += 1
    
    return all_clients

# ❌ Bad: Requesting too much data at once
# This might timeout or consume too much memory
all_clients = await client.clients.get_clients(limit=10000)
```

### 4. Authentication Best Practices

```python
# ✅ Good: Proper token management
class AuthenticatedClient:
    def __init__(self, email: str, password: str):
        self.email = email
        self.password = password
        self.client = CarespaceClient()
        self.token_expires_at = None
    
    async def ensure_authenticated(self):
        if not self.token_expires_at or datetime.now() > self.token_expires_at:
            login_response = await self.client.login_and_set_token(
                self.email, self.password
            )
            self.token_expires_at = datetime.now() + timedelta(
                seconds=login_response.expires_in - 60  # 1 minute buffer
            )
    
    async def get_users(self):
        await self.ensure_authenticated()
        return await self.client.users.get_users()

# ❌ Bad: Ignoring token expiration
# Token might expire during long-running operations
```

### 5. Logging and Monitoring

```python
import logging

# ✅ Good: Structured logging
logger = logging.getLogger(__name__)

async def monitored_operation():
    try:
        logger.info("Starting user data sync")
        users = await client.users.get_users()
        logger.info(f"Successfully synced {len(users.data)} users")
        return users
    except CarespaceError as e:
        logger.error(
            "API operation failed",
            extra={
                "error_type": type(e).__name__,
                "status_code": e.status_code,
                "message": e.message
            }
        )
        raise
```

### 6. Configuration Management

```python
# ✅ Good: Environment-based configuration
import os
from dataclasses import dataclass

@dataclass
class CarespaceConfig:
    api_key: str
    base_url: str
    timeout: float = 30.0
    max_retries: int = 3
    
    @classmethod
    def from_environment(cls, env: str = "development"):
        return cls(
            api_key=os.getenv(f"CARESPACE_API_KEY_{env.upper()}"),
            base_url=os.getenv(
                f"CARESPACE_BASE_URL_{env.upper()}",
                "https://api-dev.carespace.ai" if env == "development" 
                else "https://api.carespace.ai"
            ),
            timeout=float(os.getenv("CARESPACE_TIMEOUT", "30.0")),
            max_retries=int(os.getenv("CARESPACE_MAX_RETRIES", "3"))
        )

# Usage
config = CarespaceConfig.from_environment("production")
client = CarespaceClient(**config.__dict__)
```

This comprehensive usage guide provides practical examples and best practices for effectively using the Carespace Python SDK in real-world healthcare applications.