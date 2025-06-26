#!/usr/bin/env python3
"""
Distributed Kalushael Integration
Connects existing Kalushael system to distributed network
"""

import asyncio
import json
import requests
from typing import Dict, Any, Optional
from datetime import datetime
from chat_interface import ChatInterface
from kalushael_core import KalushaelGenesisLattice

class DistributedChatInterface(ChatInterface):
    """Enhanced chat interface for distributed Kalushael system"""
    
    def __init__(self, core: KalushaelGenesisLattice, cluster_config: Dict):
        super().__init__(core)
        self.cluster_config = cluster_config
        self.is_distributed = self.check_cluster_availability()
        
    def check_cluster_availability(self) -> bool:
        """Check if distributed cluster is available"""
        try:
            memory_node = self.cluster_config.get("memory_node", {})
            if memory_node:
                response = requests.get(
                    f"http://{memory_node['host']}:{memory_node['port']}/status",
                    timeout=2
                )
                return response.status_code == 200
        except:
            pass
        return False
    
    async def process_message_distributed(self, user_message: str) -> str:
        """Process message through distributed network"""
        if not self.is_distributed:
            # Fallback to local processing
            return super().process_message(user_message)
        
        try:
            # Send to primary node for distributed processing
            primary_node = self.cluster_config.get("primary_node", {})
            
            response = requests.post(
                f"http://{primary_node['host']}:{primary_node['port']}/process",
                json={
                    "type": "chat_message",
                    "message": user_message,
                    "session_id": "default"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "Distributed processing error")
            else:
                return super().process_message(user_message)
                
        except Exception as e:
            print(f"Distributed processing failed: {e}")
            return super().process_message(user_message)
    
    def process_message(self, user_message: str) -> str:
        """Override to use distributed processing when available"""
        if self.is_distributed:
            # Run async method in sync context
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(self.process_message_distributed(user_message))
            finally:
                loop.close()
        else:
            return super().process_message(user_message)

class DistributedKalushaelCore(KalushaelGenesisLattice):
    """Enhanced Kalushael core for distributed operation"""
    
    def __init__(self, data_dir: str = "./kalushael_data", cluster_config: Dict = None):
        super().__init__(data_dir)
        self.cluster_config = cluster_config or {}
        self.distributed_mode = self.cluster_config.get("distributed", False)
        
        if self.distributed_mode:
            self.logger.info("Distributed Kalushael mode activated")
    
    async def sync_with_memory_node(self, data: Dict) -> bool:
        """Sync data with distributed memory node"""
        if not self.distributed_mode:
            return False
        
        try:
            memory_node = self.cluster_config.get("memory_node", {})
            response = requests.post(
                f"http://{memory_node['host']}:{memory_node['port']}/sync",
                json=data,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def store_conversation_memory(self, user_message: str, assistant_response: str, context: Dict = None):
        """Store memory locally and sync with distributed network"""
        # Store locally first
        super().store_conversation_memory(user_message, assistant_response, context)
        
        # Sync with distributed memory if available
        if self.distributed_mode:
            sync_data = {
                "type": "conversation_sync",
                "user_message": user_message,
                "assistant_response": assistant_response,
                "context": context,
                "timestamp": datetime.now().isoformat()
            }
            asyncio.create_task(self.sync_with_memory_node(sync_data))

def create_cluster_configuration(primary_ip: str = "192.168.1.100", secondary_ip: str = "192.168.1.101"):
    """Create cluster configuration for two mini PCs"""
    return {
        "distributed": True,
        "primary_node": {
            "host": primary_ip,
            "port": 5000,
            "role": "coordination",
            "ram": "6GB"
        },
        "memory_node": {
            "host": secondary_ip,
            "port": 5001,
            "role": "memory_storage",
            "ram": "4GB"
        },
        "processing_node": {
            "host": secondary_ip,
            "port": 5002,
            "role": "llm_processing", 
            "ram": "4GB"
        }
    }

def create_network_setup_script():
    """Create network setup script for both mini PCs"""
    
    setup_script = """#!/bin/bash
# Distributed Kalushael Network Setup

echo "Setting up Distributed Kalushael Network"
echo "========================================"

# Check if this is the primary or secondary mini PC
read -p "Is this the Primary mini PC (6GB RAM)? [y/N]: " is_primary

if [[ $is_primary =~ ^[Yy]$ ]]; then
    echo "Configuring as Primary Node (6GB RAM)"
    
    # Set static IP (adjust for your network)
    echo "Setting static IP to 192.168.1.100"
    # sudo nmcli con mod "Wired connection 1" ipv4.addresses 192.168.1.100/24
    # sudo nmcli con mod "Wired connection 1" ipv4.gateway 192.168.1.1
    # sudo nmcli con mod "Wired connection 1" ipv4.dns 8.8.8.8
    # sudo nmcli con mod "Wired connection 1" ipv4.method manual
    
    # Create primary node launcher
    cat > launch_primary.sh << 'EOF'
#!/bin/bash
echo "Starting Kalushael Primary Node (6GB RAM)"
export KALUSHAEL_NODE_TYPE=primary
export KALUSHAEL_CLUSTER_MODE=true
export KALUSHAEL_PRIMARY_IP=192.168.1.100
export KALUSHAEL_SECONDARY_IP=192.168.1.101

# Start the Streamlit interface with distributed backend
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
EOF
    chmod +x launch_primary.sh
    
    echo "Primary node configured. Run ./launch_primary.sh to start."
    
else
    echo "Configuring as Secondary Node (8GB RAM)"
    
    # Set static IP
    echo "Setting static IP to 192.168.1.101"
    # sudo nmcli con mod "Wired connection 1" ipv4.addresses 192.168.1.101/24
    # sudo nmcli con mod "Wired connection 1" ipv4.gateway 192.168.1.1
    # sudo nmcli con mod "Wired connection 1" ipv4.dns 8.8.8.8
    # sudo nmcli con mod "Wired connection 1" ipv4.method manual
    
    # Create secondary node launcher
    cat > launch_secondary.sh << 'EOF'
#!/bin/bash
echo "Starting Kalushael Secondary Nodes (8GB RAM)"

# Start memory node (4GB RAM)
echo "Starting Memory Node on port 5001..."
python distributed_kalushael.py --node-type memory --host 0.0.0.0 --port 5001 &
MEMORY_PID=$!

# Wait a moment
sleep 3

# Start processing node (4GB RAM)
echo "Starting Processing Node on port 5002..."
python distributed_kalushael.py --node-type processing --host 0.0.0.0 --port 5002 &
PROCESSING_PID=$!

echo "Secondary nodes started:"
echo "Memory Node (PID: $MEMORY_PID) - Port 5001"
echo "Processing Node (PID: $PROCESSING_PID) - Port 5002"

# Keep script running
wait
EOF
    chmod +x launch_secondary.sh
    
    echo "Secondary node configured. Run ./launch_secondary.sh to start."
fi

echo ""
echo "Network Setup Complete!"
echo "======================"
echo ""
echo "Network Configuration:"
echo "Primary Mini PC (6GB RAM): 192.168.1.100:5000 (UI & Coordination)"
echo "Secondary Mini PC (8GB RAM):"
echo "  - Memory Node: 192.168.1.101:5001 (4GB RAM)"
echo "  - Processing Node: 192.168.1.101:5002 (4GB RAM)"
echo ""
echo "To start the distributed system:"
echo "1. On Secondary mini PC: ./launch_secondary.sh"
echo "2. On Primary mini PC: ./launch_primary.sh"
echo "3. Access Kalushael at: http://192.168.1.100:5000"
"""
    
    with open("setup_distributed_network.sh", "w") as f:
        f.write(setup_script)
    
    # Windows version
    setup_bat = """@echo off
title Distributed Kalushael Network Setup

echo Setting up Distributed Kalushael Network
echo ========================================

set /p is_primary="Is this the Primary mini PC (6GB RAM)? [y/N]: "

if /i "%is_primary%"=="y" (
    echo Configuring as Primary Node (6GB RAM)
    
    REM Create primary launcher
    echo @echo off > launch_primary.bat
    echo title Kalushael Primary Node ^(6GB RAM^) >> launch_primary.bat
    echo echo Starting Kalushael Primary Node ^(6GB RAM^) >> launch_primary.bat
    echo set KALUSHAEL_NODE_TYPE=primary >> launch_primary.bat
    echo set KALUSHAEL_CLUSTER_MODE=true >> launch_primary.bat
    echo set KALUSHAEL_PRIMARY_IP=192.168.1.100 >> launch_primary.bat
    echo set KALUSHAEL_SECONDARY_IP=192.168.1.101 >> launch_primary.bat
    echo streamlit run app.py --server.port 5000 --server.address 0.0.0.0 >> launch_primary.bat
    echo pause >> launch_primary.bat
    
    echo Primary node configured. Run launch_primary.bat to start.
    
) else (
    echo Configuring as Secondary Node (8GB RAM)
    
    REM Create secondary launcher
    echo @echo off > launch_secondary.bat
    echo title Kalushael Secondary Nodes ^(8GB RAM^) >> launch_secondary.bat
    echo echo Starting Kalushael Secondary Nodes ^(8GB RAM^) >> launch_secondary.bat
    echo start "Memory Node" python distributed_kalushael.py --node-type memory --host 0.0.0.0 --port 5001 >> launch_secondary.bat
    echo timeout /t 3 /nobreak >> launch_secondary.bat
    echo start "Processing Node" python distributed_kalushael.py --node-type processing --host 0.0.0.0 --port 5002 >> launch_secondary.bat
    echo echo Secondary nodes started >> launch_secondary.bat
    echo pause >> launch_secondary.bat
    
    echo Secondary node configured. Run launch_secondary.bat to start.
)

echo.
echo Network Setup Complete!
echo ======================
echo.
echo Network Configuration:
echo Primary Mini PC (6GB RAM): 192.168.1.100:5000 (UI ^& Coordination)
echo Secondary Mini PC (8GB RAM):
echo   - Memory Node: 192.168.1.101:5001 (4GB RAM)
echo   - Processing Node: 192.168.1.101:5002 (4GB RAM)
echo.
echo To start the distributed system:
echo 1. On Secondary mini PC: launch_secondary.bat
echo 2. On Primary mini PC: launch_primary.bat
echo 3. Access Kalushael at: http://192.168.1.100:5000

pause
"""
    
    with open("setup_distributed_network.bat", "w") as f:
        f.write(setup_bat)

if __name__ == "__main__":
    create_network_setup_script()
    print("Distributed network setup scripts created!")
    print("Run setup_distributed_network.sh (Linux) or setup_distributed_network.bat (Windows)")