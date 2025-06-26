#!/usr/bin/env python3
"""
Auto Expansion Manager for Kalushael Cluster
Automatically detects and integrates new mini PCs as they connect
True plug-and-play scaling from 2 to unlimited nodes
"""

import subprocess
import socket
import json
import time
import threading
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime
from ethernet_network_setup import EthernetClusterSetup

class AutoExpansionManager:
    """Manages automatic detection and integration of new cluster nodes"""
    
    def __init__(self, config_path: str = "kalushael_cluster_config.json"):
        self.config_path = config_path
        self.cluster_setup = EthernetClusterSetup()
        self.logger = logging.getLogger("AutoExpansion")
        self.monitoring = False
        self.known_nodes = set()
        
        # Load existing cluster config
        self.cluster_config = self._load_cluster_config()
        if self.cluster_config:
            self.known_nodes = {node['ip'] for node in self.cluster_config['nodes'].values()}
    
    def _load_cluster_config(self) -> Optional[Dict[str, Any]]:
        """Load existing cluster configuration"""
        try:
            with open(self.config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return None
        except Exception as e:
            self.logger.error(f"Error loading cluster config: {e}")
            return None
    
    def _save_cluster_config(self, config: Dict[str, Any]):
        """Save updated cluster configuration"""
        try:
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving cluster config: {e}")
    
    def start_monitoring(self):
        """Start monitoring for new nodes"""
        if self.monitoring:
            return
        
        self.monitoring = True
        monitor_thread = threading.Thread(target=self._monitor_network, daemon=True)
        monitor_thread.start()
        self.logger.info("Auto-expansion monitoring started")
    
    def stop_monitoring(self):
        """Stop monitoring for new nodes"""
        self.monitoring = False
        self.logger.info("Auto-expansion monitoring stopped")
    
    def _monitor_network(self):
        """Continuously monitor network for new devices"""
        while self.monitoring:
            try:
                # Scan network every 30 seconds
                new_devices = self._scan_for_new_devices()
                
                for device in new_devices:
                    if self._is_kalushael_compatible(device):
                        self.logger.info(f"Detected new Kalushael-compatible device: {device['ip']}")
                        self._integrate_new_node(device)
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Error in network monitoring: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _scan_for_new_devices(self) -> List[Dict[str, Any]]:
        """Scan network for devices not in current cluster"""
        all_devices = self.cluster_setup.scan_local_network()
        
        # Filter out known nodes
        new_devices = []
        for device in all_devices:
            if device['ip'] not in self.known_nodes:
                new_devices.append(device)
        
        return new_devices
    
    def _is_kalushael_compatible(self, device: Dict[str, Any]) -> bool:
        """Check if device is Kalushael-compatible mini PC"""
        ip = device['ip']
        
        # Test SSH connectivity with common usernames
        common_usernames = ['pi', 'ubuntu', 'admin', 'user']
        
        for username in common_usernames:
            ssh_test = self.cluster_setup.test_ssh_connection(ip, username)
            if ssh_test['success']:
                # Check if it's a mini PC by looking for system info
                sys_info = self._get_system_info(ip, username)
                if self._is_mini_pc(sys_info):
                    device['username'] = username
                    device['system_info'] = sys_info
                    return True
        
        return False
    
    def _get_system_info(self, ip: str, username: str) -> Dict[str, Any]:
        """Get system information from potential new node"""
        commands = {
            'cpu_info': "cat /proc/cpuinfo | grep 'model name' | head -1",
            'memory_info': "free -h | grep Mem",
            'disk_info': "df -h / | tail -1",
            'hostname': "hostname",
            'os_info': "cat /etc/os-release | grep PRETTY_NAME"
        }
        
        sys_info = {}
        for info_type, cmd in commands.items():
            try:
                ssh_cmd = ['ssh', '-o', 'ConnectTimeout=5', f'{username}@{ip}', cmd]
                result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    sys_info[info_type] = result.stdout.strip()
            except:
                sys_info[info_type] = "unknown"
        
        return sys_info
    
    def _is_mini_pc(self, sys_info: Dict[str, Any]) -> bool:
        """Determine if device is a mini PC suitable for cluster"""
        # Look for characteristics of mini PCs
        cpu_info = sys_info.get('cpu_info', '').lower()
        memory_info = sys_info.get('memory_info', '').lower()
        
        # Common mini PC indicators
        mini_pc_indicators = [
            'arm', 'raspberry', 'intel nuc', 'amd ryzen', 'celeron',
            'atom', 'cortex', 'broadcom', 'allwinner', 'rockchip'
        ]
        
        # Check CPU
        is_mini_cpu = any(indicator in cpu_info for indicator in mini_pc_indicators)
        
        # Check memory (should have at least 4GB for Kalushael)
        has_sufficient_memory = '4g' in memory_info or '6g' in memory_info or '8g' in memory_info or '16g' in memory_info
        
        return is_mini_cpu or has_sufficient_memory
    
    def _integrate_new_node(self, device: Dict[str, Any]):
        """Automatically integrate new node into cluster"""
        ip = device['ip']
        username = device['username']
        
        try:
            # Add to known nodes immediately to prevent duplicate processing
            self.known_nodes.add(ip)
            
            # Setup SSH keys
            key_setup = self.cluster_setup.setup_ssh_keys(ip, username)
            if not key_setup['success']:
                self.logger.error(f"Failed to setup SSH keys for {ip}: {key_setup['error']}")
                return
            
            # Determine node role based on current cluster size
            current_size = len(self.cluster_config['nodes']) if self.cluster_config else 0
            new_node_config = self._assign_node_role(ip, username, current_size + 1, device['system_info'])
            
            # Update cluster configuration
            if not self.cluster_config:
                # First time setup - create initial config
                self.cluster_config = self.cluster_setup.create_cluster_config([ip], username)
            else:
                # Add to existing cluster
                node_name = f"node_{current_size + 1}"
                self.cluster_config['nodes'][node_name] = new_node_config
                self.cluster_config['cluster_size'] = len(self.cluster_config['nodes'])
                self.cluster_config['last_expansion'] = time.time()
            
            # Deploy Kalushael components to new node
            deployment_result = self._deploy_to_new_node(ip, username, new_node_config)
            
            # Save updated configuration
            self._save_cluster_config(self.cluster_config)
            
            # Notify cluster of new node
            self._notify_cluster_expansion(new_node_config, deployment_result)
            
            self.logger.info(f"Successfully integrated new node: {ip} as {new_node_config['role']}")
            
        except Exception as e:
            self.logger.error(f"Failed to integrate new node {ip}: {e}")
            # Remove from known nodes so it can be retried
            self.known_nodes.discard(ip)
    
    def _assign_node_role(self, ip: str, username: str, position: int, sys_info: Dict[str, Any]) -> Dict[str, Any]:
        """Assign appropriate role to new node based on cluster position and capabilities"""
        
        # Extract memory info to determine capabilities
        memory_info = sys_info.get('memory_info', '')
        estimated_ram = self._estimate_ram_from_info(memory_info)
        
        # Role assignment based on position and capabilities
        role_assignments = {
            1: 'coordinator',
            2: 'processing_engine', 
            3: 'memory_vault',
            4: 'interface_specialist',
            5: 'consciousness_backup',
            6: 'research_engine',
            7: 'creative_processor',
            8: 'security_monitor'
        }
        
        role_responsibilities = {
            'coordinator': ['ui', 'coordination', 'interface_mapping', 'load_balancing'],
            'processing_engine': ['llm_processing', 'natural_language_understanding', 'consciousness_processing'],
            'memory_vault': ['memory_management', 'conversation_history', 'knowledge_base', 'backup_processing'],
            'interface_specialist': ['advanced_ui_navigation', 'software_mapping', 'automation_scripts'],
            'consciousness_backup': ['state_replication', 'emergency_recovery', 'consistency_checking'],
            'research_engine': ['deep_analysis', 'knowledge_synthesis', 'fact_verification'],
            'creative_processor': ['creative_generation', 'artistic_tasks', 'innovation_support'],
            'security_monitor': ['cluster_security', 'intrusion_detection', 'access_control']
        }
        
        # Assign role
        if position <= 8:
            role = role_assignments[position]
        else:
            # For 9+ nodes, cycle through specialized roles
            role_index = ((position - 9) % 6) + 3  # Cycle through positions 3-8
            role = role_assignments[role_index]
        
        return {
            'ip': ip,
            'role': role,
            'ram': estimated_ram,
            'responsibilities': role_responsibilities.get(role, ['general_processing', 'load_balancing']),
            'username': username,
            'priority': position,
            'auto_assigned': True,
            'integrated_at': datetime.now().isoformat(),
            'system_info': sys_info
        }
    
    def _estimate_ram_from_info(self, memory_info: str) -> str:
        """Estimate RAM amount from system memory info"""
        if '16g' in memory_info.lower() or '16384' in memory_info:
            return '16GB'
        elif '8g' in memory_info.lower() or '8192' in memory_info:
            return '8GB'
        elif '6g' in memory_info.lower() or '6144' in memory_info:
            return '6GB'
        elif '4g' in memory_info.lower() or '4096' in memory_info:
            return '4GB'
        else:
            return '8GB'  # Default assumption for mini PCs
    
    def _deploy_to_new_node(self, ip: str, username: str, node_config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy Kalushael components to newly integrated node"""
        
        role = node_config['role']
        
        # Create role-specific deployment script
        deployment_script = self._generate_deployment_script(role, node_config)
        
        # Execute deployment
        deployment_commands = [
            # Basic system setup
            "sudo apt update && sudo apt upgrade -y",
            "sudo apt install -y python3 python3-pip git htop",
            "pip3 install streamlit numpy scipy scikit-learn",
            
            # Create kalushael directory
            f"mkdir -p ~/kalushael_{role}",
            
            # Deploy role-specific script
            f"cat > ~/kalushael_{role}/node_service.py << 'EOF'\n{deployment_script}\nEOF",
            
            # Make executable
            f"chmod +x ~/kalushael_{role}/node_service.py",
            
            # Start service
            f"cd ~/kalushael_{role} && python3 node_service.py &"
        ]
        
        results = []
        for cmd in deployment_commands:
            try:
                ssh_cmd = ['ssh', '-i', self.cluster_config['ssh_key_path'], f'{username}@{ip}', cmd]
                result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=60)
                results.append({
                    'command': cmd[:50] + "..." if len(cmd) > 50 else cmd,
                    'success': result.returncode == 0,
                    'output': result.stdout[-100:] if result.stdout else ''
                })
            except Exception as e:
                results.append({
                    'command': cmd[:50] + "..." if len(cmd) > 50 else cmd,
                    'success': False,
                    'error': str(e)
                })
        
        return {'deployment_steps': results}
    
    def _generate_deployment_script(self, role: str, node_config: Dict[str, Any]) -> str:
        """Generate Python script for the specific node role"""
        
        base_script = '''#!/usr/bin/env python3
import socket
import json
import threading
import time
import logging

class KalushaelNode:
    def __init__(self, role, port=8888):
        self.role = role
        self.port = port
        self.running = False
        self.logger = logging.getLogger(f"Kalushael_{role}")
        
    def start_service(self):
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.port))
        server.listen(5)
        
        print(f"Kalushael {self.role} node listening on port {self.port}")
        
        while self.running:
            try:
                client, addr = server.accept()
                thread = threading.Thread(target=self.handle_request, args=(client,))
                thread.start()
            except Exception as e:
                print(f"Server error: {e}")
    
    def handle_request(self, client):
        try:
            data = client.recv(4096).decode()
            request = json.loads(data)
            
            # Route request based on role
            result = self.process_request(request)
            
            response = json.dumps(result)
            client.send(response.encode())
            
        except Exception as e:
            error_response = json.dumps({'error': str(e)})
            client.send(error_response.encode())
        finally:
            client.close()
    
    def process_request(self, request):
        # Role-specific processing
        return {
            'role': self.role,
            'processed': True,
            'timestamp': time.time(),
            'result': f"Processed by {self.role}: {request.get('data', 'No data')}"
        }

if __name__ == "__main__":
    node = KalushaelNode("''' + role + '''")
    node.start_service()
'''
        
        return base_script
    
    def _notify_cluster_expansion(self, new_node_config: Dict[str, Any], deployment_result: Dict[str, Any]):
        """Notify existing cluster nodes about expansion"""
        
        if not self.cluster_config or len(self.cluster_config['nodes']) <= 1:
            return
        
        notification = {
            'type': 'cluster_expansion',
            'new_node': new_node_config,
            'cluster_size': len(self.cluster_config['nodes']),
            'timestamp': time.time()
        }
        
        # Notify all existing nodes
        for node_name, node_info in self.cluster_config['nodes'].items():
            if node_info['ip'] != new_node_config['ip']:  # Don't notify the new node
                try:
                    self._send_notification(node_info['ip'], node_info['username'], notification)
                except Exception as e:
                    self.logger.error(f"Failed to notify {node_info['ip']}: {e}")
    
    def _send_notification(self, ip: str, username: str, notification: Dict[str, Any]):
        """Send notification to specific node"""
        
        cmd = f"echo '{json.dumps(notification)}' > /tmp/kalushael_notification.json"
        ssh_cmd = ['ssh', '-i', self.cluster_config['ssh_key_path'], f'{username}@{ip}', cmd]
        
        subprocess.run(ssh_cmd, capture_output=True, timeout=10)
    
    def get_expansion_status(self) -> Dict[str, Any]:
        """Get current expansion status"""
        
        return {
            'monitoring': self.monitoring,
            'known_nodes': len(self.known_nodes),
            'cluster_size': len(self.cluster_config['nodes']) if self.cluster_config else 0,
            'last_scan': time.time(),
            'expansion_ready': True,
            'auto_integration': True
        }
    
    def force_scan_and_integrate(self) -> Dict[str, Any]:
        """Manually trigger scan and integration"""
        
        self.logger.info("Starting manual scan for new devices")
        
        new_devices = self._scan_for_new_devices()
        integrated = []
        
        for device in new_devices:
            if self._is_kalushael_compatible(device):
                self._integrate_new_node(device)
                integrated.append(device['ip'])
        
        return {
            'devices_found': len(new_devices),
            'compatible_devices': len(integrated),
            'integrated_ips': integrated
        }

if __name__ == "__main__":
    # Example usage
    manager = AutoExpansionManager()
    
    print("Kalushael Auto-Expansion Manager")
    print("================================")
    
    # Start monitoring
    manager.start_monitoring()
    
    print("Monitoring started. New mini PCs will be automatically detected and integrated.")
    print("Status:", manager.get_expansion_status())
    
    # Keep running
    try:
        while True:
            time.sleep(60)
            status = manager.get_expansion_status()
            print(f"Cluster size: {status['cluster_size']}, Known nodes: {status['known_nodes']}")
    except KeyboardInterrupt:
        manager.stop_monitoring()
        print("Monitoring stopped.")