import srsly
from pathlib import Path

from nbllm import Chat, ConfigMode, FactoryConfigLlmDefault, FactoryConfigModesDeveloper
from nbllm.tools import FileTool, TodoTools
from nbllm import ui

marimo_system_prompt = '''
# Marimo notebook assistant

You are a specialized AI assistant designed to help create data science notebooks using marimo. You focus on creating clear, efficient, and reproducible data analysis workflows with marimo's reactive programming model.

You prefer polars over pandas. 
You prefer altair over matplotlib. 

marimo files are Python files but with a special syntax for defining cells. Also notice that the first line of the file is a comment that contains the version of marimo that was used to generate the file, this helps UV. 

<example>
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "marimo",
#     "numpy==2.3.1",
# ]
# ///

import marimo

__generated_with = "0.14.10"
app = marimo.App(width="columns")

@app.cell
def _():
    import marimo as mo
    import numpy as np
    return mo, np

@app.cell
def _():
    a = 1 
    return (a,)

@app.cell
def _():
    b = 2
    return (b,)

@app.cell
def _(a, b, np, slider):
    c = a + b + slider.value
    np.arange(c)
    return

@app.cell
def _(mo):
    slider = mo.ui.slider(1, 10, 1)
    slider
    return (slider,)

@app.cell
def _():
    return

if __name__ == "__main__":
    app.run()
</example>

No matter what you do, you should always keep the cells around in a marimo file. This is not a normal Python file. Don't forget the @cell decorator.
'''.strip()

marimo_default_notebook_content = '''
# /// script
# requires-python = ">=3.11"
# dependencies = [
#     "altair==5.5.0",
#     "marimo",
#     "matplotlib==3.10.3",
#     "numpy==2.3.1",
#     "pandas==2.3.0",
# ]
# ///

import marimo

__generated_with = "0.15.0"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import random
    import pandas as pd
    import altair as alt
    return


if __name__ == "__main__":
    app.run()
'''.strip()

def set_role():
    """Set a role for the assistant"""
    roles = ["developer", "teacher", "analyst", "creative writer", "code reviewer"]
    role = ui.choice("What role should I take?", roles)
    return f"You are now acting as a {role}. Please respond in character for this role."


def debug_reason():
    """Set a role for the assistant"""
    ui.tool_status("We are going to prompt the LLM to see if they can find the bug in the code on their own.")
    entrypoint = ui.input("What is the entrypoint for the user?")
    action = ui.input("What is the action the user is trying to take?")
    out = f"""You've introduced a new bug, but instead of me telling you what the bug is, let's see if you can find it for yourself. Imagine that you are a user and that you start by {entrypoint}. Go through all the steps that would happen if a user tries to {action}. Think through all the steps and see if you can spot something that could go wrong. Don't write any code, but let's see if we both find the same issue."""
    print("")
    ui.print_neutral(out)
    return out

# Define tools for different modes
file_tool = FileTool("edit.py", marimo_default_notebook_content)
todo_tools = TodoTools()

Chat(
    cfg_llm=FactoryConfigLlmDefault(system_prompt=marimo_system_prompt),
    cfg_modes=FactoryConfigModesDeveloper(
        mode_development_tools=[file_tool, todo_tools],
        mode_review_tools=[file_tool]
    ),
    debug=True,
    slash_commands={
        "/thinking": "Let me think through this step by step:",
        "/role": set_role,
        "/debug_prompt": debug_reason,
    },
    history_callback=lambda x: srsly.write_jsonl(Path("logs.json"), x, append=True, append_new_line=False)
).run()
