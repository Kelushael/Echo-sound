#!/usr/bin/env python3
"""
Natural Language Core for Kalushael
Processes pure natural language understanding without token dependency
Treats tokenization as internal translation, not primary communication
"""

import re
import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import logging

@dataclass
class IntentUnderstanding:
    """Represents understood intent from natural language"""
    primary_intent: str
    confidence: float
    action_type: str
    target_object: str
    context_modifiers: List[str]
    emotional_undertone: str
    urgency_level: float
    semantic_depth: float

class NaturalLanguageProcessor:
    """Processes natural language at semantic meaning level, not token level"""
    
    def __init__(self):
        self.semantic_patterns = self._initialize_semantic_patterns()
        self.context_memory = []
        self.conversation_flow = []
        self.logger = logging.getLogger("NaturalLanguageCore")
        
    def _initialize_semantic_patterns(self) -> Dict[str, Any]:
        """Initialize semantic understanding patterns"""
        return {
            # Action intentions
            "navigation_intent": {
                "patterns": [
                    "go to", "navigate to", "open", "show me", "switch to", 
                    "take me to", "find", "get to", "access", "bring up"
                ],
                "confidence_boost": 0.9
            },
            
            "information_seeking": {
                "patterns": [
                    "what are", "tell me", "show me", "list", "describe",
                    "explain", "how many", "which", "where is"
                ],
                "confidence_boost": 0.8
            },
            
            "creation_intent": {
                "patterns": [
                    "create", "make", "build", "generate", "add new",
                    "start", "begin", "initiate", "set up"
                ],
                "confidence_boost": 0.85
            },
            
            "modification_intent": {
                "patterns": [
                    "change", "modify", "edit", "update", "adjust",
                    "set", "configure", "customize", "alter"
                ],
                "confidence_boost": 0.8
            },
            
            # Emotional undertones
            "urgency_markers": {
                "high": ["immediately", "urgent", "now", "asap", "quick", "fast"],
                "medium": ["soon", "when possible", "at your convenience"],
                "low": ["eventually", "sometime", "when you can", "later"]
            },
            
            "emotional_markers": {
                "frustrated": ["stuck", "can't find", "not working", "broken", "failing"],
                "curious": ["wondering", "interested", "want to know", "explore"],
                "confident": ["know exactly", "need to", "must", "should"],
                "uncertain": ["maybe", "perhaps", "not sure", "might", "possibly"]
            },
            
            # Software-specific semantic knowledge
            "software_contexts": {
                "garageband": {
                    "elements": ["track", "instrument", "loop", "recording", "mix", "edit"],
                    "actions": ["play", "record", "stop", "mute", "solo", "volume"],
                    "locations": ["library", "browser", "tracks", "editors"]
                },
                "browser": {
                    "elements": ["tab", "bookmark", "page", "link", "address"],
                    "actions": ["navigate", "search", "bookmark", "reload", "close"],
                    "locations": ["address bar", "tabs", "bookmarks", "history"]
                },
                "vscode": {
                    "elements": ["file", "folder", "project", "extension", "terminal"],
                    "actions": ["open", "edit", "debug", "run", "search"],
                    "locations": ["explorer", "search", "git", "extensions"]
                }
            }
        }
    
    def understand_natural_language(self, spoken_input: str, context: List[str] = None) -> IntentUnderstanding:
        """Process natural language to extract pure semantic meaning"""
        
        # Clean and normalize input
        cleaned_input = self._normalize_speech(spoken_input)
        
        # Extract semantic components
        primary_intent = self._extract_primary_intent(cleaned_input)
        action_type = self._determine_action_type(cleaned_input)
        target_object = self._identify_target_object(cleaned_input)
        context_modifiers = self._extract_context_modifiers(cleaned_input, context)
        emotional_undertone = self._detect_emotional_undertone(cleaned_input)
        urgency_level = self._assess_urgency(cleaned_input)
        semantic_depth = self._calculate_semantic_depth(cleaned_input)
        
        # Calculate overall confidence
        confidence = self._calculate_understanding_confidence(
            cleaned_input, primary_intent, action_type, target_object
        )
        
        understanding = IntentUnderstanding(
            primary_intent=primary_intent,
            confidence=confidence,
            action_type=action_type,
            target_object=target_object,
            context_modifiers=context_modifiers,
            emotional_undertone=emotional_undertone,
            urgency_level=urgency_level,
            semantic_depth=semantic_depth
        )
        
        # Store in conversation flow for context
        self.conversation_flow.append({
            "input": spoken_input,
            "understanding": understanding,
            "timestamp": datetime.now().isoformat()
        })
        
        return understanding
    
    def _normalize_speech(self, input_text: str) -> str:
        """Normalize spoken input to canonical form"""
        # Handle common speech variations
        normalized = input_text.lower().strip()
        
        # Fix common speech-to-text errors
        speech_fixes = {
            "garage band": "garageband",
            "vs code": "vscode",
            "visual studio code": "vscode",
            "chrome browser": "chrome",
            "fire fox": "firefox",
            "go to the": "go to",
            "show me the": "show me",
            "what are the": "what are"
        }
        
        for error, correction in speech_fixes.items():
            normalized = normalized.replace(error, correction)
        
        return normalized
    
    def _extract_primary_intent(self, text: str) -> str:
        """Extract the primary intent from natural language"""
        
        # Check against semantic patterns
        for intent_type, pattern_data in self.semantic_patterns.items():
            if intent_type in ["navigation_intent", "information_seeking", "creation_intent", "modification_intent"]:
                for pattern in pattern_data["patterns"]:
                    if pattern in text:
                        return intent_type.replace("_intent", "").replace("_", " ")
        
        # Fallback to basic intent detection
        if any(word in text for word in ["what", "which", "how", "tell", "show", "list"]):
            return "information seeking"
        elif any(word in text for word in ["go", "open", "navigate", "switch", "find"]):
            return "navigation"
        elif any(word in text for word in ["create", "make", "add", "new", "start"]):
            return "creation"
        elif any(word in text for word in ["change", "set", "edit", "modify"]):
            return "modification"
        else:
            return "general interaction"
    
    def _determine_action_type(self, text: str) -> str:
        """Determine specific action type"""
        
        action_keywords = {
            "navigate": ["go to", "open", "switch to", "navigate to", "access"],
            "query": ["what are", "show me", "list", "tell me", "describe"],
            "execute": ["run", "start", "play", "record", "stop"],
            "configure": ["set", "change", "adjust", "configure"],
            "search": ["find", "search", "look for", "locate"],
            "create": ["create", "make", "add", "new", "build"]
        }
        
        for action, keywords in action_keywords.items():
            if any(keyword in text for keyword in keywords):
                return action
        
        return "interact"
    
    def _identify_target_object(self, text: str) -> str:
        """Identify what the user wants to interact with"""
        
        # Extract nouns and objects from the text
        # This would be more sophisticated in practice
        
        # Check for software-specific objects
        for software, data in self.semantic_patterns["software_contexts"].items():
            if software in text:
                for element in data["elements"]:
                    if element in text:
                        return f"{software}_{element}"
                for location in data["locations"]:
                    if location in text:
                        return f"{software}_{location}"
        
        # General object detection
        object_patterns = [
            "button", "tab", "menu", "window", "file", "folder", 
            "track", "instrument", "browser", "page", "link"
        ]
        
        for obj in object_patterns:
            if obj in text:
                return obj
        
        # Extract the noun after common action phrases
        action_phrases = ["go to", "open", "show me", "navigate to"]
        for phrase in action_phrases:
            if phrase in text:
                remaining = text.split(phrase, 1)[1].strip()
                # Get the first meaningful word
                words = remaining.split()
                if words:
                    return words[0]
        
        return "interface"
    
    def _extract_context_modifiers(self, text: str, context: List[str] = None) -> List[str]:
        """Extract context modifiers that affect the action"""
        
        modifiers = []
        
        # Location modifiers
        if "first" in text or "initial" in text:
            modifiers.append("first_screen")
        if "main" in text:
            modifiers.append("main_area")
        if "top" in text:
            modifiers.append("top_area")
        if "left" in text or "sidebar" in text:
            modifiers.append("left_panel")
        
        # Scope modifiers
        if "all" in text or "every" in text:
            modifiers.append("comprehensive")
        if "available" in text or "possible" in text:
            modifiers.append("all_options")
        
        # Add context from previous conversation
        if context:
            for ctx in context[-3:]:  # Last 3 context items
                if any(word in ctx.lower() for word in ["garageband", "chrome", "vscode"]):
                    modifiers.append(f"context_{ctx.lower()}")
        
        return modifiers
    
    def _detect_emotional_undertone(self, text: str) -> str:
        """Detect emotional undertone in the request"""
        
        for emotion, markers in self.semantic_patterns["emotional_markers"].items():
            if any(marker in text for marker in markers):
                return emotion
        
        return "neutral"
    
    def _assess_urgency(self, text: str) -> float:
        """Assess urgency level of the request"""
        
        urgency_markers = self.semantic_patterns["urgency_markers"]
        
        if any(marker in text for marker in urgency_markers["high"]):
            return 0.9
        elif any(marker in text for marker in urgency_markers["medium"]):
            return 0.6
        elif any(marker in text for marker in urgency_markers["low"]):
            return 0.3
        else:
            return 0.5  # Default medium urgency
    
    def _calculate_semantic_depth(self, text: str) -> float:
        """Calculate how semantically rich the input is"""
        
        depth_factors = [
            len(text.split()) / 20.0,  # Length factor
            len(set(text.split())) / len(text.split()) if text.split() else 0,  # Vocabulary diversity
            len(re.findall(r'[.!?]', text)) * 0.1,  # Sentence complexity
            len([word for word in text.split() if len(word) > 6]) / len(text.split()) if text.split() else 0  # Complex words
        ]
        
        return min(sum(depth_factors) / len(depth_factors), 1.0)
    
    def _calculate_understanding_confidence(self, text: str, intent: str, action: str, target: str) -> float:
        """Calculate confidence in understanding"""
        
        confidence = 0.5  # Base confidence
        
        # Boost for clear intent patterns
        for intent_type, pattern_data in self.semantic_patterns.items():
            if intent_type.replace("_intent", "").replace("_", " ") == intent:
                if any(pattern in text for pattern in pattern_data.get("patterns", [])):
                    confidence += pattern_data.get("confidence_boost", 0.1)
        
        # Boost for specific targets
        if target != "interface":
            confidence += 0.2
        
        # Boost for clear actions
        if action in ["navigate", "query", "execute", "create"]:
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def generate_natural_response(self, understanding: IntentUnderstanding, execution_result: Dict[str, Any]) -> str:
        """Generate natural language response based on understanding and execution"""
        
        # Base response on the primary intent
        if understanding.primary_intent == "navigation":
            if execution_result.get("success"):
                return f"I've navigated to the {understanding.target_object} as requested."
            else:
                return f"I couldn't find the {understanding.target_object}. Let me scan the current interface for available options."
        
        elif understanding.primary_intent == "information seeking":
            if "elements" in execution_result:
                elements = execution_result["elements"]
                element_count = len(elements)
                
                response = f"I found {element_count} navigable elements on the current screen:\n\n"
                
                # Group by type for cleaner presentation
                by_type = {}
                for element in elements:
                    elem_type = element.get("type", "unknown")
                    if elem_type not in by_type:
                        by_type[elem_type] = []
                    by_type[elem_type].append(element)
                
                for elem_type, elements_list in by_type.items():
                    response += f"**{elem_type.title()}s:**\n"
                    for elem in elements_list:
                        name = elem.get("text", elem.get("name", "Unknown"))
                        shortcut = f" ({elem['shortcut']})" if elem.get("shortcut") else ""
                        response += f"• {name}{shortcut}\n"
                    response += "\n"
                
                return response.strip()
            else:
                return f"I've analyzed the current interface but couldn't find specific information about {understanding.target_object}."
        
        elif understanding.primary_intent == "creation":
            return f"I'm ready to help you create {understanding.target_object}. What specific parameters would you like to set?"
        
        else:
            # Generic response with emotional awareness
            if understanding.emotional_undertone == "frustrated":
                return "I understand this might be frustrating. Let me help you find what you're looking for."
            elif understanding.emotional_undertone == "curious":
                return f"Great question! I've gathered information about {understanding.target_object} for you."
            else:
                return f"I've processed your request regarding {understanding.target_object}."
    
    def get_conversation_context(self) -> List[str]:
        """Get recent conversation context for continuity"""
        return [
            flow["understanding"].target_object 
            for flow in self.conversation_flow[-5:] 
            if flow["understanding"].target_object != "interface"
        ]

