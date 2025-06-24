import csv
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..core.config import settings

class LearningPathService:
    def __init__(self):
        self.csv_path = Path(settings.base_dir) / "data" / "learning_modules.csv"
        self.modules_data = self._load_modules()
    
    def _load_modules(self) -> List[Dict[str, str]]:
        """Carga los módulos desde el archivo CSV"""
        modules = []
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    modules.append(row)
        except FileNotFoundError:
            print(f"CSV file not found: {self.csv_path}")
        except Exception as e:
            print(f"Error loading modules: {e}")
        return modules
    
    def get_modules_context(self) -> str:
        """Retorna el contexto de módulos formateado para el prompt"""
        if not self.modules_data:
            return "No hay módulos disponibles actualmente."
        
        context = "MÓDULOS Y EJES TEMÁTICOS DISPONIBLES:\n\n"
        for i, module in enumerate(self.modules_data, 1):
            context += f"{i}. EJE TEMÁTICO: {module['eje_tematico']}\n"
            context += f"   MÓDULO: {module['modulo']}\n"
            context += f"   COMPETENCIA: {module['competencia']}\n"
            context += f"   PREGUNTAS DE EVALUACIÓN: {module['preguntas']}\n\n"
        
        return context
    
    def get_module_by_name(self, eje_tematico: str) -> Optional[Dict[str, str]]:
        """Busca un módulo por nombre del eje temático"""
        for module in self.modules_data:
            if module['eje_tematico'].lower() == eje_tematico.lower():
                return module
        return None
    
    def validate_learning_path(self, learning_path_json: Dict[str, Any]) -> bool:
        """Valida que la ruta de aprendizaje tenga el formato correcto"""
        required_fields = ["action", "student_profile", "recommended_modules"]
        
        if not all(field in learning_path_json for field in required_fields):
            return False
        
        if learning_path_json["action"] != "generate_learning_path":
            return False
        
        for module in learning_path_json.get("recommended_modules", []):
            if not all(key in module for key in ["eje_tematico", "modulo", "competencia"]):
                return False
        
        return True
    
    def extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extrae JSON de la respuesta del chat"""
        try:
            # Buscar el bloque JSON en la respuesta
            start_marker = "```json"
            end_marker = "```"
            
            start_idx = response.find(start_marker)
            if start_idx == -1:
                return None
            
            start_idx += len(start_marker)
            end_idx = response.find(end_marker, start_idx)
            
            if end_idx == -1:
                return None
            
            json_str = response[start_idx:end_idx].strip()
            parsed_json = json.loads(json_str)
            
            if self.validate_learning_path(parsed_json):
                return parsed_json
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error extracting JSON: {e}")
        
        return None
    
    def format_learning_path_for_display(self, learning_path: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea la ruta de aprendizaje para mostrar en la interfaz"""
        formatted_modules = []
        
        for module in learning_path.get("recommended_modules", []):
            # Buscar información adicional del módulo
            module_data = self.get_module_by_name(module["eje_tematico"])
            
            formatted_module = {
                "id": len(formatted_modules) + 1,
                "title": module["eje_tematico"],
                "module": module["modulo"],
                "competencia": module["competencia"],
                "justification": module.get("justification", ""),
                "priority": module.get("priority", "media"),
                "duration": module.get("estimated_duration", "2-3 semanas"),
                "questions": module_data["preguntas"] if module_data else "",
                "status": "pending",
                "progress": 0
            }
            formatted_modules.append(formatted_module)
        
        return {
            "student_profile": learning_path.get("student_profile", ""),
            "modules": formatted_modules,
            "learning_sequence": learning_path.get("learning_sequence", ""),
            "next_steps": learning_path.get("next_steps", ""),
            "created_at": "just now"
        }

# Instancia global del servicio
learning_path_service = LearningPathService()
