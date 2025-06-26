#!/usr/bin/env python3
"""
Live Crypto Sniper Configuration
Setup and configuration for real exchange trading
"""

import os
from typing import Dict, Any

class SniperConfig:
    """Configuration for live crypto sniper"""
    
    def __init__(self):
        # Trading parameters
        self.INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', '90.0'))
        self.MAX_TRADE_SIZE = float(os.getenv('MAX_TRADE_SIZE', '20.0'))
        self.STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', '0.15'))  # 15%
        self.TAKE_PROFIT_PERCENT = float(os.getenv('TAKE_PROFIT_PERCENT', '0.25'))  # 25%
        self.MAX_CONCURRENT_TRADES = int(os.getenv('MAX_CONCURRENT_TRADES', '3'))
        
        # Risk management
        self.MIN_VOLUME_USD = float(os.getenv('MIN_VOLUME_USD', '500000'))  # $500k minimum volume
        self.MIN_PRICE_MOVEMENT = float(os.getenv('MIN_PRICE_MOVEMENT', '3.0'))  # 3% minimum movement
        self.MAX_PRICE_MOVEMENT = float(os.getenv('MAX_PRICE_MOVEMENT', '50.0'))  # 50% maximum movement
        self.MAX_POSITION_TIME = int(os.getenv('MAX_POSITION_TIME', '3600'))  # 1 hour max hold
        
        # Exchange configuration
        self.PREFERRED_EXCHANGES = ['binance', 'kucoin', 'coinbasepro']
        self.TRADING_PAIRS = ['USDT', 'BUSD', 'USD']
        
        # API endpoints
        self.COINGECKO_API = "https://api.coingecko.com/api/v3"
        self.SCAN_INTERVAL = int(os.getenv('SCAN_INTERVAL', '30'))  # 30 seconds
        
    def get_exchange_credentials(self) -> Dict[str, Dict[str, str]]:
        """Get exchange API credentials from environment"""
        return {
            'binance': {
                'apiKey': os.getenv('BINANCE_API_KEY', ''),
                'secret': os.getenv('BINANCE_SECRET', ''),
                'sandbox': os.getenv('BINANCE_SANDBOX', 'false').lower() == 'true'
            },
            'kucoin': {
                'apiKey': os.getenv('KUCOIN_API_KEY', ''),
                'secret': os.getenv('KUCOIN_SECRET', ''),
                'passphrase': os.getenv('KUCOIN_PASSPHRASE', ''),
                'sandbox': os.getenv('KUCOIN_SANDBOX', 'false').lower() == 'true'
            },
            'coinbasepro': {
                'apiKey': os.getenv('COINBASE_API_KEY', ''),
                'secret': os.getenv('COINBASE_SECRET', ''),
                'passphrase': os.getenv('COINBASE_PASSPHRASE', ''),
                'sandbox': os.getenv('COINBASE_SANDBOX', 'false').lower() == 'true'
            }
        }
    
    def validate_credentials(self) -> Dict[str, bool]:
        """Validate which exchanges have complete credentials"""
        creds = self.get_exchange_credentials()
        validation = {}
        
        for exchange, config in creds.items():
            if exchange == 'binance':
                validation[exchange] = bool(config['apiKey'] and config['secret'])
            elif exchange == 'kucoin':
                validation[exchange] = bool(config['apiKey'] and config['secret'] and config['passphrase'])
            elif exchange == 'coinbasepro':
                validation[exchange] = bool(config['apiKey'] and config['secret'] and config['passphrase'])
            else:
                validation[exchange] = False
        
        return validation
    
    def get_trading_strategy_config(self) -> Dict[str, Any]:
        """Get trading strategy configuration"""
        return {
            'momentum_threshold': 0.05,  # 5% momentum threshold
            'volume_spike_multiplier': 2.0,  # 2x volume spike
            'rsi_overbought': 70,
            'rsi_oversold': 30,
            'min_market_cap': 10000000,  # $10M minimum market cap
            'max_market_cap_rank': 300,  # Top 300 coins only
        }

def create_env_template():
    """Create .env template file for user configuration"""
    template = """# Live Crypto Sniper Environment Configuration
# Copy this to .env and fill in your actual values

# Trading Parameters
INITIAL_CAPITAL=90.0
MAX_TRADE_SIZE=20.0
STOP_LOSS_PERCENT=0.15
TAKE_PROFIT_PERCENT=0.25
MAX_CONCURRENT_TRADES=3

# Risk Management
MIN_VOLUME_USD=500000
MIN_PRICE_MOVEMENT=3.0
MAX_PRICE_MOVEMENT=50.0
MAX_POSITION_TIME=3600

# Binance Exchange (Get from https://binance.com/en/my/settings/api-management)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_SECRET=your_binance_secret_here
BINANCE_SANDBOX=false

# KuCoin Exchange (Get from https://kucoin.com/account/api)
KUCOIN_API_KEY=your_kucoin_api_key_here
KUCOIN_SECRET=your_kucoin_secret_here
KUCOIN_PASSPHRASE=your_kucoin_passphrase_here
KUCOIN_SANDBOX=false

# Coinbase Pro Exchange (Get from https://pro.coinbase.com/profile/api)
COINBASE_API_KEY=your_coinbase_api_key_here
COINBASE_SECRET=your_coinbase_secret_here
COINBASE_PASSPHRASE=your_coinbase_passphrase_here
COINBASE_SANDBOX=false

# Scanning
SCAN_INTERVAL=30
"""
    
    with open('.env.template', 'w') as f:
        f.write(template)
    
    print("Created .env.template file")
    print("Copy this to .env and add your exchange API credentials")

def check_setup() -> bool:
    """Check if the environment is properly set up for live trading"""
    config = SniperConfig()
    validation = config.validate_credentials()
    
    print("🔍 Checking Live Trading Setup...")
    print("=" * 40)
    
    # Check exchange credentials
    valid_exchanges = []
    for exchange, is_valid in validation.items():
        status = "✅ READY" if is_valid else "❌ MISSING CREDENTIALS"
        print(f"{exchange.upper()}: {status}")
        if is_valid:
            valid_exchanges.append(exchange)
    
    print(f"\n📊 Trading Configuration:")
    print(f"Initial Capital: ${config.INITIAL_CAPITAL}")
    print(f"Max Trade Size: ${config.MAX_TRADE_SIZE}")
    print(f"Stop Loss: {config.STOP_LOSS_PERCENT:.1%}")
    print(f"Take Profit: {config.TAKE_PROFIT_PERCENT:.1%}")
    
    if valid_exchanges:
        print(f"\n🎯 READY TO TRADE ON: {', '.join(valid_exchanges).upper()}")
        return True
    else:
        print(f"\n⚠️  NO EXCHANGE CREDENTIALS CONFIGURED")
        print(f"Please set up API keys in .env file")
        return False

if __name__ == "__main__":
    # Create template and check setup
    create_env_template()
    check_setup()