"""
QuickBot - Lightweight Personal AI Assistant
Core Configuration Module
"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Configuration manager for QuickBot."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config_path = Path(config_path)
        self.config = {}
        self.load()
    
    def load(self) -> None:
        """Load configuration from file."""
        if self.config_path.exists():
            with open(self.config_path, 'r') as f:
                self.config = yaml.safe_load(f) or {}
        else:
            self.config = self.get_default_config()
            self.save()
    
    def save(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value by key (supports dot notation)."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value by key (supports dot notation)."""
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
        self.save()
    
    @staticmethod
    def get_default_config() -> Dict[str, Any]:
        """Get default configuration."""
        return {
            'bot': {
                'name': 'QuickBot',
                'timezone': 'Asia/Shanghai',
                'debug': False
            },
            'platforms': {
                'telegram': {
                    'enabled': True,
                    'token': '',
                    'allowed_users': []
                },
                'discord': {
                    'enabled': False,
                    'token': ''
                }
            },
            'ai': {
                'provider': 'openai',  # openai, anthropic, ollama
                'api_key': '',
                'model': 'gpt-4o',
                'base_url': '',  # optional custom endpoint
                'max_tokens': 2000,
                'temperature': 0.7
            },
            'memory': {
                'enabled': True,
                'max_messages': 1000,
                'storage': 'memory.db'
            },
            'scheduler': {
                'enabled': True,
                'storage': 'scheduler.db'
            },
            'tools': {
                'enabled': True,
                'directory': 'tools/'
            },
            'web': {
                'enabled': False,
                'port': 8080,
                'host': '0.0.0.0',
                'auth': ''
            },
            'logging': {
                'level': 'INFO',  # DEBUG, INFO, WARNING, ERROR
                'file': 'quickbot.log',
                'max_size': 10485760,  # 10MB
                'backup_count': 5
            }
        }
