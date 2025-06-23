from pathlib import Path
from .wallet_loader import load_or_create_wallet

if __name__ == "__main__":
    path = Path("ghost_secret.key")
    keypair = load_or_create_wallet(path)
    print(f"Wallet saved to {path}\nAddress: {keypair.pubkey()}")
