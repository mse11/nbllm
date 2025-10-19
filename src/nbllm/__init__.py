"""nbllm - An AI-powered coding assistant for editing files with interactive confirmations."""

import importlib.metadata

from .__main__ import chat
from .chat import  Chat
from .chat_config import LlmConfig, ModeConfig, ModesConfig

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
    "ChatConfig",
    "__version__"
]