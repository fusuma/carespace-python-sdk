"""
Tests for programs API endpoints.
"""

import pytest
from unittest.mock import AsyncMock

from carespace_sdk.api import ProgramsAPI
from carespace_sdk.models import (
    Program,
    CreateProgramRequest,
    UpdateProgramRequest,
    DuplicateProgramRequest,
    Exercise,
    CreateExerciseRequest,
    ProgramsListResponse,
    ExercisesListResponse,
    MessageResponse,
)
from carespace_sdk.exceptions import NotFoundError, ValidationError


class TestProgramsAPI:
    """Test programs API endpoints."""

    @pytest.mark.asyncio
    async def test_get_programs(self, mock_http_client, sample_program_data, sample_paginated_response):
        """Test getting programs list."""
        mock_http_client.get.return_value = sample_paginated_response([sample_program_data])
        programs_api = ProgramsAPI(mock_http_client)

        response = await programs_api.get_programs(
            page=1,
            limit=20,
            search="rehab",
            category="rehabilitation",
            difficulty="intermediate"
        )

        assert isinstance(response, ProgramsListResponse)
        assert len(response.data) == 1
        assert response.data[0].name == "Test Program"

        mock_http_client.get.assert_called_once_with(
            "/programs",
            {
                "page": 1,
                "limit": 20,
                "search": "rehab",
                "category": "rehabilitation",
                "difficulty": "intermediate"
            }
        )

    @pytest.mark.asyncio
    async def test_get_program(self, mock_http_client, sample_program_data):
        """Test getting a specific program."""
        mock_http_client.get.return_value = sample_program_data
        programs_api = ProgramsAPI(mock_http_client)

        program = await programs_api.get_program("program-123")

        assert isinstance(program, Program)
        assert program.id == "program-123"
        assert program.name == "Test Program"
        mock_http_client.get.assert_called_once_with("/programs/program-123")

    @pytest.mark.asyncio
    async def test_create_program(self, mock_http_client, sample_program_data):
        """Test creating a program."""
        mock_http_client.post.return_value = sample_program_data
        programs_api = ProgramsAPI(mock_http_client)

        program_data = CreateProgramRequest(
            name="Test Program",
            description="A test rehabilitation program",
            category="rehabilitation",
            difficulty="intermediate",
            duration=45
        )

        program = await programs_api.create_program(program_data)

        assert isinstance(program, Program)
        assert program.name == "Test Program"
        mock_http_client.post.assert_called_once_with("/programs", program_data)

    @pytest.mark.asyncio
    async def test_update_program(self, mock_http_client, sample_program_data):
        """Test updating a program."""
        updated_data = {**sample_program_data, "duration": 60}
        mock_http_client.put.return_value = updated_data
        programs_api = ProgramsAPI(mock_http_client)

        update_data = UpdateProgramRequest(duration=60)
        program = await programs_api.update_program("program-123", update_data)

        assert isinstance(program, Program)
        assert program.duration == 60
        mock_http_client.put.assert_called_once_with("/programs/program-123", update_data)

    @pytest.mark.asyncio
    async def test_delete_program(self, mock_http_client):
        """Test deleting a program."""
        mock_http_client.delete.return_value = {"message": "Program deleted successfully"}
        programs_api = ProgramsAPI(mock_http_client)

        response = await programs_api.delete_program("program-123")

        assert isinstance(response, MessageResponse)
        assert "deleted successfully" in response.message
        mock_http_client.delete.assert_called_once_with("/programs/program-123")

    @pytest.mark.asyncio
    async def test_get_program_exercises(self, mock_http_client, sample_exercise_data, sample_paginated_response):
        """Test getting program exercises."""
        mock_http_client.get.return_value = sample_paginated_response([sample_exercise_data])
        programs_api = ProgramsAPI(mock_http_client)

        response = await programs_api.get_program_exercises(
            "program-123",
            page=1,
            limit=50,
            search="stretch"
        )

        assert isinstance(response, ExercisesListResponse)
        assert len(response.data) == 1
        assert response.data[0].name == "Test Exercise"

        mock_http_client.get.assert_called_once_with(
            "/programs/program-123/exercises",
            {"page": 1, "limit": 50, "search": "stretch"}
        )

    @pytest.mark.asyncio
    async def test_add_exercise_to_program(self, mock_http_client, sample_exercise_data):
        """Test adding an exercise to a program."""
        mock_http_client.post.return_value = sample_exercise_data
        programs_api = ProgramsAPI(mock_http_client)

        exercise_data = CreateExerciseRequest(
            name="Test Exercise",
            description="A test exercise",
            instructions="Perform the exercise as shown",
            duration=30,
            repetitions=10,
            sets=3,
            order=1
        )

        exercise = await programs_api.add_exercise_to_program("program-123", exercise_data)

        assert isinstance(exercise, Exercise)
        assert exercise.name == "Test Exercise"
        mock_http_client.post.assert_called_once_with(
            "/programs/program-123/exercises",
            exercise_data
        )

    @pytest.mark.asyncio
    async def test_update_program_exercise(self, mock_http_client, sample_exercise_data):
        """Test updating a program exercise."""
        updated_data = {**sample_exercise_data, "duration": 45}
        mock_http_client.put.return_value = updated_data
        programs_api = ProgramsAPI(mock_http_client)

        exercise_data = CreateExerciseRequest(
            name="Updated Exercise",
            duration=45
        )

        exercise = await programs_api.update_program_exercise(
            "program-123",
            "exercise-456",
            exercise_data
        )

        assert isinstance(exercise, Exercise)
        assert exercise.duration == 45
        mock_http_client.put.assert_called_once_with(
            "/programs/program-123/exercises/exercise-456",
            exercise_data
        )

    @pytest.mark.asyncio
    async def test_remove_program_exercise(self, mock_http_client):
        """Test removing an exercise from a program."""
        mock_http_client.delete.return_value = {"message": "Exercise removed successfully"}
        programs_api = ProgramsAPI(mock_http_client)

        response = await programs_api.remove_program_exercise("program-123", "exercise-456")

        assert isinstance(response, MessageResponse)
        assert "removed successfully" in response.message
        mock_http_client.delete.assert_called_once_with(
            "/programs/program-123/exercises/exercise-456"
        )

    @pytest.mark.asyncio
    async def test_duplicate_program(self, mock_http_client, sample_program_data):
        """Test duplicating a program."""
        duplicated_data = {**sample_program_data, "id": "program-789", "name": "Duplicated Program"}
        mock_http_client.post.return_value = duplicated_data
        programs_api = ProgramsAPI(mock_http_client)

        duplicate_data = DuplicateProgramRequest(
            name="Duplicated Program",
            description="A duplicated program",
            copy_exercises=True
        )

        program = await programs_api.duplicate_program("program-123", duplicate_data)

        assert isinstance(program, Program)
        assert program.name == "Duplicated Program"
        mock_http_client.post.assert_called_once_with(
            "/programs/program-123/duplicate",
            duplicate_data
        )

    @pytest.mark.asyncio
    async def test_duplicate_program_default(self, mock_http_client, sample_program_data):
        """Test duplicating a program with default options."""
        mock_http_client.post.return_value = sample_program_data
        programs_api = ProgramsAPI(mock_http_client)

        program = await programs_api.duplicate_program("program-123")

        mock_http_client.post.assert_called_once()
        call_args = mock_http_client.post.call_args
        assert call_args[0][0] == "/programs/program-123/duplicate"
        assert isinstance(call_args[0][1], DuplicateProgramRequest)

    @pytest.mark.asyncio
    async def test_get_program_templates(self, mock_http_client, sample_program_data, sample_paginated_response):
        """Test getting program templates."""
        template_data = {**sample_program_data, "is_template": True}
        mock_http_client.get.return_value = sample_paginated_response([template_data])
        programs_api = ProgramsAPI(mock_http_client)

        response = await programs_api.get_program_templates(
            page=1,
            limit=10,
            search="template",
            category="rehabilitation",
            difficulty="beginner"
        )

        assert isinstance(response, ProgramsListResponse)
        assert len(response.data) == 1

        mock_http_client.get.assert_called_once_with(
            "/programs/templates",
            {
                "page": 1,
                "limit": 10,
                "search": "template",
                "category": "rehabilitation",
                "difficulty": "beginner"
            }
        )

    @pytest.mark.asyncio
    async def test_program_not_found(self, mock_http_client):
        """Test handling program not found error."""
        mock_http_client.get.side_effect = NotFoundError(
            "Program not found",
            status_code=404
        )
        programs_api = ProgramsAPI(mock_http_client)

        with pytest.raises(NotFoundError) as exc_info:
            await programs_api.get_program("non-existent")

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_create_program_validation_error(self, mock_http_client):
        """Test validation error when creating program."""
        mock_http_client.post.side_effect = ValidationError(
            "Invalid program data",
            status_code=422,
            response_data={"errors": {"duration": ["Duration must be positive"]}}
        )
        programs_api = ProgramsAPI(mock_http_client)

        program_data = CreateProgramRequest(
            name="Test Program",
            duration=-10  # Invalid duration
        )

        with pytest.raises(ValidationError) as exc_info:
            await programs_api.create_program(program_data)

        assert exc_info.value.status_code == 422
        assert "duration" in exc_info.value.response_data["errors"]