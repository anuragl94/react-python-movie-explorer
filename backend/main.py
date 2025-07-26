from fastapi import FastAPI, HTTPException, Query, Depends, Path
from db import db
from models import Item, MovieIn, MovieOut, CrewIn, CrewOut, GenreIn, GenreOut, RoleIn, RoleOut, MovieFilter, CrewRef, GenreRef
from typing import List, Optional
from bson import ObjectId
from pydantic import HttpUrl, ValidationError

app = FastAPI(
    title="The Local Movie DB API",
    description="A RESTful API for managing movies, crew members, and genres",
    version="1.0.0",
    docs_url="/docs"
)

# Helper to validate ObjectId
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError('Invalid ObjectId')
        return ObjectId(v)

def get_name_by_id(collection, oid):
    # Helper to get name/title by id from a collection
    return db[collection].find_one({'_id': ObjectId(oid)})

def parse_objectid_list(id_list):
    try:
        return [ObjectId(i) for i in id_list]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid ObjectId in list")

def split_csv(values: Optional[List[str]]) -> Optional[List[str]]:
    if values is None:
        return None
    result = []
    for v in values:
        result.extend([x for x in v.split(',') if x])
    return result if result else None

# TODO: Find a cleaner way?
def movie_filter(
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    directed_by: Optional[List[str]] = Query(None),
    cast: Optional[List[str]] = Query(None),
    genre: Optional[List[str]] = Query(None),
) -> MovieFilter:
    return MovieFilter(
        title=title,
        description=description,
        directed_by=split_csv(directed_by),
        cast=split_csv(cast),
        genre=split_csv(genre),
    )

def safe_url(url):
    if url is None:
        return None
    try:
        return str(HttpUrl(url))
    except (ValidationError, ValueError):
        return None

def safe_rating(rating):
    if rating is None:
        return None
    try:
        rating = int(rating)
        if 1 <= rating <= 100:
            return rating
    except Exception:
        pass
    return None

@app.get("/heartbeat", tags=["Health"])
async def heartbeat():
    """
    Health check endpoint to verify the server is running. Reserved for monitoring purposes - not to be used by client apps.
    """
    return {"message": "Server is alive"}

@app.get("/api/movies", response_model=List[MovieOut], tags=["Movies"])
async def list_movies(
    title: Optional[str] = Query(None, description="Partial movie title (case-insensitive)"),
    description: Optional[str] = Query(None, description="Movie overview"),
    release_year: Optional[int] = Query(None, description="Year the movie was released in"),
    directed_by_ids: Optional[List[str]] = Query(
        None,
        description="One or more director IDs (comma-separated or repeated)",
        example="507f1f77bcf86cd799439011,507f1f77bcf86cd799439012"
    ),
    cast_ids: Optional[List[str]] = Query(
        None,
        description="One or more cast member IDs (comma-separated or repeated)",
        example="507f1f77bcf86cd799439013,507f1f77bcf86cd799439014"
    ),
    genre_ids: Optional[List[str]] = Query(
        None,
        description="One or more genre IDs (comma-separated or repeated)",
        example="507f1f77bcf86cd799439015,507f1f77bcf86cd799439016"
    )
):
    """
    List all movies with optional filtering.
    
    **Filters:**
    - `title`: Partial match (case-insensitive)
    - `release_year`: Exact year match
    - `directed_by_ids`: Filter by director(s) - accepts multiple IDs
    - `cast_ids`: Filter by cast member(s) - accepts multiple IDs  
    - `genre_ids`: Filter by genre(s) - accepts multiple IDs
    
    **Examples:**
    - `/api/movies?title=matrix` - Find movies with "matrix" in the title
    - `/api/movies?release_year=1994` - Movies released in 1994
    - `/api/movies?directed_by_ids=id1,id2` - Movies by specific directors
    """
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    if release_year is not None:
        query["release_year"] = release_year
    if directed_by_ids:
        try:
            director_obj_ids = [ObjectId(did) for did in split_csv(directed_by_ids)]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid directed_by id(s)")
        query["directed_by"] = {"$in": director_obj_ids}
    if cast_ids:
        try:
            cast_obj_ids = [ObjectId(cid) for cid in split_csv(cast_ids)]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid cast id(s)")
        query["cast"] = {"$all": cast_obj_ids}
    if genre_ids:
        try:
            genre_obj_ids = [ObjectId(gid) for gid in split_csv(genre_ids)]
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid genre id(s)")
        query["genre"] = {"$all": genre_obj_ids}
    movies = []
    cursor = db["movies"].find(query)
    async for movie in cursor:
        # Fetch full directed_by object
        directed_by_doc = await db["crew"].find_one({"_id": movie["directed_by"]})
        directed_by = None
        if directed_by_doc:
            directed_by = CrewRef(id=str(directed_by_doc["_id"]), name=directed_by_doc["name"])
        # Fetch full cast objects
        cast_docs = db["crew"].find({"_id": {"$in": movie["cast"]}})
        cast = [CrewRef(id=str(doc["_id"]), name=doc["name"]) async for doc in cast_docs]
        # Fetch full genre objects
        genre_docs = db["genre"].find({"_id": {"$in": movie["genre"]}})
        genre = [GenreRef(id=str(doc["_id"]), name=doc["name"]) async for doc in genre_docs]
        movies.append(MovieOut(
            id=str(movie["_id"]),
            title=movie["title"],
            description=movie.get("description"),
            release_year=movie.get("release_year"),
            image_url=safe_url(movie.get("image_url")),
            user_rating=safe_rating(movie.get("user_rating")),
            directed_by=directed_by,
            cast=cast,
            genre=genre,
        ))
    return movies

