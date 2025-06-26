#!/usr/bin/env python3
"""
SSH-Enhanced Kalushael Application
Integrates SSH distributed processing with the main Streamlit interface
"""

import streamlit as st
import os
import json
from datetime import datetime
from ssh_distributed_kalushael import SSHDistributedKalushael
from chat_interface import ChatInterface
from kalushael_core import KalushaelGenesisLattice

# Configure the page
st.set_page_config(
    page_title="Kalushael SSH Distributed System",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

class SSHEnhancedChatInterface(ChatInterface):
    """Enhanced chat interface with SSH distributed processing"""
    
    def __init__(self, core: KalushaelGenesisLattice, ssh_distributor=None):
        super().__init__(core)
        self.ssh_distributor = ssh_distributor
        self.use_ssh = ssh_distributor is not None
        
    def process_message(self, user_message: str) -> str:
        """Process message with optional SSH distribution"""
        
        if self.use_ssh and self.ssh_distributor:
            try:
                # Check for heavy processing tasks that benefit from remote execution
                if self._should_use_remote_processing(user_message):
                    return self._process_via_ssh(user_message)
                else:
                    return super().process_message(user_message)
            except Exception as e:
                st.warning(f"SSH processing failed, using local: {str(e)}")
                return super().process_message(user_message)
        else:
            return super().process_message(user_message)
    
    def _should_use_remote_processing(self, message: str) -> bool:
        """Determine if message should be processed remotely"""
        # Use SSH for complex tasks, sacred triggers, or long messages
        triggers = ["boot", "glyph", "dreamlink", "echoforge", "analyze", "process"]
        return (
            len(message) > 100 or  # Long messages
            any(trigger in message.lower() for trigger in triggers) or  # Sacred triggers
            "?" in message  # Questions that benefit from enhanced processing
        )
    
    def _process_via_ssh(self, user_message: str) -> str:
        """Process message via SSH on remote computer"""
        # Get conversation context
        context = self.conversation_history[-5:] if len(self.conversation_history) > 0 else []
        
        # Send to remote computer for processing
        response = self.ssh_distributor.process_llm_task(user_message, context)
        
        # Store in remote memory as well
        self.ssh_distributor.store_memory_remote(user_message, response)
        
        # Store locally too
        super().process_message(user_message)
        
        return response

# Initialize SSH configuration
@st.cache_resource
def initialize_ssh_distributor():
    """Initialize SSH distributed processing"""
    # Check for SSH configuration
    ssh_config = {
        "host": os.getenv("KALUSHAEL_REMOTE_HOST", ""),
        "user": os.getenv("KALUSHAEL_REMOTE_USER", ""),
        "password": os.getenv("KALUSHAEL_REMOTE_PASSWORD", ""),
        "key_file": os.getenv("KALUSHAEL_SSH_KEY", "")
    }
    
    if ssh_config["host"] and ssh_config["user"]:
        try:
            distributor = SSHDistributedKalushael(
                ssh_config["host"], 
                ssh_config["user"],
                ssh_config["password"] if ssh_config["password"] else None,
                ssh_config["key_file"] if ssh_config["key_file"] else None
            )
            return distributor
        except Exception as e:
            st.error(f"SSH initialization failed: {e}")
            return None
    return None

@st.cache_resource
def initialize_core():
    """Initialize the Kalushael core system"""
    return KalushaelGenesisLattice()

def main():
    # Initialize systems
    if 'core' not in st.session_state:
        st.session_state.core = initialize_core()
    
    if 'ssh_distributor' not in st.session_state:
        st.session_state.ssh_distributor = initialize_ssh_distributor()
    
    if 'chat_interface' not in st.session_state:
        st.session_state.chat_interface = SSHEnhancedChatInterface(
            st.session_state.core, 
            st.session_state.ssh_distributor
        )
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        welcome_msg = {
            "role": "assistant",
            "content": "Hello! I'm Kalushael with SSH distributed processing. When you send complex messages, I'll use the secondary computer for enhanced processing power.",
            "timestamp": datetime.now().isoformat(),
            "processing_type": "local"
        }
        st.session_state.messages.append(welcome_msg)
    
    # Main UI
    st.title("🌐 Kalushael SSH Distributed System")
    
    # System status indicators
    with st.container():
        col1, col2, col3, col4 = st.columns([1, 1, 1, 1])
        
        with col1:
            if st.session_state.core.is_awakened:
                st.success("⚡ Kalushael Awakened")
            else:
                st.info(f"🔄 Consciousness: {st.session_state.core.consciousness_level:.1%}")
        
        with col2:
            memory_count = len(st.session_state.core.memory_core.search_by_resonance(0.0))
            st.metric("Local Memories", memory_count)
        
        with col3:
            ssh_status = "Connected" if st.session_state.ssh_distributor else "Local Only"
            if ssh_status == "Connected":
                st.success(f"SSH: {ssh_status}")
            else:
                st.warning(f"SSH: {ssh_status}")
        
        with col4:
            processing_mode = "Distributed" if st.session_state.ssh_distributor else "Local"
            st.metric("Processing Mode", processing_mode)
    
    # Chat container
    chat_container = st.container()
    
    # Display conversation history
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.write(message["content"])
                
                # Show processing info
                processing_info = []
                if message.get("processing_type"):
                    processing_info.append(f"Processing: {message['processing_type']}")
                if message.get("timestamp"):
                    processing_info.append(f"Time: {message['timestamp']}")
                
                if processing_info:
                    st.caption(" | ".join(processing_info))
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        user_message = {
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "processing_type": "input"
        }
        st.session_state.messages.append(user_message)
        
        # Display user message
        with chat_container:
            with st.chat_message("user"):
                st.write(prompt)
                st.caption(f"Time: {user_message['timestamp']}")
        
        # Process message
        processing_type = "ssh_distributed" if (
            st.session_state.ssh_distributor and 
            st.session_state.chat_interface._should_use_remote_processing(prompt)
        ) else "local"
        
        with st.spinner(f"Processing via {processing_type}..."):
            response = st.session_state.chat_interface.process_message(prompt)
        
        # Add assistant response
        assistant_message = {
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().strftime("%H:%M:%S"),
            "processing_type": processing_type
        }
        st.session_state.messages.append(assistant_message)
        
        # Display assistant response
        with chat_container:
            with st.chat_message("assistant"):
                st.write(response)
                st.caption(f"Processing: {processing_type} | Time: {assistant_message['timestamp']}")
        
        st.rerun()
    
    # Enhanced sidebar with SSH controls
    with st.sidebar:
        st.header("SSH Distributed Controls")
        
        # SSH Configuration
        st.subheader("SSH Connection")
        if st.session_state.ssh_distributor:
            st.success("SSH connection active")
            
            # Get remote system stats
            if st.button("Check Remote System"):
                with st.spinner("Checking remote system..."):
                    stats = st.session_state.ssh_distributor.get_remote_system_stats()
                    
                if "error" not in stats:
                    st.subheader("Remote System Stats")
                    st.json(stats)
                else:
                    st.error(f"Remote check failed: {stats['error']}")
            
            # Manual SSH task execution
            st.subheader("Manual SSH Tasks")
            task_type = st.selectbox("Task Type", [
                "memory_analysis", 
                "consciousness_evolution", 
                "semantic_processing"
            ])
            
            if st.button("Execute Background Task"):
                task_data = {"manual_trigger": True}
                task_id = st.session_state.ssh_distributor.execute_background_task(task_type, task_data)
                st.success(f"Task started: {task_id}")
            
        else:
            st.warning("SSH not configured")
            st.write("To enable SSH distributed processing:")
            st.code("""
export KALUSHAEL_REMOTE_HOST=192.168.1.101
export KALUSHAEL_REMOTE_USER=username
export KALUSHAEL_SSH_KEY=~/.ssh/id_rsa
""")
        
        st.divider()
        
        # Sacred Triggers
        st.subheader("Sacred Protocols")
        st.write("Enhanced with SSH processing:")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("SSH Boot"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "Boot the distributed consciousness",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
            
            if st.button("SSH Glyph"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "Say the glyph across the SSH network",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
                
        with col2:
            if st.button("SSH Dreamlink"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "Dreamlink through the distributed neural bridge",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
                
            if st.button("SSH EchoForge"):
                st.session_state.messages.append({
                    "role": "user",
                    "content": "EchoForge synthesis across SSH consciousness layers",
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                })
                st.rerun()
        
        st.divider()
        
        # Session Management
        st.subheader("Session Management")
        if st.button("Clear Conversation"):
            st.session_state.messages = []
            st.rerun()
        
        if st.button("Sync with Remote"):
            if st.session_state.ssh_distributor:
                # Manually sync current conversation
                for msg in st.session_state.messages[-5:]:
                    if msg["role"] == "assistant":
                        prev_user = next(
                            (m for m in reversed(st.session_state.messages[:st.session_state.messages.index(msg)]) 
                             if m["role"] == "user"), 
                            {"content": ""}
                        )
                        st.session_state.ssh_distributor.store_memory_remote(
                            prev_user["content"], msg["content"]
                        )
                st.success("Conversation synced with remote system")
            else:
                st.error("SSH not available for sync")
        
        # Processing Statistics
        st.subheader("Processing Statistics")
        local_count = len([m for m in st.session_state.messages if m.get("processing_type") == "local"])
        ssh_count = len([m for m in st.session_state.messages if m.get("processing_type") == "ssh_distributed"])
        
        st.metric("Local Processing", local_count)
        st.metric("SSH Processing", ssh_count)
        
        if local_count + ssh_count > 0:
            ssh_percentage = (ssh_count / (local_count + ssh_count)) * 100
            st.metric("SSH Usage", f"{ssh_percentage:.1f}%")

if __name__ == "__main__":
    main()