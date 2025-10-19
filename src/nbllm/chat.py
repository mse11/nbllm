from typing import Optional, Callable
import uuid
import llm

from rich.console import Console
from rich.spinner import Spinner
from rich.live import Live
from rich.columns import Columns
from rich.text import Text

from nbllm import config
from nbllm import ui
from nbllm.chat_config import LlmConfig, ModesConfig

# Command result constants
COMMAND_QUIT = "QUIT"
COMMAND_HANDLED = "HANDLED"


def handle_quit():
    """Handle /quit command"""
    return COMMAND_QUIT


def handle_help(user_commands):
    """Handle /help command"""
    ui.print("[cyan]Built-in commands:[/cyan]")
    ui.print("  /quit   - Exit the application")
    ui.print("  /help   - Show this help message")
    ui.print("  /tools  - Show available tools")
    ui.print("  /debug  - Toggle debug mode")

    if user_commands:
        ui.print("")
        ui.print("[cyan]Custom commands:[/cyan]")
        for cmd_name, cmd_handler in user_commands.items():
            if callable(cmd_handler):
                desc = cmd_handler.__doc__ or "Custom function"
                ui.print(f"  {cmd_name}   - {desc}")
            else:
                preview = str(cmd_handler)[:50] + "..." if len(str(cmd_handler)) > 50 else str(cmd_handler)
                ui.print(f"  {cmd_name}   - {preview}")

    ui.print("")
    return COMMAND_HANDLED


def handle_tools(tools):
    """Handle /tools command"""
    if tools:
        ui.print("[cyan]Available tools:[/cyan]")
        for tool in tools:
            tool_name = getattr(tool, 'tool_name', type(tool).__name__)
            ui.print(f"  {tool_name}")
    else:
        ui.print("[dim]No tools configured[/dim]")
    ui.print("")
    return COMMAND_HANDLED


def toggle_debug():
    """Toggle debug mode on/off"""
    config.DEBUG_MODE = not config.DEBUG_MODE
    status = "enabled" if config.DEBUG_MODE else "disabled"
    ui.print(f"[magenta]Debug mode {status}[/magenta]")
    ui.print("")
    return COMMAND_HANDLED


def handle_user_command(command, handler):
    """Handle user-defined command"""
    try:
        if callable(handler):
            result = handler()
            if result:
                if isinstance(result, str):
                    # If it looks like a message for the LLM, send it
                    if not result.startswith("[") and not result.endswith("]"):
                        return result  # Treat as LLM input
                    else:
                        # Treat as UI message
                        ui.print(result)
                        ui.print("")
                        return COMMAND_HANDLED
                else:
                    ui.print(str(result))
                    ui.print("")
                    return COMMAND_HANDLED
            else:
                return COMMAND_HANDLED
        else:
            # String - send directly to LLM
            return str(handler)
    except Exception as e:
        ui.print(f"[red]Error executing command {command}: {e}[/red]")
        ui.print("")
        return COMMAND_HANDLED


def dispatch_slash_command(command, user_commands, model, tools, conversation):
    """Dispatch slash command to appropriate handler"""
    if command == "/quit":
        return handle_quit(), conversation
    elif command == "/help":
        return handle_help(user_commands), conversation
    elif command == "/tools":
        return handle_tools(tools), conversation
    elif command == "/debug":
        return toggle_debug(), conversation
    elif command in user_commands:
        return handle_user_command(command, user_commands[command]), conversation
    else:
        ui.print(f"[red]Unknown command: {command}[/red]")
        ui.print("[dim]Type /help for available commands[/dim]")
        ui.print("")
        return COMMAND_HANDLED, conversation


