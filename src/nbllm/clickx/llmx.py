"""
Comprehensive Python wrapper for the LLM CLI using CliRunner with dataclass-based parameters.

Usage:
    wrapper = LLMWrapper()
    options = PromptOptions(
        prompt="What is 2+2?",
        model="gpt-4o-mini",
        system="Be concise"
    )
    response = wrapper.prompt(options)
    print(response)
"""

from click.testing import CliRunner
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
import json
import llm.cli


class LLMError(Exception):
    """Base exception for LLM wrapper errors"""
    pass


@dataclass
class PromptOptions:
    """Options for the prompt command"""

    prompt: Optional[str] = None
    """The prompt text to execute"""

    system: Optional[str] = None
    """System prompt to use"""

    model: Optional[str] = None
    """Model to use (e.g. 'gpt-4o-mini')"""

    database: Optional[str] = None
    """Path to log database"""

    queries: Optional[List[str]] = None
    """Use first model matching these strings"""

    attachments: Optional[List[str]] = None
    """Attachment path or URL or - (for stdin)"""

    attachment_types: Optional[List[Tuple[str, str]]] = None
    """List of (path, mimetype) tuples for attachments with explicit mimetype"""

    tools: Optional[List[str]] = None
    """Name of a tool to make available to the model"""

    functions: Optional[List[str]] = None
    """Python code block or file path defining functions to register as tools"""

    tools_debug: bool = False
    """Show full details of tool executions"""

    tools_approve: bool = False
    """Manually approve every tool execution"""

    chain_limit: int = 5
    """How many chained tool responses to allow, default 5, set 0 for unlimited"""

    options: Optional[Dict[str, str]] = None
    """key/value options for the model"""

    schema: Optional[str] = None
    """JSON schema, filepath or ID"""

    schema_multi: Optional[str] = None
    """JSON schema to use for multiple results"""

    fragments: Optional[List[str]] = None
    """Fragment (alias, URL, hash or file path) to add to the prompt"""

    system_fragments: Optional[List[str]] = None
    """Fragment to add to system prompt"""

    template: Optional[str] = None
    """Template to use"""

    params: Optional[Dict[str, str]] = None
    """Parameters for template"""

    no_stream: bool = False
    """Do not stream output"""

    no_log: bool = False
    """Don't log to database"""

    log: bool = False
    """Log prompt and response to the database"""

    continue_conversation: bool = False
    """Continue the most recent conversation"""

    conversation_id: Optional[str] = None
    """Continue the conversation with the given ID"""

    key: Optional[str] = None
    """API key to use"""

    save: Optional[str] = None
    """Save prompt with this template name"""

    async_mode: bool = False
    """Run prompt asynchronously"""

    usage: bool = False
    """Show token usage"""

    extract: bool = False
    """Extract first fenced code block"""

    extract_last: bool = False
    """Extract last fenced code block"""


@dataclass
class ChatOptions:
    """Options for the chat command"""

    system: Optional[str] = None
    """System prompt to use"""

    model: Optional[str] = None
    """Model to use"""

    continue_conversation: bool = False
    """Continue the most recent conversation"""

    conversation_id: Optional[str] = None
    """Continue the conversation with the given ID"""

    fragments: Optional[List[str]] = None
    """Fragment (alias, URL, hash or file path) to add to the prompt"""

    system_fragments: Optional[List[str]] = None
    """Fragment to add to system prompt"""

    template: Optional[str] = None
    """Template to use"""

    params: Optional[Dict[str, str]] = None
    """Parameters for template"""

    options: Optional[Dict[str, str]] = None
    """key/value options for the model"""

    database: Optional[str] = None
    """Path to log database"""

    no_stream: bool = False
    """Do not stream output"""

    key: Optional[str] = None
    """API key to use"""

    tools: Optional[List[str]] = None
    """Name of a tool to make available to the model"""

    functions: Optional[List[str]] = None
    """Python code block or file path defining functions to register as tools"""

    tools_debug: bool = False
    """Show full details of tool executions"""

    tools_approve: bool = False
    """Manually approve every tool execution"""

    chain_limit: int = 5
    """How many chained tool responses to allow, default 5, set 0 for unlimited"""


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


