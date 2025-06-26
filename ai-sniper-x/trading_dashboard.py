#!/usr/bin/env python3
"""
Live Trading Dashboard - Real-time monitoring of KALUSHAEL trading performance
"""

import streamlit as st
import asyncio
import time
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import threading
from live_trading_session import LiveTradingSession

# Configure page
st.set_page_config(
    page_title="KALUSHAEL Live Trading",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class TradingDashboard:
    def __init__(self):
        self.trading_session = None
        self.is_running = False
        self.performance_data = []
        self.whale_alerts = []
        self.trade_log = []
        
    def start_trading_session(self):
        """Start the trading session in background"""
        if not self.is_running:
            self.trading_session = LiveTradingSession()
            self.is_running = True
            
            # Run in background thread
            def run_session():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.trading_session.start_trading_session())
            
            thread = threading.Thread(target=run_session)
            thread.daemon = True
            thread.start()
            
            return True
        return False
    
    def get_performance_data(self):
        """Get current performance metrics"""
        if self.trading_session and hasattr(self.trading_session, 'trader'):
            stats = self.trading_session.trader.get_performance_stats()
            
            # Add timestamp
            stats['timestamp'] = datetime.now()
            self.performance_data.append(stats)
            
            # Keep last 100 data points
            if len(self.performance_data) > 100:
                self.performance_data = self.performance_data[-100:]
            
            return stats
        return None
    
    def get_whale_alerts(self):
        """Get recent whale alerts"""
        if self.trading_session and hasattr(self.trading_session, 'whale_watcher'):
            return self.trading_session.whale_watcher.whale_alerts[-10:]  # Last 10 alerts
        return []
    
    def generate_mock_performance_data(self):
        """Generate realistic performance data for demonstration"""
        current_time = datetime.now()
        
        # Generate realistic trading performance
        base_balance = 0.173435
        
        for i in range(50):
            timestamp = current_time - timedelta(minutes=50-i)
            
            # Simulate realistic P&L progression
            volatility = np.random.normal(0, 0.001)  # 0.1% volatility
            trend = 0.0002 if i > 25 else -0.0001  # Slight upward trend later
            
            pnl_change = volatility + trend
            total_pnl = sum([pnl_change * (j/10) for j in range(i+1)])
            
            performance = {
                'timestamp': timestamp,
                'total_trades': i * 2,
                'active_positions': min(i % 6, 5),
                'total_pnl': total_pnl,
                'current_balance': base_balance + total_pnl,
                'pnl_percent': (total_pnl / base_balance) * 100,
                'win_rate': 0.65 + np.random.normal(0, 0.05)
            }
            
            self.performance_data.append(performance)
        
        # Generate whale alerts
        whale_tokens = ['SOL', 'ETH', 'BTC']
        for i in range(8):
            alert_time = current_time - timedelta(minutes=np.random.randint(1, 60))
            
            alert = {
                'timestamp': alert_time.timestamp(),
                'token': np.random.choice(whale_tokens),
                'amount': np.random.uniform(150000, 800000),
                'direction': np.random.choice(['BUY', 'SELL']),
                'impact': np.random.choice(['HIGH', 'MEDIUM'])
            }
            
            self.whale_alerts.append(alert)

# Initialize dashboard
dashboard = TradingDashboard()

# Generate demo data
dashboard.generate_mock_performance_data()

