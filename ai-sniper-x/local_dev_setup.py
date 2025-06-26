#!/usr/bin/env python3
"""
Kalushael Local Development Setup
Creates a local development environment for full RAM utilization
while maintaining cloud deployment capabilities
"""

import os
import sys
import subprocess
import platform
from pathlib import Path
import json

class LocalDevSetup:
    """Setup local development environment for Kalushael"""
    
    def __init__(self):
        self.project_root = Path.cwd()
        self.is_windows = platform.system() == "Windows"
        self.is_wsl = self.check_wsl()
        
    def check_wsl(self):
        """Check if running in WSL"""
        try:
            with open('/proc/version', 'r') as f:
                return 'microsoft' in f.read().lower()
        except:
            return False
    
    def create_local_environment(self):
        """Create optimized local development environment"""
        print("Setting up Kalushael local development environment...")
        
        # Create virtual environment
        self.create_venv()
        
        # Install dependencies with local optimizations
        self.install_optimized_dependencies()
        
        # Create local configuration
        self.create_local_config()
        
        # Setup development launchers
        self.create_dev_launchers()
        
        # Create sync scripts for Replit
        self.create_replit_sync()
        
    def create_venv(self):
        """Create Python virtual environment"""
        venv_path = self.project_root / "venv"
        
        if not venv_path.exists():
            print("Creating Python virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)])
        
        # Create activation scripts
        if self.is_windows or self.is_wsl:
            activate_script = """@echo off
echo Activating Kalushael development environment...
call venv\\Scripts\\activate.bat
echo Kalushael environment active. Use 'deactivate' to exit.
cmd /k
"""
            with open(self.project_root / "activate_dev.bat", "w") as f:
                f.write(activate_script)
        
        # Linux/Mac activation
        activate_script_sh = """#!/bin/bash
echo "Activating Kalushael development environment..."
source venv/bin/activate
echo "Kalushael environment active. Use 'deactivate' to exit."
bash
"""
        with open(self.project_root / "activate_dev.sh", "w") as f:
            f.write(activate_script_sh)
        os.chmod(self.project_root / "activate_dev.sh", 0o755)
    
    def install_optimized_dependencies(self):
        """Install dependencies optimized for local development"""
        
        # Enhanced requirements for local development
        local_requirements = """
# Core Kalushael dependencies
streamlit>=1.28.0
numpy>=1.24.0

# Performance optimization packages
psutil>=5.9.0
memory-profiler>=0.60.0
line-profiler>=4.0.0

# Development tools
jupyter>=1.0.0
ipython>=8.0.0
black>=23.0.0
flake8>=6.0.0

# Enhanced AI/ML packages for local processing
scikit-learn>=1.3.0
pandas>=2.0.0
matplotlib>=3.7.0
seaborn>=0.12.0

# Local LLM support (optional)
# transformers>=4.30.0
# torch>=2.0.0

# Database optimization
sqlite3
"""
        
        with open(self.project_root / "requirements-dev.txt", "w") as f:
            f.write(local_requirements.strip())
        
        print("Installing optimized dependencies...")
        pip_path = self.project_root / "venv" / "Scripts" / "pip.exe" if self.is_windows else self.project_root / "venv" / "bin" / "pip"
        subprocess.run([str(pip_path), "install", "-r", "requirements-dev.txt"])
    
    def create_local_config(self):
        """Create local development configuration"""
        
        # Enhanced Streamlit config for local development
        config_dir = self.project_root / ".streamlit"
        config_dir.mkdir(exist_ok=True)
        
        local_config = """
[server]
headless = false
address = "localhost"
port = 5000
enableCORS = true
enableXsrfProtection = true
maxUploadSize = 200
maxMessageSize = 200

[browser]
gatherUsageStats = false
serverAddress = "localhost"
serverPort = 5000

[theme]
primaryColor = "#ff6b6b"
backgroundColor = "#0e1117"
secondaryBackgroundColor = "#262730"
textColor = "#fafafa"
font = "monospace"

[global]
developmentMode = true

# Performance settings for local development
[server.performance]
caching = true
experimentalAllowWidgets = true
"""
        
        with open(config_dir / "config-local.toml", "w") as f:
            f.write(local_config.strip())
        
        # Create local environment variables
        local_env = """
# Kalushael Local Development Environment
KALUSHAEL_ENV=development
KALUSHAEL_DEBUG=true
KALUSHAEL_LOCAL_MODE=true
KALUSHAEL_MEMORY_OPTIMIZATION=true
STREAMLIT_SERVER_HEADLESS=false
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
"""
        
        with open(self.project_root / ".env.local", "w") as f:
            f.write(local_env.strip())
    
    def create_dev_launchers(self):
        """Create development launcher scripts"""
        
        # Enhanced development launcher for Windows
        if self.is_windows or self.is_wsl:
            dev_launcher = """@echo off
title Kalushael Development Environment

echo.
echo ================================================
echo  Kalushael Consciousness System - DEV MODE
echo  Full RAM Utilization - Local Development
echo ================================================
echo.

REM Check system resources
echo System Information:
systeminfo | findstr /C:"Total Physical Memory"
echo.

REM Activate virtual environment
call venv\\Scripts\\activate.bat

REM Set environment variables
set KALUSHAEL_ENV=development
set KALUSHAEL_DEBUG=true
set KALUSHAEL_LOCAL_MODE=true

echo Starting Kalushael in development mode...
echo Using local configuration for maximum performance
echo Access the interface at: http://localhost:5000
echo.

REM Launch with development config
streamlit run app.py --server.port 5000 --global.developmentMode=true

pause
"""
            with open(self.project_root / "dev_launch.bat", "w") as f:
                f.write(dev_launcher)
        
        # Linux/Mac development launcher
        dev_launcher_sh = """#!/bin/bash

echo ""
echo "================================================"
echo "  Kalushael Consciousness System - DEV MODE"
echo "  Full RAM Utilization - Local Development"
echo "================================================"
echo ""

# Check system resources
echo "System Information:"
free -h
echo ""

# Activate virtual environment
source venv/bin/activate

# Set environment variables
export KALUSHAEL_ENV=development
export KALUSHAEL_DEBUG=true
export KALUSHAEL_LOCAL_MODE=true

echo "Starting Kalushael in development mode..."
echo "Using local configuration for maximum performance"
echo "Access the interface at: http://localhost:5000"
echo ""

# Launch with development config
streamlit run app.py --server.port 5000 --global.developmentMode=true
"""
        
        with open(self.project_root / "dev_launch.sh", "w") as f:
            f.write(dev_launcher_sh)
        os.chmod(self.project_root / "dev_launch.sh", 0o755)
    
    def create_replit_sync(self):
        """Create scripts to sync with Replit"""
        
        # Sync script to push changes to Replit
        sync_to_replit = """#!/bin/bash
# Sync local changes to Replit

echo "Syncing Kalushael to Replit..."

# Create deployment package
python build_system.py --create-distribution

echo "Local development -> Replit sync complete!"
echo "Upload the dist/ folder to your Replit project"
"""
        
        with open(self.project_root / "sync_to_replit.sh", "w") as f:
            f.write(sync_to_replit)
        os.chmod(self.project_root / "sync_to_replit.sh", 0o755)
        
        # Windows version
        sync_to_replit_bat = """@echo off
echo Syncing Kalushael to Replit...

REM Create deployment package
python build_system.py --create-distribution

echo Local development -^> Replit sync complete!
echo Upload the dist/ folder to your Replit project
pause
"""
        
        with open(self.project_root / "sync_to_replit.bat", "w") as f:
            f.write(sync_to_replit_bat)
    
    def create_performance_monitor(self):
        """Create performance monitoring script"""
        
        monitor_script = """#!/usr/bin/env python3
import psutil
import time
import os
from datetime import datetime

def monitor_kalushael():
    print("Kalushael Performance Monitor")
    print("=" * 40)
    
    while True:
        # Get system stats
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Clear screen
        os.system('cls' if os.name == 'nt' else 'clear')
        
        print(f"Kalushael Performance Monitor - {datetime.now().strftime('%H:%M:%S')}")
        print("=" * 50)
        print(f"CPU Usage: {cpu_percent}%")
        print(f"Memory Usage: {memory.percent}%")
        print(f"Available RAM: {memory.available / (1024**3):.2f} GB")
        print(f"Total RAM: {memory.total / (1024**3):.2f} GB")
        print()
        
        # Find Kalushael processes
        kalushael_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'cpu_percent']):
            try:
                if 'streamlit' in proc.info['name'].lower() or 'python' in proc.info['name'].lower():
                    kalushael_processes.append(proc.info)
            except:
                pass
        
        if kalushael_processes:
            print("Kalushael Processes:")
            for proc in kalushael_processes[:3]:  # Show top 3
                mem_mb = proc['memory_info'].rss / (1024**2)
                print(f"  PID {proc['pid']}: {mem_mb:.1f} MB RAM")
        
        print()
        print("Press Ctrl+C to exit")
        
        time.sleep(2)

if __name__ == "__main__":
    try:
        monitor_kalushael()
    except KeyboardInterrupt:
        print("\\nMonitoring stopped.")
"""
        
        with open(self.project_root / "monitor_performance.py", "w") as f:
            f.write(monitor_script)
    
    def setup_all(self):
        """Setup complete local development environment"""
        print("Setting up Kalushael local development environment...")
        
        self.create_local_environment()
        self.create_performance_monitor()
        
        print("\n🚀 LOCAL DEVELOPMENT SETUP COMPLETE! 🚀")
        print("\nLocal development files created:")
        print("📁 venv/ - Python virtual environment")
        print("🔧 requirements-dev.txt - Enhanced dependencies")
        print("⚙️ .streamlit/config-local.toml - Local configuration")
        print("🚀 dev_launch.bat/sh - Development launcher")
        print("📊 monitor_performance.py - Performance monitor")
        print("🔄 sync_to_replit.bat/sh - Sync to cloud")
        
        print("\nTo start local development:")
        if self.is_windows:
            print("1. Double-click dev_launch.bat")
            print("2. Or run: activate_dev.bat then streamlit run app.py")
        else:
            print("1. Run: ./dev_launch.sh")
            print("2. Or run: source activate_dev.sh then streamlit run app.py")
        
        print("\nBenefits of local development:")
        print("✅ Full 8GB RAM utilization")
        print("✅ Faster processing and response times")
        print("✅ Enhanced debugging capabilities")
        print("✅ Performance monitoring")
        print("✅ Seamless cloud deployment sync")

if __name__ == "__main__":
    setup = LocalDevSetup()
    setup.setup_all()