import json
import importlib

from typing import Union
from click.testing import CliRunner

class ClickInspector:

    @staticmethod
    def import_from_string(module_import_path, module_global_attribute = None):
        # import_from_string("llm.cli","cli")) IS EQUIVALENT 'from llm.cli import cli'
        module = importlib.import_module(module_import_path)
        return  getattr(module, module_global_attribute) if module_global_attribute else module

    @staticmethod
    def _safe_serialize(value):
        """Safely serialize Click objects and sentinels to JSON-friendly values."""
        if isinstance(value, (str, int, float, bool)) or value is None:
            return value
        if isinstance(value, (list, tuple, set)):
            return [ClickInspector._safe_serialize(v) for v in value]
        if isinstance(value, dict):
            return {k: ClickInspector._safe_serialize(v) for k, v in value.items()}
        # Fallback: return string representation
        return str(value)

    @staticmethod
    def _command_metadata(command):
        """Extract metadata from a Click command, safely serialized."""
        meta = {
            "name": command.name,
            "help": command.help or "",
            "short_help": command.short_help or "",
            "params": [],
        }
        for param in command.params:
            param_info = {
                "name": param.name,
                "param_type_name": param.param_type_name,
                "opts": getattr(param, "opts", []),
                "secondary_opts": getattr(param, "secondary_opts", []),
                "required": getattr(param, "required", False),
                "default": ClickInspector._safe_serialize(getattr(param, "default", None)),
                "nargs": getattr(param, "nargs", 1),
                "multiple": getattr(param, "multiple", False),
                "help": getattr(param, "help", ""),
            }
            meta["params"].append(param_info)
        if hasattr(command, "commands"):
            meta["subcommands"] = {
                name: ClickInspector._command_metadata(subcmd)
                for name, subcmd in command.commands.items()
            }
        return meta

    @staticmethod
    def all_click_metadata(click_cli_main):
        """Traverse Click command tree and return metadata and help dumps."""
        commands = []

        def find_commands(command, path=None):
            path = path or []
            commands.append((path + [command.name], command))
            if hasattr(command, "commands"):
                for subcommand in command.commands.values():
                    find_commands(subcommand, path + [command.name])

        find_commands(click_cli_main)

        data = {"metadata": {}, "help_texts": {}}

        for path, command in commands:
            cmd_path = " ".join(path[1:]) if len(path) > 1 else ""
            data["metadata"][cmd_path or "llm"] = ClickInspector._command_metadata(command)

            # Capture help text via CliRunner
            result = CliRunner().invoke(click_cli_main, path[1:] + ["--help"])
            data["help_texts"][cmd_path or "llm"] = result.output.replace("Usage: cli", "Usage: llm").strip()

        return data

    @staticmethod
    def all_help(click_cli_main):
        "Return all help for Click command and its subcommands"
        # First find all commands and subcommands
        # List will be [["command"], ["command", "subcommand"], ...]
        commands = []
        def find_commands(command, path=None):
            path = path or []
            commands.append(path + [command.name])
            if hasattr(command, 'commands'):
                for subcommand in command.commands.values():
                    find_commands(subcommand, path + [command.name])
        find_commands(click_cli_main)
        # Remove first item of each list (it is 'cli')
        commands = [command[1:] for command in commands]
        # Now generate help for each one, with appropriate heading level
        output = []
        for command in commands:
            heading_level = len(command) + 2
            result = CliRunner().invoke(click_cli_main, command + ["--help"])
            hyphenated = "-".join(command)
            if hyphenated:
                hyphenated = "-" + hyphenated
            output.append(f"\n(help{hyphenated})=")
            output.append("#" * heading_level + " llm " + " ".join(command) + " --help")
            output.append("```")
            output.append(result.output.replace("Usage: cli", "Usage: llm").strip())
            output.append("```")
        return "\n".join(output)

    @staticmethod
    def dump_with_llm_prompt(metadata: Union[str, dict], is_pretty = False) -> str:
        prompt = '''

I have pyhon click cli application of specific python package.  
As I know clip decorated functions cannot be directly called via python, 
I want to create some python wrapper mimic "Click-native" approach via CliRunner

See example of wrapper class

@dataclass
class ModelsListOptions:
    """Options for models list command"""

    options: bool = False
    """Show options for each model, if available"""

    async_mode: bool = False
    """List async models"""

    schemas: bool = False
    """List models that support schemas"""

    tools: bool = False
    """List models that support tools"""

    queries: Optional[List[str]] = None
    """Search for models matching these strings"""

    model_ids: Optional[List[str]] = None
    """Specific model IDs to list"""

class LLMWrapper:
    """
    Wrapper for Click CLI operations using Click's CliRunner.

    This wrapper provides a Pythonic interface to the Click command-line tool,
    allowing you to execute CLI commands programmatically without subprocess overhead.
    """

    def __init__(self, database: Optional[str] = None):
        """
        Initialize the LLM wrapper.

        Args:
            database: Optional path to logs database. If provided, will be used
                     as default for all commands that accept a database path.
        """
        self.runner = CliRunner()
        self.cli_main_function_obj = cli

    def _run_command(self, args: List[str], input: Optional[str] = None) -> Any:
        """
        Run a CLI command and return the result.

        Args:
            args: List of command arguments
            input: Optional stdin input

        Returns:
            Result output (stripped of trailing whitespace)

        Raises:
            WrapperError: If command fails (non-zero exit code)
        """
        result = self.runner.invoke(self.cli_main_function_obj, args, input=input)

        if result.exit_code != 0:
            raise LLMError(f"Command failed: {result.output}")

        return result.output.strip()
        
    # ========== MODELS COMMAND ==========

    def models_list(self, options: Optional[ModelsListOptions] = None) -> str:
        """
        List available models.

        Shows all available models from installed plugins, with optional filtering
        and detailed information about model capabilities and options.

        Args:
            options: ModelsListOptions dataclass (uses defaults if None)

        Returns:
            Formatted list of models

        Example:
            # List all models with options
            opts = ModelsListOptions(options=True, schemas=True)
            models = wrapper.models_list(opts)

            # Search for GPT-4 models
            opts = ModelsListOptions(queries=["gpt-4"])
            models = wrapper.models_list(opts)
        """
        if options is None:
            options = ModelsListOptions()

        args = ['models', 'list']

        if options.options:
            args.append('--options')
        if options.async_mode:
            args.append('--async')
        if options.schemas:
            args.append('--schemas')
        if options.tools:
            args.append('--tools')

        if options.queries:
            for query in options.queries:
                args.extend(['-q', query])

        if options.model_ids:
            for model_id in options.model_ids:
                args.extend(['-m', model_id])

        return self._run_command(args)

IMPORTANT: Instead kwargs use dataclass as options configuration object e.g. 'LogsListOptions(count=5, json_output=True)' 
IMPORTANT: each argument of command has some documentation string and some metadata so use it for dataclass members docstrings
IMPORTANT: Double check if all commands are implemented
    
Here is dump of cli structure in json:
'''.strip()

        return f"{prompt}\n\n{json.dumps(metadata, indent= 2 if is_pretty else None, ensure_ascii=False)}"

if __name__ == "__main__":
    from llm.cli import cli

    is_all = True
    if is_all:
        print(ClickInspector.dump_with_llm_prompt(
            ClickInspector.all_click_metadata(cli),
            is_pretty=True
        ))
    else:
        print(ClickInspector.all_help(cli))