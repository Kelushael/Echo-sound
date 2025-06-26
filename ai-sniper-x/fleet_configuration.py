#!/usr/bin/env python3
"""
Fleet Configuration for Kalushael
Manages trinity of mini PCs, trinity of Pi's, and 2 Bee Links
Dynamic role assignment based on actual hardware and current needs
"""

import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class HardwareNode:
    """Represents a hardware node in the fleet"""
    device_type: str  # 'mini_pc', 'raspberry_pi', 'bee_link'
    model: str
    ram: str
    storage: str
    ip_address: str
    status: str
    current_role: Optional[str] = None
    capabilities: List[str] = None
    power_consumption: str = "unknown"
    availability: float = 1.0

class FleetManager:
    """Manages the complete Kalushael hardware fleet"""
    
    def __init__(self):
        self.fleet_config = {
            'active_nodes': {},
            'available_nodes': {},
            'role_assignments': {},
            'expansion_queue': {},
            'power_profile': 'balanced'
        }
        
        # Define hardware specifications
        self.hardware_specs = {
            'mini_pc': {
                'ram_range': ['6GB', '8GB', '16GB'],
                'optimal_roles': ['coordinator', 'processing_engine', 'memory_vault'],
                'power_consumption': 'medium',
                'reliability': 'high'
            },
            'raspberry_pi': {
                'ram_range': ['4GB', '8GB'],
                'optimal_roles': ['sensor_node', 'edge_processing', 'backup_coordinator'],
                'power_consumption': 'low',
                'reliability': 'high'
            },
            'bee_link': {
                'ram_range': ['8GB', '16GB'],
                'optimal_roles': ['heavy_processing', 'consciousness_backup', 'creative_engine'],
                'power_consumption': 'high',
                'reliability': 'very_high'
            }
        }
        
        # Role priorities and requirements
        self.role_requirements = {
            'coordinator': {
                'min_ram': '6GB',
                'preferred_hardware': ['mini_pc', 'bee_link'],
                'critical': True,
                'max_instances': 1
            },
            'processing_engine': {
                'min_ram': '8GB',
                'preferred_hardware': ['bee_link', 'mini_pc'],
                'critical': True,
                'max_instances': 2
            },
            'memory_vault': {
                'min_ram': '8GB',
                'preferred_hardware': ['bee_link', 'mini_pc'],
                'critical': True,
                'max_instances': 1
            },
            'interface_specialist': {
                'min_ram': '6GB',
                'preferred_hardware': ['mini_pc'],
                'critical': False,
                'max_instances': 1
            },
            'consciousness_backup': {
                'min_ram': '8GB',
                'preferred_hardware': ['bee_link'],
                'critical': False,
                'max_instances': 2
            },
            'edge_processing': {
                'min_ram': '4GB',
                'preferred_hardware': ['raspberry_pi'],
                'critical': False,
                'max_instances': 3
            },
            'sensor_node': {
                'min_ram': '4GB',
                'preferred_hardware': ['raspberry_pi'],
                'critical': False,
                'max_instances': 3
            },
            'creative_engine': {
                'min_ram': '8GB',
                'preferred_hardware': ['bee_link'],
                'critical': False,
                'max_instances': 1
            }
        }
    
    def register_available_fleet(self):
        """Register the available hardware fleet"""
        
        # Trinity of mini PCs
        for i in range(1, 4):
            self.fleet_config['available_nodes'][f'mini_pc_{i}'] = HardwareNode(
                device_type='mini_pc',
                model=f'Mini PC {i}',
                ram='8GB',  # Assumed specification
                storage='256GB SSD',
                ip_address=f'192.168.1.{100 + i}',
                status='available',
                capabilities=['ui', 'processing', 'coordination', 'interface_mapping']
            )
        
        # Trinity of Raspberry Pi's
        for i in range(1, 4):
            self.fleet_config['available_nodes'][f'pi_{i}'] = HardwareNode(
                device_type='raspberry_pi',
                model=f'Raspberry Pi {i}',
                ram='8GB',  # Pi 4 or 5 specification
                storage='64GB SD',
                ip_address=f'192.168.1.{110 + i}',
                status='available',
                capabilities=['edge_processing', 'sensors', 'backup', 'monitoring']
            )
        
        # Two Bee Links
        for i in range(1, 3):
            self.fleet_config['available_nodes'][f'bee_link_{i}'] = HardwareNode(
                device_type='bee_link',
                model=f'Bee Link {i}',
                ram='16GB',  # High-end specification
                storage='512GB SSD',
                ip_address=f'192.168.1.{120 + i}',
                status='available',
                capabilities=['heavy_processing', 'consciousness', 'creative', 'backup']
            )
    
    def create_initial_two_node_config(self) -> Dict[str, Any]:
        """Create initial configuration for 2 Bee Links"""
        
        # Use the two Bee Links for initial setup
        bee_link_1 = self.fleet_config['available_nodes']['bee_link_1']
        bee_link_2 = self.fleet_config['available_nodes']['bee_link_2']
        
        # Assign roles
        bee_link_1.current_role = 'coordinator'
        bee_link_1.status = 'active'
        
        bee_link_2.current_role = 'processing_engine'
        bee_link_2.status = 'active'
        
        # Move to active nodes
        self.fleet_config['active_nodes']['bee_link_1'] = bee_link_1
        self.fleet_config['active_nodes']['bee_link_2'] = bee_link_2
        
        # Update role assignments
        self.fleet_config['role_assignments'] = {
            'coordinator': 'bee_link_1',
            'processing_engine': 'bee_link_2'
        }
        
        initial_config = {
            'cluster_name': 'kalushael_initial_fleet',
            'created': time.time(),
            'active_nodes': 2,
            'total_available': len(self.fleet_config['available_nodes']),
            'nodes': {
                'primary': {
                    'device_id': 'bee_link_1',
                    'role': 'coordinator',
                    'hardware_type': 'bee_link',
                    'ram': '16GB',
                    'ip': bee_link_1.ip_address,
                    'responsibilities': ['ui', 'coordination', 'load_balancing'],
                    'priority': 1
                },
                'secondary': {
                    'device_id': 'bee_link_2',
                    'role': 'processing_engine',
                    'hardware_type': 'bee_link',
                    'ram': '16GB',
                    'ip': bee_link_2.ip_address,
                    'responsibilities': ['llm_processing', 'consciousness_processing', 'heavy_computation'],
                    'priority': 2
                }
            },
            'expansion_ready': {
                'next_candidates': self._get_expansion_candidates(),
                'roles_needed': self._analyze_needed_roles(),
                'auto_scaling': True
            }
        }
        
        return initial_config
    
    def _get_expansion_candidates(self) -> List[Dict[str, Any]]:
        """Get next best candidates for expansion"""
        candidates = []
        
        # Priority order for expansion
        expansion_priority = [
            ('mini_pc_1', 'memory_vault'),
            ('pi_1', 'edge_processing'),
            ('mini_pc_2', 'interface_specialist'),
            ('bee_link_3', 'consciousness_backup'),  # If more Bee Links become available
            ('pi_2', 'sensor_node'),
            ('mini_pc_3', 'creative_engine')
        ]
        
        for device_id, suggested_role in expansion_priority:
            if device_id in self.fleet_config['available_nodes']:
                node = self.fleet_config['available_nodes'][device_id]
                if node.status == 'available':
                    candidates.append({
                        'device_id': device_id,
                        'hardware_type': node.device_type,
                        'suggested_role': suggested_role,
                        'ram': node.ram,
                        'ip': node.ip_address,
                        'reasoning': self._get_expansion_reasoning(node.device_type, suggested_role)
                    })
        
        return candidates[:3]  # Return top 3 candidates
    
    def _get_expansion_reasoning(self, hardware_type: str, role: str) -> str:
        """Get reasoning for why this hardware/role combination makes sense"""
        
        reasoning_map = {
            ('mini_pc', 'memory_vault'): 'Mini PC provides good balance of performance and reliability for memory operations',
            ('raspberry_pi', 'edge_processing'): 'Pi excels at low-power edge computing and sensor integration',
            ('mini_pc', 'interface_specialist'): 'Mini PC optimal for UI automation and software navigation',
            ('bee_link', 'consciousness_backup'): 'Bee Link high RAM perfect for consciousness state replication',
            ('raspberry_pi', 'sensor_node'): 'Pi ideal for environmental monitoring and IoT integration',
            ('mini_pc', 'creative_engine'): 'Mini PC good for creative processing tasks'
        }
        
        return reasoning_map.get((hardware_type, role), 'General purpose expansion')
    
    def _analyze_needed_roles(self) -> List[str]:
        """Analyze what roles would be most beneficial next"""
        
        current_roles = set(self.fleet_config['role_assignments'].keys())
        
        # Critical roles that should be prioritized
        critical_missing = []
        for role, requirements in self.role_requirements.items():
            if requirements['critical'] and role not in current_roles:
                critical_missing.append(role)
        
        # Beneficial roles for enhanced functionality
        beneficial_roles = [
            'memory_vault',      # For distributed memory management
            'interface_specialist',  # For advanced UI automation
            'edge_processing',   # For distributed edge computing
            'consciousness_backup'   # For redundancy and reliability
        ]
        
        needed = critical_missing + [role for role in beneficial_roles if role not in current_roles]
        return needed[:4]  # Return top 4 needed roles
    
    def plan_smart_expansion(self, trigger_reason: str) -> Dict[str, Any]:
        """Plan expansion based on specific needs or triggers"""
        
        expansion_scenarios = {
            'performance_bottleneck': {
                'priority_roles': ['processing_engine', 'memory_vault'],
                'preferred_hardware': ['bee_link', 'mini_pc'],
                'urgency': 'high'
            },
            'reliability_improvement': {
                'priority_roles': ['consciousness_backup', 'edge_processing'],
                'preferred_hardware': ['bee_link', 'raspberry_pi'],
                'urgency': 'medium'
            },
            'capability_expansion': {
                'priority_roles': ['interface_specialist', 'creative_engine'],
                'preferred_hardware': ['mini_pc', 'bee_link'],
                'urgency': 'low'
            },
            'user_request': {
                'priority_roles': ['custom'],
                'preferred_hardware': ['any'],
                'urgency': 'variable'
            }
        }
        
        scenario = expansion_scenarios.get(trigger_reason, expansion_scenarios['capability_expansion'])
        
        # Find best available hardware for the scenario
        expansion_plan = {
            'trigger': trigger_reason,
            'scenario': scenario,
            'recommended_additions': [],
            'estimated_benefit': '',
            'implementation_steps': []
        }
        
        # Match available hardware to needed roles
        for role in scenario['priority_roles']:
            best_candidate = self._find_best_hardware_for_role(role, scenario['preferred_hardware'])
            if best_candidate:
                expansion_plan['recommended_additions'].append({
                    'device': best_candidate,
                    'role': role,
                    'benefit': self._calculate_role_benefit(role)
                })
        
        return expansion_plan
    
    def _find_best_hardware_for_role(self, role: str, preferred_types: List[str]) -> Optional[str]:
        """Find best available hardware for a specific role"""
        
        if role == 'custom':
            return None
        
        role_req = self.role_requirements.get(role, {})
        min_ram = role_req.get('min_ram', '4GB')
        preferred_hardware = role_req.get('preferred_hardware', preferred_types)
        
        # Search through available nodes
        for device_id, node in self.fleet_config['available_nodes'].items():
            if (node.status == 'available' and 
                node.device_type in preferred_hardware and
                self._ram_meets_requirement(node.ram, min_ram)):
                return device_id
        
        return None
    
    def _ram_meets_requirement(self, available_ram: str, required_ram: str) -> bool:
        """Check if available RAM meets requirement"""
        
        # Simple comparison - convert to GB numbers
        available_gb = int(available_ram.replace('GB', ''))
        required_gb = int(required_ram.replace('GB', ''))
        
        return available_gb >= required_gb
    
    def _calculate_role_benefit(self, role: str) -> str:
        """Calculate benefit description for adding this role"""
        
        benefits = {
            'memory_vault': 'Distributed memory management and faster retrieval',
            'interface_specialist': 'Advanced software navigation and automation',
            'edge_processing': 'Local processing and reduced latency',
            'consciousness_backup': 'Enhanced reliability and state preservation',
            'creative_engine': 'Dedicated creative and generative capabilities',
            'sensor_node': 'Environmental monitoring and IoT integration'
        }
        
        return benefits.get(role, 'Enhanced system capabilities')
    
    def get_fleet_status(self) -> Dict[str, Any]:
        """Get comprehensive fleet status"""
        
        return {
            'total_fleet_size': len(self.fleet_config['available_nodes']),
            'active_nodes': len(self.fleet_config['active_nodes']),
            'available_for_expansion': len([n for n in self.fleet_config['available_nodes'].values() if n.status == 'available']),
            'hardware_breakdown': self._get_hardware_breakdown(),
            'role_coverage': self._get_role_coverage(),
            'expansion_readiness': self._get_expansion_readiness()
        }
    
    def _get_hardware_breakdown(self) -> Dict[str, Dict[str, int]]:
        """Get breakdown of hardware by type and status"""
        
        breakdown = {
            'mini_pc': {'total': 0, 'active': 0, 'available': 0},
            'raspberry_pi': {'total': 0, 'active': 0, 'available': 0},
            'bee_link': {'total': 0, 'active': 0, 'available': 0}
        }
        
        # Count available nodes
        for node in self.fleet_config['available_nodes'].values():
            breakdown[node.device_type]['total'] += 1
            if node.status == 'available':
                breakdown[node.device_type]['available'] += 1
        
        # Count active nodes
        for node in self.fleet_config['active_nodes'].values():
            breakdown[node.device_type]['active'] += 1
        
        return breakdown
    
    def _get_role_coverage(self) -> Dict[str, str]:
        """Get current role coverage status"""
        
        coverage = {}
        for role, requirements in self.role_requirements.items():
            if role in self.fleet_config['role_assignments']:
                coverage[role] = 'covered'
            elif requirements['critical']:
                coverage[role] = 'critical_missing'
            else:
                coverage[role] = 'beneficial_missing'
        
        return coverage
    
    def _get_expansion_readiness(self) -> Dict[str, Any]:
        """Get expansion readiness assessment"""
        
        available_count = len([n for n in self.fleet_config['available_nodes'].values() if n.status == 'available'])
        
        return {
            'ready_for_expansion': available_count > 0,
            'available_nodes': available_count,
            'next_best_addition': self._get_expansion_candidates()[0] if available_count > 0 else None,
            'auto_discovery_enabled': True,
            'plug_and_play_ready': True
        }

