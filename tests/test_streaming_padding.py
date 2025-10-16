#!/usr/bin/env python3
"""Test script to reproduce the streaming padding bug."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nbllm import ui
from io import StringIO
import contextlib

def capture_console_output():
    """Capture what gets printed to the console."""
    # Create a StringIO object to capture output
    captured_output = StringIO()
    
    # Temporarily replace the console's file with our StringIO
    original_file = ui._console.file
    ui._console.file = captured_output
    
    try:
        # Test the streaming behavior
        ui.start_streaming(ui.LEFT_PADDING)
        ui.stream_chunk("Hello world this is a test", ui.LEFT_PADDING)
        ui.end_streaming(ui.LEFT_PADDING)
        
        # Get the captured output
        output = captured_output.getvalue()
        return output
    finally:
        # Restore the original file
        ui._console.file = original_file

def test_streaming_padding():
    """Test that streaming properly applies padding to the first chunk."""
    print("Testing streaming padding...")
    
    # Capture the output
    output = capture_console_output()
    
    # Print the raw output for inspection
    print("Raw output (with repr to see spaces):")
    print(repr(output))
    
    # Check if the output starts with the expected padding
    expected_padding = " " * ui.LEFT_PADDING

    is_success = output.startswith(expected_padding)
    # The output should start with padding
    if not is_success:
        error_msg  = "\n"
        error_msg += "✗ FAIL: Output does not start with proper padding\n"
        error_msg += f"Expected to start with: {repr(expected_padding)}\n"
        error_msg += f"Actually starts with  : {repr(output[:10])}"
        assert is_success, error_msg

    print("✓ PASS: Output starts with proper padding")

if __name__ == "__main__":
    test_streaming_padding()
    print("\n✅ All mode UI tests passed!")