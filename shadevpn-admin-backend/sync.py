import os
import json
import base64
import secrets
from datetime import datetime, timezone

# We use a local config directory for development, 
# and fall back to /etc/aivpn in production via environment variable
CLIENTS_JSON_PATH = os.environ.get("AIVPN_CLIENTS_JSON", os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "config", "clients.json")))

def read_clients_db():
    if not os.path.exists(CLIENTS_JSON_PATH):
        # Create default empty template matching the Rust struct ClientDbFile
        return {
            "clients": [],
            "next_octet": 2
        }
    with open(CLIENTS_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def write_clients_db(data):
    os.makedirs(os.path.dirname(CLIENTS_JSON_PATH), exist_ok=True)
    with open(CLIENTS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def generate_key_and_add_to_json(username: str) -> dict:
    """
    Generates credentials and appends to the JSON file for the Rust Core to hot-reload.
    Returns a dict containing id, psk, vpn_ip etc.
    """
    db = read_clients_db()
    
    # 1. Ensure username uniqueness in rust db 
    for c in db.get("clients", []):
        if c.get("name") == username:
            raise ValueError(f"Client {username} already exists in clients.json")
            
    # 2. Get VPN IP allocation
    octet = db.get("next_octet", 2)
    if octet > 254:
        raise ValueError("No more VPN IPs available")
        
    vpn_ip = f"10.0.0.{octet}"
    db["next_octet"] = octet + 1
    
    # 3. Generate secure cryptographic IDs and Keys for ShadeVPN
    client_id = secrets.token_hex(4) # 4 bytes -> 8 hex chars for AIVPN compatibility
    psk_bytes = secrets.token_bytes(32) # 32 bytes for ChaCha20Poly1305
    psk_b64 = base64.b64encode(psk_bytes).decode("utf-8")
    
    # 4. Construct client object
    now_iso = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    
    new_client = {
        "id": client_id,
        "name": username,
        "psk": psk_b64,
        "vpn_ip": vpn_ip,
        "enabled": True,
        "created_at": now_iso,
        "stats": {
            "bytes_in": 0,
            "bytes_out": 0,
            "last_connected": None,
            "total_connections": 0,
            "last_handshake": None
        }
    }
    
    if "clients" not in db:
        db["clients"] = []
    
    db["clients"].append(new_client)
    write_clients_db(db)
    
    return new_client
