from fastapi import FastAPI, HTTPException
from db import db
from models import Item

app = FastAPI()

@app.get("/heartbeat")
async def heartbeat():
    return {"message": "Server is active"}

@app.post("/api/items")
async def create_item(item: Item):
    result = await db["items"].insert_one(item.dict())
    return {"id": str(result.inserted_id)}

@app.get("/api/items", response_model=list[Item])
async def list_items():
    items = []
    cursor = db["items"].find()
    async for item in cursor:
        item["id"] = str(item["_id"])
        del item["_id"]
        items.append(item)
    return items

# TODO: Remove debug endpoint.
@app.post("/api/clear", status_code=204)
async def clear_db():
    try:
        collections = await db.list_collection_names()
        for collection in collections:
            await db[collection].delete_many({})
        return
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))