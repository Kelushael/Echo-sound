#!/usr/bin/env python3
"""
Ethernet Network Setup for Kalushael Mini PC Cluster
Simple direct connection between two mini PCs on same WiFi network
"""

import subprocess
import socket
import json
import time
import platform
from typing import Dict, List, Any, Optional, Tuple
import logging

class EthernetClusterSetup:
    """Setup and manage ethernet connection between mini PCs"""
    
    def __init__(self):
        self.logger = logging.getLogger("EthernetCluster")
        self.network_config = {}
        self.connection_status = {}
        
    def detect_network_interfaces(self) -> Dict[str, Any]:
        """Detect available network interfaces"""
        interfaces = {}
        
        try:
            if platform.system() == "Darwin":  # macOS
                result = subprocess.run(['ifconfig'], capture_output=True, text=True)
                output = result.stdout
                
                # Parse ifconfig output for ethernet interfaces
                current_interface = None
                for line in output.split('\n'):
                    if line and not line.startswith('\t') and not line.startswith(' '):
                        # New interface
                        interface_name = line.split(':')[0]
                        if 'en' in interface_name or 'eth' in interface_name:
                            current_interface = interface_name
                            interfaces[current_interface] = {'type': 'ethernet', 'status': 'unknown'}
                    elif current_interface and 'inet ' in line:
                        # IP address line
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            ip = parts[1]
                            interfaces[current_interface]['ip'] = ip
                            interfaces[current_interface]['status'] = 'active'
                            
            elif platform.system() == "Linux":
                # Linux ip command
                result = subprocess.run(['ip', 'addr', 'show'], capture_output=True, text=True)
                output = result.stdout
                
                current_interface = None
                for line in output.split('\n'):
                    if line and not line.startswith(' '):
                        # Interface line
                        if 'eth' in line or 'enp' in line or 'ens' in line:
                            parts = line.split(':')
                            if len(parts) >= 2:
                                current_interface = parts[1].strip()
                                interfaces[current_interface] = {'type': 'ethernet', 'status': 'unknown'}
                    elif current_interface and 'inet ' in line:
                        # IP address
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            ip = parts[1].split('/')[0]  # Remove subnet mask
                            interfaces[current_interface]['ip'] = ip
                            interfaces[current_interface]['status'] = 'active'
            
        except Exception as e:
            self.logger.error(f"Error detecting interfaces: {e}")
        
        return interfaces
    
    def get_local_ip_addresses(self) -> List[str]:
        """Get all local IP addresses"""
        ips = []
        
        try:
            # Get hostname and resolve to IPs
            hostname = socket.gethostname()
            ip_list = socket.gethostbyname_ex(hostname)[2]
            
            # Filter out loopback
            ips = [ip for ip in ip_list if not ip.startswith("127.")]
            
        except Exception as e:
            self.logger.error(f"Error getting local IPs: {e}")
        
        return ips
    
    def scan_local_network(self, base_ip: str = None) -> List[Dict[str, Any]]:
        """Scan local network for other devices"""
        if not base_ip:
            local_ips = self.get_local_ip_addresses()
            if local_ips:
                base_ip = local_ips[0]
            else:
                return []
        
        # Extract network portion (assume /24)
        network_parts = base_ip.split('.')
        network_base = '.'.join(network_parts[:3])
        
        devices = []
        
        # Ping scan common addresses
        for i in range(1, 255):
            target_ip = f"{network_base}.{i}"
            
            try:
                # Quick ping test
                if platform.system() == "Darwin":
                    cmd = ['ping', '-c', '1', '-W', '1000', target_ip]
                else:
                    cmd = ['ping', '-c', '1', '-W', '1', target_ip]
                
                result = subprocess.run(cmd, capture_output=True, timeout=2)
                
                if result.returncode == 0:
                    # Device responds
                    device_info = {
                        'ip': target_ip,
                        'status': 'reachable',
                        'response_time': 'fast'
                    }
                    
                    # Try to get hostname
                    try:
                        hostname = socket.gethostbyaddr(target_ip)[0]
                        device_info['hostname'] = hostname
                    except:
                        device_info['hostname'] = 'unknown'
                    
                    devices.append(device_info)
                    
            except subprocess.TimeoutExpired:
                continue
            except Exception as e:
                continue
        
        return devices
    
    def test_ssh_connection(self, target_ip: str, username: str = None, key_path: str = None) -> Dict[str, Any]:
        """Test SSH connection to target device"""
        if not username:
            username = "pi"  # Common default for mini PCs
        
        try:
            if key_path:
                cmd = ['ssh', '-i', key_path, '-o', 'ConnectTimeout=5', 
                       '-o', 'StrictHostKeyChecking=no', f'{username}@{target_ip}', 'echo "Connection test"']
            else:
                cmd = ['ssh', '-o', 'ConnectTimeout=5', 
                       '-o', 'StrictHostKeyChecking=no', f'{username}@{target_ip}', 'echo "Connection test"']
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout.strip(),
                'error': result.stderr.strip(),
                'target': f'{username}@{target_ip}'
            }
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Connection timeout', 'target': f'{username}@{target_ip}'}
        except Exception as e:
            return {'success': False, 'error': str(e), 'target': f'{username}@{target_ip}'}
    
    def setup_ssh_keys(self, target_ip: str, username: str) -> Dict[str, Any]:
        """Setup SSH key authentication between devices"""
        key_path = f"{platform.os.path.expanduser('~')}/.ssh/kalushael_cluster"
        
        try:
            # Generate SSH key if it doesn't exist
            if not platform.os.path.exists(key_path):
                cmd = ['ssh-keygen', '-t', 'rsa', '-b', '4096', '-f', key_path, '-N', '']
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                if result.returncode != 0:
                    return {'success': False, 'error': 'Failed to generate SSH key'}
            
            # Copy public key to target
            pub_key_path = f"{key_path}.pub"
            cmd = ['ssh-copy-id', '-i', pub_key_path, f'{username}@{target_ip}']
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            return {
                'success': result.returncode == 0,
                'key_path': key_path,
                'public_key_path': pub_key_path,
                'output': result.stdout,
                'error': result.stderr if result.returncode != 0 else None
            }
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def create_cluster_config(self, node_ips: List[str], username: str = "pi") -> Dict[str, Any]:
        """Create cluster configuration for multiple mini PCs (2-3 nodes)"""
        
        if len(node_ips) < 2:
            raise ValueError("At least 2 nodes required for cluster")
        
        config = {
            'cluster_name': 'kalushael_ethernet_cluster',
            'created': time.time(),
            'cluster_size': len(node_ips),
            'expansion_ready': True,
            'nodes': {},
            'network': {
                'type': 'ethernet_mesh',
                'wifi_shared': True,
                'connection_method': 'ssh',
                'auto_discovery': True
            },
            'ssh_key_path': f"{platform.os.path.expanduser('~')}/.ssh/kalushael_cluster"
        }
        
        # Define node roles based on cluster size
        if len(node_ips) == 2:
            # Two-node configuration
            config['nodes']['primary'] = {
                'ip': node_ips[0],
                'role': 'coordinator',
                'ram': '6GB',
                'responsibilities': ['ui', 'coordination', 'interface_mapping'],
                'username': username,
                'priority': 1
            }
            config['nodes']['secondary'] = {
                'ip': node_ips[1],
                'role': 'processing',
                'ram': '8GB',
                'responsibilities': ['llm_processing', 'memory_management', 'heavy_computation'],
                'username': username,
                'priority': 2
            }
            
        elif len(node_ips) >= 3:
            # Multi-node configuration - specialized roles that scale infinitely
            config['nodes']['primary'] = {
                'ip': node_ips[0],
                'role': 'coordinator',
                'ram': '6GB',
                'responsibilities': ['ui', 'coordination', 'interface_mapping', 'load_balancing'],
                'username': username,
                'priority': 1
            }
            config['nodes']['processing'] = {
                'ip': node_ips[1],
                'role': 'processing_engine',
                'ram': '8GB',
                'responsibilities': ['llm_processing', 'natural_language_understanding', 'consciousness_processing'],
                'username': username,
                'priority': 2
            }
            config['nodes']['memory'] = {
                'ip': node_ips[2],
                'role': 'memory_vault',
                'ram': '8GB',
                'responsibilities': ['memory_management', 'conversation_history', 'knowledge_base', 'backup_processing'],
                'username': username,
                'priority': 3
            }
            
            # Additional nodes get specialized roles automatically
            for i, additional_ip in enumerate(node_ips[3:], start=4):
                node_roles = [
                    'interface_specialist',  # 4th node: Advanced interface navigation
                    'consciousness_backup',  # 5th node: Consciousness state backup
                    'research_engine',      # 6th node: Deep research and analysis
                    'creative_processor',   # 7th node: Creative and generative tasks
                    'security_monitor',     # 8th node: Security and monitoring
                    'expansion_coordinator' # 9th+ nodes: Handle cluster expansion
                ]
                
                role_responsibilities = {
                    'interface_specialist': ['advanced_ui_navigation', 'software_mapping', 'automation_scripts'],
                    'consciousness_backup': ['state_replication', 'emergency_recovery', 'consistency_checking'],
                    'research_engine': ['deep_analysis', 'knowledge_synthesis', 'fact_verification'],
                    'creative_processor': ['creative_generation', 'artistic_tasks', 'innovation_support'],
                    'security_monitor': ['cluster_security', 'intrusion_detection', 'access_control'],
                    'expansion_coordinator': ['new_node_integration', 'load_distribution', 'resource_optimization']
                }
                
                role_index = min(i - 4, len(node_roles) - 1)
                role_name = node_roles[role_index]
                
                config['nodes'][f'node_{i}'] = {
                    'ip': additional_ip,
                    'role': role_name,
                    'ram': '8GB',
                    'responsibilities': role_responsibilities.get(role_name, ['general_processing', 'load_balancing']),
                    'username': username,
                    'priority': i,
                    'auto_assigned': True
                }
        
        # Add expansion capabilities
        config['expansion'] = {
            'max_nodes': 'unlimited',
            'auto_discovery': True,
            'plug_and_play': True,
            'role_assignment': 'automatic',
            'load_balancing': 'dynamic'
        }
        
        return config
    
    def deploy_cluster_setup(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Deploy the cluster setup to both nodes"""
        
        results = {'primary': {}, 'secondary': {}}
        
        # Test connections
        primary_test = self.test_ssh_connection(
            config['primary_node']['ip'], 
            config['primary_node']['username'],
            config['ssh_key_path']
        )
        results['primary']['connection_test'] = primary_test
        
        secondary_test = self.test_ssh_connection(
            config['secondary_node']['ip'], 
            config['secondary_node']['username'], 
            config['ssh_key_path']
        )
        results['secondary']['connection_test'] = secondary_test
        
        # Deploy Kalushael components if connections work
        if primary_test['success'] and secondary_test['success']:
            
            # Deploy to secondary (processing node)
            secondary_deploy = self._deploy_processing_node(
                config['secondary_node']['ip'],
                config['secondary_node']['username'],
                config['ssh_key_path']
            )
            results['secondary']['deployment'] = secondary_deploy
            
            # Update primary with cluster config
            primary_deploy = self._update_primary_config(config)
            results['primary']['deployment'] = primary_deploy
            
        return results
    
    def _deploy_processing_node(self, ip: str, username: str, key_path: str) -> Dict[str, Any]:
        """Deploy processing components to secondary node"""
        
        commands = [
            # Update system
            "sudo apt update && sudo apt upgrade -y",
            
            # Install Python and dependencies
            "sudo apt install -y python3 python3-pip git",
            
            # Install specific packages for processing
            "pip3 install streamlit numpy scipy scikit-learn transformers torch",
            
            # Create kalushael directory
            "mkdir -p ~/kalushael_processing",
            
            # Create processing service script
            """cat > ~/kalushael_processing/processing_node.py << 'EOF'
#!/usr/bin/env python3
import socket
import json
import threading
import time

class ProcessingNode:
    def __init__(self, port=8888):
        self.port = port
        self.running = False
    
    def start_server(self):
        self.running = True
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind(('0.0.0.0', self.port))
        server.listen(5)
        
        print(f"Processing node listening on port {self.port}")
        
        while self.running:
            try:
                client, addr = server.accept()
                thread = threading.Thread(target=self.handle_client, args=(client,))
                thread.start()
            except Exception as e:
                print(f"Server error: {e}")
    
    def handle_client(self, client):
        try:
            data = client.recv(4096).decode()
            request = json.loads(data)
            
            # Process request based on type
            if request.get('type') == 'llm_processing':
                result = self.process_llm_task(request.get('data', {}))
            elif request.get('type') == 'memory_search':
                result = self.search_memory(request.get('data', {}))
            else:
                result = {'error': 'Unknown request type'}
            
            response = json.dumps(result)
            client.send(response.encode())
            
        except Exception as e:
            error_response = json.dumps({'error': str(e)})
            client.send(error_response.encode())
        finally:
            client.close()
    
    def process_llm_task(self, data):
        # Mock LLM processing - replace with actual implementation
        return {
            'processed': True,
            'result': f"Processed: {data.get('text', 'No text')}",
            'timestamp': time.time()
        }
    
    def search_memory(self, data):
        # Mock memory search - replace with actual implementation
        return {
            'found': True,
            'results': [f"Memory result for: {data.get('query', 'No query')}"],
            'timestamp': time.time()
        }

if __name__ == "__main__":
    node = ProcessingNode()
    node.start_server()
EOF""",
            
            # Make script executable
            "chmod +x ~/kalushael_processing/processing_node.py",
            
            # Create systemd service for auto-start
            """sudo bash -c 'cat > /etc/systemd/system/kalushael-processing.service << EOF
[Unit]
Description=Kalushael Processing Node
After=network.target

[Service]
Type=simple
User=""" + username + """
WorkingDirectory=/home/""" + username + """/kalushael_processing
ExecStart=/usr/bin/python3 processing_node.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF'""",
            
            # Enable and start service
            "sudo systemctl enable kalushael-processing",
            "sudo systemctl start kalushael-processing"
        ]
        
        results = []
        for cmd in commands:
            try:
                ssh_cmd = ['ssh', '-i', key_path, f'{username}@{ip}', cmd]
                result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=60)
                results.append({
                    'command': cmd[:50] + "..." if len(cmd) > 50 else cmd,
                    'success': result.returncode == 0,
                    'output': result.stdout[-200:] if result.stdout else '',
                    'error': result.stderr[-200:] if result.stderr else ''
                })
            except Exception as e:
                results.append({
                    'command': cmd[:50] + "..." if len(cmd) > 50 else cmd,
                    'success': False,
                    'error': str(e)
                })
        
        return {'deployment_steps': results}
    
    def _update_primary_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Update primary node with cluster configuration"""
        
        config_path = "kalushael_cluster_config.json"
        
        try:
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            return {
                'success': True,
                'config_path': config_path,
                'message': 'Primary node configured for cluster operation'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get status of the ethernet cluster"""
        
        # Try to load existing config
        try:
            with open('kalushael_cluster_config.json', 'r') as f:
                config = json.load(f)
        except:
            return {'status': 'not_configured', 'message': 'No cluster configuration found'}
        
        status = {
            'configured': True,
            'primary_node': config['primary_node'],
            'secondary_node': config['secondary_node'],
            'connection_tests': {}
        }
        
        # Test connections
        primary_test = self.test_ssh_connection(
            config['primary_node']['ip'],
            config['primary_node']['username'],
            config['ssh_key_path']
        )
        status['connection_tests']['primary'] = primary_test
        
        secondary_test = self.test_ssh_connection(
            config['secondary_node']['ip'],
            config['secondary_node']['username'],
            config['ssh_key_path']
        )
        status['connection_tests']['secondary'] = secondary_test
        
        status['operational'] = primary_test['success'] and secondary_test['success']
        
        return status

