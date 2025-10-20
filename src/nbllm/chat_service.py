
import llm
from typing import Optional, Union, Dict, Any, List, Tuple
from dataclasses import dataclass, field

from nbllm.chat_config import ConfigLlm, ConfigModes

##################################################################################
################################ LLM #############################################
##################################################################################

@dataclass
class LlmService:
    cfg_llm: ConfigLlm
    cfg_modes: ConfigModes
    llm_model: Optional[llm.Model] = field(default=None)
    llm_conversation: Optional[llm.Conversation] = field(default=None)
    llm_history_backup: Optional[List[ Dict[str, Any] ]] = field(default=None)

    def __post_init__(self):
        self.llm_exec_init()

    ### modes
    @property
    def modes_all(self):
        """Get all modes"""
        return self.cfg_modes.all_modes

    @property
    def modes_enabled(self):
        """Get all modes"""
        return True if len(self.cfg_modes.all_modes) else False

    ### mode
    @property
    def mode_current(self):
        """Get current mode."""
        mode = self.cfg_modes.current_mode
        return "default" if None is mode else mode

    @mode_current.setter
    def mode_current(self, value):
        """Set current mode."""
        self.cfg_modes.current_mode = value

    def _mode_next(self, next_mode: str = None) -> Tuple[ Union[str,None], Union[str,None] ] :
        """Switch to the next mode in the list (for keyboard shortcut)."""
        if not self.modes_enabled or len(self.modes_all) <= 1:
            return None, None

        if next_mode is None:
            current_index = self.modes_all.index(self.mode_current)
            next_index = (current_index + 1) % len(self.modes_all)
            next_mode = self.modes_all[next_index]

        # Switch mode silently (no UI feedback here, handled by input function)
        old_mode = self.mode_current
        self.mode_current = next_mode

        return old_mode, next_mode

    @property
    def mode_switch_message(self):
        """Get tools for current mode."""
        return self.cfg_modes.mode_switch_messages_by_mode.get(self.mode_current, None)

    #### llm
    @property
    def model_id(self):
        """Get model id"""
        return self.cfg_llm.model_id

    @property
    def system_prompt(self):
        """Get system prompt"""
        return self.cfg_llm.system_prompt

    @property
    def tools_current(self):
        """Get tools for current mode."""
        return self.cfg_modes.tools_by_mode.get(self.mode_current, [])

    @property
    def llm_history(self):
        return [msg.response_json for msg in self.llm_conversation.responses]

    def llm_history_store(self):
        self.llm_history_backup = self.llm_history

    def llm_history_restore(self):
        # Replay conversation history
        for msg in self.llm_history_backup:
            if msg.get("role") == "user":
                content = msg.get("content", [])
                if content and isinstance(content, list) and content[0].get("type") == "text":
                    text = content[0].get("text", "")
                    if text:  # Only replay non-empty user messages
                        for _ in self.llm_conversation.chain(text, system=self.system_prompt):
                            pass  # Consume responses silently

        self.llm_history_backup = None

    def llm_exec_init(self):
        """Initialize the LLM model and conversation."""
        try:
            self.llm_model = llm.get_model(self.model_id)
            self.llm_conversation = self.llm_model.conversation(tools=self.tools_current)
        except Exception as e:
            raise RuntimeError(f"Error loading model '{self.model_id}': {e}")

    def llm_exec_switch(self, next_mode: str = None) -> Union[str,None] :
        """Switch to the next mode in the list (for keyboard shortcut)."""

        old_mode, next_mode= self._mode_next(next_mode=next_mode)
        if next_mode is None:
            return None

        # Save conversation history before switching
        self.llm_history_store()

        # Switch mode silently (no UI feedback here, handled by input function)
        self.llm_exec_init()

        try:
            # Send mode switch message if configured
            if self.mode_switch_message:
                for _ in self.llm_conversation.chain(self.mode_switch_message, system=self.system_prompt):
                    pass  # Consume the response silently

            # Replay conversation history
            self.llm_history_restore()

        except Exception as e:
            raise RuntimeError(f"Error conversation '{self.model_id}': {e}")

        return next_mode