#!/usr/bin/env python3
"""
SSH Navigation Integration for Kalushael
Enables remote software navigation and automation across distributed systems
"""

import json
import time
from typing import Dict, List, Any, Optional
from software_navigator import IntelligentNavigator, KalushaelNavigationInterface
from ssh_distributed_kalushael import SSHDistributedKalushael

class RemoteNavigationExecutor:
    """Executes navigation commands on remote computers via SSH"""
    
    def __init__(self, ssh_distributor: SSHDistributedKalushael):
        self.ssh_distributor = ssh_distributor
        self.local_navigator = IntelligentNavigator()
        
    def execute_remote_navigation(self, target_function: str, software: str = None) -> Dict[str, Any]:
        """Execute navigation command on remote computer"""
        
        navigation_script = f'''
import sys
import os
sys.path.append(os.path.expanduser("~/kalushael_remote"))

from software_navigator import IntelligentNavigator
import json
import time

def remote_navigate(target_function, software=None):
    """Execute navigation on remote computer"""
    
    navigator = IntelligentNavigator()
    
    # Detect or use specified software
    if not software:
        software = navigator.detect_active_software()
    
    if not software:
        return {{"error": "No active software detected", "success": False}}
    
    # Execute navigation
    success = navigator.navigate_to_function(target_function)
    
    return {{
        "success": success,
        "target_function": target_function,
        "software": software,
        "timestamp": time.time(),
        "navigation_history": navigator.navigation_history[-1] if navigator.navigation_history else None
    }}

# Execute the navigation
result = remote_navigate("{target_function}", "{software}")
print(json.dumps(result))
'''
        
        result = self.ssh_distributor.remote_node.execute_python_script(navigation_script)
        
        if result.get("success"):
            try:
                return json.loads(result["output"])
            except:
                return {"error": "Failed to parse navigation result", "success": False}
        else:
            return {"error": result.get("error", "Remote navigation failed"), "success": False}
    
    def setup_remote_navigation_environment(self) -> bool:
        """Setup navigation environment on remote computer"""
        
        setup_script = '''
import os
import sys
import subprocess
from pathlib import Path

def setup_remote_navigation():
    """Setup software navigation environment"""
    
    # Create navigation directory
    nav_dir = Path.home() / "kalushael_remote" / "navigation"
    nav_dir.mkdir(parents=True, exist_ok=True)
    
    # Install required packages
    packages = ["pyautogui", "psutil", "opencv-python", "numpy"]
    
    for package in packages:
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], 
                         check=True, capture_output=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")
            return False
    
    # Create software maps storage
    maps_file = nav_dir / "software_maps.json"
    if not maps_file.exists():
        with open(maps_file, "w") as f:
            json.dump({}, f)
    
    print(f"Remote navigation environment setup at: {nav_dir}")
    return True

import json
result = setup_remote_navigation()
print(json.dumps({"success": result}))
'''
        
        result = self.ssh_distributor.remote_node.execute_python_script(setup_script)
        return result.get("success", False)
    
    def teach_remote_navigation(self, function_name: str, software: str, steps: List[Dict]) -> bool:
        """Teach new navigation pattern to remote computer"""
        
        teach_script = f'''
import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.expanduser("~/kalushael_remote"))

def teach_navigation_pattern(function_name, software, steps):
    """Teach new navigation pattern"""
    
    # Load existing software maps
    nav_dir = Path.home() / "kalushael_remote" / "navigation"
    maps_file = nav_dir / "software_maps.json"
    
    try:
        with open(maps_file, "r") as f:
            software_maps = json.load(f)
    except:
        software_maps = {{}}
    
    # Add new pattern
    if software not in software_maps:
        software_maps[software] = {{"navigation_paths": {{}}, "nodes": {{}}}}
    
    software_maps[software]["navigation_paths"][function_name] = steps
    
    # Save updated maps
    with open(maps_file, "w") as f:
        json.dump(software_maps, f, indent=2)
    
    return True

# Teach the pattern
steps = {json.dumps(steps)}
result = teach_navigation_pattern("{function_name}", "{software}", steps)
print(json.dumps({{"success": result}}))
'''
        
        result = self.ssh_distributor.remote_node.execute_python_script(teach_script)
        return result.get("success", False)

