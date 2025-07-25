from fastapi import Query
from pydantic import BaseModel, HttpUrl, Field
from typing import Optional, List

# Shared base for MongoDB id
class MongoModel(BaseModel):
    id: Optional[str] = None  # Always use 'id' in API responses

# Item model (unchanged, but add id for consistency)
class Item(MongoModel):
    name: str
    description: Optional[str] = None
    price: float

## Note for reviewer: I wanted to create single models for each entity such that CREATE requests would expect ids for related entities,
## and GET requests would automatically be more verbose by returning full names as strings, for example
## I am sure that there is a simpler way, but in the interest of time, I'm creating Base, In, Out, Filter models for this purpose.
## Plus, it looks like even the documentation for Pydantic follows this pattern, so I'll stick with this for now.

# Movie
class MovieBase(BaseModel):
    title: str
    description: Optional[str] = None

class MovieIn(MovieBase):
    directed_by: str  # MongoDB ObjectId as string
    cast: List[str]   # List of Crew ObjectIds as strings
    genre: List[str]  # List of Genre ObjectIds as strings

class MovieOut(MovieBase, MongoModel):
    directed_by: str  # Crew name (populated in API response)
    cast: List[str]   # Crew names
    genre: List[str]  # Genre names

class MovieFilter(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    directed_by: Optional[str] = None
    cast: Optional[List[str]] = None
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