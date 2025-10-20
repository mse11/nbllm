from  typing import List, Any
from nbllm.chat_config import ConfigLlm, ConfigModes, ConfigMode

##################################################################################
################################ LLM #############################################
##################################################################################

def FactoryConfigLlmDefault(system_prompt: str) -> ConfigLlm:
    return ConfigLlm(
        system_prompt=system_prompt,
        model_id="nbllm_model", # see template_llm__extra-openai-models.yaml
        path_to_extra_openai_models="."
    )

##################################################################################
################################ MODES ###########################################
##################################################################################

def FactoryConfigModesToolsOnly(
        tools: List[Any],  # todo types
):
    return ConfigModes(
        current_mode=None,
        modes_cfg=[
            ConfigMode(
                mode="default",
                tools=tools,  # tools capabilities,
            ),
        ]
    )

def FactoryConfigModesDeveloper(
        mode_development_tools: List[Any],  # todo types
        mode_review_tools: List[Any]        # todo types
) -> ConfigModes:
    return ConfigModes(
        current_mode="development",
        modes_cfg=[
            ConfigMode(
                mode="development",
                tools=mode_development_tools,  # [file_tool, todo_tools] Full development capabilities,
                mode_switch_message="You are now in development mode. You can edit files and manage todos. Focus on implementing features and fixing bugs."
            ),
            ConfigMode(
                mode="review",
                tools=mode_review_tools,  # [file_tool]  Code review mode - can read files but no todo management
                mode_switch_message="You are now in review mode. You can read files to understand the codebase but cannot make changes. Focus on analyzing code and providing feedback."
            ),
            ConfigMode(
                mode="planning",
                tools=[],  # Planning mode - no tools, pure discussion
                mode_switch_message="You are now in planning mode. You cannot access files or tools. Focus on high-level discussion, architecture planning, and strategic thinking."
            ),
        ]
    )