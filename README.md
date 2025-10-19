# nbllm

```

███╗   ██╗██████╗ ██╗     ██╗     ███╗   ███╗
████╗  ██║██╔══██╗██║     ██║     ████╗ ████║
██╔██╗ ██║██████╔╝██║     ██║     ██╔████╔██║
██║╚██╗██║██╔══██╗██║     ██║     ██║╚██╔╝██║
██║ ╚████║██████╔╝███████╗███████╗██║ ╚═╝ ██║
╚═╝  ╚═══╝╚═════╝ ╚══════╝╚══════╝╚═╝     ╚═╝


A terminal chat experience that you can configure yourself.
```

This project is clone of [bespoken](https://github.com/koaning/bespoken) 
 - commit 0537087f32e90a8ced9185a35ac12211b7735ec6
 - feature/chat-class-refactor
 - whole idea comes from originating repo, so credit to Vincent :)

I would like to decouple llm / iu / cli into some more generic approach if possible (will see).

## Installation

Basic installation:

To preserve the namespace on pypi (as my hobby project) no pypi package exists. Use uv to solve installation process:

```bash
uvx --with git+https://github.com/mse11/nbllm[marimo,browser] python apps/coding_agent__marimo_notebook.py
```

Developer installation:

```bash
# development
https://github.com/mse11/nbllm.git
cd nbllm
uv sync --all-extras           # install all extra dependencies [dev,browser]
source .venv/Scripts/activate  # for WINDOWS Gitbash
source .venv/bin/activate      # for LINUX
```

## Usage

This library uses [llm](https://llm.datasette.io/en/stable/) under the hood to provide you with building blocks to make LLM chat interfaces from the commandline. Here's an example:

```python
from nbllm import chat
from nbllm.tools import FileTool, TodoTools, PlaywrightTool

chat(
    model_name="anthropic/claude-3-5-sonnet-20240620",
    tools=[FileTool("edit.py")],
    system_prompt="You are a coding assistant that can make edits to a single file.",
    debug=True,
)
```

## Features 

### Autocomplete 

Tab completion for commands and file paths. Use `@file.py` to get file path suggestions, "/" + <kbd>TAB></kbd> to autocomplete commands or use arrow keys for command history.

### Custom slash commands

Define your own `/commands` that either send text to the LLM or trigger interactive functions:

```python
def save_conversation():
    """Save conversation to file"""
    filename = ui.input("Filename: ")
    return f"Saved to {filename}"

chat(
    ...,
    slash_commands={
        "/save": save_conversation,
        "/formal": "Please respond in a formal manner.",
    }
)
```

## Why? 

The goal is to host a bunch of tools that you can pass to the LLM, but the main idea here is that you can also make it easy to constrain the chat. The `FileTool`, for example, only allows the LLM to make edits to a single file declared upfront. This significantly reduces any injection risks and still covers a lot of use-cases. It is also a nice exercise to make tools like claude code feel less magical, and you can also swap out the LLM with any other one as you see fit. 

This project is in early days at the moment, but it feels exciting to work on!