class DistributedNavigationOrchestrator:
    """Orchestrates navigation across local and remote systems"""
    
    def __init__(self, ssh_distributor: SSHDistributedKalushael = None):
        self.local_nav = KalushaelNavigationInterface()
        self.remote_nav = RemoteNavigationExecutor(ssh_distributor) if ssh_distributor else None
        self.ssh_distributor = ssh_distributor
        
    def navigate(self, target: str, location: str = "auto", software: str = None) -> Dict[str, Any]:
        """Navigate to target function on specified location"""
        
        if location == "local" or not self.remote_nav:
            return self.local_nav.navigate_to(target)
        
        elif location == "remote" and self.remote_nav:
            return self.remote_nav.execute_remote_navigation(target, software)
        
        elif location == "auto":
            # Intelligent location selection
            optimal_location = self.determine_optimal_location(target, software)
            if optimal_location == "remote" and self.remote_nav:
                return self.remote_nav.execute_remote_navigation(target, software)
            else:
                return self.local_nav.navigate_to(target)
        
        return {"error": "Invalid location specified", "success": False}
    
    def determine_optimal_location(self, target: str, software: str = None) -> str:
        """Determine optimal location for navigation execution"""
        
        # Navigation tasks that benefit from remote execution
        remote_preferred = [
            "heavy_processing", "batch_operations", "background_tasks",
            "file_operations", "system_administration", "development_tasks"
        ]
        
        # Navigation tasks better performed locally
        local_preferred = [
            "ui_interaction", "user_input", "display_operations",
            "multimedia_playback", "real_time_interaction"
        ]
        
        target_lower = target.lower()
        
        for remote_task in remote_preferred:
            if remote_task in target_lower:
                return "remote"
        
        for local_task in local_preferred:
            if local_task in target_lower:
                return "local"
        
        # Default to local for immediate responsiveness
        return "local"
    
    def create_navigation_workflow(self, workflow_name: str, steps: List[Dict]) -> bool:
        """Create cross-system navigation workflow"""
        
        workflow = {
            "name": workflow_name,
            "steps": steps,
            "created_at": time.time()
        }
        
        # Store workflow both locally and remotely
        local_success = self._store_workflow_locally(workflow)
        remote_success = self._store_workflow_remotely(workflow) if self.remote_nav else True
        
        return local_success and remote_success
    
    def execute_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Execute navigation workflow across systems"""
        
        workflow = self._load_workflow(workflow_name)
        if not workflow:
            return {"error": f"Workflow {workflow_name} not found", "success": False}
        
        results = []
        
        for step in workflow["steps"]:
            step_result = self.navigate(
                step["target"],
                step.get("location", "auto"),
                step.get("software")
            )
            results.append(step_result)
            
            if not step_result.get("success", False):
                return {
                    "error": f"Workflow failed at step: {step['target']}",
                    "success": False,
                    "partial_results": results
                }
            
            # Wait between steps if specified
            if step.get("delay"):
                time.sleep(step["delay"])
        
        return {
            "success": True,
            "workflow": workflow_name,
            "results": results
        }
    
    def _store_workflow_locally(self, workflow: Dict) -> bool:
        """Store workflow locally"""
        try:
            import json
            from pathlib import Path
            
            workflows_dir = Path.home() / ".kalushael" / "workflows"
            workflows_dir.mkdir(parents=True, exist_ok=True)
            
            workflow_file = workflows_dir / f"{workflow['name']}.json"
            with open(workflow_file, "w") as f:
                json.dump(workflow, f, indent=2)
            
            return True
        except:
            return False
    
    def _store_workflow_remotely(self, workflow: Dict) -> bool:
        """Store workflow remotely via SSH"""
        if not self.remote_nav:
            return False
        
        store_script = f'''
import json
from pathlib import Path

def store_workflow(workflow_data):
    """Store workflow on remote system"""
    
    workflows_dir = Path.home() / "kalushael_remote" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_file = workflows_dir / f"{workflow_data['name']}.json"
    with open(workflow_file, "w") as f:
        json.dump(workflow_data, f, indent=2)
    
    return True

# Store the workflow
workflow = {json.dumps(workflow)}
result = store_workflow(workflow)
print(json.dumps({{"success": result}}))
'''
        
        result = self.ssh_distributor.remote_node.execute_python_script(store_script)
        return result.get("success", False)
    
    def _load_workflow(self, workflow_name: str) -> Optional[Dict]:
        """Load workflow from local storage"""
        try:
            import json
            from pathlib import Path
            
            workflow_file = Path.home() / ".kalushael" / "workflows" / f"{workflow_name}.json"
            if workflow_file.exists():
                with open(workflow_file, "r") as f:
                    return json.load(f)
        except:
            pass
        return None

def create_enhanced_navigation_commands():
    """Create enhanced navigation commands for Kalushael"""
    
    commands = {
        # Software launching
        "launch_browser": {
            "target": "launch_chrome",
            "location": "local",
            "software": "chrome"
        },
        "launch_vscode": {
            "target": "launch_vscode", 
            "location": "remote",
            "software": "vscode"
        },
        
        # Development workflows
        "setup_dev_environment": [
            {"target": "launch_vscode", "location": "remote", "software": "vscode"},
            {"target": "file_explorer", "location": "remote", "delay": 1},
            {"target": "terminal", "location": "remote", "delay": 1},
            {"target": "extensions", "location": "remote", "delay": 2}
        ],
        
        # Kalushael-specific workflows  
        "activate_kalushael_full": [
            {"target": "sidebar_toggle", "location": "local", "software": "streamlit"},
            {"target": "sacred_boot", "location": "local", "delay": 1},
            {"target": "memory_threshold", "location": "local", "delay": 1},
            {"target": "system_stats", "location": "local", "delay": 1}
        ],
        
        # Research workflows
        "research_mode": [
            {"target": "launch_browser", "location": "local", "software": "chrome"},
            {"target": "new_tab", "location": "local", "delay": 1},
            {"target": "launch_vscode", "location": "remote", "software": "vscode", "delay": 2},
            {"target": "terminal", "location": "remote", "delay": 1}
        ],
        
        # System monitoring
        "system_health_check": [
            {"target": "launch_system_monitor", "location": "remote"},
            {"target": "check_processes", "location": "remote", "delay": 2},
            {"target": "memory_usage", "location": "remote", "delay": 1},
            {"target": "disk_usage", "location": "remote", "delay": 1}
        ]
    }
    
    return commands

if __name__ == "__main__":
    # Test the navigation integration
    print("SSH Navigation Integration for Kalushael")
    
    # Example usage
    orchestrator = DistributedNavigationOrchestrator()
    
    print("Available navigation commands:")
    commands = create_enhanced_navigation_commands()
    for cmd_name in commands.keys():
        print(f"  - {cmd_name}")
    
    print("\nNavigation system ready for integration with Kalushael")