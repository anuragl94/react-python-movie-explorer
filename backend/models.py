from fastapi import Query
from pydantic import BaseModel, HttpUrl, Field, conint
from typing import Optional, List

# Shared base for MongoDB id
class MongoModel(BaseModel):
    """Base model that includes an optional ID field for API responses."""
    id: Optional[str] = None

# Item model
class Item(MongoModel):
    """Generic item model for testing purposes."""
    name: str
    description: Optional[str] = None
    price: float

# Reference models for nested objects in MovieOut
class CrewRef(BaseModel):
    """Reference to a crew member with ID and name."""
    id: str
    name: str

class GenreRef(BaseModel):
    """Reference to a genre with ID and name."""
    id: str
    name: str

# Movie models
class MovieBase(BaseModel):
    """Base movie model with common fields."""
    title: str = Field(..., description="Movie title")
    description: Optional[str] = Field(None, description="Movie description")
    release_year: int = Field(..., description="Year the movie was released")
    image_url: Optional[HttpUrl] = Field(None, description="URL to the movie's poster or image")
    user_rating: Optional[conint(ge=1, le=100)] = Field(None, description="User rating between 1 and 100")

class MovieIn(MovieBase):
    """Movie model for creating new movies (requires IDs for related entities)."""
    directed_by: str = Field(..., description="Director's crew ID (MongoDB ObjectId)")
    cast: List[str] = Field(..., description="List of cast member IDs (MongoDB ObjectIds)")
    genre: List[str] = Field(..., description="List of genre IDs (MongoDB ObjectIds)")

class MovieOut(MovieBase, MongoModel):
    """Movie model for API responses (includes full objects for related entities)."""
    directed_by: Optional[CrewRef] = Field(None, description="Director information")
    cast: List[CrewRef] = Field(default_factory=list, description="List of cast members")
    genre: List[GenreRef] = Field(default_factory=list, description="List of genres")

class MovieFilter(BaseModel):
    """Filter model for movie queries."""
    title: Optional[str] = Field(None, description="Partial movie title (case-insensitive)")
    description: Optional[str] = Field(None, description="Exact movie description")
    release_year: Optional[int] = Field(None, description="Year the movie was released")
    directed_by: Optional[List[str]] = Field(None, description="List of director IDs")
    cast: Optional[List[str]] = Field(None, description="List of cast member IDs")
    genre: Optional[List[str]] = Field(None, description="List of genre IDs")

# Crew models
class CrewBase(BaseModel):
    """Base crew model with common fields."""
    name: str = Field(..., description="Crew member's name")

class CrewIn(CrewBase):
    """Crew model for creating new crew members."""
    pass

class CrewOut(CrewBase, MongoModel):
    """Crew model for API responses."""
    pass

# Role models
class RoleBase(BaseModel):
    """Base role model with common fields."""
    title: str = Field(..., description="Role title (e.g., Actor, Director, Producer)")

class RoleIn(RoleBase):
    """Role model for creating new roles."""
    pass

class RoleOut(RoleBase, MongoModel):
    """Role model for API responses."""
    pass

# Genre models
class GenreBase(BaseModel):
    """Base genre model with common fields."""
    name: str = Field(..., description="Genre name")

class GenreIn(GenreBase):
    """Genre model for creating new genres."""
    pass

class GenreOut(GenreBase, MongoModel):
    """Genre model for API responses."""
    pass