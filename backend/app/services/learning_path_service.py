import csv
import json
import re
import unicodedata
from pathlib import Path
from typing import List, Dict, Any, Optional
from ..core.config import settings

class LearningPathService:
    def __init__(self):
        self.csv_path = Path(settings.base_dir) / "data" / "learning_modules.csv"
        self.modules_data = self._load_modules()
        # Índice normalizado por eje_tematico para matching rápido
        self._axis_index = {}
        # Índice por nombre de módulo -> lista de filas (para incluir varios ejes)
        self._module_index = {}
        for row in self.modules_data:
            axis_key = self._normalize(row.get('eje_tematico', ''))
            if axis_key:
                self._axis_index[axis_key] = row
            mod_key = self._normalize(row.get('modulo', ''))
            if mod_key:
                self._module_index.setdefault(mod_key, []).append(row)

    def _normalize(self, s: str) -> str:
        if not s:
            return ""
        s = unicodedata.normalize('NFKD', s)
        s = s.encode('ascii', 'ignore').decode('ascii')
        s = s.lower()
        s = re.sub(r'[^a-z0-9 ]+', ' ', s)
        s = re.sub(r'\s+', ' ', s).strip()
        return s

    def _match_csv_axis(self, eje_text: str) -> Optional[Dict[str, str]]:
        """Devuelve la fila del CSV cuyo eje_tematico coincide (exacto o parcialmente) con eje_text."""
        if not eje_text:
            return None
        norm = self._normalize(eje_text)
        # 1) Igualdad exacta normalizada
        if norm in self._axis_index:
            return self._axis_index[norm]
        # 2) Búsqueda por contains
        for k, row in self._axis_index.items():
            if norm and (norm in k or k in norm):
                return row
        return None

    def _match_csv_module_rows(self, modulo_text: str) -> List[Dict[str, str]]:
        """Devuelve todas las filas del CSV cuyo modulo coincide (exacto o parcialmente) con modulo_text."""
        if not modulo_text:
            return []
        norm = self._normalize(modulo_text)
        rows = []
        # Exacto
        if norm in self._module_index:
            return list(self._module_index[norm])
        # Contains
        for key, lst in self._module_index.items():
            if norm and (norm in key or key in norm):
                rows.extend(lst)
        return rows

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
    
    def get_modules_context(self, max_modules: int = None, compact: bool = False) -> str:
        """Retorna el contexto de módulos formateado para el prompt con gestión de tokens"""
        if not self.modules_data:
            return "No hay módulos disponibles actualmente."
        
        # Limitar módulos si se especifica
        modules_to_show = self.modules_data[:max_modules] if max_modules else self.modules_data
        
        if compact:
            # Versión compacta organizada por categorías
            context = "EJES TEMÁTICOS POR CATEGORÍA:\n\n"
            
            # Agrupar por categoría
            categories = {}
            for module in modules_to_show:
                categoria = module.get('categoria', 'General')
                if categoria not in categories:
                    categories[categoria] = []
                categories[categoria].append(module)
            
            for categoria, modules in categories.items():
                context += f"📁 {categoria.upper()}:\n"
                for module in modules:
                    context += f"  • {module['eje_tematico']}\n"
                context += "\n"
            
            context += f"Total disponibles: {len(self.modules_data)} ejes"
            if max_modules and len(self.modules_data) > max_modules:
                context += f" (mostrando primeros {max_modules})"
        else:
            # Versión completa para módulos pequeños
            context = "MÓDULOS Y EJES TEMÁTICOS DISPONIBLES:\n\n"
            for i, module in enumerate(modules_to_show, 1):
                context += f"{i}. EJE TEMÁTICO: {module['eje_tematico']}\n"
                context += f"   MÓDULO: {module['modulo']}\n"
                context += f"   COMPETENCIA: {module['competencia']}\n"
                context += f"   CATEGORÍA: {module.get('categoria', 'General')}\n"
                # Solo incluir preguntas si son pocos módulos
                if len(modules_to_show) <= 10:
                    context += f"   PREGUNTAS DE EVALUACIÓN: {module['preguntas']}\n"
                context += "\n"
        
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
            # Permitimos que falte eje_tematico si viene modulo, para cubrir el caso de incluir todos los ejes del módulo
            if not (module.get("eje_tematico") or module.get("modulo")):
                return False
        
        return True
    
    def extract_json_from_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Extrae JSON de la respuesta del chat de forma simple y robusta"""
        try:
            print(f"🔍 DEBUG - Extracting JSON from response (length: {len(response)})")
            print(f"🔍 DEBUG - Response: {response[:500]}...")
            
            # Intentar parsear la respuesta completa como JSON
            try:
                parsed = json.loads(response.strip())
                if self.validate_learning_path(parsed):
                    print("✅ Direct JSON parsing successful")
                    return parsed
            except json.JSONDecodeError:
                pass
            
            # Buscar el primer { y el último } balanceado
            start = response.find('{')
            if start == -1:
                print("❌ No opening brace found")
                return None
            
            # Contar llaves para encontrar el cierre correcto
            brace_count = 0
            end = start
            
            for i in range(start, len(response)):
                if response[i] == '{':
                    brace_count += 1
                elif response[i] == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            if end <= start:
                print("❌ No closing brace found")
                return None
            
            json_str = response[start:end].strip()
            print(f"🔍 DEBUG - Extracted JSON: {json_str[:200]}...")
            
            try:
                parsed = json.loads(json_str)
                if self.validate_learning_path(parsed):
                    print("✅ JSON extraction successful")
                    return parsed
                else:
                    print("❌ JSON validation failed")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                
        except Exception as e:
            print(f"❌ Error in extract_json_from_response: {e}")
            
        return None
    
    def format_learning_path_for_display(self, learning_path: Dict[str, Any]) -> Dict[str, Any]:
        """Formatea la ruta para la interfaz. Si el modelo no genera suficientes ejes,
        usa los datos del CSV manteniendo la cantidad solicitada."""
        formatted_modules: List[Dict[str, Any]] = []
        used_axes = set()

        # Función helper para agregar una fila del CSV como tarjeta
        def add_csv_row(row_item: Dict[str, str], priority: str = "media", duration: str = "3-4 semanas"):
            eje_key = self._normalize(row_item.get('eje_tematico', ''))
            if not eje_key or eje_key in used_axes:
                return False
            used_axes.add(eje_key)

            title = row_item.get('eje_tematico') or "Módulo"
            competencia = row_item.get('competencia') or ""
            questions = row_item.get('preguntas', '')

            formatted_modules.append({
                "id": len(formatted_modules) + 1,
                "title": title,
                "module": title,
                "competencia": competencia,
                "justification": f"Fundamentos clave en {title.split(':')[0] if ':' in title else title}",
                "priority": priority,
                "duration": duration,
                "questions": questions,
                "status": "pending",
                "progress": 0
            })
            return True

        # 1) Primero, intentar usar los módulos generados por el modelo
        recommended_modules = learning_path.get("recommended_modules", [])
        if recommended_modules:
            print(f"🔍 DEBUG - Model generated {len(recommended_modules)} modules")
            for module in recommended_modules:
                eje = module.get("eje_tematico") or module.get("axis") or module.get("tema")
                row = self._match_csv_axis(eje) if eje else None
                if row:
                    priority = module.get("priority", "media")
                    duration = module.get("estimated_duration", "3-4 semanas")
                    add_csv_row(row, priority, duration)

        # 2) Si el modelo no generó suficientes (menos de 3), completar con CSV hasta 5 por defecto
        target_count = len(recommended_modules) if recommended_modules and len(recommended_modules) >= 3 else 5
        target_count = min(target_count, 6)  # Máximo 6
        
        print(f"🔍 DEBUG - Target count: {target_count}, current count: {len(formatted_modules)}")
        
        if len(formatted_modules) < target_count:
            for row_item in self.modules_data:
                if len(formatted_modules) >= target_count:
                    break
                add_csv_row(row_item, priority="media", duration="3-4 semanas")

        return {
            "student_profile": learning_path.get("student_profile", "Estudiante interesado en STEM+, nivel inicial, buscando adquirir conocimientos básicos"),
            "modules": formatted_modules,
            "learning_sequence": learning_path.get("learning_sequence", f"Se recomienda seguir la secuencia: 1. Ecosistemas de Innovación → 2. Aprendizaje Experiencial → 3. Neurociencia → 4. Sostenibilidad → 5. Transdisciplinariedad" + (" → 6. Pedagogías Emergentes" if len(formatted_modules) == 6 else "")),
            "next_steps": learning_path.get("next_steps", "Te recomendaría dedicar tiempo y esfuerzo a cada curso, practicar los conceptos aprendidos y buscar aplicaciones prácticas en proyectos personales o académicos."),
            "created_at": "just now"
        }

# Instancia global del servicio
learning_path_service = LearningPathService()
