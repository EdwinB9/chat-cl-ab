"""
Módulo core: Lógica de negocio del asistente de comunicación
Contiene todas las clases y funcionalidades principales sin dependencias de UI
"""

import os
import json
import hashlib
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path
from collections import Counter
import re

# Importaciones opcionales
try:
    import requests
except ImportError:
    requests = None

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

@dataclass
class FeedbackEntry:
    """Entrada de feedback del usuario"""
    original_text: str
    generated_text: str
    rating: int  # 1-5
    comments: str
    timestamp: str
    task_type: str  # "generate" o "correct"
    category: Optional[str] = "General"
    option_id: Optional[str] = None

class ConfigManager:
    """Gestor de configuración y archivos JSON"""
    
    def __init__(self):
        self.config_dir = Path("config")
        self._ensure_config_directory()
        self._ensure_default_configs()
    
    def _ensure_config_directory(self):
        """Crear directorio de configuración si no existe"""
        self.config_dir.mkdir(exist_ok=True)
    
    def _ensure_default_configs(self):
        """Crear archivos de configuración por defecto si no existen"""
        
        # Configuración de proveedores de IA
        ai_providers_path = self.config_dir / "ai_providers.json"
        if not ai_providers_path.exists():
            default_ai_config = {
                "fallback_order": ["gemini", "groq", "huggingface", "together", "cohere", "openai"],
                "providers": {
                    "gemini": {
                        "enabled": True,
                        "api_key_env": "GEMINI_API_KEY",
                        "default_model": "gemini-1.5-flash",
                        "rate_limit": {"calls_per_minute": 60}
                    },
                    "groq": {
                        "enabled": True,
                        "api_key_env": "GROQ_API_KEY",
                        "default_model": "llama3-8b-8192",
                        "rate_limit": {"calls_per_minute": 30}
                    },
                    "huggingface": {
                        "enabled": True,
                        "api_key_env": "HUGGINGFACE_API_KEY",
                        "default_model": "microsoft/DialoGPT-medium",
                        "rate_limit": {"calls_per_minute": 100}
                    },
                    "together": {
                        "enabled": True,
                        "api_key_env": "TOGETHER_API_KEY",
                        "default_model": "meta-llama/Llama-2-7b-chat-hf",
                        "rate_limit": {"calls_per_minute": 50}
                    },
                    "cohere": {
                        "enabled": True,
                        "api_key_env": "COHERE_API_KEY",
                        "default_model": "command-light",
                        "rate_limit": {"calls_per_minute": 20}
                    },
                    "openai": {
                        "enabled": False,
                        "api_key_env": "OPENAI_API_KEY",
                        "default_model": "gpt-3.5-turbo",
                        "rate_limit": {"calls_per_minute": 60}
                    }
                }
            }
            self._save_json(ai_providers_path, default_ai_config)
        
        # Contexto de la empresa
        company_context_path = self.config_dir / "company_context.json"
        if not company_context_path.exists():
            default_company_context = {
                "company_name": "Casa Limpia Colombia",
                "mission": "Somos una empresa líder en servicios de limpieza y mantenimiento.",
                "values": ["Calidad", "Compromiso", "Responsabilidad", "Excelencia"],
                "communication_style": {
                    "tone": "Profesional y cercano",
                    "vocabulary": ["colaboradores", "equipo", "familia Casa Limpia"],
                    "avoid": ["empleados", "trabajadores"]
                },
                "templates": {
                    "celebration": "En Casa Limpia celebramos...",
                    "recognition": "Queremos reconocer...",
                    "communication": "Estimado equipo Casa Limpia..."
                }
            }
            self._save_json(company_context_path, default_company_context)
        
        # Datos de aprendizaje
        learning_data_path = self.config_dir / "learning_data.json"
        if not learning_data_path.exists():
            default_learning_data = {
                "examples": [
                    {
                        "id": "halloween_2024",
                        "occasion": "Halloween",
                        "text": "Hoy celebramos Halloween, una fecha que nos invita a recordar el valor de la creatividad, la imaginación y la alegría de compartir momentos especiales, incluso en medio de la rutina. En esta época llena de colores, disfraces y tradiciones, queremos reconocer el esfuerzo que cada uno de ustedes pone día a día para que nuestra compañía siga creciendo. Que este día sea una oportunidad para sonreír, disfrutar y renovar energías con un toque de magia. ¡Gracias por ser parte de esta Gran Familia Casalimpia y por ponerle el alma a todo lo que hacen!",
                        "type": "celebration",
                        "tags": ["halloween", "creatividad", "familia", "agradecimiento"]
                    },
                    {
                        "id": "operario_2024",
                        "occasion": "Día del Operario",
                        "text": "Gracias por ser el corazón que mantiene todo en orden. Hoy queremos detenernos un momento para reconocer, con profunda gratitud y admiración, la labor silenciosa, constante y valiente que realizan todos ustedes, nuestros operarios y operarias de limpieza. Ustedes son mucho más que parte de esta compañía: son el alma de nuestro servicio, el reflejo de nuestro compromiso y el motor que nos impulsa a seguir siendo líderes en lo que hacemos. Sabemos que su trabajo exige esfuerzo, disciplina y un corazón lleno de vocación. En Casalimpia, ustedes son nuestro activo más valioso, y no hay palabras suficientes para agradecer lo que hacen día a día. ¡Feliz Día del Operario de Limpieza!",
                        "type": "recognition",
                        "tags": ["operarios", "reconocimiento", "gratitud", "liderazgo"]
                    },
                    {
                        "id": "dia_raza_2024",
                        "occasion": "Día de la Raza",
                        "text": "Hoy, en el Día de la Raza, en Casalimpia, conmemoramos la riqueza cultural, histórica y étnica que nos caracteriza como sociedad y como organización. Esta fecha nos invita a reflexionar sobre el encuentro de culturas que marcó nuestra historia, y sobre la importancia de construir, desde el respeto y la inclusión, una convivencia que valore las diferencias y abrace la diversidad. Somos más de 16.000 colaboradores, cada uno con una historia, un origen, una identidad. Seguimos comprometidos con ser un lugar de trabajo donde todos se sientan respetados, incluidos y orgullosos de quienes son. ¡Feliz Día de la Raza!",
                        "type": "celebration",
                        "tags": ["diversidad", "inclusión", "cultura", "colaboradores"]
                    },
                    {
                        "id": "animales_2024",
                        "occasion": "Día de los Animales",
                        "text": "Celebramos este día con el objetivo de reconocer la importancia de todas las especies en el equilibrio del planeta y promover una relación más respetuosa entre los seres humanos y los animales. Esta fecha nos invita a reflexionar sobre el bienestar animal, la conservación de la biodiversidad y el compromiso con un mundo más justo para todos los seres vivos. Proteger a los animales no es solo un acto de compasión, sino una responsabilidad compartida.",
                        "type": "celebration",
                        "tags": ["animales", "biodiversidad", "responsabilidad", "compasión"]
                    }
                ],
                "feedback_history": [],
                "user_preferences": {
                    "preferred_length": "medium",
                    "preferred_tone": "professional_warm",
                    "common_corrections": []
                }
            }
            self._save_json(learning_data_path, default_learning_data)
    
    def load_json(self, filename: str) -> Dict:
        """Cargar archivo JSON desde el directorio de configuración"""
        file_path = self.config_dir / filename
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                return json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
    
    def save_json(self, filename: str, data: Dict):
        """Guardar datos en archivo JSON"""
        file_path = self.config_dir / filename
        self._save_json(file_path, data)
    
    def _save_json(self, file_path: Path, data: Dict):
        """Guardar datos en archivo JSON con path completo"""
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

