import hashlib

def static_hash(id) -> str:
    return hashlib.sha256(id.encode()).hexdigest()