class Chat:
    """Chat session manager with support for configurable modes."""

    def __init__(
            self,
            cfg_llm: LlmConfig,
            cfg_modes: ModesConfig,
            debug: bool = False,
            slash_commands: dict = None,
            history_callback: Optional[Callable] = None,
            first_message: Optional[str] = None,
            show_banner: bool = True,
    ):
        """Initialize chat session.

        Args:
            debug: Enable debug mode
            slash_commands: User-defined slash commands
            history_callback: Callback for conversation history
            first_message: Initial message to display
            show_banner: Whether to show banner
        """
        self.debug = debug
        self.model_name = cfg_llm.model_id
        self.system_prompt = cfg_llm.system_prompt
        self.slash_commands = slash_commands or {}
        self.history_callback = history_callback
        self.first_message = first_message
        self.show_banner = show_banner
        self.current_mode = cfg_modes.initial_mode
        self.mode_switch_messages = cfg_modes.mode_switch_message_to_dict()
        self.conversation_history = []

        tools = cfg_modes.mode_tools_to_dict()
        self.mode_tools = tools
        self.available_modes = list(tools.keys())

        # Initialize model and conversation
        self.model = None
        self.conversation = None
        self._initialize_model()

    def _initialize_model(self):
        """Initialize the LLM model and conversation."""
        try:
            self.model = llm.get_model(self.model_name)
        except Exception as e:
            ui.print(f"[red]Error loading model '{self.model_name}': {e}[/red]")
            raise typer.Exit(1)

        current_tools = self._get_current_tools()
        self.conversation = self.model.conversation(tools=current_tools)

    def _get_current_tools(self):
        """Get tools for current mode."""
        if self.current_mode is None:
            return self.mode_tools.get("default", [])
        return self.mode_tools.get(self.current_mode, [])

    def _is_modes_enabled(self) -> bool:
        """Check if modes are configured."""
        return self.current_mode is not None

    def get_available_modes(self) -> list:
        """Return list of available modes."""
        return self.available_modes.copy() if self._is_modes_enabled() else []

    def switch_to_next_mode(self) -> str:
        """Switch to the next mode in the list (for keyboard shortcut)."""
        if not self._is_modes_enabled() or len(self.available_modes) <= 1:
            return None

        current_index = self.available_modes.index(self.current_mode)
        next_index = (current_index + 1) % len(self.available_modes)
        next_mode = self.available_modes[next_index]

        # Save conversation history before switching
        self.conversation_history = [msg.response_json for msg in self.conversation.responses]

        # Switch mode silently (no UI feedback here, handled by input function)
        old_mode = self.current_mode
        self.current_mode = next_mode
        self._initialize_model()

        # Send mode switch message if configured
        if next_mode in self.mode_switch_messages:
            switch_message = self.mode_switch_messages[next_mode]
            for _ in self.conversation.chain(switch_message, system=self.system_prompt):
                pass  # Consume the response silently

        # Replay conversation history
        for msg in self.conversation_history:
            if msg.get("role") == "user":
                content = msg.get("content", [])
                if content and isinstance(content, list) and content[0].get("type") == "text":
                    text = content[0].get("text", "")
                    if text:  # Only replay non-empty user messages
                        for _ in self.conversation.chain(text, system=self.system_prompt):
                            pass  # Consume responses silently

        return next_mode

    def switch_mode(self, new_mode: str):
        """Switch to a different mode."""
        if not self._is_modes_enabled():
            ui.print("[red]Modes are not configured for this session[/red]")
            return False

        if new_mode not in self.available_modes:
            ui.print(f"[red]Unknown mode: {new_mode}[/red]")
            ui.print(f"[dim]Available modes: {', '.join(self.available_modes)}[/dim]")
            return False

        if new_mode == self.current_mode:
            ui.print(f"[dim]Already in {new_mode} mode[/dim]")
            return True

        # Save conversation history
        self.conversation_history = [msg.response_json for msg in self.conversation.responses]

        # Switch mode and reinitialize
        old_mode = self.current_mode
        self.current_mode = new_mode
        self._initialize_model()

        # Send mode switch message if configured
        if new_mode in self.mode_switch_messages:
            switch_message = self.mode_switch_messages[new_mode]
            # Send the switch message to establish new mode context
            for _ in self.conversation.chain(switch_message, system=self.system_prompt):
                pass  # Consume the response silently

        # Replay conversation history
        for msg in self.conversation_history:
            if msg.get("role") == "user":
                content = msg.get("content", [])
                if content and isinstance(content, list) and content[0].get("type") == "text":
                    text = content[0].get("text", "")
                    if text:  # Only replay non-empty user messages
                        for _ in self.conversation.chain(text, system=self.system_prompt):
                            pass  # Consume responses silently

        ui.print(f"[green]Switched from {old_mode} to {new_mode} mode[/green]")
        ui.print("")
        return True

    def run(self):
        """Main chat loop."""
        # Set debug mode globally
        config.DEBUG_MODE = self.debug

        # Initialize user slash commands
        user_commands = self.slash_commands.copy()

        console = Console()

        # Show the banner
        if self.show_banner:
            ui.show_banner()

        if self.first_message:
            ui.print(self.first_message)
            ui.print("")

        if self.debug:
            ui.print("[magenta]Debug mode enabled[/magenta]")
            ui.print("")

        history = []
        try:
            while True:
                # Define available commands for completion (builtin + user commands + mode commands)
                builtin_commands = ["/quit", "/help", "/tools", "/debug"]
                if self._is_modes_enabled():
                    builtin_commands.extend(["/mode", "/modes"])

                user_command_names = list(user_commands.keys())
                completions = builtin_commands + user_command_names

                # Show completion hint on first prompt
                if not hasattr(self, '_shown_completion_hint'):
                    tip_text = "[dim]Tips: TAB for completions • @file.py for file paths • ↑/↓ for history • Ctrl+U to clear"
                    if self._is_modes_enabled() and len(self.available_modes) > 1:
                        tip_text += " • Shift+TAB to switch modes"
                    tip_text += "[/dim]"
                    ui.print(tip_text)
                    self._shown_completion_hint = True

                # Create mode-aware prompt
                if self._is_modes_enabled():
                    prompt = f"[{self.current_mode}] > "
                else:
                    prompt = "> "

                # Prepare mode switching for keyboard shortcut
                mode_switcher = self.switch_to_next_mode if self._is_modes_enabled() else None
                available_modes = self.get_available_modes() if self._is_modes_enabled() else None

                out = ui.input(
                    prompt,
                    completions=completions,
                    mode_switcher_callback=mode_switcher,
                    available_modes=available_modes
                ).strip()

                # Handle slash commands (only if it's a known command)
                if out.startswith("/"):
                    # Parse command and arguments
                    parts = out.split(None, 1)  # Split at most once to preserve spaces in args
                    command = parts[0] if parts else out
                    args = parts[1] if len(parts) > 1 else ""

                    # Check if it's a known command
                    if command in builtin_commands or command in user_commands:
                        result, self.conversation = self._dispatch_slash_command(command, args, user_commands)

                        if result == COMMAND_QUIT:
                            break
                        elif result == COMMAND_HANDLED:
                            continue
                        else:
                            # Command returned text for LLM
                            out = result
                    # If it starts with / but isn't a known command, treat as regular text

                # Skip empty input
                if not out.strip():
                    continue

                # Show spinner while getting initial response
                # Create a padded spinner
                spinner_text = Text("Thinking...", style="dim")
                padded_spinner = Columns([Text(" " * ui.LEFT_PADDING), Spinner("dots"), spinner_text], expand=False)
                response_started = False

                with Live(padded_spinner, console=console, refresh_per_second=10, transient=True) as live:
                    if self.history_callback:
                        new_id = str(uuid.uuid4()).replace("-", "")[:24]
                        self.history_callback(
                            [{"id": f"msg_{new_id}", "role": "user", "content": [{"text": out, "type": "text"}]}])
                    for chunk in self.conversation.chain(out, system=self.system_prompt):
                        if not response_started:
                            # First chunk received, clear and stop the spinner so it disappears
                            try:
                                live.update(Text(""), refresh=True)
                            except Exception:
                                pass
                            live.stop()
                            response_started = True
                            # Initialize streaming state
                            ui.start_streaming(ui.LEFT_PADDING)

                        # Stream each chunk as it arrives
                        ui.stream_chunk(chunk, ui.LEFT_PADDING)

                    # Finish streaming and print any remaining text
                    if response_started:
                        ui.end_streaming(ui.LEFT_PADDING)
                    ids = set([e["id"] for e in history])
                    new_responses = [e for e in self.conversation.responses if e.response_json["id"] not in ids]
                    if self.history_callback:
                        self.history_callback([e.response_json for e in new_responses])

                ui.print("")  # Add extra newline after bot response
        except KeyboardInterrupt:
            ui.print("")  # Add newlines
            ui.print("[cyan]Thanks for using nbllm. Goodbye![/cyan]")
            ui.print("")  # Add final newline

    def _dispatch_slash_command(self, command, args, user_commands):
        """Dispatch slash command to appropriate handler."""
        if command == "/quit":
            return handle_quit(), self.conversation
        elif command == "/help":
            return self._handle_help(user_commands), self.conversation
        elif command == "/tools":
            return self._handle_tools(), self.conversation
        elif command == "/debug":
            return toggle_debug(), self.conversation
        elif command == "/mode":
            return self._handle_mode_command(args), self.conversation
        elif command == "/modes":
            return self._handle_modes_command(), self.conversation
        elif command in user_commands:
            return handle_user_command(command, user_commands[command]), self.conversation
        else:
            ui.print(f"[red]Unknown command: {command}[/red]")
            ui.print("[dim]Type /help for available commands[/dim]")
            ui.print("")
            return COMMAND_HANDLED, self.conversation

    def _handle_help(self, user_commands):
        """Handle /help command with mode awareness."""
        ui.print("[cyan]Built-in commands:[/cyan]")
        ui.print("  /quit   - Exit the application")
        ui.print("  /help   - Show this help message")
        ui.print("  /tools  - Show available tools")
        ui.print("  /debug  - Toggle debug mode")

        if self._is_modes_enabled():
            ui.print("  /mode   - Switch mode interactively or /mode <mode_name>")
            ui.print("  /modes  - List available modes")
            if len(self.available_modes) > 1:
                ui.print("  [dim]Shift+TAB - Quick switch to next mode[/dim]")

        if user_commands:
            ui.print("")
            ui.print("[cyan]Custom commands:[/cyan]")
            for cmd_name, cmd_handler in user_commands.items():
                if callable(cmd_handler):
                    desc = cmd_handler.__doc__ or "Custom function"
                    ui.print(f"  {cmd_name}   - {desc}")
                else:
                    preview = str(cmd_handler)[:50] + "..." if len(str(cmd_handler)) > 50 else str(cmd_handler)
                    ui.print(f"  {cmd_name}   - {preview}")

        ui.print("")
        return COMMAND_HANDLED

    def _handle_tools(self):
        """Handle /tools command with mode awareness."""
        current_tools = self._get_current_tools()

        if self._is_modes_enabled():
            ui.print(f"[cyan]Available tools in {self.current_mode} mode:[/cyan]")
        else:
            ui.print("[cyan]Available tools:[/cyan]")

        if current_tools:
            for tool in current_tools:
                tool_name = getattr(tool, 'tool_name', type(tool).__name__)
                ui.print(f"  {tool_name}")
        else:
            ui.print("[dim]No tools configured[/dim]")
        ui.print("")
        return COMMAND_HANDLED

    def _handle_mode_command(self, args=""):
        """Handle /mode command."""
        if not self._is_modes_enabled():
            ui.print("[red]Modes are not configured for this session[/red]")
            ui.print("")
            return COMMAND_HANDLED

        if not args.strip():
            # No mode specified, show interactive picker
            try:
                # Create choices with current mode indicator
                choices = []
                for mode in self.available_modes:
                    if mode == self.current_mode:
                        choices.append(f"{mode} (current)")
                    else:
                        choices.append(mode)

                selected = ui.choice("Select mode:", choices)
                if selected:
                    # Extract mode name (remove " (current)" if present)
                    target_mode = selected.replace(" (current)", "")
                    if target_mode != self.current_mode:
                        self.switch_mode(target_mode)
                    else:
                        ui.print(f"[dim]Already in {target_mode} mode[/dim]")
                        ui.print("")
            except KeyboardInterrupt:
                ui.print("[dim]Mode selection cancelled[/dim]")
                ui.print("")
            return COMMAND_HANDLED

        # Switch to the specified mode
        target_mode = args.strip()
        self.switch_mode(target_mode)
        return COMMAND_HANDLED

    def _handle_modes_command(self):
        """Handle /modes command."""
        if not self._is_modes_enabled():
            ui.print("[red]Modes are not configured for this session[/red]")
            ui.print("")
            return COMMAND_HANDLED

        ui.print("[cyan]Available modes:[/cyan]")
        for mode in self.available_modes:
            if mode == self.current_mode:
                ui.print(f"  {mode} [green](current)[/green]")
            else:
                ui.print(f"  {mode}")
        ui.print("")
        return COMMAND_HANDLED