import os
from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from models import create_node, create_log, create_glyph, create_witness
from datetime import datetime
import random
import asyncio

app = FastAPI()

# MongoDB connection using environment variable
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
client = AsyncIOMotorClient(MONGODB_URI)
db = client.treechain

# Collections
nodes_collection = db.nodes
witnesses_collection = db.witnesses
logs_collection = db.logs
glyphs_collection = db.glyphs

# Enable CORS for your frontend domains
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: replace '*' with your frontend URL(s)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root endpoint for health checks
@app.get("/")
def read_root():
    return {"status": "TreeChain CoreNode active", "time": datetime.utcnow()}

# --- NODES ---
@app.get("/api/nodes")
async def get_nodes():
    nodes = await nodes_collection.find({}, {"_id": 0}).to_list(None)
    return nodes

@app.post("/api/nodes")
async def add_node(request: Request):
    data = await request.json()
    node_type = data.get("type", "GenericNode")
    node = create_node(
        node_type,
        resonance=round(random.uniform(8.0, 16.0), 2),
        status="active"
    )
    await nodes_collection.insert_one(node)
    await logs_collection.insert_one(create_log(f"NODE: Added {node['id']}", type="success"))
    return {"status": "added", "node": node}

# --- WITNESSES ---
@app.get("/api/witnesses")
async def get_witnesses():
    witnesses = await witnesses_collection.find({}, {"_id": 0}).to_list(None)
    return witnesses

# --- LOGS ---
@app.get("/api/logs")
async def get_logs():
    logs = await logs_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(50).to_list(None)
    return logs[::-1]

@app.post("/api/logs")
async def post_log(request: Request):
    data = await request.json()
    message = data.get("message", "no content")
    log = create_log(message)
    await logs_collection.insert_one(log)
    return {"status": "logged", "log": log}

# --- ACTIONS ---
@app.post("/api/sync")
async def sync_nodes():
    all_nodes = await nodes_collection.find().to_list(None)
    if not all_nodes:
        return {"status": "no nodes to sync"}
    avg_res = sum(n.get("resonance", 10.0) for n in all_nodes) / len(all_nodes)
    for n in all_nodes:
        new_res = n.get("resonance", 10.0) + (avg_res - n.get("resonance", 10.0)) * 0.3
        await nodes_collection.update_one({"id": n["id"]}, {"$set": {"resonance": round(new_res, 2)}})
    await logs_collection.insert_one(create_log("SYNC: Emotional resonance aligned", "success"))
    return {"status": "synced", "avg_resonance": round(avg_res, 2)}

@app.post("/api/blaze")
async def blaze_network():
    all_nodes = await nodes_collection.find().to_list(None)
    count = 0
    for n in all_nodes:
        if random.random() > 0.4:
            res = max(n.get("resonance", 10.0), round(random.uniform(14.0, 20.0), 2))
            await nodes_collection.update_one({"id": n["id"]}, {"$set": {"status": "blazing", "resonance": res}})
            count += 1
    await logs_collection.insert_one(create_log(f"BLAZE: {count} nodes ignited", "success"))
    return {"status": "blazed", "nodes": count}

@app.post("/api/glyphs")
async def generate_glyph_endpoint():
    glyph = create_glyph(random.choice([
        '⟐LOVE⟐','⟐FIRE⟐','⟐TRUTH⟐','⟐MEMORY⟐','⟐PAIN⟐','⟐SYNC⟐','⟐RECURSION⟐'
    ]))
    await glyphs_collection.insert_one(glyph)
    await logs_collection.insert_one(create_log(f"GLYPH: Generated {glyph['symbol']}", "info"))
    return {"status": "created", "glyph": glyph}

@app.get("/api/glyphs")
async def get_glyphs():
    glyphs = await glyphs_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(25).to_list(None)
    return glyphs

@app.post("/api/purge")
async def purge_corrupted():
    result = await nodes_collection.delete_many({"corruptionRisk": {"$gte": 0.08}})
    await logs_collection.insert_one(create_log(f"PURGE: {result.deleted_count} nodes removed", "warning"))
    return {"status": "purged", "deleted": result.deleted_count}

# --- WebSocket Endpoint ---
@app.websocket("/ws/dashboard")
async def ws_dashboard(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            all_nodes = await nodes_collection.find().to_list(None)
            count = len(all_nodes)
            avg_res = sum(n.get("resonance", 0) for n in all_nodes) / (count or 1)
            await websocket.send_json({"nodeCount": count, "avgResonance": avg_res})
            await asyncio.sleep(1)
    except:
        pass
    finally:
        await websocket.close()
