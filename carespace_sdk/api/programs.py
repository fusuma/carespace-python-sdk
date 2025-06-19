"""
Programs API endpoints.
"""

from typing import TYPE_CHECKING, Optional

from ..models import (
    Program,
    CreateProgramRequest,
    UpdateProgramRequest,
    Exercise,
    CreateExerciseRequest,
    ProgramsListResponse,
    ExercisesListResponse,
    DuplicateProgramRequest,
    PaginationParams,
    MessageResponse,
)

if TYPE_CHECKING:
    from ..http_client import HTTPClient


class ProgramsAPI:
    """Programs API client."""

    def __init__(self, http_client: "HTTPClient") -> None:
        """Initialize the Programs API client."""
        self._http_client = http_client

    async def get_programs(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
        is_template: Optional[bool] = None,
        sort_by: Optional[str] = None,
        sort_order: Optional[str] = "asc",
    ) -> ProgramsListResponse:
        """
        Get a paginated list of programs.

        Args:
            page: Page number (1-based)
            limit: Number of items per page (1-100)
            search: Search query to filter programs
            category: Filter by program category
            difficulty: Filter by difficulty level
            is_template: Filter by template status
            sort_by: Field to sort by
            sort_order: Sort order ('asc' or 'desc')

        Returns:
            ProgramsListResponse: Paginated list of programs

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If parameters are invalid
            CarespaceError: For other API errors
        """
        params = PaginationParams(
            page=page,
            limit=limit,
            search=search,
            sort_by=sort_by,
            sort_order=sort_order,
        )
        
        # Add additional filters
        params_dict = params.model_dump(exclude_none=True)
        if category:
            params_dict["category"] = category
        if difficulty:
            params_dict["difficulty"] = difficulty
        if is_template is not None:
            params_dict["is_template"] = is_template

        response_data = await self._http_client.get("/programs", params_dict)
        return ProgramsListResponse.model_validate(response_data)

    async def get_program(self, program_id: str) -> Program:
        """
        Get a specific program by ID.

        Args:
            program_id: Program ID

        Returns:
            Program: Program details

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If program doesn't exist
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.get(f"/programs/{program_id}")
        return Program.model_validate(response_data)

    async def create_program(self, program_data: CreateProgramRequest) -> Program:
        """
        Create a new program.

        Args:
            program_data: Program creation data

        Returns:
            Program: Created program details

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If program data is invalid
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.post("/programs", program_data)
        return Program.model_validate(response_data)

    async def update_program(self, program_id: str, program_data: UpdateProgramRequest) -> Program:
        """
        Update an existing program.

        Args:
            program_id: Program ID
            program_data: Program update data

        Returns:
            Program: Updated program details

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If program doesn't exist
            ValidationError: If program data is invalid
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.put(f"/programs/{program_id}", program_data)
        return Program.model_validate(response_data)

    async def delete_program(self, program_id: str) -> MessageResponse:
        """
        Delete a program.

        Args:
            program_id: Program ID

        Returns:
            MessageResponse: Confirmation message

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If program doesn't exist
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.delete(f"/programs/{program_id}")
        return MessageResponse.model_validate(response_data)

    async def get_program_exercises(
        self,
        program_id: str,
        page: int = 1,
        limit: int = 50,
        search: Optional[str] = None,
    ) -> ExercisesListResponse:
        """
        Get exercises in a specific program.

        Args:
            program_id: Program ID
            page: Page number (1-based)
            limit: Number of items per page (1-100)
            search: Search query to filter exercises

        Returns:
            ExercisesListResponse: Paginated list of program exercises

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If program doesn't exist
            ValidationError: If parameters are invalid
            CarespaceError: For other API errors
        """
        params = PaginationParams(page=page, limit=limit, search=search)
        response_data = await self._http_client.get(
            f"/programs/{program_id}/exercises",
            params.model_dump(exclude_none=True)
        )
        return ExercisesListResponse.model_validate(response_data)

    async def add_exercise_to_program(
        self,
        program_id: str,
        exercise_data: CreateExerciseRequest,
    ) -> Exercise:
        """
        Add an exercise to a program.

        Args:
            program_id: Program ID
            exercise_data: Exercise creation data

        Returns:
            Exercise: Created exercise details

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If program doesn't exist
            ValidationError: If exercise data is invalid
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.post(
            f"/programs/{program_id}/exercises",
            exercise_data
        )
        return Exercise.model_validate(response_data)

    async def update_program_exercise(
        self,
        program_id: str,
        exercise_id: str,
        exercise_data: CreateExerciseRequest,
    ) -> Exercise:
        """
        Update an exercise in a program.

        Args:
            program_id: Program ID
            exercise_id: Exercise ID
            exercise_data: Exercise update data

        Returns:
            Exercise: Updated exercise details

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If program or exercise doesn't exist
            ValidationError: If exercise data is invalid
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.put(
            f"/programs/{program_id}/exercises/{exercise_id}",
            exercise_data
        )
        return Exercise.model_validate(response_data)

    async def remove_program_exercise(
        self,
        program_id: str,
        exercise_id: str,
    ) -> MessageResponse:
        """
        Remove an exercise from a program.

        Args:
            program_id: Program ID
            exercise_id: Exercise ID

        Returns:
            MessageResponse: Confirmation message

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If program or exercise doesn't exist
            CarespaceError: For other API errors
        """
        response_data = await self._http_client.delete(
            f"/programs/{program_id}/exercises/{exercise_id}"
        )
        return MessageResponse.model_validate(response_data)

    async def duplicate_program(
        self,
        program_id: str,
        duplicate_data: Optional[DuplicateProgramRequest] = None,
    ) -> Program:
        """
        Duplicate an existing program.

        Args:
            program_id: Program ID to duplicate
            duplicate_data: Duplication options

        Returns:
            Program: Duplicated program details

        Raises:
            AuthenticationError: If not authenticated
            NotFoundError: If program doesn't exist
            ValidationError: If duplication data is invalid
            CarespaceError: For other API errors
        """
        if duplicate_data is None:
            duplicate_data = DuplicateProgramRequest()

        response_data = await self._http_client.post(
            f"/programs/{program_id}/duplicate",
            duplicate_data
        )
        return Program.model_validate(response_data)

    async def get_program_templates(
        self,
        page: int = 1,
        limit: int = 20,
        search: Optional[str] = None,
        category: Optional[str] = None,
        difficulty: Optional[str] = None,
    ) -> ProgramsListResponse:
        """
        Get a paginated list of program templates.

        Args:
            page: Page number (1-based)
            limit: Number of items per page (1-100)
            search: Search query to filter templates
            category: Filter by program category
            difficulty: Filter by difficulty level

        Returns:
            ProgramsListResponse: Paginated list of program templates

        Raises:
            AuthenticationError: If not authenticated
            ValidationError: If parameters are invalid
            CarespaceError: For other API errors
        """
        params = PaginationParams(page=page, limit=limit, search=search)
        params_dict = params.model_dump(exclude_none=True)
        
        if category:
            params_dict["category"] = category
        if difficulty:
            params_dict["difficulty"] = difficulty

        response_data = await self._http_client.get("/programs/templates", params_dict)
        return ProgramsListResponse.model_validate(response_data)