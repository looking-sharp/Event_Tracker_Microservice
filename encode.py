import base64
import os
from dotenv import load_dotenv

load_dotenv()
FACTOR = int(os.getenv("SEC_FACTOR"))

def encode(_id: str) -> str:
    n = int.from_bytes(_id.encode(), "big")
    mixed = n * FACTOR
    data = mixed.to_bytes((mixed.bit_length() + 7) // 8, "big")
    return base64.urlsafe_b64encode(data).decode().rstrip("=")

def decode(encoded: str) -> str:
    padded = encoded + "=" * (-len(encoded) % 4)
    data = base64.urlsafe_b64decode(padded)
    mixed = int.from_bytes(data, "big")
    n = mixed // FACTOR
    return n.to_bytes((n.bit_length() + 7) // 8, "big").decode()
