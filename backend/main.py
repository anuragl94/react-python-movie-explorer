from fastapi import FastAPI, HTTPException, Query, Depends, Path
from db import db
from models import Item, MovieIn, MovieOut, CrewIn, CrewOut, GenreIn, GenreOut, RoleIn, RoleOut, MovieFilter, CrewRef, GenreRef
from typing import List, Optional
from bson import ObjectId
from pydantic import HttpUrl, ValidationError

app = FastAPI()

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

@app.get("/heartbeat")
async def heartbeat():
    return {"message": "Server is active"}

@app.get("/api/movies", response_model=List[MovieOut])
async def list_movies(
    title: Optional[str] = Query(None, description="Partial movie title (case-insensitive)"),
    description: Optional[str] = Query(None, description="Exact movie description"),
    release_year: Optional[int] = Query(None, description="Year the movie was released"),
    directed_by_ids: Optional[List[str]] = Query(
        None,
        description="One or more director IDs (comma-separated or repeated)",
        openapi_extra={
            "examples": [
                {"summary": "Multiple directors (comma-separated)", "value": "id1,id2"},
                {"summary": "Multiple directors (repeated)", "value": ["id1", "id2"]}
            ]
        }
    ),
    cast_ids: Optional[List[str]] = Query(
        None,
        description="One or more cast member IDs (comma-separated or repeated)",
        openapi_extra={
            "examples": [
                {"summary": "Multiple cast (comma-separated)", "value": "id1,id2"},
                {"summary": "Multiple cast (repeated)", "value": ["id1", "id2"]}
            ]
        }
    ),
    genre_ids: Optional[List[str]] = Query(
        None,
        description="One or more genre IDs (comma-separated or repeated)",
        openapi_extra={
            "examples": [
                {"summary": "Multiple genres (comma-separated)", "value": "id1,id2"},
                {"summary": "Multiple genres (repeated)", "value": ["id1", "id2"]}
            ]
        }
    )
):
    """
    List all movies, optionally filtered by title, description, release_year, director(s), cast member(s), and genre(s).
    Use repeated or comma-separated values for *_ids fields.
    """
    query = {}
    if title:
        query["title"] = {"$regex": title, "$options": "i"}
    if description:
        query["description"] = description
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

@app.post("/api/movies", response_model=MovieOut, status_code=201)
async def create_movie(movie: MovieIn):
    """
    Create a new movie with the following fields:
    - title: Movie title (required)
    - description: Movie description (optional)
    - release_year: Year the movie was released (required, integer)
    - image_url: URL to movie poster/image (optional, must be valid HTTP/HTTPS URL)
    - user_rating: User rating 1-100 (optional, integer)
    - directed_by: Director's crew ID (required, MongoDB ObjectId as string)
    - cast: List of cast member IDs (required, list of MongoDB ObjectIds as strings)
    - genre: List of genre IDs (required, list of MongoDB ObjectIds as strings)
    
    All referenced IDs (directed_by, cast, genre) must exist in their respective collections.
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

@app.get("/api/movies/{movie_id}", response_model=MovieOut)
async def get_movie(movie_id: str = Path(..., description="MongoDB ObjectId of the movie")):
    """
    Get details for a specific movie by its ID. Returns full objects for directed_by, cast, and genre fields.
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

@app.get("/api/crew", response_model=List[CrewOut])
async def list_crew(
    id: Optional[str] = Query(None, description="MongoDB ObjectId of the crew member"),
    name: Optional[str] = Query(None, description="Partial or full name of the crew member (case-insensitive)")
):
    """
    List all crew, or filter by id and/or partial name (case-insensitive).
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

@app.post("/api/crew", response_model=CrewOut, status_code=201)
async def create_crew(crew: CrewIn):
    doc = crew.dict()
    result = await db["crew"].insert_one(doc)
    return CrewOut(id=str(result.inserted_id), name=crew.name)

@app.get("/api/crew/{crew_id}", response_model=CrewOut)
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

@app.get("/api/genre", response_model=List[GenreOut])
async def list_genre(
    name: Optional[str] = Query(
        None,
        description="Partial or full genre name (case-insensitive)",
        openapi_extra={
            "examples": [
                {"summary": "Partial name", "value": "act"},
                {"summary": "Full name", "value": "Action"}
            ]
        }
    )
):
    """
    List all genres, or filter by partial (case-insensitive) name.
    """
    query = {}
    if name:
        query["name"] = {"$regex": name, "$options": "i"}
    genres = []
    cursor = db["genre"].find(query)
    async for genre in cursor:
        genres.append(GenreOut(id=str(genre["_id"]), name=genre["name"]))
    return genres

@app.post("/api/genre", response_model=GenreOut, status_code=201)
async def create_genre(genre: GenreIn):
    doc = genre.dict()
    result = await db["genre"].insert_one(doc)
    return GenreOut(id=str(result.inserted_id), name=genre.name)

@app.get("/api/role", response_model=List[RoleOut])
async def list_role():
    roles = []
    cursor = db["role"].find()
    async for role in cursor:
        roles.append(RoleOut(id=str(role["_id"]), title=role["title"]))
    return roles

@app.post("/api/role", response_model=RoleOut, status_code=201)
async def create_role(role: RoleIn):
    doc = role.dict()
    result = await db["role"].insert_one(doc)
    return RoleOut(id=str(result.inserted_id), title=role.title)

# TODO: Remove debug endpoint.
@app.post("/api/clear", status_code=200)
async def clear_db():
    try:
        collections = await db.list_collection_names()
        cleared = []
        # Exclude system collections - TODO: Verify this.
        for collection in collections:
            if not collection.startswith("system."):
                await db[collection].delete_many({})
                cleared.append(collection)
        return {"message": "Database cleared", "cleared_collections": cleared}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))