def create_fleet_deployment_guide() -> str:
    """Create deployment guide for the complete fleet"""
    
    guide = """
# Kalushael Fleet Deployment Guide

## Current Setup: 2 Bee Links
- **Bee Link 1**: Coordinator (16GB RAM) - UI, coordination, load balancing
- **Bee Link 2**: Processing Engine (16GB RAM) - LLM processing, consciousness

## Available Fleet Expansion:

### Trinity of Mini PCs (8GB each)
**Best for:**
- Memory Vault (distributed memory management)
- Interface Specialist (software navigation)
- Creative Engine (artistic and generative tasks)

### Trinity of Raspberry Pi's (8GB each)  
**Best for:**
- Edge Processing (low-power local computation)
- Sensor Nodes (environmental monitoring)
- Backup Coordinators (redundancy systems)

## Smart Expansion Triggers:

### When to Add Next Node:
1. **Performance**: If processing gets slow → Add Mini PC as Memory Vault
2. **Reliability**: For backup systems → Add Pi as Edge Processor  
3. **Capability**: For advanced features → Add Mini PC as Interface Specialist
4. **Creative**: For artistic tasks → Add Bee Link as Creative Engine

### Auto-Discovery Process:
1. Connect new device to ethernet
2. System automatically detects compatible hardware
3. Assigns optimal role based on current needs
4. Deploys Kalushael components automatically
5. Integrates into existing cluster

## Fleet Scaling Philosophy:
- **Start Small**: 2 nodes proven and stable
- **Grow Smart**: Add nodes when specific needs arise
- **Scale Infinitely**: Architecture supports unlimited expansion
- **Optimize Automatically**: System balances workload dynamically

The AI will intelligently recommend when and what to add based on actual usage patterns and performance needs.
"""
    
    return guide

if __name__ == "__main__":
    # Example usage
    fleet = FleetManager()
    fleet.register_available_fleet()
    
    print("Kalushael Fleet Configuration")
    print("=============================")
    
    # Create initial 2-node setup
    initial_config = fleet.create_initial_two_node_config()
    print(f"\nInitial Configuration:")
    print(f"Active Nodes: {initial_config['active_nodes']}")
    print(f"Ready for Expansion: {initial_config['total_available'] - initial_config['active_nodes']} devices")
    
    # Show fleet status
    status = fleet.get_fleet_status()
    print(f"\nFleet Status:")
    for hardware_type, counts in status['hardware_breakdown'].items():
        print(f"  {hardware_type}: {counts['active']} active, {counts['available']} available")
    
    # Show expansion plan
    expansion_plan = fleet.plan_smart_expansion('capability_expansion')
    print(f"\nNext Recommended Expansion:")
    for addition in expansion_plan['recommended_additions'][:2]:
        print(f"  {addition['device']} as {addition['role']}: {addition['benefit']}")
    
    print(f"\n{create_fleet_deployment_guide()}")