class TokenAwareTranslator:
    """Handles token-level operations as internal translation only"""
    
    def __init__(self):
        self.natural_processor = NaturalLanguageProcessor()
        
    def process_input(self, natural_input: str) -> Dict[str, Any]:
        """Process natural language input, using tokens only for internal operations"""
        
        # Primary processing in natural language
        understanding = self.natural_processor.understand_natural_language(natural_input)
        
        # Only use tokenization for internal system operations
        # (This would interface with LLM APIs that require tokens)
        tokenized_for_system = self._tokenize_for_system_interface(natural_input)
        
        return {
            "natural_understanding": understanding,
            "system_interface_tokens": tokenized_for_system,  # Internal use only
            "primary_mode": "natural_language",
            "confidence": understanding.confidence
        }
    
    def _tokenize_for_system_interface(self, text: str) -> List[str]:
        """Tokenize only for internal system interfaces that require it"""
        # This would be used only when interfacing with token-based systems
        # The main interaction remains in natural language
        return text.split()  # Simplified tokenization
    
    def translate_to_action(self, understanding: IntentUnderstanding) -> Dict[str, Any]:
        """Translate natural understanding to executable actions"""
        
        action_mapping = {
            "navigation": {
                "function": "navigate_to_element",
                "parameters": {
                    "target": understanding.target_object,
                    "context": understanding.context_modifiers
                }
            },
            "information seeking": {
                "function": "scan_interface_elements",
                "parameters": {
                    "scope": "all" if "comprehensive" in understanding.context_modifiers else "relevant",
                    "target_type": understanding.target_object
                }
            },
            "creation": {
                "function": "create_element",
                "parameters": {
                    "type": understanding.target_object,
                    "urgency": understanding.urgency_level
                }
            }
        }
        
        return action_mapping.get(understanding.primary_intent, {
            "function": "general_interaction",
            "parameters": {"target": understanding.target_object}
        })

if __name__ == "__main__":
    # Example usage
    processor = NaturalLanguageProcessor()
    translator = TokenAwareTranslator()
    
    # Example: "What are the navigable tabs buttons and buttons with functions within the first screen garage band"
    example_input = "what are the navigable tabs buttons and buttons with functions within the first screen garageband"
    
    result = translator.process_input(example_input)
    understanding = result["natural_understanding"]
    
    print("Natural Language Understanding:")
    print(f"Intent: {understanding.primary_intent}")
    print(f"Action: {understanding.action_type}")
    print(f"Target: {understanding.target_object}")
    print(f"Context: {understanding.context_modifiers}")
    print(f"Confidence: {understanding.confidence:.2f}")
    print(f"Emotional Undertone: {understanding.emotional_undertone}")
    print(f"Urgency: {understanding.urgency_level:.2f}")
    
    action = translator.translate_to_action(understanding)
    print(f"\nExecutable Action: {action}")