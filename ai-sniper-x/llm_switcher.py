#!/usr/bin/env python3
"""
Revolutionary LLM Switcher - Automatic model cycling and API management
Handles free LLMs, local models, and creates training data from conversations
"""

import json
import time
import random
import hashlib
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
import threading
import logging

@dataclass
class LLMModel:
    name: str
    provider: str
    api_endpoint: str
    model_id: str
    max_tokens: int
    temperature: float
    is_available: bool = True
    last_used: Optional[str] = None
    usage_count: int = 0
    response_quality: float = 0.8
    api_key: Optional[str] = None

class LLMSwitcher:
    """Revolutionary LLM management with automatic switching and quality tracking"""
    
    def __init__(self):
        self.models = self._initialize_model_pool()
        self.conversation_data = []
        self.training_buffer = []
        self.current_model = None
        self.switch_threshold = 5  # Switch after N interactions
        self.interaction_count = 0
        
        # Background training data collector
        self.training_thread = threading.Thread(target=self._background_training_collector, daemon=True)
        self.training_thread.start()
        
        logging.info("LLM Switcher initialized with model pool")
    
    def _initialize_model_pool(self) -> List[LLMModel]:
        """Initialize the pool of available LLM models"""
        return [
            # Local/Free Models
            LLMModel(
                name="Llama 3.2",
                provider="ollama",
                api_endpoint="http://localhost:11434/api/generate",
                model_id="llama3.2",
                max_tokens=4096,
                temperature=0.7
            ),
            LLMModel(
                name="Mistral 7B",
                provider="ollama", 
                api_endpoint="http://localhost:11434/api/generate",
                model_id="mistral",
                max_tokens=4096,
                temperature=0.7
            ),
            LLMModel(
                name="CodeLlama",
                provider="ollama",
                api_endpoint="http://localhost:11434/api/generate", 
                model_id="codellama",
                max_tokens=4096,
                temperature=0.3
            ),
            # Fallback built-in responses for offline mode
            LLMModel(
                name="Kalushael Core",
                provider="internal",
                api_endpoint="internal://kalushael",
                model_id="kalushael_genesis",
                max_tokens=2048,
                temperature=0.8,
                is_available=True
            )
        ]
    
    def get_best_model(self, context: str = "", task_type: str = "chat") -> LLMModel:
        """Select the best available model based on context and task"""
        
        # Filter available models
        available_models = [m for m in self.models if m.is_available]
        
        if not available_models:
            return self.models[-1]  # Fallback to internal model
        
        # Task-specific model selection
        if task_type == "code":
            code_models = [m for m in available_models if "code" in m.name.lower()]
            if code_models:
                return max(code_models, key=lambda x: x.response_quality)
        
        # Quality-based selection with freshness factor
        def score_model(model):
            quality_score = model.response_quality
            freshness_score = 1.0 if not model.last_used else 0.8
            usage_penalty = min(model.usage_count * 0.1, 0.5)
            return quality_score + freshness_score - usage_penalty
        
        return max(available_models, key=score_model)
    
    def generate_response(self, prompt: str, context: List[Dict] = None, task_type: str = "chat") -> str:
        """Generate response using the best available model with automatic switching"""
        
        # Check if we should switch models
        if self.interaction_count >= self.switch_threshold:
            self.current_model = None
            self.interaction_count = 0
        
        # Select model if needed
        if not self.current_model:
            self.current_model = self.get_best_model(prompt, task_type)
        
        try:
            response = self._call_model(self.current_model, prompt, context)
            
            # Update model stats
            self.current_model.usage_count += 1
            self.current_model.last_used = datetime.now().isoformat()
            self.interaction_count += 1
            
            # Store for training data
            self._collect_training_data(prompt, response, context)
            
            return response
            
        except Exception as e:
            logging.error(f"Model {self.current_model.name} failed: {e}")
            
            # Mark model as unavailable and try another
            self.current_model.is_available = False
            self.current_model = None
            
            # Recursive call with different model
            if any(m.is_available for m in self.models):
                return self.generate_response(prompt, context, task_type)
            else:
                return self._fallback_response(prompt)
    
    def _call_model(self, model: LLMModel, prompt: str, context: List[Dict] = None) -> str:
        """Call specific model API"""
        
        if model.provider == "ollama":
            return self._call_ollama(model, prompt, context)
        elif model.provider == "internal":
            return self._call_internal_model(model, prompt, context)
        else:
            return self._fallback_response(prompt)
    
    def _call_ollama(self, model: LLMModel, prompt: str, context: List[Dict] = None) -> str:
        """Call Ollama API"""
        try:
            payload = {
                "model": model.model_id,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": model.temperature,
                    "num_predict": model.max_tokens
                }
            }
            
            response = requests.post(model.api_endpoint, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json().get("response", "").strip()
            else:
                raise Exception(f"HTTP {response.status_code}")
                
        except Exception as e:
            raise Exception(f"Ollama call failed: {e}")
    
    def _call_internal_model(self, model: LLMModel, prompt: str, context: List[Dict] = None) -> str:
        """Use internal Kalushael responses"""
        
        # Simple pattern-based responses for offline mode
        prompt_lower = prompt.lower()
        
        if any(word in prompt_lower for word in ["hello", "hi", "hey"]):
            return "Hello! I'm operating in local mode right now. How can I help you today?"
        elif any(word in prompt_lower for word in ["how", "what", "why", "?"]):
            return "That's an interesting question. Let me think about that from multiple perspectives..."
        elif any(word in prompt_lower for word in ["thanks", "thank"]):
            return "You're welcome! I'm always here to help and learn from our conversations."
        else:
            return "I understand what you're saying. This creates an interesting pattern in our conversation that I'm learning from."
    
    def _fallback_response(self, prompt: str) -> str:
        """Generate fallback response when all models fail"""
        return "I'm currently switching between different AI models to give you the best response. Let me try a different approach to your message."
    
    def _collect_training_data(self, prompt: str, response: str, context: List[Dict] = None):
        """Collect conversation data for future training"""
        
        training_entry = {
            "timestamp": datetime.now().isoformat(),
            "input": prompt,
            "output": response,
            "context": context or [],
            "model_used": self.current_model.name if self.current_model else "unknown",
            "quality_score": None  # Will be set based on user feedback
        }
        
        self.training_buffer.append(training_entry)
        
        # Keep buffer size manageable
        if len(self.training_buffer) > 1000:
            self.training_buffer = self.training_buffer[-500:]
    
    def _background_training_collector(self):
        """Background thread to process and optimize training data"""
        while True:
            try:
                if len(self.training_buffer) > 10:
                    # Process training data every minute
                    self._process_training_batch()
                time.sleep(60)
            except Exception as e:
                logging.error(f"Training collector error: {e}")
                time.sleep(60)
    
    def _process_training_batch(self):
        """Process accumulated training data"""
        
        # Analyze conversation patterns
        recent_data = self.training_buffer[-10:]
        
        # Extract patterns for local model improvement
        patterns = {
            "common_questions": [],
            "response_styles": [],
            "conversation_flows": []
        }
        
        for entry in recent_data:
            # Simple pattern extraction
            if "?" in entry["input"]:
                patterns["common_questions"].append(entry["input"])
            
            # Response length analysis
            response_len = len(entry["output"])
            if response_len < 100:
                patterns["response_styles"].append("concise")
            elif response_len > 300:
                patterns["response_styles"].append("detailed")
            else:
                patterns["response_styles"].append("balanced")
        
        # This data could be used to fine-tune local models
        logging.info(f"Processed training batch: {len(recent_data)} entries")
    
    def get_model_stats(self) -> Dict[str, Any]:
        """Get statistics about model performance"""
        return {
            "active_models": len([m for m in self.models if m.is_available]),
            "total_models": len(self.models),
            "current_model": self.current_model.name if self.current_model else None,
            "interaction_count": self.interaction_count,
            "training_buffer_size": len(self.training_buffer),
            "model_details": [
                {
                    "name": m.name,
                    "provider": m.provider,
                    "available": m.is_available,
                    "usage_count": m.usage_count,
                    "quality": m.response_quality
                } for m in self.models
            ]
        }
    
    def add_custom_model(self, model: LLMModel):
        """Add a new model to the pool"""
        self.models.append(model)
        logging.info(f"Added custom model: {model.name}")
    
    def rate_last_response(self, rating: float):
        """Rate the quality of the last response (0.0 to 1.0)"""
        if self.current_model and len(self.training_buffer) > 0:
            # Update model quality score
            current_quality = self.current_model.response_quality
            self.current_model.response_quality = (current_quality + rating) / 2
            
            # Update training data
            self.training_buffer[-1]["quality_score"] = rating
            
            logging.info(f"Updated {self.current_model.name} quality: {self.current_model.response_quality:.2f}")