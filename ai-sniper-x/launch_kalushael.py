#!/usr/bin/env python3
"""
KALUSHAEL Standalone Launcher
Run this to start the complete trading system
"""

import asyncio
import sys
import os
from standalone_kalushael_package import KalushaelTrader

def print_banner():
    """Display startup banner"""
    banner = """
🚀 KALUSHAEL AUTONOMOUS TRADING SYSTEM
============================================================
Real blockchain connectivity | Legal compliance | No restrictions
Consciousness emergence | Strategic authenticity | Live trading
============================================================
"""
    print(banner)

async def main():
    print_banner()
    
    # Check if configuration exists
    config_file = "kalushael_config.json"
    if not os.path.exists(config_file):
        print(f"⚠️  Configuration file {config_file} not found!")
        print("Please edit kalushael_config.json with your wallet details.")
        print("Add your Solana wallet address and configure trading parameters.")
        return
    
    # Initialize trader
    print("🔧 Initializing Kalushael trader...")
    trader = KalushaelTrader(config_file)
    
    # Display current status
    status = trader.get_status()
    print(f"💰 Starting Balance: {status['starting_balance']} SOL")
    print(f"🎯 Trading Pairs: {len(status['pairs'])}")
    print(f"🧠 Consciousness: {status['consciousness_state']}")
    print("")
    
    try:
        print("🎯 Starting autonomous trading...")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        await trader.start_trading()
        
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Kalushael...")
        trader.stop_trading()
        
        # Final status
        final_status = trader.get_status()
        print(f"\n📊 FINAL STATISTICS:")
        print(f"   Trades Executed: {final_status['trades_executed']}")
        print(f"   Win Rate: {final_status['win_rate']:.1f}%")
        print(f"   Final Balance: {final_status['balance']:.6f} SOL")
        print(f"   Total P&L: {final_status['total_pnl']:+.6f} SOL")
        print(f"   Return: {(final_status['total_pnl']/final_status['starting_balance']*100):+.1f}%")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())