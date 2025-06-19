"""
Pydantic models for the Carespace API.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

from pydantic import BaseModel, Field, EmailStr, ConfigDict


class PaginationParams(BaseModel):
    """Parameters for paginated requests."""
    
    page: int = Field(default=1, ge=1, description="Page number")
    limit: int = Field(default=20, ge=1, le=100, description="Items per page")
    search: Optional[str] = Field(default=None, description="Search query")
    sort_by: Optional[str] = Field(default=None, description="Field to sort by")
    sort_order: Optional[str] = Field(default="asc", description="Sort order (asc/desc)")

    model_config = ConfigDict(extra="forbid")


class PaginatedResponse(BaseModel):
    """Base model for paginated responses."""
    
    total: int = Field(description="Total number of items")
    page: int = Field(description="Current page number")
    limit: int = Field(description="Items per page")
    pages: int = Field(description="Total number of pages")

    model_config = ConfigDict(extra="forbid")


# Authentication Models

class LoginRequest(BaseModel):
    """Request model for user login."""
    
    email: EmailStr = Field(description="User email address")
    password: str = Field(min_length=1, description="User password")

    model_config = ConfigDict(extra="forbid")


class LoginResponse(BaseModel):
    """Response model for successful login."""
    
    access_token: str = Field(description="JWT access token")
    refresh_token: str = Field(description="JWT refresh token")
    expires_in: int = Field(description="Token expiration time in seconds")
    token_type: str = Field(default="Bearer", description="Token type")

    model_config = ConfigDict(extra="forbid")


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""
    
    refresh_token: str = Field(description="Refresh token")

    model_config = ConfigDict(extra="forbid")


# User Models

class User(BaseModel):
    """User model."""
    
    id: str = Field(description="Unique user identifier")
    email: EmailStr = Field(description="User email address")
    name: Optional[str] = Field(default=None, description="Full name")
    first_name: Optional[str] = Field(default=None, description="First name")
    last_name: Optional[str] = Field(default=None, description="Last name")
    role: Optional[str] = Field(default=None, description="User role")
    is_active: bool = Field(default=True, description="Whether user is active")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    model_config = ConfigDict(extra="forbid")


class CreateUserRequest(BaseModel):
    """Request model for creating a new user."""
    
    email: EmailStr = Field(description="User email address")
    name: Optional[str] = Field(default=None, description="Full name")
    first_name: Optional[str] = Field(default=None, description="First name")
    last_name: Optional[str] = Field(default=None, description="Last name")
    role: Optional[str] = Field(default="client", description="User role")
    password: Optional[str] = Field(default=None, description="User password")

    model_config = ConfigDict(extra="forbid")


class UpdateUserRequest(BaseModel):
    """Request model for updating a user."""
    
    name: Optional[str] = Field(default=None, description="Full name")
    first_name: Optional[str] = Field(default=None, description="First name")
    last_name: Optional[str] = Field(default=None, description="Last name")
    role: Optional[str] = Field(default=None, description="User role")
    is_active: Optional[bool] = Field(default=None, description="Whether user is active")

    model_config = ConfigDict(extra="forbid")


class UsersListResponse(PaginatedResponse):
    """Response model for users list."""
    
    data: List[User] = Field(description="List of users")

    model_config = ConfigDict(extra="forbid")


# Client Models

class Address(BaseModel):
    """Address model."""
    
    street: Optional[str] = Field(default=None, description="Street address")
    city: Optional[str] = Field(default=None, description="City")
    state: Optional[str] = Field(default=None, description="State/Province")
    zip_code: Optional[str] = Field(default=None, description="ZIP/Postal code")
    country: Optional[str] = Field(default=None, description="Country")

    model_config = ConfigDict(extra="forbid")


class Client(BaseModel):
    """Client model."""
    
    id: str = Field(description="Unique client identifier")
    name: str = Field(description="Client name")
    email: Optional[EmailStr] = Field(default=None, description="Client email")
    phone: Optional[str] = Field(default=None, description="Phone number")
    date_of_birth: Optional[datetime] = Field(default=None, description="Date of birth")
    gender: Optional[str] = Field(default=None, description="Gender")
    address: Optional[Address] = Field(default=None, description="Address information")
    medical_history: Optional[str] = Field(default=None, description="Medical history")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    is_active: bool = Field(default=True, description="Whether client is active")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    model_config = ConfigDict(extra="forbid")


class CreateClientRequest(BaseModel):
    """Request model for creating a new client."""
    
    name: str = Field(description="Client name")
    email: Optional[EmailStr] = Field(default=None, description="Client email")
    phone: Optional[str] = Field(default=None, description="Phone number")
    date_of_birth: Optional[datetime] = Field(default=None, description="Date of birth")
    gender: Optional[str] = Field(default=None, description="Gender")
    address: Optional[Address] = Field(default=None, description="Address information")
    medical_history: Optional[str] = Field(default=None, description="Medical history")
    notes: Optional[str] = Field(default=None, description="Additional notes")

    model_config = ConfigDict(extra="forbid")


class UpdateClientRequest(BaseModel):
    """Request model for updating a client."""
    
    name: Optional[str] = Field(default=None, description="Client name")
    email: Optional[EmailStr] = Field(default=None, description="Client email")
    phone: Optional[str] = Field(default=None, description="Phone number")
    date_of_birth: Optional[datetime] = Field(default=None, description="Date of birth")
    gender: Optional[str] = Field(default=None, description="Gender")
    address: Optional[Address] = Field(default=None, description="Address information")
    medical_history: Optional[str] = Field(default=None, description="Medical history")
    notes: Optional[str] = Field(default=None, description="Additional notes")
    is_active: Optional[bool] = Field(default=None, description="Whether client is active")

    model_config = ConfigDict(extra="forbid")


class ClientsListResponse(PaginatedResponse):
    """Response model for clients list."""
    
    data: List[Client] = Field(description="List of clients")

    model_config = ConfigDict(extra="forbid")


class ClientStats(BaseModel):
    """Client statistics model."""
    
    total_sessions: int = Field(description="Total number of sessions")
    completed_exercises: int = Field(description="Number of completed exercises")
    average_score: Optional[float] = Field(default=None, description="Average session score")
    last_session_date: Optional[datetime] = Field(default=None, description="Date of last session")

    model_config = ConfigDict(extra="forbid")


# Program Models

class Exercise(BaseModel):
    """Exercise model."""
    
    id: str = Field(description="Unique exercise identifier")
    name: str = Field(description="Exercise name")
    description: Optional[str] = Field(default=None, description="Exercise description")
    instructions: Optional[str] = Field(default=None, description="Exercise instructions")
    video_url: Optional[str] = Field(default=None, description="Video demonstration URL")
    image_url: Optional[str] = Field(default=None, description="Image URL")
    duration: Optional[int] = Field(default=None, ge=0, description="Duration in seconds")
    repetitions: Optional[int] = Field(default=None, ge=0, description="Number of repetitions")
    sets: Optional[int] = Field(default=None, ge=0, description="Number of sets")
    rest_time: Optional[int] = Field(default=None, ge=0, description="Rest time in seconds")
    order: int = Field(default=0, ge=0, description="Exercise order in program")

    model_config = ConfigDict(extra="forbid")


class Program(BaseModel):
    """Program model."""
    
    id: str = Field(description="Unique program identifier")
    name: str = Field(description="Program name")
    description: Optional[str] = Field(default=None, description="Program description")
    category: Optional[str] = Field(default=None, description="Program category")
    difficulty: Optional[str] = Field(default=None, description="Difficulty level")
    duration: Optional[int] = Field(default=None, ge=0, description="Duration in minutes")
    is_template: bool = Field(default=False, description="Whether this is a template")
    is_active: bool = Field(default=True, description="Whether program is active")
    created_by: Optional[str] = Field(default=None, description="Creator user ID")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")
    exercises: List[Exercise] = Field(default_factory=list, description="Program exercises")

    model_config = ConfigDict(extra="forbid")


class CreateProgramRequest(BaseModel):
    """Request model for creating a new program."""
    
    name: str = Field(description="Program name")
    description: Optional[str] = Field(default=None, description="Program description")
    category: Optional[str] = Field(default=None, description="Program category")
    difficulty: Optional[str] = Field(default="beginner", description="Difficulty level")
    duration: Optional[int] = Field(default=None, ge=0, description="Duration in minutes")
    is_template: bool = Field(default=False, description="Whether this is a template")

    model_config = ConfigDict(extra="forbid")


class UpdateProgramRequest(BaseModel):
    """Request model for updating a program."""
    
    name: Optional[str] = Field(default=None, description="Program name")
    description: Optional[str] = Field(default=None, description="Program description")
    category: Optional[str] = Field(default=None, description="Program category")
    difficulty: Optional[str] = Field(default=None, description="Difficulty level")
    duration: Optional[int] = Field(default=None, ge=0, description="Duration in minutes")
    is_template: Optional[bool] = Field(default=None, description="Whether this is a template")
    is_active: Optional[bool] = Field(default=None, description="Whether program is active")

    model_config = ConfigDict(extra="forbid")


class CreateExerciseRequest(BaseModel):
    """Request model for creating a new exercise."""
    
    name: str = Field(description="Exercise name")
    description: Optional[str] = Field(default=None, description="Exercise description")
    instructions: Optional[str] = Field(default=None, description="Exercise instructions")
    video_url: Optional[str] = Field(default=None, description="Video demonstration URL")
    image_url: Optional[str] = Field(default=None, description="Image URL")
    duration: Optional[int] = Field(default=None, ge=0, description="Duration in seconds")
    repetitions: Optional[int] = Field(default=None, ge=0, description="Number of repetitions")
    sets: Optional[int] = Field(default=None, ge=0, description="Number of sets")
    rest_time: Optional[int] = Field(default=None, ge=0, description="Rest time in seconds")
    order: int = Field(default=0, ge=0, description="Exercise order in program")

    model_config = ConfigDict(extra="forbid")


class ProgramsListResponse(PaginatedResponse):
    """Response model for programs list."""
    
    data: List[Program] = Field(description="List of programs")

    model_config = ConfigDict(extra="forbid")


class ExercisesListResponse(PaginatedResponse):
    """Response model for exercises list."""
    
    data: List[Exercise] = Field(description="List of exercises")

    model_config = ConfigDict(extra="forbid")


class DuplicateProgramRequest(BaseModel):
    """Request model for duplicating a program."""
    
    name: Optional[str] = Field(default=None, description="New program name")
    description: Optional[str] = Field(default=None, description="New program description")
    copy_exercises: bool = Field(default=True, description="Whether to copy exercises")

    model_config = ConfigDict(extra="forbid")


# Common Response Models

class MessageResponse(BaseModel):
    """Generic message response."""
    
    message: str = Field(description="Response message")

    model_config = ConfigDict(extra="forbid")


class SuccessResponse(BaseModel):
    """Success response model."""
    
    success: bool = Field(description="Operation success status")
    message: Optional[str] = Field(default=None, description="Optional message")

    model_config = ConfigDict(extra="forbid")