def create_simple_setup_guide() -> str:
    """Create a simple setup guide for ethernet connection"""
    
    guide = """
# Kalushael Ethernet Cluster Setup Guide

## Physical Setup
1. Connect both mini PCs to same WiFi network
2. Connect ethernet cable directly between the two mini PCs
3. Both devices will have WiFi IP addresses on same subnet

## Automatic Discovery
The system will automatically:
- Detect your network interfaces
- Scan for other devices on the network
- Identify the second mini PC
- Setup SSH key authentication
- Deploy processing components

## Usage
Once setup is complete:
- Primary PC (6GB RAM): Runs UI and coordinates tasks
- Secondary PC (8GB RAM): Handles heavy processing and memory operations
- Ethernet provides dedicated high-speed link for data transfer
- WiFi provides internet access for both devices

## Network Layout
```
Internet
   |
WiFi Router
   |    |
  PC1  PC2
   |____| (Ethernet direct connection)
```

This gives you the best of both worlds:
- Shared internet via WiFi
- High-speed direct connection via Ethernet
- Automatic failover if ethernet fails
"""
    
    return guide

if __name__ == "__main__":
    # Example usage
    cluster = EthernetClusterSetup()
    
    print("Kalushael Ethernet Cluster Setup")
    print("=================================")
    
    # Detect network interfaces
    print("\nDetecting network interfaces...")
    interfaces = cluster.detect_network_interfaces()
    for name, details in interfaces.items():
        print(f"  {name}: {details}")
    
    # Get local IPs
    print(f"\nLocal IP addresses: {cluster.get_local_ip_addresses()}")
    
    # Print setup guide
    print("\n" + create_simple_setup_guide())