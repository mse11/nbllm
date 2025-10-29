from typing import Optional

from .inspector import  ClickInspector
from .generator import  ClickWrapperGenerator

def generate_wrapper_from_cli(cli_module_import_path: str,
                              cli_global_attribute_name: str,
                              output_file: Optional[str] = None,
                              wrapper_class_name: str = "ClickWrapper") -> str:
    """
    Generate wrapper code from a Click CLI application.

    Args:

    Returns:
        Generated Python source code
    """

    click_cli_object = ClickInspector.import_from_string(
        cli_module_import_path,
        module_global_attribute=cli_global_attribute_name
    )

    # Extract metadata
    metadata = ClickInspector.all_click_metadata(click_cli_object)

    # Generate wrapper
    generator = ClickWrapperGenerator(metadata)
    code = generator.generate_wrapper_class(
        wrapper_class_name=wrapper_class_name,
        cli_module=cli_module,
        cli_function=cli_function
    )

    # Optionally write to file
    if output_file:
        with open(output_file, 'w') as f:
            f.write(code)
        print(f"Wrapper generated: {output_file}")

    return code

__all__ = [
    "generate_wrapper_from_cli",
    "ClickInspector",
    "ClickWrapperGenerator",
    #"__version__"
]