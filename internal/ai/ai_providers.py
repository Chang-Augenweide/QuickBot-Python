"""
QuickBot - AI Provider Interface and Implementations
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, AsyncIterator
import json
import logging

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """Base class for AI providers."""
    
    def __init__(self, api_key: str, model: str, **kwargs):
        self.api_key = api_key
        self.model = model
        self.config = kwargs
    
    @abstractmethod
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Send chat completion request."""
        pass
    
    @abstractmethod
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion."""
        pass


class OpenAIProvider(AIProvider):
    """OpenAI API provider."""
    
    def __init__(self, api_key: str, model: str = "gpt-4o", base_url: str = "", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self.base_url = base_url or "https://api.openai.com/v1"
        self._client = None
    
    async def _get_client(self):
        """Lazy initialize client."""
        if self._client is None:
            try:
                from openai import AsyncOpenAI
                self._client = AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
        return self._client
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Send chat completion request to OpenAI."""
        client = await self._get_client()
        
        try:
            response = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion from OpenAI."""
        client = await self._get_client()
        
        try:
            stream = await client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                **kwargs
            )
            
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            raise


class AnthropicProvider(AIProvider):
    """Anthropic (Claude) API provider."""
    
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022", **kwargs):
        super().__init__(api_key, model, **kwargs)
        self._client = None
    
    async def _get_client(self):
        """Lazy initialize client."""
        if self._client is None:
            try:
                import anthropic
                self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
        return self._client
    
    def _format_messages(self, messages: List[Dict[str, str]]) -> tuple:
        """Convert OpenAI format to Anthropic format."""
        system_messages = []
        messages_list = []
        
        for msg in messages:
            if msg['role'] == 'system':
                system_messages.append(msg['content'])
            else:
                messages_list.append({
                    'role': msg['role'] if msg['role'] != 'assistant' else 'assistant',
                    'content': msg['content']
                })
        
        system = '\n'.join(system_messages) if system_messages else None
        return system, messages_list
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Send chat completion request to Anthropic."""
        client = await self._get_client()
        system, messages_list = self._format_messages(messages)
        
        try:
            message = client.messages.create(
                model=self.model,
                system=system,
                messages=messages_list,
                max_tokens=kwargs.get('max_tokens', self.config.get('max_tokens', 2000))
            )
            return message.content[0].text
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            raise
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion from Anthropic."""
        client = await self._get_client()
        system, messages_list = self._format_messages(messages)
        
        try:
            with client.messages.stream(
                model=self.model,
                system=system,
                messages=messages_list,
                max_tokens=kwargs.get('max_tokens', self.config.get('max_tokens', 2000))
            ) as stream:
                async for text in stream.text_stream:
                    yield text
        except Exception as e:
            logger.error(f"Anthropic streaming error: {e}")
            raise


class OllamaProvider(AIProvider):
    """Local Ollama provider."""
    
    def __init__(self, model: str = "llama3.2", **kwargs):
        super().__init__("", model, **kwargs)
        self.base_url = kwargs.get('base_url', 'http://localhost:11434')
        self._session = None
    
    async def _get_session(self):
        """Lazy initialize HTTP session."""
        if self._session is None:
            import aiohttp
            self._session = aiohttp.ClientSession()
        return self._session
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> str:
        """Send chat completion request to Ollama."""
        session = await self._get_session()
        
        # Format messages for Ollama
        prompt = '\n'.join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])
        
        try:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': False
                },
                timeout=kwargs.get('timeout', 120)
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Ollama API error: {error}")
                
                data = await response.json()
                return data.get('response', '')
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            raise
    
    async def chat_stream(
        self,
        messages: List[Dict[str, str]],
        **kwargs
    ) -> AsyncIterator[str]:
        """Stream chat completion from Ollama."""
        session = await self._get_session()
        
        # Format messages for Ollama
        prompt = '\n'.join([
            f"{msg['role']}: {msg['content']}"
            for msg in messages
        ])
        
        try:
            async with session.post(
                f"{self.base_url}/api/generate",
                json={
                    'model': self.model,
                    'prompt': prompt,
                    'stream': True
                },
                timeout=kwargs.get('timeout', 120)
            ) as response:
                if response.status != 200:
                    error = await response.text()
                    raise Exception(f"Ollama API error: {error}")
                
                async for line in response.content:
                    if line:
                        try:
                            data = json.loads(line)
                            if 'response' in data:
                                yield data['response']
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error(f"Ollama streaming error: {e}")
            raise


def get_provider(provider_type: str, api_key: str, model: str, **kwargs) -> AIProvider:
    """Factory function to get AI provider."""
    providers = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'ollama': OllamaProvider
    }
    
    provider_class = providers.get(provider_type.lower())
    if not provider_class:
        raise ValueError(f"Unknown provider: {provider_type}")
    
    if provider_type.lower() == 'ollama':
        return provider_class(model=model, **kwargs)
    
    return provider_class(api_key=api_key, model=model, **kwargs)
