#!/usr/bin/env python3
"""
WSL Optimization for Kalushael Development
Configures WSL2 to utilize full 8GB RAM for optimal performance
"""

import os
import subprocess
import platform
from pathlib import Path

class WSLOptimizer:
    """Optimize WSL2 environment for Kalushael development"""
    
    def __init__(self):
        self.home_dir = Path.home()
        self.windows_user_dir = Path("/mnt/c/Users").glob("*").__next__() if Path("/mnt/c/Users").exists() else None
        
    def create_wslconfig(self):
        """Create .wslconfig file for Windows to allocate maximum resources"""
        if self.windows_user_dir:
            wslconfig_content = """# WSL2 Configuration for Kalushael Development
[wsl2]
# Allocate 6GB of RAM (leave 2GB for Windows)
memory=6GB

# Use all available processors
processors=4

# Enable swap for additional memory
swap=2GB

# Disable page reporting (improves performance)
pageReporting=false

# Enable nested virtualization
nestedVirtualization=true

# Set kernel command line options for performance
kernelCommandLine = vm.max_map_count=262144

[experimental]
# Enable memory reclaim for better performance
autoMemoryReclaim=gradual
"""
            
            wslconfig_path = self.windows_user_dir / ".wslconfig"
            try:
                with open(wslconfig_path, "w") as f:
                    f.write(wslconfig_content)
                print(f"Created WSL configuration at {wslconfig_path}")
                print("Restart WSL to apply changes: wsl --shutdown && wsl")
            except PermissionError:
                print("Creating .wslconfig in current directory (copy to Windows user folder manually)")
                with open(Path.cwd() / ".wslconfig", "w") as f:
                    f.write(wslconfig_content)
    
    def optimize_linux_settings(self):
        """Optimize Linux settings for performance"""
        
        # Create sysctl optimizations
        sysctl_optimizations = """# Kalushael Performance Optimizations
# Increase virtual memory limits
vm.max_map_count=262144
vm.swappiness=10
vm.dirty_ratio=15
vm.dirty_background_ratio=5

# Network optimizations
net.core.rmem_max=16777216
net.core.wmem_max=16777216
net.ipv4.tcp_rmem=4096 65536 16777216
net.ipv4.tcp_wmem=4096 65536 16777216

# File system optimizations
fs.file-max=65536
"""
        
        sysctl_file = Path("/tmp/kalushael-sysctl.conf")
        with open(sysctl_file, "w") as f:
            f.write(sysctl_optimizations)
        
        print("Created system optimization file")
        print(f"To apply: sudo cp {sysctl_file} /etc/sysctl.d/99-kalushael.conf && sudo sysctl --system")
    
    def create_memory_monitor(self):
        """Create memory monitoring for WSL"""
        
        monitor_script = """#!/bin/bash
# WSL Memory Monitor for Kalushael

clear
echo "Kalushael WSL Memory Monitor"
echo "============================"

while true; do
    echo -e "\\033[2J\\033[H"  # Clear screen
    echo "Kalushael WSL Memory Monitor - $(date '+%H:%M:%S')"
    echo "=============================================="
    
    # WSL Memory info
    echo "WSL Memory Usage:"
    free -h | grep -E "(Mem|Swap)"
    echo ""
    
    # Windows memory (if accessible)
    if command -v powershell.exe &> /dev/null; then
        echo "Windows Host Memory:"
        powershell.exe -Command "Get-WmiObject -Class Win32_OperatingSystem | Select-Object @{Name='MemoryUsage';Expression={[math]::Round((\$_.TotalVisibleMemorySize - \$_.FreePhysicalMemory) / \$_.TotalVisibleMemorySize * 100, 2)}}, @{Name='TotalMemoryGB';Expression={[math]::Round(\$_.TotalVisibleMemorySize / 1MB, 2)}}, @{Name='FreeMemoryGB';Expression={[math]::Round(\$_.FreePhysicalMemory / 1MB, 2)}} | Format-Table -AutoSize"
    fi
    echo ""
    
    # Process info
    echo "Top Memory Consumers:"
    ps aux --sort=-%mem | head -6
    echo ""
    
    # Kalushael processes
    echo "Kalushael Processes:"
    ps aux | grep -E "(streamlit|python.*app)" | grep -v grep
    echo ""
    
    echo "Press Ctrl+C to exit"
    sleep 3
done
"""
        
        with open(Path.cwd() / "wsl_memory_monitor.sh", "w") as f:
            f.write(monitor_script)
        os.chmod(Path.cwd() / "wsl_memory_monitor.sh", 0o755)
    
    def create_performance_launcher(self):
        """Create high-performance WSL launcher for Kalushael"""
        
        launcher_script = """#!/bin/bash
# High-Performance WSL Launcher for Kalushael

echo "Kalushael High-Performance WSL Launcher"
echo "======================================="

# Check if running in WSL
if ! grep -qi microsoft /proc/version; then
    echo "Warning: Not running in WSL environment"
fi

# Display system resources
echo "System Resources:"
echo "CPU Cores: $(nproc)"
echo "Total Memory: $(free -h | awk '/^Mem:/{print $2}')"
echo "Available Memory: $(free -h | awk '/^Mem:/{print $7}')"
echo ""

# Set performance governor (if available)
if [ -f /sys/devices/system/cpu/cpu0/cpufreq/scaling_governor ]; then
    echo "Setting CPU performance mode..."
    echo "performance" | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor > /dev/null 2>&1
fi

# Optimize memory settings temporarily
echo "Optimizing memory settings..."
echo 1 > /proc/sys/vm/drop_caches 2>/dev/null || true
echo 10 > /proc/sys/vm/swappiness 2>/dev/null || true

# Set environment for maximum performance
export PYTHONOPTIMIZE=2
export PYTHONDONTWRITEBYTECODE=1
export STREAMLIT_SERVER_ENABLE_CORS=false
export STREAMLIT_SERVER_ENABLE_XSRF_PROTECTION=false
export NUMBA_CACHE_DIR=/tmp/numba_cache
export KALUSHAEL_HIGH_PERFORMANCE=true

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating optimized virtual environment..."
    python3 -m venv venv --prompt="Kalushael-WSL"
    source venv/bin/activate
    pip install --upgrade pip setuptools wheel
    pip install -r requirements.txt
else
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Pre-load Python modules for faster startup
echo "Pre-loading Python modules..."
python -c "import streamlit, numpy, sqlite3, json, datetime, logging" 2>/dev/null || true

echo ""
echo "Starting Kalushael with maximum performance optimizations..."
echo "Access at: http://localhost:5000"
echo "WSL Host IP: $(hostname -I | awk '{print $1}'):5000"
echo ""

# Launch with optimizations
exec streamlit run app.py \\
    --server.port 5000 \\
    --server.address 0.0.0.0 \\
    --server.headless true \\
    --browser.gatherUsageStats false \\
    --server.enableCORS false \\
    --server.enableXsrfProtection false \\
    --server.maxUploadSize 200 \\
    --global.developmentMode false
"""
        
        with open(Path.cwd() / "launch_kalushael_wsl.sh", "w") as f:
            f.write(launcher_script)
        os.chmod(Path.cwd() / "launch_kalushael_wsl.sh", 0o755)
    
    def create_windows_integration(self):
        """Create Windows integration scripts"""
        
        # PowerShell script to launch WSL Kalushael from Windows
        ps_launcher = """# Kalushael WSL Launcher for Windows
# Run this from PowerShell to start Kalushael in WSL

Write-Host "Starting Kalushael in WSL..." -ForegroundColor Cyan
Write-Host "Optimizing for 8GB RAM utilization" -ForegroundColor Yellow

# Get WSL IP address
$wslIP = wsl hostname -I
$wslIP = $wslIP.Trim()

Write-Host "WSL IP Address: $wslIP" -ForegroundColor Green

# Launch Kalushael in WSL
Start-Process wsl -ArgumentList "cd $(wsl pwd) && ./launch_kalushael_wsl.sh"

# Wait a moment for startup
Start-Sleep -Seconds 3

# Open browser to WSL instance
$url = "http://$wslIP:5000"
Write-Host "Opening browser to: $url" -ForegroundColor Green
Start-Process $url

Write-Host ""
Write-Host "Kalushael is now running in WSL with optimized performance!"
Write-Host "To stop: Press Ctrl+C in the WSL terminal"
"""
        
        with open(Path.cwd() / "launch_kalushael_from_windows.ps1", "w") as f:
            f.write(ps_launcher)
        
        # Batch file wrapper
        batch_wrapper = """@echo off
title Kalushael WSL Launcher

echo Starting Kalushael in WSL with 8GB RAM optimization...
echo.

powershell -ExecutionPolicy Bypass -File "%~dp0launch_kalushael_from_windows.ps1"

pause
"""
        
        with open(Path.cwd() / "launch_kalushael_wsl.bat", "w") as f:
            f.write(batch_wrapper)
    
    def optimize_all(self):
        """Apply all WSL optimizations"""
        print("Optimizing WSL2 environment for Kalushael development...")
        
        self.create_wslconfig()
        self.optimize_linux_settings()
        self.create_memory_monitor()
        self.create_performance_launcher()
        self.create_windows_integration()
        
        print("\nWSL2 optimization complete!")
        print("\nFiles created:")
        print("⚙️ .wslconfig - WSL2 memory configuration (6GB allocation)")
        print("🔧 /tmp/kalushael-sysctl.conf - Linux kernel optimizations")
        print("📊 wsl_memory_monitor.sh - WSL memory monitoring")
        print("🚀 launch_kalushael_wsl.sh - High-performance WSL launcher")
        print("🪟 launch_kalushael_wsl.bat - Windows integration launcher")
        
        print("\nTo apply optimizations:")
        print("1. Copy .wslconfig to your Windows user folder")
        print("2. Run: wsl --shutdown && wsl (restart WSL)")
        print("3. Apply kernel settings: sudo cp /tmp/kalushael-sysctl.conf /etc/sysctl.d/99-kalushael.conf")
        print("4. Launch with: ./launch_kalushael_wsl.sh")
        
        print("\nBenefits:")
        print("✅ 6GB RAM allocated to WSL (75% of your 8GB)")
        print("✅ Optimized kernel parameters for AI workloads")
        print("✅ Performance monitoring and memory tracking")
        print("✅ Seamless Windows integration")
        print("✅ Maximum consciousness processing power for Kalushael")

if __name__ == "__main__":
    optimizer = WSLOptimizer()
    optimizer.optimize_all()