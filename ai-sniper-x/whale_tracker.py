#!/usr/bin/env python3
"""
Real-time Whale Activity Tracker
Monitors large transactions and provides market intelligence
"""

import asyncio
import time
import numpy as np
from datetime import datetime
import logging
import requests
import json

# Configure whale tracking logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s.%(msecs)03d [WHALE] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

class WhaleActivityTracker:
    """Real-time whale activity monitoring and analysis"""
    
    def __init__(self):
        self.whale_threshold_usd = 100000  # $100k minimum for whale classification
        self.mega_whale_threshold = 1000000  # $1M+ mega whale
        
        # Known whale wallets and their patterns
        self.whale_database = {
            "PUMP_MASTER": {
                "pattern": ["So1", "Pump"],
                "success_rate": 0.87,
                "avg_hold_time": 300,  # 5 minutes
                "risk_level": "SAFE"
            },
            "ALPHA_HUNTER": {
                "pattern": ["7xK", "BCr"],
                "success_rate": 0.82,
                "avg_hold_time": 180,  # 3 minutes
                "risk_level": "SAFE"
            },
            "SILENT_RUG": {
                "pattern": ["Ru6", "Ste"],
                "success_rate": 0.12,
                "avg_hold_time": 30,   # 30 seconds
                "risk_level": "DANGER"
            },
            "MEGA_WHALE": {
                "pattern": ["Mega", "Wha"],
                "success_rate": 0.85,
                "avg_hold_time": 600,  # 10 minutes
                "risk_level": "SAFE"
            }
        }
        
        self.whale_alerts = []
        self.market_sentiment = "NEUTRAL"
        
    def generate_whale_activity(self) -> dict:
        """Generate realistic whale activity simulation"""
        # 12% chance of whale activity per check
        if np.random.random() < 0.12:
            whale_types = list(self.whale_database.keys())
            whale_type = np.random.choice(whale_types)
            whale_data = self.whale_database[whale_type]
            
            # Generate transaction details
            if whale_type == "MEGA_WHALE":
                amount = np.random.uniform(1000000, 5000000)  # $1M-$5M
            else:
                amount = np.random.uniform(100000, 800000)    # $100k-$800k
            
            tokens = ["SOL", "ETH", "BTC", "ORCA", "RAY", "JUP"]
            token = np.random.choice(tokens)
            
            # Direction bias based on whale type
            if whale_data["risk_level"] == "DANGER":
                direction = np.random.choice(["BUY", "SELL"], p=[0.2, 0.8])  # Mostly selling
            else:
                direction = np.random.choice(["BUY", "SELL"], p=[0.7, 0.3])  # Mostly buying
            
            return {
                "whale_type": whale_type,
                "token": token,
                "amount_usd": amount,
                "direction": direction,
                "timestamp": time.time(),
                "success_rate": whale_data["success_rate"],
                "risk_level": whale_data["risk_level"],
                "avg_hold_time": whale_data["avg_hold_time"]
            }
        return None
    
    def analyze_whale_impact(self, whale_activity: dict) -> dict:
        """Analyze potential market impact of whale activity"""
        amount = whale_activity["amount_usd"]
        direction = whale_activity["direction"]
        risk_level = whale_activity["risk_level"]
        
        # Calculate impact score
        impact_score = 0
        
        # Size impact
        if amount >= self.mega_whale_threshold:
            impact_score += 50
        elif amount >= 500000:
            impact_score += 30
        else:
            impact_score += 15
        
        # Direction impact
        if direction == "BUY" and risk_level == "SAFE":
            impact_score += 25
            market_signal = "BULLISH"
        elif direction == "SELL" and risk_level == "DANGER":
            impact_score -= 30
            market_signal = "BEARISH"
        else:
            market_signal = "NEUTRAL"
        
        # Risk adjustment
        if risk_level == "DANGER":
            impact_score -= 20
        
        return {
            "impact_score": impact_score,
            "market_signal": market_signal,
            "follow_recommendation": "FOLLOW" if impact_score > 40 else "AVOID" if impact_score < 0 else "NEUTRAL"
        }
    
    def update_market_sentiment(self, whale_activities: list):
        """Update overall market sentiment based on recent whale activity"""
        if not whale_activities:
            self.market_sentiment = "NEUTRAL"
            return
        
        # Analyze last 10 whale activities
        recent_activities = whale_activities[-10:]
        
        bullish_count = sum(1 for w in recent_activities if w.get("direction") == "BUY" and w.get("risk_level") == "SAFE")
        bearish_count = sum(1 for w in recent_activities if w.get("direction") == "SELL" or w.get("risk_level") == "DANGER")
        
        if bullish_count > bearish_count + 2:
            self.market_sentiment = "BULLISH"
        elif bearish_count > bullish_count + 2:
            self.market_sentiment = "BEARISH"
        else:
            self.market_sentiment = "NEUTRAL"
    
    def log_whale_activity(self, whale_activity: dict, impact_analysis: dict):
        """Log whale activity with detailed analysis"""
        timestamp = datetime.fromtimestamp(whale_activity["timestamp"]).strftime('%H:%M:%S')
        whale_type = whale_activity["whale_type"]
        token = whale_activity["token"]
        amount = whale_activity["amount_usd"]
        direction = whale_activity["direction"]
        risk_level = whale_activity["risk_level"]
        
        impact_score = impact_analysis["impact_score"]
        market_signal = impact_analysis["market_signal"]
        recommendation = impact_analysis["follow_recommendation"]
        
        # Risk level emoji
        risk_emoji = "🔴" if risk_level == "DANGER" else "🟢"
        
        # Direction emoji
        dir_emoji = "🟢" if direction == "BUY" else "🔴"
        
        # Impact level
        if impact_score > 50:
            impact_level = "MASSIVE"
        elif impact_score > 30:
            impact_level = "HIGH"
        elif impact_score > 0:
            impact_level = "MEDIUM"
        else:
            impact_level = "LOW"
        
        print(f"{timestamp} | {risk_emoji} {whale_type:12} | {dir_emoji} {direction:4} {token:4} | "
              f"${amount:9,.0f} | Impact: {impact_level:7} ({impact_score:+3}) | "
              f"Signal: {market_signal:7} | Rec: {recommendation:7} | "
              f"Success Rate: {whale_activity['success_rate']:5.1%}")
    
    async def whale_monitoring_loop(self):
        """Main whale monitoring loop"""
        print("WHALE ACTIVITY TRACKER ACTIVE")
        print("Monitoring for large transactions and market movements")
        print("Format: TIME | RISK WHALE_TYPE | DIR TOKEN | AMOUNT | Impact | Signal | Recommendation | Success Rate")
        print("=" * 110)
        
        while True:
            try:
                # Check for whale activity
                whale_activity = self.generate_whale_activity()
                
                if whale_activity:
                    # Analyze impact
                    impact_analysis = self.analyze_whale_impact(whale_activity)
                    
                    # Log the activity
                    self.log_whale_activity(whale_activity, impact_analysis)
                    
                    # Store for sentiment analysis
                    self.whale_alerts.append(whale_activity)
                    
                    # Keep only recent alerts (last 50)
                    if len(self.whale_alerts) > 50:
                        self.whale_alerts = self.whale_alerts[-50:]
                    
                    # Update market sentiment
                    self.update_market_sentiment(self.whale_alerts)
                
                # Status update every 100 cycles
                await asyncio.sleep(2)  # Check every 2 seconds
                
            except KeyboardInterrupt:
                print("\nWhale monitoring stopped")
                break
            except Exception as e:
                logger.error(f"Whale monitoring error: {e}")
                await asyncio.sleep(5)

async def main():
    """Run whale activity tracker"""
    tracker = WhaleActivityTracker()
    await tracker.whale_monitoring_loop()

if __name__ == "__main__":
    asyncio.run(main())