from nbllm import Chat
from nbllm.prompts import socratic_prompt
from nbllm import ui


def set_voice():
    """Set a role for the assistant"""
    roles = ["technical teacher", "pirate", "twitter techbro"]
    role = ui.choice("What role should I take?", roles)
    return f"You are now acting as a {role}. Please respond in character but stick to the topic of teaching."


Chat(
    model_name="anthropic/claude-3-5-sonnet-20240620",
    tools=[],
    system_prompt=socratic_prompt,
    debug=False,
    slash_commands={
        "/voice": set_voice,
    },
    first_message="I can teach you anything about a technical topic. What would you like to learn?",
    show_banner=False
).run()
