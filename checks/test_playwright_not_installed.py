"""
This test should be run in an environment without playwright installed.
"""

did_fail = False

try:
    from nbllm.tools import PlaywrightTool
    PlaywrightTool()
except ModuleNotFoundError:
    did_fail = True

assert did_fail, "PlaywrightTool should not be available when playwright is not installed"