@dataclass
class LogsListOptions:
    """Options for logs list command"""

    count: Optional[int] = None
    """Number of entries to show - defaults to 3, use 0 for all"""

    database: Optional[str] = None
    """Path to log database"""

    model: Optional[str] = None
    """Filter by model or model alias"""

    query: Optional[str] = None
    """Search for logs matching this string"""

    fragments: Optional[List[str]] = None
    """Filter for prompts using these fragments"""

    tools: Optional[List[str]] = None
    """Filter for prompts with results from these tools"""

    any_tools: bool = False
    """Filter for prompts with results from any tools"""

    schema: Optional[str] = None
    """JSON schema, filepath or ID to filter by"""

    schema_multi: Optional[str] = None
    """JSON schema used for multiple results"""

    latest: bool = False
    """Return latest results matching search query"""

    data: bool = False
    """Output newline-delimited JSON data for schema"""

    data_array: bool = False
    """Output JSON array of data for schema"""

    data_key: Optional[str] = None
    """Return JSON objects from array in this key"""

    data_ids: bool = False
    """Attach corresponding IDs to JSON objects"""

    truncate: bool = False
    """Truncate long strings in output"""

    short: bool = False
    """Shorter YAML output with truncated prompts"""

    usage: bool = False
    """Include token usage"""

    response_only: bool = False
    """Just output the last response"""

    extract: bool = False
    """Extract first fenced code block"""

    extract_last: bool = False
    """Extract last fenced code block"""

    current_conversation: bool = False
    """Show logs from the current conversation"""

    conversation_id: Optional[str] = None
    """Show logs for this conversation ID"""

    id_gt: Optional[str] = None
    """Return responses with ID > this"""

    id_gte: Optional[str] = None
    """Return responses with ID >= this"""

    json_output: bool = False
    """Output logs as JSON"""

    expand: bool = False
    """Expand fragments to show their content"""


@dataclass
class EmbedOptions:
    """Options for embed command"""

    collection: Optional[str] = None
    """Collection name to store embedding in"""

    id: Optional[str] = None
    """ID for the embedding"""

    input_path: Optional[str] = None
    """File to embed"""

    model: Optional[str] = None
    """Embedding model to use"""

    store: bool = False
    """Store the text itself in the database"""

    database: Optional[str] = None
    """Path to embeddings database"""

    content: Optional[str] = None
    """Content to embed"""

    binary: bool = False
    """Treat input as binary data"""

    metadata: Optional[Dict] = None
    """JSON object metadata to store"""

    format: Optional[str] = None
    """Output format (json, blob, base64, hex)"""


@dataclass
class EmbedMultiOptions:
    """Options for embed-multi command"""

    collection: str
    """Collection name to store embeddings in"""

    input_path: Optional[str] = None
    """Path to input file (CSV, JSON, JSONL, TSV)"""

    format: Optional[str] = None
    """Format of input file - defaults to auto-detect (json, csv, tsv, nl)"""

    files: Optional[List[Tuple[str, str]]] = None
    """List of (directory, glob_pattern) tuples for embedding files"""

    encodings: Optional[List[str]] = None
    """Encodings to try when reading --files"""

    binary: bool = False
    """Treat --files as binary data"""

    sql: Optional[str] = None
    """Read input using this SQL query"""

    attach: Optional[List[Tuple[str, str]]] = None
    """Additional databases to attach - list of (alias, file_path) tuples"""

    batch_size: Optional[int] = None
    """Batch size to use when running embeddings"""

    prefix: str = ""
    """Prefix to add to the IDs"""

    model: Optional[str] = None
    """Embedding model to use"""

    prepend: Optional[str] = None
    """Prepend this string to all content before embedding"""

    store: bool = False
    """Store the text itself in the database"""

    database: Optional[str] = None
    """Path to embeddings database"""


@dataclass
class SimilarOptions:
    """Options for similar command"""

    collection: str
    """Collection name to search in"""

    id: Optional[str] = None
    """ID to find similar items for"""

    input_path: Optional[str] = None
    """File to embed for comparison"""

    content: Optional[str] = None
    """Content to embed for comparison"""

    binary: bool = False
    """Treat input as binary data"""

    number: int = 10
    """Number of results to return"""

    plain: bool = False
    """Output in plain text format"""

    database: Optional[str] = None
    """Path to embeddings database"""

    prefix: str = ""
    """Just IDs with this prefix"""


@dataclass
class ToolsListOptions:
    """Options for tools list command"""

    tool_defs: Optional[List[str]] = None
    """Specific tool names to show"""

    json_output: bool = False
    """Output as JSON"""

    functions: Optional[List[str]] = None
    """Python code block or file path defining functions to register as tools"""


@dataclass
class PluginsListOptions:
    """Options for plugins list command"""

    all_plugins: bool = False
    """Include built-in default plugins"""

    hooks: Optional[List[str]] = None
    """Filter for plugins that implement these hooks"""


@dataclass
class AliasesListOptions:
    """Options for aliases list command"""

    json_output: bool = False
    """Output as JSON"""


