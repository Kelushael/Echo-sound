# Modified and sanitized code for GhostSniper
import os
import random
import json
from datetime import datetime
import time
import logging
from logging.handlers import RotatingFileHandler
from dataclasses import dataclass, field

from solders.keypair import Keypair
import requests


class GhostIdentity:
    """Create a basic identity with a generated key pair."""

    def __init__(self):
        self.entropy = os.urandom(64)
        self.keypair = Keypair.from_secret_key(self.entropy[:32])
        self.public = self.keypair.public_key


@dataclass
class SniperConfig:
    """Configuration options for :class:`GhostSniper`."""

    target_min_usd: float = 1000
    target_max_usd: float = 10000
    time_limit_hrs: float = 36
    usd_per_sol: float = 150
    stop_loss_pct: float = 0.05
    take_profit_pct: float = 0.15
    log_file: str = "ghost.log"


class GhostSniper:
    """Simplified trading helper without automatic bridging logic."""

    def __init__(self, bankroll_usd: float = 10, config: SniperConfig | None = None):
        self.cfg = config or SniperConfig()
        self.identity = GhostIdentity()
        self.memory: list[dict] = []
        self.ghost_logs: list[dict] = []
        self.known_whales = {"So1Pump": 90, "Ru6Stealth": -85}
        self.start_time = time.time()
        self.USD_PER_SOL = self.fetch_sol_price()
        # Convert USD bankroll to SOL
        self.bankroll = bankroll_usd / self.USD_PER_SOL
        self.logger = self._setup_logger()

    def _setup_logger(self) -> logging.Logger:
        """Configure a rotating logger for bot activities."""
        logger = logging.getLogger("ghost")
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            handler = RotatingFileHandler(
                self.cfg.log_file, maxBytes=10240, backupCount=3
            )
            formatter = logging.Formatter(
                "%(asctime)s [%(levelname)s] %(message)s", "%Y-%m-%d %H:%M:%S"
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        return logger

    def fetch_sol_price(self):
        """Fetch the current SOL price in USD."""
        try:
            resp = requests.get(
                "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
            )
            price = resp.json()["solana"]["usd"]
            self.logger.info("Fetched SOL price: $%s", price)
            return price
        except Exception:
            # Fall back to an arbitrary price if the request fails.
            self.logger.warning("Could not fetch SOL price; using fallback.")
            return self.cfg.usd_per_sol

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
        return random.randint(10**6, 10**7)

    def _dream_log(self, action, why):
        entry = {"action": action, "why": why, "block": self._current_block()}
        self.logger.info("DREAM %s", json.dumps(entry))

    def _reversal_signal(self, c):
        if len(c) < 3:
            return None
        r = c[-3:]
        if r[0]["c"] > r[0]["o"] and r[1]["c"] < r[1]["o"] and r[2]["c"] > r[2]["o"]:
            return "Micro-bull reversal"
        return None

    def _risk_check(self, pnl: float) -> None:
        """Adjust bankroll with a basic stop-loss/take-profit check."""
        if pnl < 0 and abs(pnl) >= self.cfg.stop_loss_pct * self.bankroll:
            self.logger.info("Stop loss triggered")
            self.bankroll += pnl
        elif pnl > 0 and pnl >= self.cfg.take_profit_pct * self.bankroll:
            self.logger.info("Take profit")
            self.bankroll += pnl

    def execute_trade(self, direction: str, size: float) -> float:
        """Placeholder trade execution returning mocked PnL."""
        # This function simulates trade execution without network calls.
        pnl = random.uniform(-0.02, 0.03) * size
        self.logger.info("Executed %s trade with size %.2f (pnl %.4f)", direction, size, pnl)
        return pnl

    def evaluate_pool(self, token, wallet, lp, age, unlocked_pct, gas, candles):
        import time

        # Target/Timer Logic
        elapsed_hrs = (time.time() - self.start_time) / 3600
        bankroll_usd = self.bankroll * self.USD_PER_SOL
        if bankroll_usd >= self.cfg.target_min_usd or elapsed_hrs > self.cfg.time_limit_hrs:
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
                pnl = self.execute_trade("sell", self.bankroll * 0.2)
                self._risk_check(pnl)
                return "SELL TRIGGERED"
            self._dream_log("burst_trade", "Whale injection")
            pnl = self.execute_trade("buy", self.bankroll * 0.2)
            self._risk_check(pnl)
            return f"BURST {self.bankroll:.2f}"
        else:
            self.logger.info("Skipping token %s; no whale signal", token)

    def run_cycle(self, pools: list[dict]) -> None:
        """Evaluate a batch of pools in sequence."""
        for p in pools:
            self.evaluate_pool(
                p["token"],
                p.get("wallet", ""),
                p.get("lp", 0),
                p.get("age", 0),
                p.get("unlocked_pct", 0),
                p.get("gas", []),
                p.get("candles", []),
            )

