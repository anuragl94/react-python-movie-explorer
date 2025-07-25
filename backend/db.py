from motor.motor_asyncio import AsyncIOMotorClient
import os

# Use environment variable for MongoDB URI, fallback to localhost for development
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGO_URI)
db = client["mydb"]