@dataclass
class AliasesSetOptions:
    """Options for aliases set command"""

    alias: str
    """Alias name to set"""

    model_id: Optional[str] = None
    """Model ID to alias (can use -q instead)"""

    queries: Optional[List[str]] = None
    """Set alias for model matching these strings"""


@dataclass
class FragmentsListOptions:
    """Options for fragments list command"""

    queries: Optional[List[str]] = None
    """Search for fragments matching these strings"""

    aliases: bool = False
    """Show only fragments with aliases"""

    json_output: bool = False
    """Output as JSON"""


@dataclass
class FragmentsSetOptions:
    """Options for fragments set command"""

    alias: str
    """Alias name for the fragment (must be alphanumeric)"""

    fragment: str
    """File path, URL, hash or '-' for stdin"""


@dataclass
class SchemasListOptions:
    """Options for schemas list command"""

    database: Optional[str] = None
    """Path to log database"""

    queries: Optional[List[str]] = None
    """Search for schemas matching this string"""

    full: bool = False
    """Output full schema contents"""

    json_output: bool = False
    """Output as JSON"""

    nl: bool = False
    """Output as newline-delimited JSON"""


@dataclass
class TemplatesListOptions:
    """Options for templates list command"""
    pass  # No options for this command


@dataclass
class CollectionsListOptions:
    """Options for collections list command"""

    database: Optional[str] = None
    """Path to embeddings database"""

    json_output: bool = False
    """Output as JSON"""


@dataclass
class EmbedModelsListOptions:
    """Options for embed-models list command"""

    queries: Optional[List[str]] = None
    """Search for embedding models matching these strings"""


