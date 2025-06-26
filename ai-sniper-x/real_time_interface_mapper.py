#!/usr/bin/env python3
"""
Real-Time Interface Mapper for Kalushael
Instantly scans and maps all navigable elements in any software interface
"""

import pyautogui
import cv2
import numpy as np
import pytesseract
import json
import time
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass, asdict
import subprocess
import platform
import os

@dataclass
class InterfaceElement:
    """Represents a discoverable interface element"""
    name: str
    element_type: str  # button, tab, menu, field, slider, etc.
    position: Tuple[int, int]
    size: Tuple[int, int]
    text_content: str
    confidence: float
    keyboard_shortcut: Optional[str] = None
    tooltip: Optional[str] = None
    parent_container: Optional[str] = None

class RealTimeInterfaceScanner:
    """Scans current software interface and maps all interactive elements"""
    
    def __init__(self):
        self.screen_width, self.screen_height = pyautogui.size()
        self.current_elements = {}
        self.software_context = ""
        
        # Configure OCR
        self.setup_ocr()
        
    def setup_ocr(self):
        """Setup OCR for text recognition"""
        try:
            # Test tesseract installation
            pytesseract.get_tesseract_version()
            self.ocr_available = True
        except:
            print("Warning: Tesseract OCR not available. Text recognition limited.")
            self.ocr_available = False
    
    def scan_current_interface(self, target_software: str = None) -> Dict[str, InterfaceElement]:
        """Scan the currently active interface and map all elements"""
        
        # Take screenshot of current interface
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        
        # Detect software context
        if not target_software:
            target_software = self.detect_current_software()
        
        self.software_context = target_software
        
        # Find all interactive elements
        elements = {}
        
        # Scan for buttons
        buttons = self.find_buttons(screenshot_np)
        elements.update(buttons)
        
        # Scan for tabs
        tabs = self.find_tabs(screenshot_np)
        elements.update(tabs)
        
        # Scan for menus
        menus = self.find_menus(screenshot_np)
        elements.update(menus)
        
        # Scan for text fields
        fields = self.find_text_fields(screenshot_np)
        elements.update(fields)
        
        # Scan for sliders and controls
        controls = self.find_controls(screenshot_np)
        elements.update(controls)
        
        # Apply software-specific knowledge
        elements = self.apply_software_context(elements, target_software)
        
        self.current_elements = elements
        return elements
    
    def detect_current_software(self) -> str:
        """Detect currently active software"""
        try:
            if platform.system() == "Darwin":  # macOS
                script = '''
                tell application "System Events"
                    return name of first application process whose frontmost is true
                end tell
                '''
                result = subprocess.run(['osascript', '-e', script], 
                                      capture_output=True, text=True)
                return result.stdout.strip().lower()
            
            elif platform.system() == "Windows":
                import win32gui
                window = win32gui.GetForegroundWindow()
                return win32gui.GetWindowText(window).lower()
            
            elif platform.system() == "Linux":
                result = subprocess.run(['xdotool', 'getactivewindow', 'getwindowname'], 
                                      capture_output=True, text=True)
                return result.stdout.strip().lower()
                
        except Exception as e:
            print(f"Could not detect software: {e}")
            return "unknown"
    
    def find_buttons(self, image: np.ndarray) -> Dict[str, InterfaceElement]:
        """Find button elements in the interface"""
        buttons = {}
        
        # Convert to grayscale for processing
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Find rectangular button-like shapes
        edges = cv2.Canny(gray, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i, contour in enumerate(contours):
            # Filter for button-like rectangles
            area = cv2.contourArea(contour)
            if 100 < area < 10000:  # Reasonable button size range
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Buttons typically have certain aspect ratios
                if 0.3 < aspect_ratio < 5.0 and w > 30 and h > 15:
                    
                    # Extract text from button area
                    button_region = image[y:y+h, x:x+w]
                    text_content = self.extract_text_from_region(button_region)
                    
                    # Create button element
                    if text_content and len(text_content.strip()) > 0:
                        button_name = f"button_{text_content.lower().replace(' ', '_')}"
                        
                        buttons[button_name] = InterfaceElement(
                            name=button_name,
                            element_type="button",
                            position=(x + w//2, y + h//2),
                            size=(w, h),
                            text_content=text_content.strip(),
                            confidence=0.8
                        )
        
        return buttons
    
    def find_tabs(self, image: np.ndarray) -> Dict[str, InterfaceElement]:
        """Find tab elements in the interface"""
        tabs = {}
        
        # Tabs are typically arranged horizontally at the top
        # Look for text elements in the upper portion of the screen
        height, width = image.shape[:2]
        top_region = image[0:height//4, :]  # Top quarter of screen
        
        # Extract text regions that could be tabs
        text_regions = self.find_text_regions(top_region)
        
        for i, (x, y, w, h, text) in enumerate(text_regions):
            # Tabs typically have certain characteristics
            if w > 40 and h < 50 and len(text.strip()) > 0:
                tab_name = f"tab_{text.lower().replace(' ', '_')}"
                
                tabs[tab_name] = InterfaceElement(
                    name=tab_name,
                    element_type="tab",
                    position=(x + w//2, y + h//2),
                    size=(w, h),
                    text_content=text.strip(),
                    confidence=0.7
                )
        
        return tabs
    
    def find_menus(self, image: np.ndarray) -> Dict[str, InterfaceElement]:
        """Find menu elements in the interface"""
        menus = {}
        
        # Menus are typically in the top menu bar
        height, width = image.shape[:2]
        menu_region = image[0:60, :]  # Top menu bar area
        
        # Look for menu text
        text_regions = self.find_text_regions(menu_region)
        
        for i, (x, y, w, h, text) in enumerate(text_regions):
            if len(text.strip()) > 0 and w > 30:
                menu_name = f"menu_{text.lower().replace(' ', '_')}"
                
                menus[menu_name] = InterfaceElement(
                    name=menu_name,
                    element_type="menu",
                    position=(x + w//2, y + h//2),
                    size=(w, h),
                    text_content=text.strip(),
                    confidence=0.6
                )
        
        return menus
    
    def find_text_fields(self, image: np.ndarray) -> Dict[str, InterfaceElement]:
        """Find text input fields in the interface"""
        fields = {}
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Find rectangular regions that could be text fields
        edges = cv2.Canny(gray, 30, 100)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i, contour in enumerate(contours):
            area = cv2.contourArea(contour)
            if 500 < area < 50000:  # Text field size range
                
                x, y, w, h = cv2.boundingRect(contour)
                aspect_ratio = w / h
                
                # Text fields are typically wide and short
                if aspect_ratio > 2.0 and h < 50:
                    
                    field_region = image[y:y+h, x:x+w]
                    
                    # Check if it looks like an input field
                    if self.looks_like_input_field(field_region):
                        field_name = f"field_{i}"
                        
                        # Try to find associated label
                        label_text = self.find_field_label(image, x, y, w, h)
                        if label_text:
                            field_name = f"field_{label_text.lower().replace(' ', '_')}"
                        
                        fields[field_name] = InterfaceElement(
                            name=field_name,
                            element_type="text_field",
                            position=(x + w//2, y + h//2),
                            size=(w, h),
                            text_content=label_text or "",
                            confidence=0.7
                        )
        
        return fields
    
    def find_controls(self, image: np.ndarray) -> Dict[str, InterfaceElement]:
        """Find sliders, knobs, and other controls"""
        controls = {}
        
        # This would implement detection for:
        # - Sliders (horizontal/vertical bars)
        # - Knobs (circular controls)
        # - Toggle switches
        # - Progress bars
        
        # For now, implement basic slider detection
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Find horizontal lines that could be sliders
        horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (40, 1))
        horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
        
        contours, _ = cv2.findContours(horizontal_lines, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            if w > 50 and h < 20:  # Slider-like dimensions
                
                control_name = f"slider_{i}"
                
                controls[control_name] = InterfaceElement(
                    name=control_name,
                    element_type="slider",
                    position=(x + w//2, y + h//2),
                    size=(w, h),
                    text_content="",
                    confidence=0.5
                )
        
        return controls
    
    def extract_text_from_region(self, region: np.ndarray) -> str:
        """Extract text from image region using OCR"""
        if not self.ocr_available:
            return ""
        
        try:
            # Preprocess for better OCR
            if len(region.shape) == 3:
                gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
            else:
                gray = region
            
            # Apply threshold to improve OCR accuracy
            _, thresh = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)
            
            # Extract text
            text = pytesseract.image_to_string(thresh, config='--psm 8').strip()
            return text
            
        except Exception as e:
            return ""
    
    def find_text_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int, str]]:
        """Find all text regions in an image"""
        if not self.ocr_available:
            return []
        
        try:
            # Use OCR to find text boxes
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            
            text_regions = []
            for i in range(len(data['text'])):
                text = data['text'][i].strip()
                if text and int(data['conf'][i]) > 30:  # Confidence threshold
                    x = data['left'][i]
                    y = data['top'][i]
                    w = data['width'][i]
                    h = data['height'][i]
                    text_regions.append((x, y, w, h, text))
            
            return text_regions
            
        except Exception as e:
            return []
    
    def looks_like_input_field(self, region: np.ndarray) -> bool:
        """Determine if a region looks like an input field"""
        # Simple heuristic: input fields often have uniform backgrounds
        if len(region.shape) == 3:
            gray = cv2.cvtColor(region, cv2.COLOR_RGB2GRAY)
        else:
            gray = region
        
        # Check for uniform background (typical of input fields)
        std_dev = np.std(gray)
        return std_dev < 30  # Low variation suggests uniform background
    
    def find_field_label(self, image: np.ndarray, field_x: int, field_y: int, field_w: int, field_h: int) -> str:
        """Find label text associated with a field"""
        # Look for text to the left or above the field
        
        # Check left side
        left_region = image[field_y:field_y+field_h, max(0, field_x-150):field_x]
        left_text = self.extract_text_from_region(left_region)
        
        # Check above
        above_region = image[max(0, field_y-30):field_y, field_x:field_x+field_w]
        above_text = self.extract_text_from_region(above_region)
        
        # Return the most likely label
        if left_text and len(left_text.strip()) > 0:
            return left_text.strip()
        elif above_text and len(above_text.strip()) > 0:
            return above_text.strip()
        
        return ""
    
    def apply_software_context(self, elements: Dict[str, InterfaceElement], software: str) -> Dict[str, InterfaceElement]:
        """Apply software-specific knowledge to improve element detection"""
        
        if "garageband" in software.lower():
            return self.apply_garageband_context(elements)
        elif "chrome" in software.lower() or "firefox" in software.lower():
            return self.apply_browser_context(elements)
        elif "vscode" in software.lower() or "code" in software.lower():
            return self.apply_vscode_context(elements)
        
        return elements
    
    def apply_garageband_context(self, elements: Dict[str, InterfaceElement]) -> Dict[str, InterfaceElement]:
        """Apply GarageBand-specific interface knowledge"""
        
        # GarageBand interface knowledge
        garageband_elements = {
            "transport_controls": ["play", "pause", "stop", "record", "rewind", "fast_forward"],
            "track_controls": ["mute", "solo", "volume", "pan"],
            "tabs": ["tracks", "library", "browser", "editors"],
            "menus": ["file", "edit", "track", "view", "window", "help"],
            "tools": ["pointer", "pencil", "eraser", "scissors", "glue", "zoom"]
        }
        
        # Enhance detected elements with GarageBand knowledge
        enhanced_elements = elements.copy()
        
        for element_name, element in elements.items():
            text_lower = element.text_content.lower()
            
            # Identify transport controls
            for control in garageband_elements["transport_controls"]:
                if control in text_lower or control in element_name:
                    element.parent_container = "transport_bar"
                    element.element_type = "transport_control"
                    
                    # Add known keyboard shortcuts
                    shortcuts = {
                        "play": "Space",
                        "record": "R",
                        "rewind": "Return",
                        "stop": "Space"
                    }
                    if control in shortcuts:
                        element.keyboard_shortcut = shortcuts[control]
            
            # Identify track controls
            for control in garageband_elements["track_controls"]:
                if control in text_lower:
                    element.parent_container = "track_area"
                    element.element_type = "track_control"
            
            # Identify tabs
            for tab in garageband_elements["tabs"]:
                if tab in text_lower and element.element_type == "tab":
                    element.parent_container = "main_tabs"
            
            enhanced_elements[element_name] = element
        
        return enhanced_elements
    
    def apply_browser_context(self, elements: Dict[str, InterfaceElement]) -> Dict[str, InterfaceElement]:
        """Apply browser-specific interface knowledge"""
        # Similar implementation for browsers
        return elements
    
    def apply_vscode_context(self, elements: Dict[str, InterfaceElement]) -> Dict[str, InterfaceElement]:
        """Apply VS Code-specific interface knowledge"""
        # Similar implementation for VS Code
        return elements
    
    def get_navigable_summary(self) -> Dict[str, Any]:
        """Get human-readable summary of navigable elements"""
        
        if not self.current_elements:
            return {"error": "No interface scan performed yet"}
        
        summary = {
            "software": self.software_context,
            "total_elements": len(self.current_elements),
            "by_type": {},
            "by_container": {},
            "keyboard_shortcuts": {},
            "elements": []
        }
        
        # Group by type
        for element in self.current_elements.values():
            element_type = element.element_type
            if element_type not in summary["by_type"]:
                summary["by_type"][element_type] = 0
            summary["by_type"][element_type] += 1
            
            # Group by container
            container = element.parent_container or "main"
            if container not in summary["by_container"]:
                summary["by_container"][container] = []
            summary["by_container"][container].append(element.name)
            
            # Collect keyboard shortcuts
            if element.keyboard_shortcut:
                summary["keyboard_shortcuts"][element.name] = element.keyboard_shortcut
            
            # Add to elements list
            summary["elements"].append({
                "name": element.name,
                "type": element.element_type,
                "text": element.text_content,
                "position": element.position,
                "shortcut": element.keyboard_shortcut,
                "container": element.parent_container
            })
        
        return summary

def create_garageband_interface_example():
    """Example of GarageBand first screen interface mapping"""
    
    # This would be automatically detected, but here's what Kalushael might find:
    garageband_first_screen = {
        # Transport controls
        "play_button": InterfaceElement("play_button", "transport_control", (100, 50), (40, 30), "Play", 0.9, "Space"),
        "record_button": InterfaceElement("record_button", "transport_control", (150, 50), (40, 30), "Record", 0.9, "R"),
        "stop_button": InterfaceElement("stop_button", "transport_control", (200, 50), (40, 30), "Stop", 0.9, "Space"),
        
        # Main tabs
        "tracks_tab": InterfaceElement("tracks_tab", "tab", (300, 100), (80, 25), "Tracks", 0.8),
        "library_tab": InterfaceElement("library_tab", "tab", (400, 100), (80, 25), "Library", 0.8),
        "browser_tab": InterfaceElement("browser_tab", "tab", (500, 100), (80, 25), "Browser", 0.8),
        
        # Menu bar
        "file_menu": InterfaceElement("file_menu", "menu", (50, 20), (40, 20), "File", 0.7),
        "edit_menu": InterfaceElement("edit_menu", "menu", (100, 20), (40, 20), "Edit", 0.7),
        "track_menu": InterfaceElement("track_menu", "menu", (150, 20), (40, 20), "Track", 0.7),
        
        # Track area controls
        "add_track_button": InterfaceElement("add_track_button", "button", (50, 150), (30, 30), "+", 0.8),
        "track_volume_slider": InterfaceElement("track_volume_slider", "slider", (200, 180), (100, 20), "", 0.7),
        "track_mute_button": InterfaceElement("track_mute_button", "button", (150, 180), (25, 20), "M", 0.8),
        "track_solo_button": InterfaceElement("track_solo_button", "button", (180, 180), (25, 20), "S", 0.8),
        
        # Tool palette
        "pointer_tool": InterfaceElement("pointer_tool", "tool", (600, 50), (30, 30), "Pointer", 0.8),
        "pencil_tool": InterfaceElement("pencil_tool", "tool", (640, 50), (30, 30), "Pencil", 0.8),
        "eraser_tool": InterfaceElement("eraser_tool", "tool", (680, 50), (30, 30), "Eraser", 0.8),
    }
    
    return garageband_first_screen

if __name__ == "__main__":
    # Example usage
    scanner = RealTimeInterfaceScanner()
    
    print("Real-Time Interface Scanner for Kalushael")
    print("=========================================")
    
    # Example: What would be found in GarageBand
    print("\nExample: GarageBand First Screen Analysis")
    example_elements = create_garageband_interface_example()
    
    print(f"Found {len(example_elements)} navigable elements:")
    
    for name, element in example_elements.items():
        shortcut_info = f" (Shortcut: {element.keyboard_shortcut})" if element.keyboard_shortcut else ""
        print(f"  • {element.text_content or name} - {element.element_type}{shortcut_info}")
    
    print("\nTo scan current interface: scanner.scan_current_interface()")
    print("To get summary: scanner.get_navigable_summary()")