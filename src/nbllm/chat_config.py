import os

from dataclasses import dataclass, field
from typing import List, Any, Union
from pathlib import Path

##################################################################################
################################ LLM #############################################
##################################################################################
@dataclass
class ConfigLlm:
    system_prompt: str
    model_id: str = "nbllm_model"            # 'extra-openai-models.yaml' is use by 'llm'
    path_to_extra_openai_models: str = None  # 'extra-openai-models.yaml' is use by 'llm'

    def __post_init__(self):
        # export 'llm' config for compatibility with OpenAI API

        if self.path_to_extra_openai_models is None:
            return

        file_content = """
- model_id: nbllm_model
  model_name: qwen3-coder:30b
#  api_base: http://localhost:1234/v1   # LOCAL models running by LM Studio
  api_base: http://localhost:11434/v1   # LOCAL models running by OLLAMA
  supports_tools: true
""".strip()

        file_path = Path(self.path_to_extra_openai_models) / "extra-openai-models.yaml"
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(file_content)

        # export path for 'llm' tool
        os.environ['LLM_USER_PATH'] = self.path_to_extra_openai_models

##################################################################################
################################ MODES ###########################################
##################################################################################
@dataclass
class ConfigMode:
    """Configuration for a single mode with associated tools and mode switch message"""
    mode: str
    tools: List[Any] = field(default_factory=list) # Todo type
    mode_switch_message: str = ""


@dataclass
class ConfigModes:
    """"""
    current_mode: Union[str, None] = None
    modes_cfg: List[ConfigMode] = field(default_factory=list)

    def __post_init__(self):
        # Ensure all mode names are unique
        mode_names = [mode.mode for mode in self.modes_cfg]
        if len(mode_names) != len(set(mode_names)):
            raise ValueError("Duplicate mode names detected")

    @property
    def tools_by_mode(self) -> dict[str, List[Any]]:
        """Get tools for all modes as a dictionary"""
        return {m.mode: m.tools for m in self.modes_cfg}

    @property
    def mode_switch_messages_by_mode(self) -> dict[str, str]:
        """Get switch messages for all modes as a dictionary"""
        return {m.mode: m.mode_switch_message for m in self.modes_cfg}

    @property
    def all_modes(self) -> List[str]:
        """Get all modes"""
        return [m.mode for m in self.modes_cfg]