class LLMWrapper:
    """
    Wrapper for LLM CLI operations using Click's CliRunner.

    This wrapper provides a Pythonic interface to the LLM command-line tool,
    allowing you to execute LLM commands programmatically without subprocess overhead.

    Example:
        wrapper = LLMWrapper()

        # Execute a prompt
        opts = PromptOptions(
            prompt="What is 2+2?",
            model="gpt-4o-mini"
        )
        response = wrapper.prompt(opts)

        # List models
        models = wrapper.models_list()

        # Check logs
        log_opts = LogsListOptions(count=5, json_output=True)
        logs = wrapper.logs_list(log_opts)
    """

    def __init__(self, database: Optional[str] = None):
        """
        Initialize the LLM wrapper.

        Args:
            database: Optional path to logs database. If provided, will be used
                     as default for all commands that accept a database path.
        """
        self.runner = CliRunner()
        self.database = database

    def _run_command(self, args: List[str], input: Optional[str] = None) -> Any:
        """
        Run a CLI command and return the result.

        Args:
            args: List of command arguments
            input: Optional stdin input

        Returns:
            Result output (stripped of trailing whitespace)

        Raises:
            LLMError: If command fails (non-zero exit code)
        """
        result = self.runner.invoke(llm.cli.cli, args, input=input)

        if result.exit_code != 0:
            raise LLMError(f"Command failed: {result.output}")

        return result.output.strip()

    # ========== PROMPT COMMAND ==========

    def prompt(self, options: PromptOptions) -> str:
        """
        Execute a prompt.

        This is the main command for executing prompts against language models.
        Supports attachments, tools, streaming, schemas, and more.

        Args:
            options: PromptOptions dataclass with all configuration

        Returns:
            The model's response as a string

        Raises:
            LLMError: If the prompt execution fails

        Example:
            opts = PromptOptions(
                prompt="What is 2+2?",
                model="gpt-4o-mini",
                system="Be concise"
            )
            response = wrapper.prompt(opts)
            print(response)
        """
        args = ['prompt']

        if options.prompt:
            args.append(options.prompt)

        if options.system:
            args.extend(['-s', options.system])
        if options.model:
            args.extend(['-m', options.model])
        if options.database or self.database:
            args.extend(['-d', options.database or self.database])

        if options.queries:
            for query in options.queries:
                args.extend(['-q', query])

        if options.attachments:
            for attachment in options.attachments:
                args.extend(['-a', attachment])

        if options.attachment_types:
            for path, mimetype in options.attachment_types:
                args.extend(['--at', path, mimetype])

        if options.tools:
            for tool in options.tools:
                args.extend(['-T', tool])

        if options.functions:
            for func in options.functions:
                args.extend(['--functions', func])

        if options.tools_debug:
            args.append('--td')
        if options.tools_approve:
            args.append('--ta')
        if options.chain_limit != 5:
            args.extend(['--cl', str(options.chain_limit)])

        if options.options:
            for key_name, value in options.options.items():
                args.extend(['-o', key_name, value])

        if options.schema:
            args.extend(['--schema', options.schema])
        if options.schema_multi:
            args.extend(['--schema-multi', options.schema_multi])

        if options.fragments:
            for fragment in options.fragments:
                args.extend(['-f', fragment])

        if options.system_fragments:
            for frag in options.system_fragments:
                args.extend(['--sf', frag])

        if options.template:
            args.extend(['-t', options.template])
        if options.params:
            for key_name, value in options.params.items():
                args.extend(['-p', key_name, value])

        if options.no_stream:
            args.append('--no-stream')
        if options.no_log:
            args.append('--no-log')
        if options.log:
            args.append('--log')
        if options.continue_conversation:
            args.append('--continue')
        if options.conversation_id:
            args.extend(['--cid', options.conversation_id])
        if options.key:
            args.extend(['--key', options.key])
        if options.save:
            args.extend(['--save', options.save])
        if options.async_mode:
            args.append('--async')
        if options.usage:
            args.append('--usage')
        if options.extract:
            args.append('--extract')
        if options.extract_last:
            args.append('--extract-last')

        return self._run_command(args)

    # ========== CHAT COMMAND ==========

    def chat(self, options: ChatOptions, interactive_input: Optional[str] = None) -> str:
        """
        Start a chat session.

        Note: The chat command is interactive by design. This wrapper has limited
        functionality for chat. Consider using prompt() with conversation_id for
        multi-turn conversations instead.

        Args:
            options: ChatOptions dataclass with configuration
            interactive_input: Optional input to provide to chat session

        Returns:
            Chat output

        Example:
            opts = ChatOptions(
                model="gpt-4o-mini",
                system="You are a helpful assistant"
            )
            # Note: This won't work well for interactive sessions
            wrapper.chat(opts, interactive_input="Hello\\nexit\\n")
        """
        args = ['chat']

        if options.system:
            args.extend(['-s', options.system])
        if options.model:
            args.extend(['-m', options.model])
        if options.continue_conversation:
            args.append('--continue')
        if options.conversation_id:
            args.extend(['--cid', options.conversation_id])

        if options.fragments:
            for fragment in options.fragments:
                args.extend(['-f', fragment])

        if options.system_fragments:
            for frag in options.system_fragments:
                args.extend(['--sf', frag])

        if options.template:
            args.extend(['-t', options.template])
        if options.params:
            for key_name, value in options.params.items():
                args.extend(['-p', key_name, value])

        if options.options:
            for key_name, value in options.options.items():
                args.extend(['-o', key_name, value])

        if options.database or self.database:
            args.extend(['-d', options.database or self.database])

        if options.no_stream:
            args.append('--no-stream')
        if options.key:
            args.extend(['--key', options.key])

        if options.tools:
            for tool in options.tools:
                args.extend(['-T', tool])

        if options.functions:
            for func in options.functions:
                args.extend(['--functions', func])

        if options.tools_debug:
            args.append('--td')
        if options.tools_approve:
            args.append('--ta')
        if options.chain_limit != 5:
            args.extend(['--cl', str(options.chain_limit)])

        return self._run_command(args, input=interactive_input)

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

    def models_default(self, model: Optional[str] = None) -> str:
        """
        Show or set the default model.

        Args:
            model: Model to set as default. If None, shows current default.

        Returns:
            Current default model name (or empty if setting)

        Example:
            # Show current default
            current = wrapper.models_default()

            # Set new default
            wrapper.models_default("gpt-4o-mini")
        """
        args = ['models', 'default']
        if model:
            args.append(model)
        return self._run_command(args)

    # ========== KEYS COMMAND ==========

    def keys_list(self) -> str:
        """
        List names of all stored API keys.

        Returns:
            Newline-separated list of key names

        Example:
            keys = wrapper.keys_list()
            print(keys)  # openai\\nanthropic\\n...
        """
        return self._run_command(['keys', 'list'])

    def keys_get(self, name: str) -> str:
        """
        Return the value of a stored key.

        Args:
            name: Name of the key to retrieve

        Returns:
            The key value

        Raises:
            LLMError: If key not found

        Example:
            api_key = wrapper.keys_get("openai")
        """
        return self._run_command(['keys', 'get', name])

    def keys_set(self, name: str, value: str) -> None:
        """
        Save a key in the keys.json file.

        Args:
            name: Name for the key
            value: The API key value

        Example:
            wrapper.keys_set("openai", "sk-...")
        """
        self._run_command(['keys', 'set', name, '--value', value])

    def keys_path(self) -> str:
        """
        Output the path to the keys.json file.

        Returns:
            Full path to keys.json

        Example:
            path = wrapper.keys_path()
            print(f"Keys stored at: {path}")
        """
        return self._run_command(['keys', 'path'])

    # ========== LOGS COMMAND ==========

    def logs_list(self, options: Optional[LogsListOptions] = None) -> str:
        """
        Show logged prompts and their responses.

        Retrieves conversation history from the logs database with extensive
        filtering and formatting options.

        Args:
            options: LogsListOptions dataclass (uses defaults if None)

        Returns:
            Formatted log output (format depends on options)

        Example:
            # Get last 5 logs as JSON
            opts = LogsListOptions(count=5, json_output=True)
            logs = wrapper.logs_list(opts)

            # Get logs for a specific model with usage info
            opts = LogsListOptions(model="gpt-4o", usage=True)
            logs = wrapper.logs_list(opts)

            # Search logs
            opts = LogsListOptions(query="python", count=10)
            logs = wrapper.logs_list(opts)
        """
        if options is None:
            options = LogsListOptions()

        args = ['logs', 'list']

        if options.count is not None:
            args.extend(['-n', str(options.count)])
        if options.database or self.database:
            args.extend(['-d', options.database or self.database])
        if options.model:
            args.extend(['-m', options.model])
        if options.query:
            args.extend(['-q', options.query])

        if options.fragments:
            for fragment in options.fragments:
                args.extend(['-f', fragment])

        if options.tools:
            for tool in options.tools:
                args.extend(['-T', tool])

        if options.any_tools:
            args.append('--tools')
        if options.schema:
            args.extend(['--schema', options.schema])
        if options.schema_multi:
            args.extend(['--schema-multi', options.schema_multi])
        if options.latest:
            args.append('--latest')
        if options.truncate:
            args.append('--truncate')
        if options.short:
            args.append('--short')
        if options.usage:
            args.append('--usage')
        if options.response_only:
            args.append('--response')
        if options.extract:
            args.append('--extract')
        if options.extract_last:
            args.append('--extract-last')
        if options.current_conversation:
            args.append('--current')
        if options.conversation_id:
            args.extend(['--cid', options.conversation_id])
        if options.json_output:
            args.append('--json')
        if options.expand:
            args.append('--expand')

        return self._run_command(args)

    def logs_path(self) -> str:
        """
        Output the path to the logs.db file.

        Returns:
            Full path to logs.db
        """
        return self._run_command(['logs', 'path'])

    def logs_status(self) -> str:
        """
        Show current status of database logging.

        Returns:
            Status information including log count and database size
        """
        return self._run_command(['logs', 'status'])

    def logs_on(self) -> None:
        """Turn on logging for all prompts."""
        self._run_command(['logs', 'on'])

    def logs_off(self) -> None:
        """Turn off logging for all prompts."""
        self._run_command(['logs', 'off'])

    def logs_backup(self, path: str) -> str:
        """
        Backup your logs database to a file.

        Args:
            path: Destination path for backup

        Returns:
            Confirmation message with file size
        """
        return self._run_command(['logs', 'backup', path])

    # ========== TEMPLATES COMMAND ==========

    def templates_list(self) -> str:
        """
        List available prompt templates.

        Returns:
            Formatted list of templates with their content
        """
        return self._run_command(['templates', 'list'])

    def templates_show(self, name: str) -> str:
        """
        Show the specified prompt template.

        Args:
            name: Template name

        Returns:
            Template content in YAML format
        """
        return self._run_command(['templates', 'show', name])

    def templates_path(self) -> str:
        """
        Output the path to the templates directory.

        Returns:
            Full path to templates directory
        """
        return self._run_command(['templates', 'path'])

    # ========== ALIASES COMMAND ==========

    def aliases_list(self, options: Optional[AliasesListOptions] = None) -> str:
        """
        List current model aliases.

        Args:
            options: AliasesListOptions dataclass

        Returns:
            List of aliases (formatted or JSON)
        """
        if options is None:
            options = AliasesListOptions()

        args = ['aliases', 'list']
        if options.json_output:
            args.append('--json')
        return self._run_command(args)

    def aliases_set(self, options: AliasesSetOptions) -> None:
        """
        Set an alias for a model.

        Args:
            options: AliasesSetOptions dataclass

        Example:
            # Direct alias
            opts = AliasesSetOptions(
                alias="mini",
                model_id="gpt-4o-mini"
            )
            wrapper.aliases_set(opts)

            # Search-based alias
            opts = AliasesSetOptions(
                alias="mini",
                queries=["4o", "mini"]
            )
            wrapper.aliases_set(opts)
        """
        args = ['aliases', 'set', options.alias]
        if options.model_id:
            args.append(options.model_id)
        if options.queries:
            for query in options.queries:
                args.extend(['-q', query])
        self._run_command(args)

    def aliases_remove(self, alias: str) -> None:
        """
        Remove an alias.

        Args:
            alias: Alias name to remove

        Example:
            wrapper.aliases_remove("mini")
        """
        self._run_command(['aliases', 'remove', alias])

    def aliases_path(self) -> str:
        """
        Output the path to the aliases.json file.

        Returns:
            Full path to aliases.json
        """
        return self._run_command(['aliases', 'path'])

    # ========== FRAGMENTS COMMAND ==========

    def fragments_list(self, options: Optional[FragmentsListOptions] = None) -> str:
        """
        List current fragments.

        Fragments are reusable snippets of text shared across multiple prompts.

        Args:
            options: FragmentsListOptions dataclass

        Returns:
            List of fragments (formatted or JSON)

        Example:
            # List all fragments with aliases
            opts = FragmentsListOptions(aliases=True)
            fragments = wrapper.fragments_list(opts)

            # Search fragments
            opts = FragmentsListOptions(queries=["docs"])
            fragments = wrapper.fragments_list(opts)
        """
        if options is None:
            options = FragmentsListOptions()

        args = ['fragments', 'list']

        if options.queries:
            for query in options.queries:
                args.extend(['-q', query])

        if options.aliases:
            args.append('--aliases')
        if options.json_output:
            args.append('--json')

        return self._run_command(args)

    def fragments_set(self, options: FragmentsSetOptions) -> None:
        """
        Set an alias for a fragment.

        Args:
            options: FragmentsSetOptions dataclass

        Example:
            opts = FragmentsSetOptions(
                alias="mydocs",
                fragment="./docs.md"
            )
            wrapper.fragments_set(opts)
        """
        args = ['fragments', 'set', options.alias, options.fragment]
        self._run_command(args)

    def fragments_show(self, alias_or_hash: str) -> str:
        """
        Display the fragment stored under an alias or hash.

        Args:
            alias_or_hash: Fragment alias or hash

        Returns:
            Fragment content

        Example:
            content = wrapper.fragments_show("mydocs")
        """
        return self._run_command(['fragments', 'show', alias_or_hash])

    def fragments_remove(self, alias: str) -> None:
        """
        Remove a fragment alias.

        Args:
            alias: Fragment alias to remove

        Example:
            wrapper.fragments_remove("mydocs")
        """
        self._run_command(['fragments', 'remove', alias])

    # ========== SCHEMAS COMMAND ==========

    def schemas_list(self, options: Optional[SchemasListOptions] = None) -> str:
        """
        List stored schemas.

        Args:
            options: SchemasListOptions dataclass

        Returns:
            List of schemas (formatted or JSON)

        Example:
            opts = SchemasListOptions(full=True, json_output=True)
            schemas = wrapper.schemas_list(opts)
        """
        if options is None:
            options = SchemasListOptions()

        args = ['schemas', 'list']

        if options.database or self.database:
            args.extend(['-d', options.database or self.database])

        if options.queries:
            for query in options.queries:
                args.extend(['-q', query])

        if options.full:
            args.append('--full')
        if options.json_output:
            args.append('--json')
        if options.nl:
            args.append('--nl')

        return self._run_command(args)

    def schemas_show(self, schema_id: str, database: Optional[str] = None) -> str:
        """
        Show a stored schema.

        Args:
            schema_id: Schema ID to show
            database: Optional path to log database

        Returns:
            Schema as JSON

        Example:
            schema = wrapper.schemas_show("abc123")
        """
        args = ['schemas', 'show', schema_id]
        if database or self.database:
            args.extend(['-d', database or self.database])
        return self._run_command(args)

    def schemas_dsl(self, input: str, multi: bool = False) -> str:
        """
        Convert LLM's schema DSL to a JSON schema.

        Args:
            input: DSL input string
            multi: Wrap in an array

        Returns:
            JSON schema

        Example:
            schema = wrapper.schemas_dsl("name, age int, bio: their bio")
        """
        args = ['schemas', 'dsl', input]
        if multi:
            args.append('--multi')
        return self._run_command(args)

    # ========== EMBEDDINGS ==========

    def embed(self, options: EmbedOptions) -> str:
        """
        Embed text and store or return the result.

        Args:
            options: EmbedOptions dataclass

        Returns:
            Embedding result (format depends on options)

        Example:
            # Embed and store
            opts = EmbedOptions(
                collection="docs",
                id="doc1",
                content="Sample text",
                store=True
            )
            wrapper.embed(opts)

            # Just get embedding
            opts = EmbedOptions(
                content="Sample text",
                format="json"
            )
            embedding = wrapper.embed(opts)
        """
        args = ['embed']

        if options.collection:
            args.append(options.collection)
        if options.id:
            args.append(options.id)
        if options.input_path:
            args.extend(['-i', options.input_path])
        if options.model:
            args.extend(['-m', options.model])
        if options.store:
            args.append('--store')
        if options.database:
            args.extend(['-d', options.database])
        if options.content:
            args.extend(['-c', options.content])
        if options.binary:
            args.append('--binary')
        if options.metadata:
            args.extend(['--metadata', json.dumps(options.metadata)])
        if options.format:
            args.extend(['-f', options.format])

        return self._run_command(args)

    def embed_multi(self, options: EmbedMultiOptions) -> None:
        """
        Store embeddings for multiple strings at once.

        Input can come from CSV/JSON/JSONL files, SQL queries, or file directories.

        Args:
            options: EmbedMultiOptions dataclass

        Example:
            # From CSV file
            opts = EmbedMultiOptions(
                collection="docs",
                input_path="input.csv",
                model="text-embedding-3-small"
            )
            wrapper.embed_multi(opts)

            # From files in directory
            opts = EmbedMultiOptions(
                collection="docs",
                files=[("./docs", "**/*.md")],
                model="text-embedding-3-small"
            )
            wrapper.embed_multi(opts)
        """
        args = ['embed-multi', options.collection]

        if options.input_path:
            args.append(options.input_path)

        if options.format:
            args.extend(['--format', options.format])

        if options.files:
            for directory, pattern in options.files:
                args.extend(['--files', directory, pattern])

        if options.encodings:
            for encoding in options.encodings:
                args.extend(['--encoding', encoding])

        if options.binary:
            args.append('--binary')
        if options.sql:
            args.extend(['--sql', options.sql])

        if options.attach:
            for alias, path in options.attach:
                args.extend(['--attach', alias, path])

        if options.batch_size:
            args.extend(['--batch-size', str(options.batch_size)])
        if options.prefix:
            args.extend(['--prefix', options.prefix])
        if options.model:
            args.extend(['-m', options.model])
        if options.prepend:
            args.extend(['--prepend', options.prepend])
        if options.store:
            args.append('--store')
        if options.database:
            args.extend(['-d', options.database])

        self._run_command(args)

    def similar(self, options: SimilarOptions) -> str:
        """
        Return top N similar IDs from a collection using cosine similarity.

        Args:
            options: SimilarOptions dataclass

        Returns:
            Similar items (formatted or JSON)

        Example:
            # Find similar by content
            opts = SimilarOptions(
                collection="docs",
                content="I like cats",
                number=5
            )
            results = wrapper.similar(opts)

            # Find similar by ID
            opts = SimilarOptions(
                collection="docs",
                id="doc1",
                number=10
            )
            results = wrapper.similar(opts)
        """
        args = ['similar', options.collection]

        if options.id:
            args.append(options.id)
        if options.input_path:
            args.extend(['-i', options.input_path])
        if options.content:
            args.extend(['-c', options.content])
        if options.binary:
            args.append('--binary')
        if options.number != 10:
            args.extend(['-n', str(options.number)])
        if options.plain:
            args.append('--plain')
        if options.database:
            args.extend(['-d', options.database])
        if options.prefix:
            args.extend(['--prefix', options.prefix])

        return self._run_command(args)

    # ========== EMBEDDING MODELS ==========

    def embed_models_list(self, options: Optional[EmbedModelsListOptions] = None) -> str:
        """
        List available embedding models.

        Args:
            options: EmbedModelsListOptions dataclass

        Returns:
            List of embedding models

        Example:
            opts = EmbedModelsListOptions(queries=["openai"])
            models = wrapper.embed_models_list(opts)
        """
        if options is None:
            options = EmbedModelsListOptions()

        args = ['embed-models', 'list']

        if options.queries:
            for query in options.queries:
                args.extend(['-q', query])

        return self._run_command(args)

    def embed_models_default(self, model: Optional[str] = None, remove_default: bool = False) -> str:
        """
        Show or set the default embedding model.

        Args:
            model: Model to set as default (None to show current)
            remove_default: Reset to no default model

        Returns:
            Current default model (or empty if setting/removing)

        Example:
            # Show current
            current = wrapper.embed_models_default()

            # Set default
            wrapper.embed_models_default("text-embedding-3-small")

            # Remove default
            wrapper.embed_models_default(remove_default=True)
        """
        args = ['embed-models', 'default']
        if remove_default:
            args.append('--remove-default')
        elif model:
            args.append(model)
        return self._run_command(args)

    # ========== COLLECTIONS ==========

    def collections_list(self, options: Optional[CollectionsListOptions] = None) -> str:
        """
        View a list of embedding collections.

        Args:
            options: CollectionsListOptions dataclass

        Returns:
            List of collections (formatted or JSON)

        Example:
            opts = CollectionsListOptions(json_output=True)
            collections = wrapper.collections_list(opts)
        """
        if options is None:
            options = CollectionsListOptions()

        args = ['collections', 'list']

        if options.database:
            args.extend(['-d', options.database])
        if options.json_output:
            args.append('--json')

        return self._run_command(args)

    def collections_delete(self, collection: str, database: Optional[str] = None) -> None:
        """
        Delete the specified collection.

        Args:
            collection: Collection name to delete
            database: Optional path to embeddings database

        Example:
            wrapper.collections_delete("my-collection")
        """
        args = ['collections', 'delete', collection]
        if database:
            args.extend(['-d', database])
        self._run_command(args)

    def collections_path(self) -> str:
        """
        Output the path to the embeddings database.

        Returns:
            Full path to embeddings.db
        """
        return self._run_command(['collections', 'path'])

    # ========== TOOLS ==========

    def tools_list(self, options: Optional[ToolsListOptions] = None) -> str:
        """
        List available tools that have been provided by plugins.

        Args:
            options: ToolsListOptions dataclass

        Returns:
            List of tools (formatted or JSON)

        Example:
            # List all tools as JSON
            opts = ToolsListOptions(json_output=True)
            tools = wrapper.tools_list(opts)

            # List specific tools
            opts = ToolsListOptions(tool_defs=["weather", "calculator"])
            tools = wrapper.tools_list(opts)
        """
        if options is None:
            options = ToolsListOptions()

        args = ['tools', 'list']

        if options.tool_defs:
            args.extend(options.tool_defs)
        if options.json_output:
            args.append('--json')
        if options.functions:
            for func in options.functions:
                args.extend(['--functions', func])

        return self._run_command(args)

    # ========== PLUGINS ==========

    def plugins_list(self, options: Optional[PluginsListOptions] = None) -> str:
        """
        List installed plugins.

        Args:
            options: PluginsListOptions dataclass

        Returns:
            JSON list of plugins

        Example:
            # List all plugins
            plugins = wrapper.plugins_list()

            # Filter by hooks
            opts = PluginsListOptions(hooks=["register_models"])
            plugins = wrapper.plugins_list(opts)
        """
        if options is None:
            options = PluginsListOptions()

        args = ['plugins']

        if options.all_plugins:
            args.append('--all')
        if options.hooks:
            for hook in options.hooks:
                args.extend(['--hook', hook])

        return self._run_command(args)

    # ========== INSTALLATION ==========

    def install(
            self,
            packages: List[str],
            upgrade: bool = False,
            editable: Optional[str] = None,
            force_reinstall: bool = False,
            no_cache_dir: bool = False,
            pre: bool = False
    ) -> str:
        """
        Install packages from PyPI into the same environment as LLM.

        Args:
            packages: List of package names to install
            upgrade: Upgrade packages to latest version
            editable: Install a project in editable mode from this path
            force_reinstall: Reinstall all packages even if up-to-date
            no_cache_dir: Disable the cache
            pre: Include pre-release and development versions

        Returns:
            Installation output

        Example:
            # Install a plugin
            wrapper.install(["llm-claude-3"])

            # Install in editable mode
            wrapper.install([], editable="./llm-myplugin")
        """
        args = ['install']

        if upgrade:
            args.append('--upgrade')
        if editable:
            args.extend(['--editable', editable])
        if force_reinstall:
            args.append('--force-reinstall')
        if no_cache_dir:
            args.append('--no-cache-dir')
        if pre:
            args.append('--pre')

        args.extend(packages)

        return self._run_command(args)

    def uninstall(self, packages: List[str], yes: bool = False) -> str:
        """
        Uninstall Python packages from the LLM environment.

        Args:
            packages: List of package names to uninstall
            yes: Don't ask for confirmation

        Returns:
            Uninstallation output

        Example:
            wrapper.uninstall(["llm-claude-3"], yes=True)
        """
        args = ['uninstall']
        args.extend(packages)
        if yes:
            args.append('-y')

        return self._run_command(args)


# ========== CONVENIENCE FUNCTIONS ==========

def quick_prompt(prompt: str, model: Optional[str] = None, **kwargs) -> str:
    """
    Convenience function for quick prompts without creating options object.

    Args:
        prompt: The prompt text
        model: Optional model name
        **kwargs: Additional PromptOptions fields

    Returns:
        Response text

    Example:
        response = quick_prompt("What is 2+2?", model="gpt-4o-mini")
        response = quick_prompt("Explain", system="Be brief", usage=True)
    """
    wrapper = LLMWrapper()
    options = PromptOptions(prompt=prompt, model=model, **kwargs)
    return wrapper.prompt(options)