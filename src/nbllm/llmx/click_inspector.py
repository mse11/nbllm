import json
from click.testing import CliRunner

class ClickInspector:

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
    def all_click_metadata(cli):
        """Traverse Click command tree and return metadata and help dumps."""
        commands = []

        def find_commands(command, path=None):
            path = path or []
            commands.append((path + [command.name], command))
            if hasattr(command, "commands"):
                for subcommand in command.commands.values():
                    find_commands(subcommand, path + [command.name])

        find_commands(cli)

        data = {"metadata": {}, "help_texts": {}}

        for path, command in commands:
            cmd_path = " ".join(path[1:]) if len(path) > 1 else ""
            data["metadata"][cmd_path or "llm"] = ClickInspector._command_metadata(command)

            # Capture help text via CliRunner
            result = CliRunner().invoke(cli, path[1:] + ["--help"])
            data["help_texts"][cmd_path or "llm"] = result.output.replace("Usage: cli", "Usage: llm").strip()

        return data

    @staticmethod
    def all_help(cli):
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
        find_commands(cli)
        # Remove first item of each list (it is 'cli')
        commands = [command[1:] for command in commands]
        # Now generate help for each one, with appropriate heading level
        output = []
        for command in commands:
            heading_level = len(command) + 2
            result = CliRunner().invoke(cli, command + ["--help"])
            hyphenated = "-".join(command)
            if hyphenated:
                hyphenated = "-" + hyphenated
            output.append(f"\n(help{hyphenated})=")
            output.append("#" * heading_level + " llm " + " ".join(command) + " --help")
            output.append("```")
            output.append(result.output.replace("Usage: cli", "Usage: llm").strip())
            output.append("```")
        return "\n".join(output)


if __name__ == "__main__":
    from llm.cli import cli

    is_all = False
    if is_all:
        metadata = ClickInspector.all_click_metadata(cli)
        print(json.dumps(metadata, indent=2, ensure_ascii=False))
    else:
        metadata = ClickInspector.all_help(cli)
        print(metadata)