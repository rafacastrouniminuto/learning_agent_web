# Servicio AWS Bedrock para Learning Agent Web
# Reemplazo de OpenAI con AWS Bedrock (Claude 3)

import boto3
import json
from typing import List, Dict, Optional, AsyncGenerator
from botocore.exceptions import ClientError
import logging

logger = logging.getLogger(__name__)


class BedrockService:
    """
    Servicio para interactuar con AWS Bedrock (Claude 3)
    Reemplazo directo de OpenAI API
    """
    
    # Modelos disponibles
    MODELS = {
        "haiku": "anthropic.claude-3-haiku-20240307-v1:0",
        "sonnet": "anthropic.claude-3-sonnet-20240229-v1:0",
        "opus": "anthropic.claude-3-opus-20240229-v1:0"
    }
    
    def __init__(
        self,
        region_name: str = "us-east-1",
        model: str = "haiku",
        max_tokens: int = 1000,
        temperature: float = 0.7
    ):
        """
        Inicializar servicio Bedrock
        
        Args:
            region_name: Región AWS donde está habilitado Bedrock
            model: Modelo a usar (haiku, sonnet, opus)
            max_tokens: Máximo de tokens en respuesta
            temperature: Control de creatividad (0.0-1.0)
        """
        self.client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region_name
        )
        self.model_id = self.MODELS.get(model, self.MODELS["haiku"])
        self.max_tokens = max_tokens
        self.temperature = temperature
        
        logger.info(f"Bedrock Service initialized with model: {self.model_id}")
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None,
        stream: bool = False
    ) -> Dict:
        """
        Generar respuesta de chat
        Compatible con formato OpenAI
        
        Args:
            messages: Lista de mensajes [{"role": "user", "content": "..."}]
            tools: Herramientas MCP disponibles (function calling)
            stream: Si True, retorna generator para streaming
        
        Returns:
            Respuesta del modelo o generator si stream=True
        """
        try:
            # Construir payload para Bedrock
            body = self._build_request_body(messages, tools)
            
            if stream:
                return self._invoke_model_stream(body)
            else:
                return self._invoke_model(body)
                
        except ClientError as e:
            logger.error(f"Bedrock API error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    def _build_request_body(
        self,
        messages: List[Dict[str, str]],
        tools: Optional[List[Dict]] = None
    ) -> str:
        """
        Construir cuerpo de petición para Bedrock Claude
        """
        # Convertir mensajes al formato Claude
        claude_messages = self._convert_messages(messages)
        
        body = {
            "anthropic_version": "bedrock-2023-05-31",
            "max_tokens": self.max_tokens,
            "messages": claude_messages,
            "temperature": self.temperature,
            "top_p": 0.9
        }
        
        # Agregar tools si están disponibles (MCP integration)
        if tools:
            body["tools"] = self._convert_tools_to_claude_format(tools)
        
        return json.dumps(body)
    
    def _convert_messages(self, messages: List[Dict]) -> List[Dict]:
        """
        Convertir mensajes de formato OpenAI a Claude
        
        OpenAI: [{"role": "system"|"user"|"assistant", "content": "..."}]
        Claude: [{"role": "user"|"assistant", "content": "..."}]
        
        Claude no tiene "system" role, se maneja diferente
        """
        claude_messages = []
        system_content = None
        
        for msg in messages:
            role = msg["role"]
            content = msg["content"]
            
            if role == "system":
                # Claude maneja system messages en un campo separado
                system_content = content
            elif role in ["user", "assistant"]:
                claude_messages.append({
                    "role": role,
                    "content": content
                })
        
        # Si hay system message, se agrega al principio como user message
        if system_content and claude_messages:
            # Prefijar al primer mensaje del usuario
            if claude_messages[0]["role"] == "user":
                claude_messages[0]["content"] = (
                    f"{system_content}\n\n{claude_messages[0]['content']}"
                )
            else:
                # Insertar al inicio
                claude_messages.insert(0, {
                    "role": "user",
                    "content": system_content
                })
        
        return claude_messages
    
    def _convert_tools_to_claude_format(self, tools: List[Dict]) -> List[Dict]:
        """
        Convertir herramientas MCP de formato OpenAI a Claude
        
        OpenAI functions -> Claude tools
        """
        claude_tools = []
        
        for tool in tools:
            if tool["type"] == "function":
                func = tool["function"]
                claude_tools.append({
                    "name": func["name"],
                    "description": func["description"],
                    "input_schema": func["parameters"]
                })
        
        return claude_tools
    
    def _invoke_model(self, body: str) -> Dict:
        """
        Invocar modelo Bedrock (sin streaming)
        """
        response = self.client.invoke_model(
            modelId=self.model_id,
            body=body
        )
        
        # Parsear respuesta
        response_body = json.loads(response['body'].read())
        
        # Convertir a formato compatible con OpenAI
        return self._convert_response_to_openai_format(response_body)
    
    async def _invoke_model_stream(self, body: str) -> AsyncGenerator[str, None]:
        """
        Invocar modelo Bedrock con streaming
        """
        response = self.client.invoke_model_with_response_stream(
            modelId=self.model_id,
            body=body
        )
        
        # Stream chunks
        for event in response['body']:
            chunk = json.loads(event['chunk']['bytes'].decode())
            
            # Extraer texto del chunk
            if chunk['type'] == 'content_block_delta':
                if 'delta' in chunk and 'text' in chunk['delta']:
                    yield chunk['delta']['text']
            
            # Tool use (function calling)
            elif chunk['type'] == 'content_block_start':
                if 'content_block' in chunk:
                    block = chunk['content_block']
                    if block.get('type') == 'tool_use':
                        yield json.dumps({
                            "tool_call": {
                                "name": block.get('name'),
                                "id": block.get('id')
                            }
                        })
    
    def _convert_response_to_openai_format(self, bedrock_response: Dict) -> Dict:
        """
        Convertir respuesta de Bedrock a formato OpenAI
        Para compatibilidad con código existente
        """
        content = ""
        tool_calls = []
        
        # Extraer contenido
        for block in bedrock_response.get('content', []):
            if block['type'] == 'text':
                content += block['text']
            elif block['type'] == 'tool_use':
                tool_calls.append({
                    "id": block['id'],
                    "type": "function",
                    "function": {
                        "name": block['name'],
                        "arguments": json.dumps(block['input'])
                    }
                })
        
        # Formato OpenAI
        openai_response = {
            "choices": [{
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": bedrock_response.get('stop_reason', 'stop')
            }],
            "usage": {
                "prompt_tokens": bedrock_response.get('usage', {}).get('input_tokens', 0),
                "completion_tokens": bedrock_response.get('usage', {}).get('output_tokens', 0),
                "total_tokens": (
                    bedrock_response.get('usage', {}).get('input_tokens', 0) +
                    bedrock_response.get('usage', {}).get('output_tokens', 0)
                )
            }
        }
        
        # Agregar tool_calls si existen
        if tool_calls:
            openai_response["choices"][0]["message"]["tool_calls"] = tool_calls
        
        return openai_response
    
    async def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generar embeddings usando Amazon Titan Embeddings
        (Bedrock no tiene embeddings de Claude, usar Titan)
        """
        embeddings_client = boto3.client(
            service_name='bedrock-runtime',
            region_name='us-east-1'
        )
        
        embeddings = []
        model_id = "amazon.titan-embed-text-v1"
        
        for text in texts:
            body = json.dumps({
                "inputText": text
            })
            
            response = embeddings_client.invoke_model(
                modelId=model_id,
                body=body
            )
            
            response_body = json.loads(response['body'].read())
            embeddings.append(response_body.get('embedding', []))
        
        return embeddings


# Instancia global del servicio
bedrock_service = BedrockService(
    region_name="us-east-1",
    model="haiku",  # Más económico
    max_tokens=1000,
    temperature=0.7
)


# Funciones de conveniencia (compatible con openai_service.py)
async def chat_completion(
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict]] = None,
    stream: bool = False
):
    """
    Función de conveniencia compatible con openai_service
    """
    return await bedrock_service.chat_completion(messages, tools, stream)


async def chat_completion_stream(
    messages: List[Dict[str, str]],
    tools: Optional[List[Dict]] = None
) -> AsyncGenerator[str, None]:
    """
    Stream de chat completion
    """
    async for chunk in await bedrock_service.chat_completion(
        messages, tools, stream=True
    ):
        yield chunk