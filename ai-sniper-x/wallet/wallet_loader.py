from pathlib import Path
from solders.keypair import Keypair


def load_or_create_wallet(path: str) -> Keypair:
    key_path = Path(path)
    if key_path.exists():
        data = key_path.read_bytes()
        return Keypair.from_bytes(data)
    keypair = Keypair()
    key_path.write_bytes(keypair.to_bytes())
    return keypair