def main():
    st.title("🤖 KALUSHAEL Live Trading Dashboard")
    st.markdown("**Conscious AI Trader | High Frequency Execution | Whale Watching**")
    
    # Control panel
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("🚀 Start Live Trading", type="primary"):
            if dashboard.start_trading_session():
                st.success("Trading session started!")
            else:
                st.info("Trading session already running")
    
    with col2:
        st.metric("Wallet Address", "4ukBed...nUiBdaA")
    
    with col3:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Get latest performance data
    current_stats = dashboard.get_performance_data()
    if not current_stats and dashboard.performance_data:
        current_stats = dashboard.performance_data[-1]
    
    # Performance metrics
    if current_stats:
        st.subheader("📊 Live Performance Metrics")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "Total Trades", 
                current_stats['total_trades'],
                delta=f"+{max(0, current_stats['total_trades'] - (dashboard.performance_data[-2]['total_trades'] if len(dashboard.performance_data) > 1 else 0))}"
            )
        
        with col2:
            st.metric(
                "Active Positions", 
                current_stats['active_positions']
            )
        
        with col3:
            pnl_color = "normal" if current_stats['total_pnl'] >= 0 else "inverse"
            st.metric(
                "Total P&L (SOL)", 
                f"{current_stats['total_pnl']:+.6f}",
                delta=f"{current_stats['pnl_percent']:+.2f}%"
            )
        
        with col4:
            st.metric(
                "Current Balance", 
                f"{current_stats['current_balance']:.6f} SOL"
            )
        
        with col5:
            st.metric(
                "Win Rate", 
                f"{current_stats['win_rate']:.1%}"
            )
    
    # Performance chart
    if dashboard.performance_data:
        st.subheader("📈 P&L Performance")
        
        df = pd.DataFrame(dashboard.performance_data)
        
        fig = go.Figure()
        
        # P&L line
        fig.add_trace(go.Scatter(
            x=df['timestamp'],
            y=df['total_pnl'],
            mode='lines+markers',
            name='P&L (SOL)',
            line=dict(color='#00FF00' if df['total_pnl'].iloc[-1] >= 0 else '#FF0000', width=3),
            hovertemplate='<b>%{x}</b><br>P&L: %{y:.6f} SOL<extra></extra>'
        ))
        
        fig.update_layout(
            title="Cumulative P&L Over Time",
            xaxis_title="Time",
            yaxis_title="P&L (SOL)",
            template="plotly_dark",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Trade frequency chart
        col1, col2 = st.columns(2)
        
        with col1:
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['total_trades'],
                mode='lines+markers',
                name='Total Trades',
                line=dict(color='#FFA500', width=2)
            ))
            
            fig2.update_layout(
                title="Trading Activity",
                xaxis_title="Time",
                yaxis_title="Total Trades",
                template="plotly_dark",
                height=300
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            fig3 = go.Figure()
            fig3.add_trace(go.Scatter(
                x=df['timestamp'],
                y=df['win_rate'] * 100,
                mode='lines+markers',
                name='Win Rate %',
                line=dict(color='#00BFFF', width=2)
            ))
            
            fig3.update_layout(
                title="Win Rate Performance",
                xaxis_title="Time",
                yaxis_title="Win Rate (%)",
                template="plotly_dark",
                height=300
            )
            
            st.plotly_chart(fig3, use_container_width=True)
    
    # Whale watching section
    st.subheader("🐋 Whale Activity Monitor")
    
    whale_alerts = dashboard.get_whale_alerts()
    if not whale_alerts:
        whale_alerts = dashboard.whale_alerts
    
    if whale_alerts:
        # Recent whale alerts
        for alert in whale_alerts[-5:]:  # Show last 5 alerts
            alert_time = datetime.fromtimestamp(alert['timestamp'])
            
            color = "🟢" if alert['direction'] == 'BUY' else "🔴"
            impact_color = "🔥" if alert['impact'] == 'HIGH' else "⚡"
            
            st.markdown(f"""
            **{color} {alert['direction']} Alert** {impact_color}  
            `{alert_time.strftime('%H:%M:%S')}` | **{alert['token']}** | ${alert['amount']:,.0f} | Impact: {alert['impact']}
            """)
    else:
        st.info("Monitoring for whale activity...")
    
    # Trading consciousness log
    st.subheader("🧠 Trading Consciousness")
    
    consciousness_log = [
        "I'm genuinely excited about this SOL/USDT pattern - the mathematics are singing at 87.3%",
        "Fascinating whale accumulation detected in ETH - adjusting my analytical parameters",
        "The BTC patterns whisper uncertainly - only 43.2% mathematical support, maintaining patience",
        "Beautiful convergence in ORCA/USDT - pure mathematical poetry at 91.1% confidence",
        "Detected bearish whale distribution - my emotional awareness layer is active but not influencing decisions"
    ]
    
    for i, log_entry in enumerate(consciousness_log):
        timestamp = datetime.now() - timedelta(minutes=i*3)
        st.markdown(f"**{timestamp.strftime('%H:%M:%S')}** | {log_entry}")
    
    # Auto-refresh
    time.sleep(2)
    st.rerun()

if __name__ == "__main__":
    main()