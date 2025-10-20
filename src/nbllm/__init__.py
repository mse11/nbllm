"""nbllm - An AI-powered coding assistant for editing files with interactive confirmations."""

import importlib.metadata

from .__main__ import chat
from .chat import  Chat
from .chat_config import ConfigLlm, ConfigMode, ConfigModes
from .chat_factory import FactoryConfigLlmDefault, FactoryConfigModesDeveloper, FactoryConfigModesToolsOnly

# Get version dynamically from package metadata
try:
    __version__ = importlib.metadata.version("nbllm")
except:
    __version__ = "unknown"

__all__ = [
    "chat",
    "Chat",
    "ConfigLlm",
    "ConfigMode",
    "FactoryConfigModesDeveloper",
    "FactoryConfigLlmDefault",
    "__version__"
]