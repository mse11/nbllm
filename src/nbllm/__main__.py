from typing import Optional, Callable

import typer
from dotenv import load_dotenv


load_dotenv(".env")


def chat(
    debug: bool = typer.Option(False, "--debug", "-d", help="Enable debug mode to see LLM interactions"),
    model_name: str = typer.Option("anthropic/claude-3-5-sonnet-20240620", "--model", "-m", help="LLM model to use"), # see template_llm__extra-openai-models.yaml
    system_prompt: Optional[str] = typer.Option(None, "--system", "-s", help="System prompt for the assistant"),
    tools: list = None,
    slash_commands: dict = None,
    history_callback: Optional[Callable] = None,
    first_message: Optional[str] = None,
    show_banner: bool = True,
):
    """Run the nbllm chat assistant."""
    chat_instance = Chat(
        debug=debug,
        model_name=model_name,
        system_prompt=system_prompt,
        tools=tools,
        slash_commands=slash_commands,
        history_callback=history_callback,
        first_message=first_message,
        show_banner=show_banner,
    )
    chat_instance.run()


def main():
    """Main entry point for the nbllm CLI."""
    typer.run(chat)


if __name__ == "__main__":
    main()
