# database.py
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client["treechain"]

nodes_collection = db["nodes"]
witnesses_collection = db["witnesses"]
glyphs_collection = db["glyphs"]
logs_collection = db["logs"]
