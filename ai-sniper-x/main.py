import asyncio
import os
from pathlib import Path
from dotenv import load_dotenv
import yaml

from llm.decision_engine import LocalDecisionEngine
from wallet.wallet_loader import load_or_create_wallet
from wallet.funding_checker import check_funding
from trading.sniper_logic import generate_market_snapshot
from trading.tx_executor import send_transaction
from bridge.bridge_module import bridge_sol_to_btc
from utils import scheduler
from utils.logger import logger


async def main():
    load_dotenv(Path('config/.env'))
    rpc_url = os.getenv('RPC_ENDPOINT')
    wallet_path = os.getenv('WALLET_PATH', 'ghost_secret.key')
    target_profit = float(os.getenv('TARGET_PROFIT_SOL', '0'))
    bridge_enabled = os.getenv('BRIDGE_ENABLED', 'false').lower() == 'true'
    model_path = os.getenv('LLM_MODEL', 'model.gguf')

    settings = yaml.safe_load(Path('config/sniper_settings.yaml').read_text())

    kp = load_or_create_wallet(wallet_path)
    logger.info(f'Using wallet {kp.pubkey()}')

    engine = LocalDecisionEngine(model_path)

    async def trade_cycle():
        balance = await check_funding(rpc_url, kp.pubkey())
        snapshot = generate_market_snapshot()
        decision = engine.ask(open('llm/prompts/trade_prompt.txt').read().format(data=snapshot))
        logger.info(f'Decision: {decision} | Balance: {balance:.4f} SOL')
        if decision == 'BUY':
            # TODO: build and send transaction
            tx_signature = await send_transaction(rpc_url, 'signed_tx_data')
            logger.info(f'Trade sent: {tx_signature}')
        if bridge_enabled and balance >= target_profit:
            await bridge_sol_to_btc(target_profit, os.getenv('BTC_DEST', ''))

    await scheduler.periodic(settings.get('cooldown_seconds', 5), trade_cycle)


if __name__ == '__main__':
    asyncio.run(main())
