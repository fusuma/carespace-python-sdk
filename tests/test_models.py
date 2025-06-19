"""
Tests for Pydantic models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from carespace_sdk.models import (
    User,
    CreateUserRequest,
    UpdateUserRequest,
    Client,
    CreateClientRequest,
    UpdateClientRequest,
    Address,
    Program,
    CreateProgramRequest,
    UpdateProgramRequest,
    Exercise,
    CreateExerciseRequest,
    LoginRequest,
    LoginResponse,
    TokenRefreshRequest,
    TokenRefreshResponse,
    UsersListResponse,
    ClientsListResponse,
    ProgramsListResponse,
    ExercisesListResponse,
    ClientStats,
    PaginationParams,
    MessageResponse,
    SuccessResponse,
    DuplicateProgramRequest,
)


class TestUserModels:
    """Test user-related models."""

    def test_user_model(self):
        """Test User model validation."""
        user_data = {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User",
            "first_name": "Test",
            "last_name": "User",
            "role": "user",
            "is_active": True,
            "is_verified": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        user = User.model_validate(user_data)
        assert user.id == "user-123"
        assert user.email == "test@example.com"
        assert user.name == "Test User"
        assert user.is_active is True

    def test_create_user_request(self):
        """Test CreateUserRequest model."""
        user_data = CreateUserRequest(
            email="test@example.com",
            name="Test User",
            first_name="Test",
            last_name="User",
            role="user",
            password="secure-password"
        )
        
        assert user_data.email == "test@example.com"
        assert user_data.name == "Test User"
        assert user_data.password == "secure-password"

    def test_create_user_request_minimal(self):
        """Test CreateUserRequest with minimal data."""
        user_data = CreateUserRequest(
            email="test@example.com",
            name="Test User"
        )
        
        assert user_data.email == "test@example.com"
        assert user_data.name == "Test User"
        assert user_data.password is None

    def test_update_user_request(self):
        """Test UpdateUserRequest model."""
        update_data = UpdateUserRequest(
            name="Updated User",
            is_active=False
        )
        
        assert update_data.name == "Updated User"
        assert update_data.is_active is False
        assert update_data.email is None  # Not provided


class TestClientModels:
    """Test client-related models."""

    def test_address_model(self):
        """Test Address model."""
        address = Address(
            street="123 Main St",
            city="New York",
            state="NY",
            zip_code="10001",
            country="USA"
        )
        
        assert address.street == "123 Main St"
        assert address.city == "New York"
        assert address.zip_code == "10001"

    def test_client_model(self):
        """Test Client model with address."""
        client_data = {
            "id": "client-123",
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "+1234567890",
            "date_of_birth": "1990-01-01",
            "gender": "male",
            "address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001"
            },
            "is_active": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        client = Client.model_validate(client_data)
        assert client.id == "client-123"
        assert client.name == "John Doe"
        assert client.address.street == "123 Main St"
        assert client.date_of_birth.year == 1990

    def test_create_client_request(self):
        """Test CreateClientRequest model."""
        address = Address(
            street="123 Main St",
            city="New York",
            state="NY",
            zip_code="10001"
        )
        
        client_data = CreateClientRequest(
            name="John Doe",
            email="john@example.com",
            phone="+1234567890",
            address=address
        )
        
        assert client_data.name == "John Doe"
        assert client_data.email == "john@example.com"
        assert client_data.address.street == "123 Main St"

    def test_client_stats_model(self):
        """Test ClientStats model."""
        stats_data = {
            "total_sessions": 10,
            "completed_exercises": 25,
            "average_score": 85.5,
            "last_session_date": "2024-01-15T10:30:00Z",
            "progress_percentage": 75.0
        }
        
        stats = ClientStats.model_validate(stats_data)
        assert stats.total_sessions == 10
        assert stats.average_score == 85.5
        assert stats.progress_percentage == 75.0


class TestProgramModels:
    """Test program-related models."""

    def test_exercise_model(self):
        """Test Exercise model."""
        exercise_data = {
            "id": "exercise-123",
            "name": "Push-ups",
            "description": "Standard push-up exercise",
            "instructions": "Lower your body until your chest touches the floor",
            "video_url": "https://example.com/video.mp4",
            "duration": 30,
            "repetitions": 10,
            "sets": 3,
            "rest_time": 60,
            "order": 1,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        exercise = Exercise.model_validate(exercise_data)
        assert exercise.id == "exercise-123"
        assert exercise.name == "Push-ups"
        assert exercise.duration == 30
        assert exercise.repetitions == 10

    def test_program_model(self):
        """Test Program model with exercises."""
        exercise_data = {
            "id": "exercise-123",
            "name": "Push-ups",
            "description": "Standard push-up exercise",
            "duration": 30,
            "repetitions": 10,
            "sets": 3,
            "order": 1,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        program_data = {
            "id": "program-123",
            "name": "Beginner Workout",
            "description": "A beginner-friendly workout program",
            "category": "fitness",
            "difficulty": "beginner",
            "duration": 45,
            "is_template": False,
            "exercises": [exercise_data],
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        program = Program.model_validate(program_data)
        assert program.id == "program-123"
        assert program.name == "Beginner Workout"
        assert program.difficulty == "beginner"
        assert len(program.exercises) == 1
        assert program.exercises[0].name == "Push-ups"

    def test_create_program_request(self):
        """Test CreateProgramRequest model."""
        program_data = CreateProgramRequest(
            name="Test Program",
            description="A test program",
            category="rehabilitation",
            difficulty="intermediate",
            duration=60,
            is_template=True
        )
        
        assert program_data.name == "Test Program"
        assert program_data.category == "rehabilitation"
        assert program_data.is_template is True

    def test_duplicate_program_request(self):
        """Test DuplicateProgramRequest model."""
        duplicate_data = DuplicateProgramRequest(
            name="Duplicated Program",
            description="A duplicated program",
            copy_exercises=True
        )
        
        assert duplicate_data.name == "Duplicated Program"
        assert duplicate_data.copy_exercises is True

    def test_duplicate_program_request_defaults(self):
        """Test DuplicateProgramRequest with default values."""
        duplicate_data = DuplicateProgramRequest()
        
        assert duplicate_data.copy_exercises is True  # Default value


class TestAuthModels:
    """Test authentication models."""

    def test_login_request(self):
        """Test LoginRequest model."""
        login_data = LoginRequest(
            email="test@example.com",
            password="password123"
        )
        
        assert login_data.email == "test@example.com"
        assert login_data.password == "password123"

    def test_login_response(self):
        """Test LoginResponse model."""
        user_data = {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "user"
        }
        
        login_data = {
            "access_token": "access-token-123",
            "refresh_token": "refresh-token-123",
            "token_type": "Bearer",
            "expires_in": 3600,
            "user": user_data
        }
        
        response = LoginResponse.model_validate(login_data)
        assert response.access_token == "access-token-123"
        assert response.expires_in == 3600
        assert response.user.email == "test@example.com"

    def test_token_refresh_request(self):
        """Test TokenRefreshRequest model."""
        refresh_data = TokenRefreshRequest(
            refresh_token="refresh-token-123"
        )
        
        assert refresh_data.refresh_token == "refresh-token-123"


class TestListResponseModels:
    """Test paginated list response models."""

    def test_users_list_response(self):
        """Test UsersListResponse model."""
        user_data = {
            "id": "user-123",
            "email": "test@example.com",
            "name": "Test User",
            "role": "user",
            "is_active": True,
            "is_verified": True,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
        
        response_data = {
            "data": [user_data],
            "total": 1,
            "page": 1,
            "limit": 20,
            "pages": 1
        }
        
        response = UsersListResponse.model_validate(response_data)
        assert len(response.data) == 1
        assert response.total == 1
        assert response.data[0].email == "test@example.com"

    def test_pagination_params(self):
        """Test PaginationParams model."""
        params = PaginationParams(
            page=2,
            limit=50,
            search="test query",
            sort_by="created_at",
            sort_order="desc"
        )
        
        assert params.page == 2
        assert params.limit == 50
        assert params.search == "test query"

    def test_pagination_params_validation(self):
        """Test PaginationParams validation."""
        # Test invalid page
        with pytest.raises(ValidationError):
            PaginationParams(page=0)
        
        # Test invalid limit
        with pytest.raises(ValidationError):
            PaginationParams(limit=101)
        
        # Test invalid sort order
        with pytest.raises(ValidationError):
            PaginationParams(sort_order="invalid")


class TestResponseModels:
    """Test response models."""

    def test_message_response(self):
        """Test MessageResponse model."""
        response = MessageResponse(message="Operation completed successfully")
        assert response.message == "Operation completed successfully"

    def test_success_response(self):
        """Test SuccessResponse model."""
        response = SuccessResponse(success=True)
        assert response.success is True

    def test_success_response_with_message(self):
        """Test SuccessResponse with optional message."""
        response_data = {
            "success": True,
            "message": "User created successfully"
        }
        
        response = SuccessResponse.model_validate(response_data)
        assert response.success is True
        assert response.message == "User created successfully"


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_model_dump_json(self):
        """Test model JSON serialization."""
        user_data = CreateUserRequest(
            email="test@example.com",
            name="Test User",
            password="secret"
        )
        
        json_data = user_data.model_dump_json()
        assert '"email":"test@example.com"' in json_data
        assert '"name":"Test User"' in json_data

    def test_model_dump_exclude_none(self):
        """Test model dict serialization excluding None values."""
        update_data = UpdateUserRequest(
            name="Updated Name"
            # email is None
        )
        
        data_dict = update_data.model_dump(exclude_none=True)
        assert "name" in data_dict
        assert "email" not in data_dict

    def test_datetime_serialization(self):
        """Test datetime field serialization."""
        client_data = CreateClientRequest(
            name="John Doe",
            email="john@example.com",
            date_of_birth=datetime(1990, 1, 1)
        )
        
        data_dict = client_data.model_dump()
        assert isinstance(data_dict["date_of_birth"], datetime)