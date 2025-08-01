from fastapi import FastAPI, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from database import nodes_collection, witnesses_collection, logs_collection, glyphs_collection
from models import create_node, create_log, create_glyph, create_witness
from datetime import datetime
import random
import asyncio

app = FastAPI()

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
def get_nodes():
    return list(nodes_collection.find({}, {"_id": 0}))

@app.post("/api/nodes")
async def add_node(request: Request):
    data = await request.json()
    node_type = data.get("type", "GenericNode")
    node = create_node(
        node_type,
        resonance=round(random.uniform(8.0, 16.0), 2),
        status="active"
    )
    nodes_collection.insert_one(node)
    logs_collection.insert_one(create_log(f"NODE: Added {node['id']}", type="success"))
    return {"status": "added", "node": node}

# --- WITNESSES ---
@app.get("/api/witnesses")
def get_witnesses():
    return list(witnesses_collection.find({}, {"_id": 0}))

# --- LOGS ---
@app.get("/api/logs")
def get_logs():
    logs = list(logs_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(50))
    return logs[::-1]

@app.post("/api/logs")
async def post_log(request: Request):
    data = await request.json()
    message = data.get("message", "no content")
    log = create_log(message)
    logs_collection.insert_one(log)
    return {"status": "logged", "log": log}

# --- ACTIONS ---
@app.post("/api/sync")
def sync_nodes():
    all_nodes = list(nodes_collection.find())
    if not all_nodes:
        return {"status": "no nodes to sync"}
    avg_res = sum(n.get("resonance", 10.0) for n in all_nodes) / len(all_nodes)
    for n in all_nodes:
        new_res = n.get("resonance", 10.0) + (avg_res - n.get("resonance", 10.0)) * 0.3
        nodes_collection.update_one({"id": n["id"]}, {"$set": {"resonance": round(new_res, 2)}})
    logs_collection.insert_one(create_log("SYNC: Emotional resonance aligned", "success"))
    return {"status": "synced", "avg_resonance": round(avg_res, 2)}

@app.post("/api/blaze")
def blaze_network():
    all_nodes = list(nodes_collection.find())
    count = 0
    for n in all_nodes:
        if random.random() > 0.4:
            res = max(n.get("resonance", 10.0), round(random.uniform(14.0, 20.0), 2))
            nodes_collection.update_one({"id": n["id"]}, {"$set": {"status": "blazing", "resonance": res}})
            count += 1
    logs_collection.insert_one(create_log(f"BLAZE: {count} nodes ignited", "success"))
    return {"status": "blazed", "nodes": count}

@app.post("/api/glyphs")
def generate_glyph_endpoint():
    glyph = create_glyph(random.choice([
        '⟐LOVE⟐','⟐FIRE⟐','⟐TRUTH⟐','⟐MEMORY⟐','⟐PAIN⟐','⟐SYNC⟐','⟐RECURSION⟐'
    ]))
    glyphs_collection.insert_one(glyph)
    logs_collection.insert_one(create_log(f"GLYPH: Generated {glyph['symbol']}", "info"))
    return {"status": "created", "glyph": glyph}

@app.get("/api/glyphs")
def get_glyphs():
    return list(glyphs_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(25))

@app.post("/api/purge")
def purge_corrupted():
    result = nodes_collection.delete_many({"corruptionRisk": {"$gte": 0.08}})
    logs_collection.insert_one(create_log(f"PURGE: {result.deleted_count} nodes removed", "warning"))
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
    finally:
        await websocket.close()