@app.post("/api/movies", response_model=MovieOut, status_code=201, tags=["Movies"])
async def create_movie(movie: MovieIn):
    """
    Create a new entry for a movie. Duplicates are allowed.
    
    **Required Fields:**
    - `title`: Movie title
    - `release_year`: Year the movie was released
    - `directed_by`: Director's ID (crew) (MongoDB ObjectId)
    - `cast`: List of cast member IDs (crew) (MongoDB ObjectIds)
    - `genre`: List of genre IDs (MongoDB ObjectIds)
    
    **Optional Fields:**
    - `description`: Movie overview
    - `image_url`: Valid HTTP/HTTPS URL to movie poster
    - `user_rating`: Integer between 1-100
    
    **Validation:**
    - All referenced IDs must exist in their respective collections
    - Image URL must be a valid HTTP/HTTPS URL
    - User rating must be between 1-100
    """
    # Validate referenced IDs
    if not ObjectId.is_valid(movie.directed_by):
        raise HTTPException(status_code=400, detail="Invalid directed_by id")
    for cid in movie.cast:
        if not ObjectId.is_valid(cid):
            raise HTTPException(status_code=400, detail="Invalid cast id")
    for gid in movie.genre:
        if not ObjectId.is_valid(gid):
            raise HTTPException(status_code=400, detail="Invalid genre id")
    # Check existence
    if not await db["crew"].find_one({"_id": ObjectId(movie.directed_by)}):
        raise HTTPException(status_code=404, detail="Directed_by crew not found")
    if await db["crew"].count_documents({"_id": {"$in": [ObjectId(cid) for cid in movie.cast]}}) != len(movie.cast):
        raise HTTPException(status_code=404, detail="One or more cast members not found")
    if await db["genre"].count_documents({"_id": {"$in": [ObjectId(gid) for gid in movie.genre]}}) != len(movie.genre):
        raise HTTPException(status_code=404, detail="One or more genres not found")
    doc = movie.dict(exclude_unset=True)
    # Convert HttpUrl to string for MongoDB storage
    if "image_url" in doc and doc["image_url"] is not None:
        doc["image_url"] = str(doc["image_url"])
    doc["directed_by"] = ObjectId(doc["directed_by"])
    doc["cast"] = [ObjectId(cid) for cid in doc["cast"]]
    doc["genre"] = [ObjectId(gid) for gid in doc["genre"]]
    # Ensure all fields are present
    doc.setdefault("image_url", None)
    doc.setdefault("user_rating", None)
    doc.setdefault("release_year", None)
    result = await db["movies"].insert_one(doc)
    # Fetch full directed_by object
    directed_by_doc = await db["crew"].find_one({"_id": doc["directed_by"]})
    directed_by = None
    if directed_by_doc:
        directed_by = CrewRef(id=str(directed_by_doc["_id"]), name=directed_by_doc["name"])
    # Fetch full cast objects
    cast_docs = db["crew"].find({"_id": {"$in": doc["cast"]}})
    cast = [CrewRef(id=str(c["_id"]), name=c["name"]) async for c in cast_docs]
    # Fetch full genre objects
    genre_docs = db["genre"].find({"_id": {"$in": doc["genre"]}})
    genre = [GenreRef(id=str(g["_id"]), name=g["name"]) async for g in genre_docs]
    return MovieOut(
        id=str(result.inserted_id),
        title=movie.title,
        description=movie.description,
        release_year=movie.release_year,
        image_url=safe_url(doc.get("image_url")),
        user_rating=safe_rating(doc.get("user_rating")),
        directed_by=directed_by,
        cast=cast,
        genre=genre,
    )

@app.get("/api/movies/{movie_id}", response_model=MovieOut, tags=["Movies"])
async def get_movie(movie_id: str = Path(..., description="MongoDB ObjectId of the movie")):
    """
    Get details for a specific movie by its ID.
    
    Returns the movie with full objects for:
    - `directed_by`: Director information
    - `cast`: List of cast members with names
    - `genre`: List of genres with names
    """
    if not ObjectId.is_valid(movie_id):
        raise HTTPException(status_code=400, detail="Invalid movie id")
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    # Fetch full directed_by object
    directed_by_doc = await db["crew"].find_one({"_id": movie["directed_by"]})
    directed_by = None
    if directed_by_doc:
        directed_by = CrewRef(id=str(directed_by_doc["_id"]), name=directed_by_doc["name"])
    # Fetch full cast objects
    cast_docs = db["crew"].find({"_id": {"$in": movie["cast"]}})
    cast = [CrewRef(id=str(doc["_id"]), name=doc["name"]) async for doc in cast_docs]
    # Fetch full genre objects
    genre_docs = db["genre"].find({"_id": {"$in": movie["genre"]}})
    genre = [GenreRef(id=str(doc["_id"]), name=doc["name"]) async for doc in genre_docs]
    return MovieOut(
        id=str(movie["_id"]),
        title=movie["title"],
        description=movie.get("description"),
        release_year=movie.get("release_year"),
        image_url=safe_url(movie.get("image_url")),
        user_rating=safe_rating(movie.get("user_rating")),
        directed_by=directed_by,
        cast=cast,
        genre=genre,
    )

