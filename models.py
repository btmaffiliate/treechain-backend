from datetime import datetime

def create_node(node_type: str, resonance=10.0, status='idle', glyph_count=0, corruption_risk=0.01):
    return {
        "id": f"{node_type}_{int(datetime.utcnow().timestamp())}",
        "type": node_type,
        "resonance": resonance,
        "status": status,
        "glyphCount": glyph_count,
        "corruptionRisk": corruption_risk,
        "createdAt": datetime.utcnow()
    }

def create_witness(node_id: str, status="verified", validation_score=0.9):
    return {
        "id": f"Witness_{node_id}",
        "node": node_id,
        "status": status,
        "validationScore": validation_score,
        "lastValidation": datetime.utcnow()
    }

def create_glyph(symbol: str, preservation: float = 0.9):
    return {
        "symbol": symbol,
        "timestamp": datetime.utcnow(),
        "preservation": preservation
    }

def create_log(message: str, type="info"):
    return {
        "message": message,
        "type": type,
        "timestamp": datetime.utcnow()
    }