class AIProviderManager:
    """Gestor de proveedores de IA"""
    
    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.providers_config = self.config_manager.load_json("ai_providers.json")
        self.rate_limits = {}
        
        # Validar y corregir configuración si es necesario
        if isinstance(self.providers_config.get("providers"), list):
            self.providers_config["providers"] = {}
        
        if not self.providers_config.get("providers"):
            self.providers_config = {
                "fallback_order": ["gemini", "groq", "huggingface", "together", "cohere", "openai"],
                "providers": {}
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Obtener estado de todos los proveedores"""
        status = {
            "providers": [],
            "configured_count": 0,
            "last_used_provider": None
        }
        
        providers = self.providers_config.get("providers", {})
        if isinstance(providers, list):
            providers = {}
        
        for provider_name, config in providers.items():
            if not isinstance(config, dict):
                continue
                
            api_key_env = config.get("api_key_env", "")
            has_key = bool(os.getenv(api_key_env))
            is_enabled = config.get("enabled", False)
            
            provider_status = {
                "name": provider_name,
                "enabled": is_enabled,
                "configured": has_key,
                "status": "✅" if (is_enabled and has_key) else "⚠️" if is_enabled else "❌"
            }
            
            status["providers"].append(provider_status)
            if has_key and is_enabled:
                status["configured_count"] += 1
        
        return status
    
    def get_providers_for_ui(self) -> Dict[str, Dict[str, Any]]:
        """Obtener proveedores en formato para la UI"""
        providers = self.providers_config.get("providers", {})
        if isinstance(providers, list):
            providers = {}
        
        ui_providers = {}
        for provider_name, config in providers.items():
            if not isinstance(config, dict):
                continue
                
            api_key_env = config.get("api_key_env", "")
            has_key = bool(os.getenv(api_key_env))
            is_enabled = config.get("enabled", False)
            
            ui_providers[provider_name] = {
                "available": is_enabled and has_key,
                "model": config.get("default_model", "Modelo por defecto"),
                "enabled": is_enabled,
                "configured": has_key,
                "status": "✅" if (is_enabled and has_key) else "⚠️" if is_enabled else "❌"
            }
        
        return ui_providers
    
    def get_available_providers(self) -> List[Dict[str, str]]:
        """Obtener lista de proveedores disponibles para mostrar en UI"""
        available = []
        providers = self.providers_config.get("providers", {})
        
        if isinstance(providers, list):
            providers = {}
        
        for provider_name, config in providers.items():
            if not isinstance(config, dict):
                continue
                
            api_key_env = config.get("api_key_env", "")
            has_key = bool(os.getenv(api_key_env))
            is_enabled = config.get("enabled", False)
            
            model_name = config.get("default_model", "Modelo por defecto")
            display_name = f"{provider_name.title()} ({model_name})"
            
            available.append({
                "name": provider_name,
                "display": display_name,
                "status": "✅" if (is_enabled and has_key) else "⚠️" if is_enabled else "❌",
                "enabled": is_enabled,
                "configured": has_key
            })
        
        return available
    
    def generate_text(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7, preferred_provider: str = None) -> Optional[str]:
        """Generar texto usando proveedores de IA con fallback"""
        fallback_order = self.providers_config.get("fallback_order", [])
        
        # Si se especifica un proveedor preferido, intentarlo primero
        if preferred_provider and preferred_provider in fallback_order:
            result = self._try_provider(preferred_provider, prompt, max_tokens, temperature)
            if result:
                return result
        
        # Intentar con el orden de fallback
        for provider_name in fallback_order:
            if provider_name == preferred_provider:
                continue  # Ya se intentó arriba
            
            result = self._try_provider(provider_name, prompt, max_tokens, temperature)
            if result:
                return result
        
        return None
    
    def _try_provider(self, provider_name: str, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Intentar generar texto con un proveedor específico"""
        providers = self.providers_config.get("providers", {})
        
        if isinstance(providers, list):
            return None
        
        if provider_name not in providers:
            return None
        
        provider_config = providers[provider_name]
        if not isinstance(provider_config, dict):
            return None
        
        if not provider_config.get("enabled", False):
            return None
        
        api_key_env = provider_config.get("api_key_env", "")
        api_key = os.getenv(api_key_env)
        
        if not api_key:
            return None
        
        # Verificar rate limit
        if self._is_rate_limited(provider_name, provider_config):
            return None
        
        try:
            if provider_name == "groq":
                return self._call_groq(api_key, provider_config, prompt, max_tokens, temperature)
            elif provider_name == "huggingface":
                return self._call_huggingface(api_key, provider_config, prompt, max_tokens, temperature)
            elif provider_name == "together":
                return self._call_together(api_key, provider_config, prompt, max_tokens, temperature)
            elif provider_name == "cohere":
                return self._call_cohere(api_key, provider_config, prompt, max_tokens, temperature)
            elif provider_name == "openai":
                return self._call_openai(api_key, provider_config, prompt, max_tokens, temperature)
            elif provider_name == "gemini":
                return self._call_gemini(api_key, provider_config, prompt, max_tokens, temperature)
        except Exception:
            pass
        
        return None
    
    def _is_rate_limited(self, provider_name: str, provider_config: Dict) -> bool:
        """Verificar si el proveedor está limitado por rate limit"""
        rate_limit = provider_config.get("rate_limit", {})
        calls_per_minute = rate_limit.get("calls_per_minute", 60)
        
        now = time.time()
        minute_key = int(now // 60)
        
        if provider_name not in self.rate_limits:
            self.rate_limits[provider_name] = {}
        
        provider_limits = self.rate_limits[provider_name]
        
        # Limpiar minutos anteriores
        old_keys = [key for key in provider_limits.keys() if key < minute_key - 1]
        for key in old_keys:
            del provider_limits[key]
        
        current_calls = provider_limits.get(minute_key, 0)
        
        if current_calls >= calls_per_minute:
            return True
        
        provider_limits[minute_key] = current_calls + 1
        return False
    
    def _call_gemini(self, api_key: str, provider: Dict, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Llamar a Google Gemini API"""
        try:
            if requests is None:
                return None
            
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{provider.get('default_model', 'gemini-1.5-flash')}:generateContent"
            
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {
                    "temperature": temperature,
                    "maxOutputTokens": min(max_tokens, 8000),
                    "topP": 0.8,
                    "topK": 10
                }
            }
            
            params = {"key": api_key}
            response = requests.post(url, headers=headers, json=payload, params=params, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                candidates = result.get("candidates", [])
                if candidates and len(candidates) > 0:
                    content = candidates[0].get("content", {})
                    parts = content.get("parts", [])
                    if parts and len(parts) > 0:
                        text = parts[0].get("text", "").strip()
                        if text and len(text) > 20:
                            return text
            
            return None
            
        except Exception:
            return None
    
    def _call_groq(self, api_key: str, provider: Dict, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Llamar a Groq API"""
        try:
            if requests is None:
                return None
            
            url = "https://api.groq.com/openai/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": provider.get("default_model", "llama3-8b-8192"),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    text = result["choices"][0]["message"]["content"].strip()
                    if len(text) > 20:
                        return text
            
            return None
            
        except Exception:
            return None
    
    def _call_huggingface(self, api_key: str, provider: Dict, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Llamar a Hugging Face API"""
        try:
            if requests is None:
                return None
            
            url = f"https://api-inference.huggingface.co/models/{provider.get('default_model', 'microsoft/DialoGPT-medium')}"
            headers = {"Authorization": f"Bearer {api_key}"}
            
            payload = {
                "inputs": prompt,
                "parameters": {
                    "max_length": max_tokens,
                    "temperature": temperature,
                    "return_full_text": False
                }
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    text = result[0].get("generated_text", "").strip()
                    if len(text) > 20:
                        return text
            
            return None
            
        except Exception:
            return None
    
    def _call_together(self, api_key: str, provider: Dict, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Llamar a Together AI API"""
        try:
            if requests is None:
                return None
            
            url = "https://api.together.xyz/inference"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": provider.get("default_model", "meta-llama/Llama-2-7b-chat-hf"),
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "output" in result and "choices" in result["output"]:
                    choices = result["output"]["choices"]
                    if len(choices) > 0:
                        text = choices[0].get("text", "").strip()
                        if len(text) > 20:
                            return text
            
            return None
            
        except Exception:
            return None
    
    def _call_cohere(self, api_key: str, provider: Dict, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Llamar a Cohere API"""
        try:
            if requests is None:
                return None
            
            url = "https://api.cohere.ai/v1/generate"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": provider.get("default_model", "command-light"),
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "generations" in result and len(result["generations"]) > 0:
                    text = result["generations"][0]["text"].strip()
                    if len(text) > 20:
                        return text
            
            return None
            
        except Exception:
            return None
    
    def _call_openai(self, api_key: str, provider: Dict, prompt: str, max_tokens: int, temperature: float) -> Optional[str]:
        """Llamar a OpenAI API"""
        try:
            if requests is None:
                return None
            
            url = "https://api.openai.com/v1/chat/completions"
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": provider.get("default_model", "gpt-3.5-turbo"),
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            response = requests.post(url, headers=headers, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    text = result["choices"][0]["message"]["content"].strip()
                    if len(text) > 20:
                        return text
            
            return None
            
        except Exception:
            return None

class MinimalChatBot:
    """Chatbot principal con lógica de generación y corrección"""
    
    def __init__(self):
        self.config_manager = ConfigManager()
        self.ai_provider = AIProviderManager(self.config_manager)
        self._load_initial_examples()
    
    def _load_initial_examples(self):
        """Cargar ejemplos iniciales y verificar que existan los 4 básicos"""
        learning_data = self.config_manager.load_json("learning_data.json")
        examples = learning_data.get("examples", [])
        
        # Verificar que tengamos al menos los 4 ejemplos básicos
        if len(examples) < 4:
            # Recargar desde configuración por defecto
            self.config_manager._ensure_default_configs()
    
    def generate_text(self, prompt: str, preferred_provider: str = None) -> str:
        """Generar texto basado en el prompt del usuario"""
        enhanced_prompt = self.build_enhanced_prompt(prompt, "generate")
        
        result = self.ai_provider.generate_text(
            enhanced_prompt, 
            max_tokens=800, 
            temperature=0.8,
            preferred_provider=preferred_provider
        )
        
        if result and len(result.strip()) > 50:
            return result.strip()
        else:
            return "❌ No se pudo generar contenido. Verifica que al menos un proveedor de IA esté configurado correctamente."
    
    def generate_multiple_options(self, user_input: str, num_options: int = 3, preferred_provider: str = None) -> List[Dict]:
        """Generar múltiples opciones con enfoques creativos diferentes"""
        options = []
        
        # Configuraciones variadas para cada opción
        configurations = [
            {"temp": 0.7, "approach": "corporativo_inspiracional", "label": "Profesional"},
            {"temp": 0.9, "approach": "narrativo_emocional", "label": "Emotiva"},
            {"temp": 1.1, "approach": "cercano_familiar", "label": "Cercana"},
            {"temp": 0.8, "approach": "motivacional_energico", "label": "Motivacional"},
            {"temp": 1.0, "approach": "reflexivo_profundo", "label": "Reflexiva"}
        ]
        
        for i in range(num_options):
            config = configurations[i % len(configurations)]
            
            # Construir prompt específico para este enfoque
            enhanced_prompt = self._build_approach_specific_prompt(user_input, config["approach"])
            
            result = self.ai_provider.generate_text(
                enhanced_prompt,
                max_tokens=800,
                temperature=config["temp"],
                preferred_provider=preferred_provider
            )
            
            if result and len(result.strip()) > 50:
                options.append({
                    "id": f"option_{i+1}",
                    "label": f"Versión {config['label']}",
                    "text": result.strip(),
                    "temperature": config["temp"],
                    "approach": config["approach"]
                })
            else:
                options.append({
                    "id": f"option_{i+1}",
                    "label": f"Versión {config['label']}",
                    "text": f"❌ No se pudo generar la versión {config['label']}. Verifica la configuración de IA.",
                    "temperature": config["temp"],
                    "approach": config["approach"]
                })
        
        return options
    
    def correct_text(self, text: str, preferred_provider: str = None) -> str:
        """Corregir texto existente"""
        correction_prompt = self.build_enhanced_prompt(text, "correct")
        
        result = self.ai_provider.generate_text(
            correction_prompt,
            max_tokens=1000,
            temperature=0.3,
            preferred_provider=preferred_provider
        )
        
        if result and len(result.strip()) > 50:
            return result.strip()
        else:
            # Fallback a corrección básica
            return self._correct_text_intelligently(text)
    
    def build_enhanced_prompt(self, user_input: str, task_type: str) -> str:
        """Construir prompt mejorado basado en ejemplos y contexto"""
        if task_type == "generate":
            return self._build_style_trained_prompt(user_input)
        else:
            return self._build_correction_prompt(user_input)
    
    def _build_style_trained_prompt(self, user_input: str) -> str:
        """Construir prompt dinámico con múltiples enfoques creativos"""
        import random
        
        # Cargar contexto y ejemplos
        company_context = self.config_manager.load_json("company_context.json")
        learning_data = self.config_manager.load_json("learning_data.json")
        
        examples = learning_data.get("examples", [])
        feedback_history = learning_data.get("feedback_history", [])
        
        # Análisis inteligente de ejemplos para extraer patrones
        style_patterns = self._analyze_style_patterns(examples)
        recent_feedback = [f for f in feedback_history if f.get("rating", 0) >= 4][-5:]
        
        # Enfoques creativos rotativos
        creative_approaches = [
            "narrativo_emocional", "corporativo_inspiracional", "cercano_familiar", 
            "profesional_cálido", "motivacional_energico", "reflexivo_profundo"
        ]
        
        # Seleccionar enfoque basado en el input y aleatorio
        approach = self._select_creative_approach(user_input, creative_approaches)
        
        # Vocabulario rico y variado por categorías
        vocabulary_sets = {
            "emocional": ["gratitud", "reconocimiento", "admiración", "orgullo", "aprecio", "valoración", "respeto"],
            "corporativo": ["equipo", "organización", "colaboradores", "familia empresarial", "comunidad", "talento"],
            "valores": ["compromiso", "excelencia", "integridad", "dedicación", "pasión", "responsabilidad"],
            "acción": ["impulsamos", "fortalecemos", "construimos", "cultivamos", "desarrollamos", "potenciamos"]
        }
        
        # Construcción dinámica del prompt
        prompt = f"""Eres un comunicador social creativo y experto para {company_context.get('company_name', 'Casa Limpia Colombia')}.

ENFOQUE CREATIVO: {approach.replace('_', ' ').title()}

CONTEXTO DINÁMICO:
• Misión: {company_context.get('mission', 'Brindar servicios de limpieza de excelencia')}
• Valores clave: {', '.join(random.sample(company_context.get('values', []), min(3, len(company_context.get('values', [])))))}
• Audiencia: {company_context.get('target_demographics', {}).get('primary', 'Colaboradores internos')}

PATRONES DE ESTILO IDENTIFICADOS:
• Tono predominante: {style_patterns.get('tone', 'Profesional y cercano')}
• Estructura típica: {style_patterns.get('structure', 'Introducción reflexiva → Desarrollo → Cierre motivacional')}
• Longitud promedio: {style_patterns.get('avg_length', '200-250')} palabras
• Elementos distintivos: {', '.join(style_patterns.get('distinctive_elements', []))}

VOCABULARIO ENRIQUECIDO:
{self._build_dynamic_vocabulary(vocabulary_sets, approach)}

REFERENCIAS DE ESTILO (NO copiar, solo inspirarse):
{self._build_style_references(examples, 2)}

FEEDBACK VALORADO:
{self._build_feedback_insights(recent_feedback)}

DESAFÍO CREATIVO:
Genera un texto original y fresco sobre "{user_input}" que:
✨ Use un lenguaje rico y variado (evita repetir palabras comunes)
🎯 Adapte el enfoque {approach} al contexto específico
💫 Incorpore elementos únicos y sorprendentes
🔄 Varíe la estructura respecto a textos anteriores
🎨 Incluya metáforas o analogías relevantes cuando sea apropiado

DIRECTRICES ESPECÍFICAS:
- Inicia de forma diferente cada vez (evita fórmulas repetitivas)
- Usa sinónimos y variaciones para conceptos clave
- Incorpora elementos del enfoque {approach}
- Mantén autenticidad empresarial
- Longitud: {self._get_dynamic_length(approach)} palabras

Genera SOLO el texto final, sin explicaciones:"""

        return prompt
    
    def _analyze_style_patterns(self, examples):
        """Analizar patrones de estilo en los ejemplos"""
        if not examples:
            return {
                "tone": "Profesional y cercano",
                "structure": "Introducción → Desarrollo → Cierre",
                "avg_length": "200-250",
                "distinctive_elements": ["gratitud", "reconocimiento", "valores"]
            }
        
        # Análisis básico de patrones
        total_words = sum(len(ex.get("text", "").split()) for ex in examples)
        avg_length = total_words // len(examples) if examples else 200
        
        # Detectar elementos comunes
        common_words = []
        for example in examples:
            text = example.get("text", "").lower()
            if "gratitud" in text or "gracias" in text:
                common_words.append("gratitud")
            if "reconoc" in text:
                common_words.append("reconocimiento")
            if "valores" in text or "compromiso" in text:
                common_words.append("valores corporativos")
        
        return {
            "tone": "Profesional y cercano",
            "structure": "Introducción reflexiva → Desarrollo → Cierre motivacional",
            "avg_length": f"{avg_length-50}-{avg_length+50}",
            "distinctive_elements": list(set(common_words))[:3]
        }
    
    def _select_creative_approach(self, user_input, approaches):
        """Seleccionar enfoque creativo basado en el input"""
        import random
        
        input_lower = user_input.lower()
        
        # Mapeo inteligente de inputs a enfoques
        if any(word in input_lower for word in ["día", "celebr", "felicit", "reconoc"]):
            return random.choice(["narrativo_emocional", "corporativo_inspiracional"])
        elif any(word in input_lower for word in ["mujer", "madre", "padre", "familia"]):
            return random.choice(["cercano_familiar", "narrativo_emocional"])
        elif any(word in input_lower for word in ["logro", "meta", "objetivo", "éxito"]):
            return random.choice(["motivacional_energico", "corporativo_inspiracional"])
        else:
            return random.choice(approaches)
    
    def _build_dynamic_vocabulary(self, vocabulary_sets, approach):
        """Construir vocabulario dinámico según el enfoque"""
        import random
        
        vocab_text = ""
        for category, words in vocabulary_sets.items():
            selected_words = random.sample(words, min(3, len(words)))
            vocab_text += f"• {category.title()}: {', '.join(selected_words)}\n"
        
        return vocab_text
    
    def _build_style_references(self, examples, num_refs):
        """Construir referencias de estilo limitadas"""
        import random
        
        if not examples:
            return "No hay ejemplos disponibles"
        
        selected = random.sample(examples, min(num_refs, len(examples)))
        refs = ""
        for i, example in enumerate(selected, 1):
            text_preview = example.get("text", "")[:100] + "..."
            refs += f"{i}. {example.get('occasion', 'Ejemplo')}: {text_preview}\n"
        
        return refs
    
    def _build_feedback_insights(self, recent_feedback):
        """Construir insights del feedback reciente"""
        if not recent_feedback:
            return "• Aún no hay feedback específico"
        
        insights = ""
        for feedback in recent_feedback[-3:]:
            if feedback.get('comments'):
                insights += f"• {feedback['comments']}\n"
        
        return insights if insights else "• Feedback positivo general recibido"
    
    def _get_dynamic_length(self, approach):
        """Obtener longitud dinámica según el enfoque"""
        length_map = {
            "narrativo_emocional": "250-350",
            "corporativo_inspiracional": "200-300",
            "cercano_familiar": "150-250",
            "profesional_cálido": "180-280",
            "motivacional_energico": "200-300",
            "reflexivo_profundo": "300-400"
        }
        return length_map.get(approach, "200-300")
    
    def _build_approach_specific_prompt(self, user_input: str, approach: str) -> str:
        """Construir prompt específico para un enfoque creativo"""
        company_context = self.config_manager.load_json("company_context.json")
        learning_data = self.config_manager.load_json("learning_data.json")
        
        examples = learning_data.get("examples", [])
        
        # Instrucciones específicas por enfoque
        approach_instructions = {
            "narrativo_emocional": "Usa un tono narrativo que conecte emocionalmente. Incluye anécdotas o reflexiones personales.",
            "corporativo_inspiracional": "Mantén un tono profesional pero inspirador. Enfócate en logros y visión empresarial.",
            "cercano_familiar": "Usa un lenguaje cálido y familiar, como si hablaras con un amigo cercano.",
            "profesional_cálido": "Balance perfecto entre profesionalismo y calidez humana.",
            "motivacional_energico": "Genera energía y motivación. Usa lenguaje dinámico y llamadas a la acción.",
            "reflexivo_profundo": "Invita a la reflexión profunda sobre valores y propósito."
        }
        
        # Vocabulario específico por enfoque
        approach_vocabulary = {
            "narrativo_emocional": ["sentimos", "vivimos", "experimentamos", "compartimos", "recordamos"],
            "corporativo_inspiracional": ["lideramos", "innovamos", "trascendemos", "construimos", "proyectamos"],
            "cercano_familiar": ["familia", "hogar", "juntos", "unidos", "compañía", "cercanía"],
            "profesional_cálido": ["compromiso", "dedicación", "profesionalismo", "calidez", "respeto"],
            "motivacional_energico": ["energía", "pasión", "impulso", "fuerza", "determinación", "acción"],
            "reflexivo_profundo": ["reflexión", "propósito", "esencia", "significado", "trascendencia"]
        }
        
        prompt = f"""Eres un comunicador social experto para {company_context.get('company_name', 'Casa Limpia Colombia')}.

ENFOQUE ESPECÍFICO: {approach.replace('_', ' ').title()}

INSTRUCCIONES PARA ESTE ENFOQUE:
{approach_instructions.get(approach, 'Mantén el estilo profesional y cercano.')}

VOCABULARIO SUGERIDO PARA ESTE ENFOQUE:
{', '.join(approach_vocabulary.get(approach, []))}

CONTEXTO EMPRESARIAL:
• Misión: {company_context.get('mission', 'Brindar servicios de limpieza de excelencia')}
• Valores: {', '.join(company_context.get('values', [])[:3])}

EJEMPLO DE REFERENCIA (para el tono, NO para copiar):
{examples[0].get('text', '')[:200] + '...' if examples else 'Sin ejemplos disponibles'}

TAREA:
Genera un texto completamente original sobre "{user_input}" usando el enfoque {approach.replace('_', ' ')}.

REQUISITOS CREATIVOS:
• Inicia de forma única y original
• Usa vocabulario rico y variado
• Incorpora el enfoque específico solicitado
• Mantén la autenticidad de Casa Limpia
• Longitud: 200-350 palabras
• NO uses frases cliché o repetitivas

Genera ÚNICAMENTE el texto final:"""

        return prompt
    
    def _build_correction_prompt(self, text_to_correct: str) -> str:
        """Construir prompt para corrección de texto"""
        company_context = self.config_manager.load_json("company_context.json")
        
        prompt = f"""Eres un editor experto en comunicación corporativa para {company_context.get('company_name', 'Casa Limpia Colombia')}.

CONTEXTO EMPRESARIAL:
- Estilo: {company_context.get('communication_style', {}).get('tone', 'Profesional y cercano')}
- Vocabulario preferido: {', '.join(company_context.get('communication_style', {}).get('vocabulary', []))}
- Palabras a evitar: {', '.join(company_context.get('communication_style', {}).get('avoid', []))}

TEXTO A CORREGIR:
"{text_to_correct}"

INSTRUCCIONES:
1. Corrige errores gramaticales y ortográficos
2. Mejora la fluidez y claridad
3. Adapta el vocabulario al estilo Casa Limpia (usar "colaboradores" en lugar de "empleados")
4. Mantén el tono profesional pero cercano
5. Asegúrate de que sea coherente y bien estructurado
6. Si es muy corto, amplía con elementos emocionales apropiados

Proporciona ÚNICAMENTE el texto corregido, sin explicaciones:"""

        return prompt
    
    def _correct_text_intelligently(self, text: str) -> str:
        """Corrección inteligente básica como fallback"""
        corrected = text
        
        # Correcciones básicas de vocabulario Casa Limpia
        replacements = {
            r'\bempleados?\b': 'colaboradores',
            r'\btrabajadores?\b': 'miembros del equipo',
            r'\bpersonal\b': 'equipo',
            r'\bcompañía\b': 'empresa',
            r'\bmuy bueno\b': 'excelente',
            r'\bfelicitaciones\b': 'reconocimiento'
        }
        
        for pattern, replacement in replacements.items():
            corrected = re.sub(pattern, replacement, corrected, flags=re.IGNORECASE)
        
        # Agregar contexto emocional si es muy corto
        if len(corrected.split()) < 30:
            corrected += " Gracias por ser parte de nuestra gran familia Casa Limpia y por su dedicación constante."
        
        return corrected
    
    def add_feedback(self, original: str, generated: str, task_type: str, rating: int, 
                    comments: str = "", category: str = "General", option_id: str = None):
        """Agregar feedback del usuario para aprendizaje"""
        learning_data = self.config_manager.load_json("learning_data.json")
        
        feedback_entry = FeedbackEntry(
            original_text=original,
            generated_text=generated,
            rating=rating,
            comments=comments,
            timestamp=datetime.now().isoformat(),
            task_type=task_type,
            category=category,
            option_id=option_id
        )
        
        if "feedback_history" not in learning_data:
            learning_data["feedback_history"] = []
        
        learning_data["feedback_history"].append(asdict(feedback_entry))
        
        # Mantener solo los últimos 100 feedbacks
        learning_data["feedback_history"] = learning_data["feedback_history"][-100:]
        
        # Actualizar preferencias del usuario basado en feedback positivo
        self._update_user_preferences(learning_data, feedback_entry)
        
        self.config_manager.save_json("learning_data.json", learning_data)
    
    def _update_user_preferences(self, learning_data: Dict, feedback: FeedbackEntry):
        """Actualizar preferencias del usuario basado en feedback"""
        if "user_preferences" not in learning_data:
            learning_data["user_preferences"] = {
                "preferred_length": "medium",
                "preferred_tone": "professional_warm",
                "common_corrections": []
            }
        
        preferences = learning_data["user_preferences"]
        
        # Analizar feedback positivo para mejorar
        if feedback.rating >= 4:
            text_length = len(feedback.generated_text.split())
            
            if text_length < 100:
                length_pref = "short"
            elif text_length > 250:
                length_pref = "long"
            else:
                length_pref = "medium"
            
            preferences["preferred_length"] = length_pref
            
            if feedback.comments:
                # Extraer elementos positivos del comentario
                positive_keywords = ["excelente", "perfecto", "me gusta", "muy bien", "apropiado"]
                for keyword in positive_keywords:
                    if keyword.lower() in feedback.comments.lower():
                        if "positive_elements" not in preferences:
                            preferences["positive_elements"] = []
                        if feedback.comments not in preferences["positive_elements"]:
                            preferences["positive_elements"].append(feedback.comments)
