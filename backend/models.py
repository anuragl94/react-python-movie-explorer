from fastapi import Query
from pydantic import BaseModel, HttpUrl, Field, conint
from typing import Optional, List

# Shared base for MongoDB id
class MongoModel(BaseModel):
    id: Optional[str] = None  # Always use 'id' in API responses

# Item model
class Item(MongoModel):
    name: str
    description: Optional[str] = None
    price: float

## Note for reviewer: I wanted to create single models for each entity such that CREATE requests would expect ids for related entities,
## and GET requests would automatically be more verbose by returning full names as strings, for example
## I am sure that there is a simpler way, but in the interest of time, I'm creating Base, In, Out, Filter models for this purpose.
## Plus, it looks like even the documentation for Pydantic follows this pattern, so I'll stick with this for now.

# Reference models for nested objects in MovieOut
class CrewRef(BaseModel):
    id: str
    name: str

class GenreRef(BaseModel):
    id: str
    name: str

# Movie
class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None
    release_year: int = Field(..., description="Year the movie was released in")
    image_url: Optional[HttpUrl] = Field(None, description="URL to the movie's poster or image")
    user_rating: Optional[conint(ge=1, le=100)] = Field(None, description="User rating between 1 and 100")

class MovieIn(MovieBase):
    directed_by: str  # MongoDB ObjectId as string
    cast: List[str]   # List of Crew ObjectIds as strings
    genre: List[str]  # List of Genre ObjectIds as strings

class MovieOut(MovieBase, MongoModel):
    directed_by: Optional[CrewRef]  # Full object for director
    cast: List[CrewRef]             # List of full objects for cast
    genre: List[GenreRef]           # List of full objects for genres

class MovieFilter(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    release_year: Optional[int] = Field(None, description="Year the movie was released in")
    directed_by: Optional[List[str]] = None  # Accepts multiple director ids
    cast: Optional[List[str]] = None         # Accepts multiple cast ids
    genre: Optional[List[str]] = None

# Crew (Everyone involved with a movie)
class CrewBase(BaseModel):
    name: str

class CrewIn(CrewBase):
    pass

class CrewOut(CrewBase, MongoModel):
    # Add list of associated movies???
    pass

# Role (Actor, Director, Producer, ...)
class RoleBase(BaseModel):
    title: str

class RoleIn(RoleBase):
    pass

class RoleOut(RoleBase, MongoModel):
    pass

# Genre
class GenreBase(BaseModel):
    name: str

class GenreIn(GenreBase):
    pass

class GenreOut(GenreBase, MongoModel):
    pass