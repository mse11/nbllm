"""nbllm - An AI-powered coding assistant for editing files with interactive confirmations."""

import importlib.metadata

from .__main__ import chat
from .chat import  Chat
from .chat_config import LlmConfig, ModeConfig, ModesConfig
from .chat_factory import LlmConfigFactoryDefault, ModesConfigFactoryDeveloper, ModesConfigFactoryToolsOnly

# Get version dynamically from package metadata
try:
    __version__ = importlib.metadata.version("nbllm")
except:
    __version__ = "unknown"

__all__ = [
    "chat",
    "Chat",
    "LlmConfig",
    "ModeConfig",
    "ModesConfigFactoryDeveloper",
    "LlmConfigFactoryDefault",
    "__version__"
]