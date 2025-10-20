# import importlib
#
# def _import_from_string(import_path, global_altribute=None):
#     # import_from_string("llm.cli","cli")) IS EQUIVALENT 'from llm.cli import cli'
#     module = importlib.import_module(import_path)
#     return  getattr(module, global_altribute) if global_altribute else module
#
# def _doc_getter_click(import_path, global_altribute = None):
#     "Return all help for Click command and its subcommands"
#
#     try:
#         from click.testing import CliRunner
#
#         cli = _import_from_string(import_path, global_altribute)
#
#         # First find all commands and subcommands
#         # List will be [["command"], ["command", "subcommand"], ...]
#         commands = []
#
#         def find_commands(command, path=None):
#             path = path or []
#             commands.append(path + [command.name])
#             if hasattr(command, 'commands'):
#                 for subcommand in command.commands.values():
#                     find_commands(subcommand, path + [command.name])
#
#         find_commands(cli)
#         # Remove first item of each list (it is 'cli')
#         commands = [command[1:] for command in commands]
#         # Now generate help for each one, with appropriate heading level
#         output = []
#         for command in commands:
#             heading_level = len(command) + 2
#             result = CliRunner().invoke(cli, command + ["--help"])
#             hyphenated = "-".join(command)
#             if hyphenated:
#                 hyphenated = "-" + hyphenated
#             output.append(f"\n(help{hyphenated})=")
#             output.append("#" * heading_level + " llm " + " ".join(command) + " --help")
#             output.append("```")
#             output.append(result.output.replace("Usage: cli", "Usage: llm").strip())
#             output.append("```")
#     except ImportError:
#         output = "Error on import "
#
#     return "\n".join(output)
#
#
# print(_doc_getter_click("llm.cli","cli"))

from nbllm import ConfigLlm

c = ConfigLlm(system_prompt="ako")
c.ensure_config()