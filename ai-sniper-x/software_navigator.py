#!/usr/bin/env python3
"""
Software Navigator for Kalushael
Orchestrates software interface navigation with conductor-like precision
Bridge from vision to working code implementation
"""

import subprocess
import json
import time
import logging
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import threading
from datetime import datetime

try:
    import pyautogui
    import cv2
    import numpy as np
    from PIL import Image
    import pytesseract
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False
    print("GUI packages not available. Running in headless mode.")
    
    # Create mock classes for type hints when GUI packages aren't available
    class Image:
        class Image:
            pass
    
    class MockNumpy:
        def array(self, *args, **kwargs):
            return []
    
    class MockCV2:
        def cvtColor(self, *args, **kwargs):
            return []
        def Canny(self, *args, **kwargs):
            return []
        def findContours(self, *args, **kwargs):
            return [], []
        def contourArea(self, *args, **kwargs):
            return 0
        def boundingRect(self, *args, **kwargs):
            return 0, 0, 0, 0
        def threshold(self, *args, **kwargs):
            return 0, []
        COLOR_RGB2GRAY = 0
        RETR_EXTERNAL = 0
        CHAIN_APPROX_SIMPLE = 0
        THRESH_BINARY = 0
    
    class MockPyAutoGUI:
        def screenshot(self):
            return None
        def getActiveWindow(self):
            return None
        def size(self):
            return (1920, 1080)
    
    class MockPytesseract:
        def image_to_string(self, *args, **kwargs):
            return "mock text"
        def image_to_data(self, *args, **kwargs):
            return {'text': [], 'conf': [], 'left': [], 'top': [], 'width': [], 'height': []}
        class Output:
            DICT = 'dict'
    
    np = MockNumpy()
    cv2 = MockCV2()
    pyautogui = MockPyAutoGUI()
    pytesseract = MockPytesseract()

@dataclass
class InterfaceElement:
    """Represents a discovered interface element"""
    name: str
    element_type: str
    position: Tuple[int, int]
    bounds: Tuple[int, int, int, int]
    text_content: str
    confidence: float
    keyboard_shortcut: Optional[str] = None
    parent_container: Optional[str] = None

