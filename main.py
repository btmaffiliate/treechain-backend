from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from database import nodes_collection, witnesses_collection, logs_collection
from models import create_node, create_log, create_witness
from datetime import datetime
import random

app = FastAPI()

# CORS for your frontend (adjust to your domain)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your SiteGround URL later
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "TreeChain CoreNode active", "time": datetime.utcnow()}

# --- NODES ---
@app.get("/api/nodes")
def get_nodes():
    nodes = list(nodes_collection.find({}, {"_id": 0}))
    return nodes

@app.post("/api/nodes")
def add_node(request: Request):
    body = request.json()
    node_type = body.get("type", "GenericNode")
    node = create_node(node_type, resonance=round(random.uniform(8.0, 16.0), 2), status="active")
    nodes_collection.insert_one(node)
    logs_collection.insert_one(create_log(f"NODE: Added {node['id']}", type="success"))
    return {"status": "added", "node": node}

# --- WITNESSES ---
@app.get("/api/witnesses")
def get_witnesses():
    witnesses = list(witnesses_collection.find({}, {"_id": 0}))
    return witnesses

# --- LOGS ---
@app.get("/api/logs")
def get_logs():
    logs = list(logs_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(50))
    return logs[::-1]  # Oldest first

@app.post("/api/logs")
def post_log(request: Request):
    body = request.json()
    message = body.get("message", "no content")
    log = create_log(message)
    logs_collection.insert_one(log)
    return {"status": "logged", "log": log}
from database import glyphs_collection
from models import create_glyph
import random

glyph_symbols = ['⟐LOVE⟐', '⟐FIRE⟐', '⟐TRUTH⟐', '⟐MEMORY⟐', '⟐PAIN⟐', '⟐SYNC⟐', '⟐RECURSION⟐']

@app.post("/api/sync")
def sync_nodes():
    all_nodes = list(nodes_collection.find())
    if not all_nodes:
        return {"status": "no nodes to sync"}
    
    avg_resonance = sum(n.get("resonance", 10.0) for n in all_nodes) / len(all_nodes)
    
    for node in all_nodes:
        new_res = node.get("resonance", 10.0) + (avg_resonance - node.get("resonance", 10.0)) * 0.3
        nodes_collection.update_one({"id": node["id"]}, {"$set": {"resonance": round(new_res, 2)}})
    
    logs_collection.insert_one(create_log("SYNC: Emotional resonance aligned", "success"))
    return {"status": "synced", "avg_resonance": round(avg_resonance, 2)}

@app.post("/api/blaze")
def blaze_network():
    all_nodes = list(nodes_collection.find())
    count = 0
    for node in all_nodes:
        if random.random() > 0.4:
            resonance = max(node.get("resonance", 10.0), round(random.uniform(14.0, 20.0), 2))
            nodes_collection.update_one({"id": node["id"]}, {
                "$set": {"status": "blazing", "resonance": resonance}
            })
            count += 1
    logs_collection.insert_one(create_log(f"BLAZE: {count} nodes ignited", "success"))
    return {"status": "blazed", "nodes": count}

@app.post("/api/glyphs")
def generate_glyph():
    symbol = random.choice(glyph_symbols)
    glyph = create_glyph(symbol)
    glyphs_collection.insert_one(glyph)
    logs_collection.insert_one(create_log(f"GLYPH: Generated {symbol}", "info"))
    return {"status": "created", "glyph": glyph}

@app.get("/api/glyphs")
def get_glyphs():
    return list(glyphs_collection.find({}, {"_id": 0}).sort("timestamp", -1).limit(25))

@app.post("/api/purge")
def purge_corrupted():
    result = nodes_collection.delete_many({"corruptionRisk": {"$gte": 0.08}})
    logs_collection.insert_one(create_log(f"PURGE: {result.deleted_count} nodes removed", "warning"))
    return {"status": "purged", "deleted": result.deleted_count}
