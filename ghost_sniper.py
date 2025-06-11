# Modified and sanitized code for GhostSniper
import os
import random
import json
from datetime import datetime
import time

from solders.keypair import Keypair
import requests


class GhostIdentity:
    """Create a basic identity with a generated key pair."""

    def __init__(self):
        self.entropy = os.urandom(64)
        self.keypair = Keypair.from_secret_key(self.entropy[:32])
        self.public = self.keypair.public_key


class GhostSniper:
    """Simplified trading helper without automatic bridging logic."""

    TARGET_MIN_USD = 1000
    TARGET_MAX_USD = 10000
    TIME_LIMIT_HRS = 36
    START_TIME = None
    USD_PER_SOL = 150  # Updated using fetch_sol_price on init

    def __init__(self, bankroll_usd=10):
        self.identity = GhostIdentity()
        self.memory = []
        self.ghost_logs = []
        self.known_whales = {"So1Pump": 90, "Ru6Stealth": -85}
        self.START_TIME = self.START_TIME or time.time()
        self.USD_PER_SOL = self.fetch_sol_price()
        # Convert USD bankroll to SOL
        self.bankroll = bankroll_usd / self.USD_PER_SOL

    def fetch_sol_price(self):
        """Fetch the current SOL price in USD."""
        try:
            resp = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
            )
            return resp.json()["solana"]["usd"]
        except Exception:
            # Fall back to an arbitrary price if the request fails.
            return 150

    def _get_time_mode(self):
        h = datetime.utcnow().hour
        return "stealth" if h < 6 else "burst" if h < 18 else "defensive"

    def _whale_signal(self, wallet):
        return any(wallet.startswith(k) for k in self.known_whales)

    def _gas_spike(self, gas):
        return gas[-1] > sum(gas[-5:-1]) / 4

    def _avoid_mistake(self, context):
        return any(log["context"] == context for log in self.ghost_logs)

    def log_failure(self, context, reason):
        self.ghost_logs.append(
            {"context": context, "reason": reason, "block": self._current_block()}
        )

    def _current_block(self):
        return random.randint(10 ** 6, 10 ** 7)

    def _dream_log(self, action, why):
        entry = {"action": action, "why": why, "block": self._current_block()}
        print("GHOST DREAM:", json.dumps(entry))

    def _reversal_signal(self, c):
        if len(c) < 3:
            return None
        r = c[-3:]
        if r[0]["c"] > r[0]["o"] and r[1]["c"] < r[1]["o"] and r[2]["c"] > r[2]["o"]:
            return "Micro-bull reversal"
        return None

    def evaluate_pool(self, token, wallet, lp, age, unlocked_pct, gas, candles):
        import time

        # Target/Timer Logic
        elapsed_hrs = (time.time() - self.START_TIME) / 3600
        bankroll_usd = self.bankroll * self.USD_PER_SOL
        if bankroll_usd >= self.TARGET_MIN_USD or elapsed_hrs > self.TIME_LIMIT_HRS:
            self._dream_log(
                "TARGET_REACHED",
                f"Bankroll: ${bankroll_usd:.2f}, Hours: {elapsed_hrs:.2f}",
            )
            # In the original version this would swap and bridge out; we avoid
            # that behavior in the sanitized implementation.
            print(
                "[GHOST] Target reached or time expired. Exiting without external calls."
            )
            return

        # Normal pool evaluation logic
        if self._whale_signal(wallet):
            if lp < 10000 or age < 7 or unlocked_pct > 70:
                self.log_failure(token, "Failed LP/age filter")
                return
            if self._gas_spike(gas):
                self.log_failure(token, "Gas spike abort")
                return
            if self._avoid_mistake(token):
                return
            reversal = self._reversal_signal(candles)
            if reversal:
                self._dream_log("auto-sell", reversal)
                return "SELL TRIGGERED"
            self._dream_log("burst_trade", "Whale injection")
            self.bankroll += self.bankroll * 0.28
            return f"BURST {self.bankroll:.2f}"