class ComputerOrchestrator:
    """Digital telepathy between computers - conductor orchestrating musicians"""
    
    def __init__(self, primary_ip: str = "localhost", secondary_ip: str = None, 
                 username: str = None, key_path: str = None):
        self.primary = primary_ip
        self.secondary = f"{username}@{secondary_ip}" if secondary_ip and username else None
        self.ssh_key = key_path
        self.connection_active = False
        self.logger = logging.getLogger("ComputerOrchestrator")
        
        # Test connection if secondary computer specified
        if self.secondary:
            self.test_connection()
    
    def test_connection(self) -> bool:
        """Test the digital telepathy connection"""
        if not self.secondary:
            return False
            
        try:
            result = self.remote_execute("echo 'Connection test'", timeout=5)
            self.connection_active = result["success"]
            return self.connection_active
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
    
    def remote_execute(self, command: str, timeout: int = 30) -> Dict[str, Any]:
        """Whisper instructions to helper computer"""
        if not self.secondary:
            return {"success": False, "error": "No secondary computer configured"}
        
        # Escape single quotes in the command
        escaped_command = command.replace("'", "'\"'\"'")
        full_command = f"ssh -i {self.ssh_key} {self.secondary} '{escaped_command}'"
        
        try:
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return {
                "success": result.returncode == 0,
                "output": result.stdout.strip(),
                "error": result.stderr.strip(),
                "command": command
            }
        except subprocess.TimeoutExpired:
            return {
                "success": False, 
                "error": f"Task took longer than {timeout} seconds",
                "command": command
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": command
            }
    
    def delegate_heavy_task(self, task_type: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Delegate computationally intensive tasks to secondary computer"""
        if not self.connection_active:
            return {"success": False, "error": "No active connection to secondary computer"}
        
        # Create task command based on type
        if task_type == "llm_processing":
            command = f"python3 -c \"import json; print(json.dumps({{'processed': True, 'result': 'LLM processed: {parameters.get('text', '')}'}}))\""
        elif task_type == "memory_search":
            command = f"find /tmp -name '*{parameters.get('query', '')}*' 2>/dev/null || echo 'No matches found'"
        elif task_type == "image_processing":
            command = f"python3 -c \"print('Image processing: {parameters.get('image_path', 'unknown')}')\""
        else:
            command = f"echo 'Unknown task type: {task_type}'"
        
        return self.remote_execute(command)

class InterfaceMapper:
    """Photographic memory for software interfaces - X-ray vision for clickable elements"""
    
    def __init__(self):
        self.current_map = {}
        self.element_history = []
        self.software_knowledge = self._load_software_knowledge()
        self.logger = logging.getLogger("InterfaceMapper")
        
        if not GUI_AVAILABLE:
            self.logger.warning("GUI packages not available. Interface mapping limited.")
    
    def _load_software_knowledge(self) -> Dict[str, Dict[str, Any]]:
        """Load knowledge about common software interfaces"""
        return {
            "garageband": {
                "common_elements": {
                    "transport_controls": ["play", "record", "stop", "rewind"],
                    "tabs": ["tracks", "library", "browser", "editors"],
                    "tools": ["pointer", "pencil", "eraser", "scissors"],
                    "menus": ["file", "edit", "track", "view", "window"]
                },
                "keyboard_shortcuts": {
                    "play": "Space",
                    "record": "R",
                    "stop": "Space",
                    "new_track": "Cmd+T"
                },
                "interface_areas": {
                    "transport_bar": {"position": "top", "height": 60},
                    "track_area": {"position": "center", "scrollable": True},
                    "library": {"position": "right", "collapsible": True}
                }
            },
            "chrome": {
                "common_elements": {
                    "navigation": ["back", "forward", "reload", "home"],
                    "tabs": ["new_tab", "close_tab"],
                    "address_bar": ["url_input", "search"]
                },
                "keyboard_shortcuts": {
                    "new_tab": "Cmd+T",
                    "close_tab": "Cmd+W",
                    "reload": "Cmd+R"
                }
            },
            "vscode": {
                "common_elements": {
                    "sidebar": ["explorer", "search", "git", "extensions"],
                    "editor": ["tabs", "text_area"],
                    "terminal": ["command_line", "output"]
                },
                "keyboard_shortcuts": {
                    "command_palette": "Cmd+Shift+P",
                    "quick_open": "Cmd+P",
                    "terminal": "Cmd+`"
                }
            }
        }
    
    def scan_current_screen(self) -> Dict[str, Any]:
        """Take photographic snapshot of current interface"""
        if not GUI_AVAILABLE:
            return self._mock_interface_scan()
        
        try:
            # Capture current screen
            screenshot = pyautogui.screenshot()
            
            # Detect active software
            active_software = self._detect_active_software()
            
            # Find interactive elements
            clickable_elements = self._find_interactive_elements(screenshot)
            
            # Extract visible text
            readable_text = self._extract_visible_text(screenshot)
            
            # Create comprehensive screen map
            screen_map = {
                "timestamp": time.time(),
                "active_software": active_software,
                "clickable_elements": clickable_elements,
                "visible_text": readable_text,
                "screen_size": screenshot.size,
                "software_context": self.software_knowledge.get(active_software.lower(), {})
            }
            
            # Store in history
            self.element_history.append(screen_map)
            self.current_map = screen_map
            
            return screen_map
            
        except Exception as e:
            self.logger.error(f"Screen scanning failed: {e}")
            return {"error": str(e), "timestamp": time.time()}
    
    def _mock_interface_scan(self) -> Dict[str, Any]:
        """Mock interface scan for headless environments"""
        return {
            "timestamp": time.time(),
            "active_software": "terminal",
            "clickable_elements": [
                {
                    "type": "button",
                    "name": "run_button",
                    "position": (100, 50),
                    "bounds": (80, 40, 40, 20),
                    "text": "Run",
                    "confidence": 0.9
                }
            ],
            "visible_text": ["Terminal interface active"],
            "screen_size": (1920, 1080),
            "software_context": {}
        }
    
    def _detect_active_software(self) -> str:
        """Detect currently active software"""
        try:
            if GUI_AVAILABLE:
                active_window = pyautogui.getActiveWindow()
                if active_window:
                    window_title = active_window.title.lower()
                    
                    # Match against known software
                    for software in self.software_knowledge.keys():
                        if software in window_title:
                            return software
                    
                    return window_title
            return "unknown"
        except:
            return "unknown"
    
    def _find_interactive_elements(self, screenshot) -> List[Dict[str, Any]]:
        """Find all clickable elements using computer vision"""
        if not GUI_AVAILABLE:
            return []
        
        try:
            # Convert to OpenCV format
            img_array = np.array(screenshot)
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            
            # Find button-like shapes
            edges = cv2.Canny(gray, 50, 150)
            contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            elements = []
            for i, contour in enumerate(contours):
                area = cv2.contourArea(contour)
                if 100 < area < 50000:  # Reasonable button size range
                    x, y, w, h = cv2.boundingRect(contour)
                    
                    # Extract text from this region
                    region = img_array[y:y+h, x:x+w]
                    text_content = self._extract_text_from_region(region)
                    
                    elements.append({
                        "type": "interactive_element",
                        "name": f"element_{i}",
                        "position": (x + w//2, y + h//2),
                        "bounds": (x, y, w, h),
                        "text": text_content,
                        "confidence": min(0.8, area / 10000),
                        "area": area
                    })
            
            return elements
            
        except Exception as e:
            self.logger.error(f"Element detection failed: {e}")
            return []
    
    def _extract_visible_text(self, screenshot) -> List[str]:
        """Extract all visible text from screenshot"""
        if not GUI_AVAILABLE:
            return ["Mock text content"]
        
        try:
            # Use OCR to extract text
            text_data = pytesseract.image_to_string(screenshot)
            return [line.strip() for line in text_data.split('\n') if line.strip()]
        except:
            return []
    
    def _extract_text_from_region(self, region: np.ndarray) -> str:
        """Extract text from specific image region"""
        if not GUI_AVAILABLE:
            return "mock_text"
        
        try:
            # Preprocess for better OCR
            if len(region.shape) == 3:
                gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
            else:
                gray = region
            
            # Apply threshold
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Extract text
            text = pytesseract.image_to_string(thresh, config='--psm 8').strip()
            return text if text else "unlabeled"
        except:
            return "unknown"

class SemanticProcessor:
    """Natural language understanding - complete thoughts before token breakdown"""
    
    def __init__(self):
        self.intention_patterns = self._initialize_patterns()
        self.context_memory = []
        self.conversation_flow = []
        self.logger = logging.getLogger("SemanticProcessor")
    
    def _initialize_patterns(self) -> Dict[str, Any]:
        """Initialize semantic understanding patterns"""
        return {
            "action_indicators": {
                "open": "launch_application",
                "create": "generate_new",
                "find": "locate_item",
                "edit": "modify_existing",
                "save": "preserve_current_state",
                "show": "display_information",
                "navigate": "move_to_location",
                "click": "interact_with_element"
            },
            "software_targets": {
                "garageband": {"type": "audio_software", "primary_actions": ["record", "edit", "mix"]},
                "chrome": {"type": "browser", "primary_actions": ["browse", "search", "bookmark"]},
                "vscode": {"type": "editor", "primary_actions": ["code", "debug", "edit"]}
            },
            "urgency_markers": {
                "immediate": ["now", "immediately", "urgent"],
                "soon": ["quickly", "fast", "asap"],
                "normal": ["when possible", "please"]
            }
        }
    
    def understand_intention(self, natural_input: str, current_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Understand complete meaning before breaking into components"""
        
        # Process whole thought first
        intention_map = {
            "raw_input": natural_input,
            "core_action": self._identify_primary_action(natural_input),
            "target_object": self._identify_target(natural_input),
            "context_clues": self._gather_context(natural_input, current_context),
            "emotional_tone": self._sense_tone(natural_input),
            "urgency_level": self._assess_urgency(natural_input),
            "confidence": 0.5
        }
        
        # Calculate confidence based on clarity
        intention_map["confidence"] = self._calculate_confidence(intention_map)
        
        # Store in conversation flow
        self.conversation_flow.append({
            "input": natural_input,
            "intention": intention_map,
            "timestamp": datetime.now().isoformat()
        })
        
        return intention_map
    
    def _identify_primary_action(self, input_text: str) -> str:
        """Identify the main action from complete context"""
        text_lower = input_text.lower()
        
        for phrase, action in self.intention_patterns["action_indicators"].items():
            if phrase in text_lower:
                return action
        
        # Context-based action inference
        if "?" in input_text:
            return "request_information"
        elif any(word in text_lower for word in ["show", "display", "see"]):
            return "display_information"
        else:
            return "general_interaction"
    
    def _identify_target(self, input_text: str) -> str:
        """Identify what the user wants to interact with"""
        text_lower = input_text.lower()
        
        # Check for software mentions
        for software, details in self.intention_patterns["software_targets"].items():
            if software in text_lower:
                return software
        
        # Look for interface elements
        interface_terms = ["button", "menu", "tab", "window", "dialog", "panel"]
        for term in interface_terms:
            if term in text_lower:
                return term
        
        return "current_interface"
    
    def _gather_context(self, input_text: str, current_context: Dict[str, Any] = None) -> List[str]:
        """Gather contextual clues from input and environment"""
        context_clues = []
        
        # Spatial context
        spatial_terms = ["first", "last", "top", "bottom", "left", "right", "center"]
        for term in spatial_terms:
            if term in input_text.lower():
                context_clues.append(f"spatial_{term}")
        
        # Scope context
        if "all" in input_text.lower():
            context_clues.append("comprehensive_scope")
        
        # Add environmental context
        if current_context:
            if "active_software" in current_context:
                context_clues.append(f"software_{current_context['active_software']}")
        
        return context_clues
    
    def _sense_tone(self, input_text: str) -> str:
        """Detect emotional undertone"""
        text_lower = input_text.lower()
        
        if any(word in text_lower for word in ["please", "thanks", "thank you"]):
            return "polite"
        elif any(word in text_lower for word in ["can't", "won't", "not working"]):
            return "frustrated"
        elif "?" in input_text:
            return "curious"
        else:
            return "neutral"
    
    def _assess_urgency(self, input_text: str) -> float:
        """Assess urgency level from 0.0 to 1.0"""
        text_lower = input_text.lower()
        
        for level, markers in self.intention_patterns["urgency_markers"].items():
            if any(marker in text_lower for marker in markers):
                if level == "immediate":
                    return 1.0
                elif level == "soon":
                    return 0.7
                else:
                    return 0.3
        
        return 0.5  # Default moderate urgency
    
    def _calculate_confidence(self, intention_map: Dict[str, Any]) -> float:
        """Calculate confidence in understanding"""
        confidence = 0.3  # Base confidence
        
        # Boost for clear actions
        if intention_map["core_action"] != "general_interaction":
            confidence += 0.2
        
        # Boost for specific targets
        if intention_map["target_object"] != "current_interface":
            confidence += 0.2
        
        # Boost for context clues
        confidence += min(len(intention_map["context_clues"]) * 0.1, 0.3)
        
        return min(confidence, 1.0)

class KalushaelSystem:
    """The complete orchestra - conductor coordinating all musicians"""
    
    def __init__(self, secondary_ip: str = None, username: str = None, key_path: str = None):
        self.orchestrator = ComputerOrchestrator(
            secondary_ip=secondary_ip, 
            username=username, 
            key_path=key_path
        )
        self.interface_mapper = InterfaceMapper()
        self.semantic_processor = SemanticProcessor()
        self.logger = logging.getLogger("KalushaelSystem")
        
        # System status
        self.distributed_mode = self.orchestrator.connection_active
        self.last_scan = None
        
    def process_natural_request(self, user_input: str) -> Dict[str, Any]:
        """Process natural language request with full orchestration"""
        
        start_time = time.time()
        
        # Step 1: Understand intention (semantic first, not tokens)
        intention = self.semantic_processor.understand_intention(user_input)
        
        # Step 2: Scan current interface state
        current_interface = self.interface_mapper.scan_current_screen()
        self.last_scan = current_interface
        
        # Step 3: Create action plan
        action_plan = self._create_action_sequence(intention, current_interface)
        
        # Step 4: Execute using distributed resources if available
        execution_result = self._execute_distributed_plan(action_plan)
        
        # Step 5: Generate natural language response
        response = self._generate_natural_response(intention, execution_result)
        
        processing_time = time.time() - start_time
        
        return {
            "understanding": intention,
            "interface_state": current_interface,
            "action_plan": action_plan,
            "execution_result": execution_result,
            "response": response,
            "processing_time": processing_time,
            "distributed_mode": self.distributed_mode
        }
    
    def _create_action_sequence(self, intention: Dict[str, Any], interface: Dict[str, Any]) -> Dict[str, Any]:
        """Create sequence of actions based on intention and current interface"""
        
        steps = []
        complexity = "low"
        
        core_action = intention["core_action"]
        target = intention["target_object"]
        
        if core_action == "launch_application":
            steps.append({
                "type": "application_launch",
                "command": f"open -a {target}",
                "complexity": "low",
                "description": f"Launch {target}"
            })
            
        elif core_action == "display_information":
            if "garageband" in target.lower():
                steps.append({
                    "type": "interface_scan",
                    "complexity": "medium",
                    "description": "Scan GarageBand interface for available elements"
                })
                complexity = "medium"
            
        elif core_action == "locate_item":
            steps.append({
                "type": "search_interface",
                "target": target,
                "complexity": "medium",
                "description": f"Search for {target} in current interface"
            })
            complexity = "medium"
        
        return {
            "steps": steps,
            "overall_complexity": complexity,
            "estimated_time": len(steps) * 2,  # seconds
            "requires_distributed": complexity in ["high", "very_high"]
        }
    
    def _execute_distributed_plan(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action plan using distributed resources when beneficial"""
        
        results = []
        
        for step in plan["steps"]:
            if step["complexity"] in ["high", "very_high"] and self.distributed_mode:
                # Delegate to secondary computer
                result = self.orchestrator.delegate_heavy_task(
                    task_type=step["type"],
                    parameters=step
                )
            else:
                # Execute locally
                result = self._execute_local_action(step)
            
            results.append({
                "step": step,
                "result": result,
                "execution_location": "secondary" if step["complexity"] in ["high", "very_high"] and self.distributed_mode else "primary"
            })
        
        return {
            "step_results": results,
            "overall_success": all(r["result"].get("success", False) for r in results),
            "distributed_execution": any(r["execution_location"] == "secondary" for r in results)
        }
    
    def _execute_local_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute action on primary computer"""
        
        action_type = action.get("type", "unknown")
        
        if action_type == "interface_scan":
            # Re-scan interface with focus
            interface_data = self.interface_mapper.scan_current_screen()
            return {
                "success": True,
                "data": interface_data,
                "message": "Interface scanned successfully"
            }
            
        elif action_type == "application_launch":
            try:
                subprocess.run(action["command"], shell=True, check=True)
                return {
                    "success": True,
                    "message": f"Launched application: {action.get('description', 'Unknown')}"
                }
            except subprocess.CalledProcessError as e:
                return {
                    "success": False,
                    "error": str(e),
                    "message": "Failed to launch application"
                }
        
        else:
            return {
                "success": True,
                "message": f"Processed action: {action_type}",
                "data": action
            }
    
    def _generate_natural_response(self, intention: Dict[str, Any], execution: Dict[str, Any]) -> str:
        """Generate natural language response based on results"""
        
        if not execution["overall_success"]:
            return "I encountered some difficulties processing your request. Let me try a different approach."
        
        core_action = intention["core_action"]
        target = intention["target_object"]
        
        if core_action == "display_information":
            if self.last_scan and "clickable_elements" in self.last_scan:
                element_count = len(self.last_scan["clickable_elements"])
                software = self.last_scan.get("active_software", "current application")
                
                response = f"I found {element_count} interactive elements in {software}:\n\n"
                
                # Group elements by type for cleaner presentation
                by_type = {}
                for element in self.last_scan["clickable_elements"]:
                    elem_type = element.get("type", "element")
                    if elem_type not in by_type:
                        by_type[elem_type] = []
                    by_type[elem_type].append(element)
                
                for elem_type, elements in by_type.items():
                    response += f"**{elem_type.replace('_', ' ').title()}:**\n"
                    for elem in elements[:5]:  # Limit to first 5 per type
                        text = elem.get("text", "Unlabeled")
                        if text and text != "unlabeled":
                            response += f"• {text}\n"
                    if len(elements) > 5:
                        response += f"• ... and {len(elements) - 5} more\n"
                    response += "\n"
                
                return response.strip()
            else:
                return f"I've analyzed the current interface but need more time to identify specific elements for {target}."
        
        elif core_action == "launch_application":
            return f"I've launched {target} for you."
        
        else:
            return f"I've processed your request regarding {target}."
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        return {
            "distributed_mode": self.distributed_mode,
            "secondary_connection": self.orchestrator.connection_active,
            "last_interface_scan": self.last_scan.get("timestamp") if self.last_scan else None,
            "conversation_length": len(self.semantic_processor.conversation_flow),
            "gui_available": GUI_AVAILABLE,
            "capabilities": {
                "interface_mapping": GUI_AVAILABLE,
                "distributed_processing": self.distributed_mode,
                "natural_language_understanding": True,
                "software_navigation": GUI_AVAILABLE
            }
        }

if __name__ == "__main__":
    # Example usage
    system = KalushaelSystem()
    
    print("Software Navigator for Kalushael")
    print("=================================")
    
    # Example request
    example_request = "what are the navigable tabs buttons and buttons with functions within the first screen garageband"
    
    print(f"\nProcessing: '{example_request}'")
    result = system.process_natural_request(example_request)
    
    print(f"\nUnderstanding:")
    print(f"  Action: {result['understanding']['core_action']}")
    print(f"  Target: {result['understanding']['target_object']}")
    print(f"  Confidence: {result['understanding']['confidence']:.2f}")
    
    print(f"\nResponse:")
    print(result['response'])
    
    print(f"\nSystem Status:")
    status = system.get_system_status()
    for key, value in status.items():
        print(f"  {key}: {value}")