@app.get("/api/crew", response_model=List[CrewOut], tags=["Crew"])
async def list_crew(
    id: Optional[str] = Query(None, description="MongoDB ObjectId of the crew member"),
    name: Optional[str] = Query(None, description="Partial or full name of the crew member (case-insensitive)")
):
    """
    List all crew members with optional filtering.
    
    **Filters:**
    - `id`: Exact crew member ID
    - `name`: Partial name match (case-insensitive)
    
    **Examples:**
    - `/api/crew?name=christopher` - Find crew members with "christopher" in name
    - `/api/crew?id=507f1f77bcf86cd799439011` - Get specific crew member
    """
    query = {}
    if id:
        if not ObjectId.is_valid(id):
            raise HTTPException(status_code=400, detail="Invalid crew id")
        query["_id"] = ObjectId(id)
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    crew = []
    cursor = db["crew"].find(query)
    async for member in cursor:
        crew.append(CrewOut(id=str(member["_id"]), name=member["name"]))
    return crew

@app.post("/api/crew", response_model=CrewOut, status_code=201, tags=["Crew"])
async def create_crew(crew: CrewIn):
    """
    Create a new crew member.
    
    **Required Fields:**
    - `name`: Crew member's name
    """
    doc = crew.dict()
    result = await db["crew"].insert_one(doc)
    return CrewOut(id=str(result.inserted_id), name=crew.name)

@app.get("/api/crew/{crew_id}", response_model=CrewOut, tags=["Crew"])
async def get_crew(crew_id: str = Path(..., description="MongoDB ObjectId of the crew member")):
    """
    Get details for a specific crew member by their ID.
    """
    if not ObjectId.is_valid(crew_id):
        raise HTTPException(status_code=400, detail="Invalid crew id")
    crew = await db["crew"].find_one({"_id": ObjectId(crew_id)})
    if not crew:
        raise HTTPException(status_code=404, detail="Crew member not found")
    return CrewOut(id=str(crew["_id"]), name=crew["name"])

@app.get("/api/genre", response_model=List[GenreOut], tags=["Genres"])
async def list_genre(
    name: Optional[str] = Query(
        None,
        description="Partial or full genre name (case-insensitive)",
        example="action"
    )
):
    """
    List all genres with optional filtering.
    
    **Filters:**
    - `name`: Partial name match (case-insensitive)
    
    **Examples:**
    - `/api/genre?name=fiction` - Find genres with "fiction" in the name (Fiction, Science Fiction, etc.)
    """
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    genres = []
    cursor = db["genre"].find(query)
    async for genre in cursor:
        genres.append(GenreOut(id=str(genre["_id"]), name=genre["name"]))
    return genres

@app.post("/api/genre", response_model=GenreOut, status_code=201, tags=["Genres"])
async def create_genre(genre: GenreIn):
    """
    Create a new genre.
    
    **Required Fields:**
    - `name`: Genre name
    """
    doc = genre.dict()
    result = await db["genre"].insert_one(doc)
    return GenreOut(id=str(result.inserted_id), name=genre.name)

@app.get("/api/role", response_model=List[RoleOut], tags=["Roles"])
async def list_role():
    """
    List all available roles (Actor, Director, Producer, etc.).
    """
    roles = []
    cursor = db["role"].find()
    async for role in cursor:
        roles.append(RoleOut(id=str(role["_id"]), title=role["title"]))
    return roles

@app.post("/api/role", response_model=RoleOut, status_code=201, tags=["Roles"])
async def create_role(role: RoleIn):
    """
    Create a new role.
    
    **Required Fields:**
    - `title`: Role title (e.g., "Actor", "Director", "Producer")
    """
    doc = role.dict()
    result = await db["role"].insert_one(doc)
    return RoleOut(id=str(result.inserted_id), title=role.title)

@app.post("/api/clear", status_code=200, tags=["Debug"])
async def clear_db():
    """
    Clear all data from the database.
    
    **Warning:** This will delete all movies, crew members, genres, and roles.
    This endpoint is for development/debugging purposes only. REMOVE before production deployment.
    """
    try:
        collections = await db.list_collection_names()
        cleared = []
        # Exclude system collections
        for collection in collections:
            if not collection.startswith("system."):
                await db[collection].delete_many({})
                cleared.append(collection)
        return {"message": "Database cleared", "cleared_collections": cleared}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))