from typing import Dict, Any

class ClickWrapperGenerator:
    """Generates Python wrapper code from Click CLI metadata."""

    # Type mapping from Click parameter types to Python types
    TYPE_MAPPING = {
        "argument": "str",
        "option": "str",
        "flag": "bool",
    }

    def __init__(self, metadata: Dict[str, Any]):
        """
        Initialize the generator with Click metadata.

        Args:
            metadata: Output from ClickInspector.all_click_metadata()
        """
        self.metadata = metadata
        self.generated_classes = []
        self.generated_methods = []

    @staticmethod
    def _to_python_name(name: str) -> str:
        """Convert CLI option name to Python identifier."""
        # Remove leading dashes
        name = name.lstrip('-')
        # Replace dashes with underscores
        name = name.replace('-', '_')
        # Handle reserved keywords
        if name in ('from', 'import', 'class', 'def', 'return', 'async'):
            name = f"{name}_"
        return name

    @staticmethod
    def _to_class_name(command_path: str) -> str:
        """Convert command path to PascalCase class name."""
        if not command_path:
            command_path = "main"
        parts = command_path.split()
        return ''.join(word.capitalize() for word in parts) + "Options"

    @staticmethod
    def _to_method_name(command_path: str) -> str:
        """Convert command path to snake_case method name."""
        if not command_path:
            return "execute"
        return command_path.replace(' ', '_').replace('-', '_')

    def _infer_python_type(self, param: Dict[str, Any]) -> str:
        """Infer Python type from Click parameter metadata."""
        param_type = param.get("param_type_name", "option")
        is_multiple = param.get("multiple", False)
        nargs = param.get("nargs", 1)
        default = param.get("default")

        # Handle flags (boolean options)
        if param_type == "flag" or (isinstance(default, bool) and not param.get("opts")):
            return "bool"

        # Determine base type
        if isinstance(default, int):
            base_type = "int"
        elif isinstance(default, float):
            base_type = "float"
        elif isinstance(default, list):
            base_type = "List[str]"
        elif isinstance(default, dict):
            base_type = "Dict[str, str]"
        elif isinstance(default, tuple) and len(default) == 2:
            # Likely a tuple type like (str, str)
            base_type = "List[Tuple[str, str]]"
        else:
            base_type = "str"

        # Handle multiple values
        if is_multiple or nargs == -1:
            if base_type == "str":
                base_type = "List[str]"
            elif base_type not in ("List[str]", "Dict[str, str]", "List[Tuple[str, str]]"):
                base_type = f"List[{base_type}]"

        # Make optional if not required
        if not param.get("required", False):
            return f"Optional[{base_type}]"

        return base_type

    def _get_default_value(self, param: Dict[str, Any]) -> str:
        """Get the default value representation for a parameter."""
        default = param.get("default")
        python_type = self._infer_python_type(param)

        if default is None:
            return "None"
        elif isinstance(default, bool):
            return str(default)
        elif isinstance(default, (int, float)):
            return str(default)
        elif isinstance(default, str):
            return f'"{default}"'
        elif isinstance(default, list):
            return "None" if not default else f"field(default_factory=lambda: {default})"
        elif isinstance(default, dict):
            return "None" if not default else f"field(default_factory=lambda: {default})"
        else:
            return "None"

    def _generate_options_class(self, command_path: str, command_meta: Dict[str, Any]) -> str:
        """Generate a dataclass for command options."""
        class_name = self._to_class_name(command_path)
        command_name = command_path if command_path else "main command"

        lines = [
            f"@dataclass",
            f"class {class_name}:",
            f'    """Options for the {command_name}"""',
            ""
        ]

        # Process parameters
        params = command_meta.get("params", [])
        if not params:
            lines.append("    pass")
        else:
            for param in params:
                param_name = self._to_python_name(param["name"])
                param_type = self._infer_python_type(param)
                default_value = self._get_default_value(param)
                help_text = param.get("help", "")

                # Add field with type and default
                lines.append(f"    {param_name}: {param_type} = {default_value}")

                # Add docstring if help text exists
                if help_text:
                    lines.append(f'    """{help_text}"""')
                lines.append("")

        return "\n".join(lines)

    def _generate_wrapper_method(self, command_path: str, command_meta: Dict[str, Any]) -> str:
        """Generate a wrapper method for a command."""
        method_name = self._to_method_name(command_path)
        class_name = self._to_class_name(command_path)
        command_name = command_path if command_path else "main"
        help_text = command_meta.get("help", "")

        # Build method signature
        lines = [
            f"    def {method_name}(self, options: {class_name}) -> str:",
            f'        """'
        ]

        if help_text:
            lines.append(f"        {help_text}")
            lines.append("")

        lines.extend([
            f"        Args:",
            f"            options: {class_name} dataclass with all configuration",
            "",
            f"        Returns:",
            f"            Command output as a string",
            "",
            f"        Raises:",
            f"            ClickWrapperError: If the command execution fails",
            f'        """',
            f"        args = [{repr(command_name)}]" if command_path else "        args = []",
            ""
        ])

        # Generate argument building logic
        params = command_meta.get("params", [])
        for param in params:
            param_name = self._to_python_name(param["name"])
            param_type_name = param.get("param_type_name", "option")
            opts = param.get("opts", [])
            is_flag = param.get("param_type_name") == "flag" or isinstance(param.get("default"), bool)
            is_multiple = param.get("multiple", False)

            # Get primary option name
            opt_name = opts[0] if opts else f"--{param['name']}"

            if param_type_name == "argument":
                # Positional argument
                lines.append(f"        if options.{param_name}:")
                if is_multiple:
                    lines.append(f"            args.extend(options.{param_name})")
                else:
                    lines.append(f"            args.append(options.{param_name})")
            elif is_flag:
                # Boolean flag
                lines.append(f"        if options.{param_name}:")
                lines.append(f"            args.append('{opt_name}')")
            elif is_multiple or param.get("nargs") == -1:
                # Multiple values
                lines.append(f"        if options.{param_name}:")
                lines.append(f"            for value in options.{param_name}:")
                # Check if it's a tuple (like attachment_types)
                if "Tuple" in self._infer_python_type(param):
                    lines.append(f"                args.extend(['{opt_name}', *value])")
                else:
                    lines.append(f"                args.extend(['{opt_name}', value])")
            elif isinstance(param.get("default"), dict):
                # Dictionary type (key-value pairs)
                lines.append(f"        if options.{param_name}:")
                lines.append(f"            for key, value in options.{param_name}.items():")
                lines.append(f"                args.extend(['{opt_name}', key, value])")
            else:
                # Single value option
                if param.get("default") is not None and not isinstance(param.get("default"), bool):
                    # Has a non-boolean default, check if different from default
                    default_val = param.get("default")
                    lines.append(f"        if options.{param_name} != {repr(default_val)}:")
                else:
                    lines.append(f"        if options.{param_name} is not None:")
                lines.append(f"            args.extend(['{opt_name}', str(options.{param_name})])")

            lines.append("")

        lines.append("        return self._run_command(args)")
        lines.append("")

        return "\n".join(lines)

    def generate_wrapper_class(self,
                               wrapper_class_name: str = "ClickWrapper",
                               cli_module: str = "cli",
                               cli_function: str = "cli") -> str:
        """
        Generate complete wrapper class code.

        Args:
            wrapper_class_name: Name for the generated wrapper class
            cli_module: Module path to the CLI (e.g., "myapp.cli")
            cli_function: Name of the Click CLI function/group

        Returns:
            Complete Python source code for the wrapper
        """
        code_parts = [
            '"""',
            f'Auto-generated wrapper for Click CLI application.',
            'Generated by ClickWrapperGenerator.',
            '"""',
            '',
            'from dataclasses import dataclass, field',
            'from typing import Optional, List, Dict, Tuple, Any',
            'from click.testing import CliRunner',
            f'import {cli_module}',
            '',
            '',
            'class ClickWrapperError(Exception):',
            '    """Exception raised when CLI command fails."""',
            '    pass',
            '',
            ''
        ]

        # Generate all options dataclasses
        for command_path, command_meta in self.metadata.get("metadata", {}).items():
            options_class = self._generate_options_class(command_path, command_meta)
            code_parts.append(options_class)
            code_parts.append("")

        # Generate wrapper class
        code_parts.extend([
            f'class {wrapper_class_name}:',
            f'    """',
            f'    Wrapper for CLI operations using Click\'s CliRunner.',
            f'    ',
            f'    This wrapper provides a Pythonic interface to the CLI tool,',
            f'    allowing you to execute commands programmatically.',
            f'    """',
            '',
            '    def __init__(self, **default_options):',
            '        """',
            '        Initialize the wrapper.',
            '        ',
            '        Args:',
            '            **default_options: Default options to apply to all commands',
            '        """',
            '        self.runner = CliRunner()',
            '        self.default_options = default_options',
            '',
            '    def _run_command(self, args: List[str], input: Optional[str] = None) -> str:',
            '        """',
            '        Run a CLI command and return the result.',
            '        ',
            '        Args:',
            '            args: List of command arguments',
            '            input: Optional stdin input',
            '        ',
            '        Returns:',
            '            Result output (stripped of trailing whitespace)',
            '        ',
            '        Raises:',
            '            ClickWrapperError: If command fails (non-zero exit code)',
            '        """',
            f'        result = self.runner.invoke({cli_module}.{cli_function}, args, input=input)',
            '',
            '        if result.exit_code != 0:',
            '            raise ClickWrapperError(f"Command failed: {result.output}")',
            '',
            '        return result.output.strip()',
            '',
        ])

        # Generate all wrapper methods
        for command_path, command_meta in self.metadata.get("metadata", {}).items():
            method = self._generate_wrapper_method(command_path, command_meta)
            code_parts.append(method)

        return "\n".join(code_parts)
