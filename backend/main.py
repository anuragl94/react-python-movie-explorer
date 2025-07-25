from fastapi import FastAPI, HTTPException, Query, Depends, Path
from db import db
from models import Item, MovieIn, MovieOut, CrewIn, CrewOut, GenreIn, GenreOut, RoleIn, RoleOut, MovieFilter
from typing import List, Optional
from bson import ObjectId

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

# TODO: Find a cleaner way?
def movie_filter(
    title: Optional[str] = Query(None),
    description: Optional[str] = Query(None),
    directed_by: Optional[str] = Query(None),
    cast: Optional[List[str]] = Query(None),
    genre: Optional[List[str]] = Query(None),
) -> MovieFilter:
    return MovieFilter(
        title=title,
        description=description,
        directed_by=directed_by,
        cast=cast,
        genre=genre,
    )

@app.get("/heartbeat")
async def heartbeat():
    return {"message": "Server is active"}

@app.get("/api/movies", response_model=List[MovieOut])
async def list_movies(
    filter: MovieFilter = Depends(movie_filter),
    cast_id: Optional[str] = Query(None, description="MongoDB ObjectId of a cast member to filter movies by"),
    genre_id: Optional[str] = Query(None, description="MongoDB ObjectId of a genre to filter movies by")
):
    """
    List all movies, optionally filtered by any combination of fields in MovieFilter.
    You can also filter by a single cast member's id or genre's id using the 'cast_id' or 'genre_id' query parameters.
    Returns MovieOut with related names populated.
    """
    query = {}
    if filter.title:
        query["title"] = filter.title
    if filter.description:
        query["description"] = filter.description
    if filter.directed_by:
        if not ObjectId.is_valid(filter.directed_by):
            raise HTTPException(status_code=400, detail="Invalid directed_by id")
        query["directed_by"] = ObjectId(filter.directed_by)
    if filter.cast:
        query["cast"] = {"$all": parse_objectid_list(filter.cast)}
    if cast_id:
        if not ObjectId.is_valid(cast_id):
            raise HTTPException(status_code=400, detail="Invalid cast_id")
        query["cast"] = ObjectId(cast_id)
    if filter.genre:
        query["genre"] = {"$all": parse_objectid_list(filter.genre)}
    if genre_id:
        if not ObjectId.is_valid(genre_id):
            raise HTTPException(status_code=400, detail="Invalid genre_id")
        query["genre"] = ObjectId(genre_id)
    movies = []
    cursor = db["movies"].find(query)
    async for movie in cursor:
        # Populate names for related fields
        directed_by_doc = await db["crew"].find_one({"_id": movie["directed_by"]})
        cast_docs = db["crew"].find({"_id": {"$in": movie["cast"]}})
        genre_docs = db["genre"].find({"_id": {"$in": movie["genre"]}})
        movie_out = MovieOut(
            id=str(movie["_id"]),
            title=movie["title"],
            description=movie.get("description"),
            directed_by=directed_by_doc["name"] if directed_by_doc else None,
            cast=[doc["name"] async for doc in cast_docs],
            genre=[doc["name"] async for doc in genre_docs],
        )
        movies.append(movie_out)
    return movies

@app.post("/api/movies", response_model=MovieOut, status_code=201)
async def create_movie(movie: MovieIn):
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
        raise HTTPException(status_code=404, detail="directed_by value not found")
    if await db["crew"].count_documents({"_id": {"$in": [ObjectId(cid) for cid in movie.cast]}}) != len(movie.cast):
        raise HTTPException(status_code=404, detail="One or more cast members not found")
    if await db["genre"].count_documents({"_id": {"$in": [ObjectId(gid) for gid in movie.genre]}}) != len(movie.genre):
        raise HTTPException(status_code=404, detail="One or more genres not found")
    doc = movie.dict()
    doc["directed_by"] = ObjectId(doc["directed_by"])
    doc["cast"] = [ObjectId(cid) for cid in doc["cast"]]
    doc["genre"] = [ObjectId(gid) for gid in doc["genre"]]
    result = await db["movies"].insert_one(doc)
    # Populate output
    directed_by_doc = await db["crew"].find_one({"_id": doc["directed_by"]})
    cast_docs = db["crew"].find({"_id": {"$in": doc["cast"]}})
    genre_docs = db["genre"].find({"_id": {"$in": doc["genre"]}})
    return MovieOut(
        id=str(result.inserted_id),
        title=movie.title,
        description=movie.description,
        directed_by=directed_by_doc["name"] if directed_by_doc else None,
        cast=[doc["name"] async for doc in cast_docs],
        genre=[doc["name"] async for doc in genre_docs],
    )

@app.get("/api/movies/{movie_id}", response_model=MovieOut)
async def get_movie(movie_id: str = Path(..., description="MongoDB ObjectId of the movie")):
    """
    Get details for a specific movie by its ID.
    """
    if not ObjectId.is_valid(movie_id):
        raise HTTPException(status_code=400, detail="Invalid movie id")
    movie = await db["movies"].find_one({"_id": ObjectId(movie_id)})
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    directed_by_doc = await db["crew"].find_one({"_id": movie["directed_by"]})
    cast_docs = db["crew"].find({"_id": {"$in": movie["cast"]}})
    genre_docs = db["genre"].find({"_id": {"$in": movie["genre"]}})
    return MovieOut(
        id=str(movie["_id"]),
        title=movie["title"],
        description=movie.get("description"),
        directed_by=directed_by_doc["name"] if directed_by_doc else None,
        cast=[doc["name"] async for doc in cast_docs],
        genre=[doc["name"] async for doc in genre_docs],
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
async def list_genre():
    genres = []
    cursor = db["genre"].find()
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
@app.post("/api/clear", status_code=204)
async def clear_db():
    try:
        collections = await db.list_collection_names()
        # Exclude system collections - TODO: Verify this.
        for collection in collections:
            if not collection.startswith("system."):
                await db[collection].delete_many({})
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))