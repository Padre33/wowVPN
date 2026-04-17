import base64
import json

shade_key = "shade://eyJpIjoiMTAuMC4wLjIwIiwicyI6IjE4NS4yMDQuNTIuMTM1OjQ0MyIsImsiOiJBQkNEIiwicCI6IjEyMzQifQ"
# This is a sample base64 key
try:
    b64 = shade_key.removeprefix("shade://")
    padded = b64 + "=" * (-len(b64) % 4)
    payload = json.loads(base64.urlsafe_b64decode(padded).decode())
    payload["s"] = "150.241.101.56:443"
    new_b64 = base64.urlsafe_b64encode(
        json.dumps(payload, separators=(',', ':')).encode()
    ).rstrip(b'=').decode()
    print("SUCCESS:", new_b64)
except Exception as e:
    print("FAILED:", e)
