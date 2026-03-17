import os
import json
import sys

# Note: This assumes resolve_connection.py exists in the same directory
# or that the DaVinci Resolve API is properly installed
try:
    from resolve_connection import connect_to_resolve
except ImportError:
    print("Error: resolve_connection module not found. Please ensure DaVinci Resolve API is properly installed.")
    sys.exit(1)

def export_color_grading(project_name, output_file):
    """
    Connects to DaVinci Resolve, extracts color grading settings from the specified project,
    and exports them to a JSON file.

    :param project_name: Name of the project to export color grading settings from.
    :param output_file: Path to the output JSON file.
    """
    # Connect to DaVinci Resolve
    resolve = connect_to_resolve()
    if not resolve:
        print("Error: Unable to connect to DaVinci Resolve.")
        sys.exit(1)

    # Get the project - using more defensive approach
    try:
        project = resolve.GetProjectByName(project_name)
        if not project:
            print(f"Error: Project '{project_name}' not found.")
            sys.exit(1)
    except AttributeError:
        print("Error: DaVinci Resolve API method 'GetProjectByName' not available.")
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to get project: {str(e)}")
        sys.exit(1)

    # Get color grading settings - with more defensive handling
    try:
        # Note: The actual method name may differ in the DaVinci Resolve API
        if hasattr(project, 'GetColorGradingSettings'):
            color_grading_settings = project.GetColorGradingSettings()
        elif hasattr(project, 'GetSettings'):
            color_grading_settings = project.GetSettings()
        else:
            print("Warning: Unable to find color grading settings method. Attempting to serialize project object.")
            color_grading_settings = {"project_name": project_name, "data": "Unable to extract settings"}
            
        # Convert to serializable format if needed
        if hasattr(color_grading_settings, '__dict__'):
            color_grading_settings = color_grading_settings.__dict__
        elif not isinstance(color_grading_settings, (dict, list, str, int, float, bool, type(None))):
            color_grading_settings = str(color_grading_settings)
    except Exception as e:
        print(f"Error: Failed to retrieve color grading settings: {str(e)}")
        sys.exit(1)

    # Export to JSON
    try:
        with open(output_file, 'w') as json_file:
            json.dump(color_grading_settings, json_file, indent=4, default=str)
        print(f"Successfully exported color grading settings to '{output_file}'.")
    except IOError as e:
        print(f"Error: Failed to write to '{output_file}': {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    # Simple CLI for exporting color grading settings
    if len(sys.argv) != 3:
        print("Usage: python export_color_grading.py <project_name> <output_file>")
        sys.exit(1)

    project_name = sys.argv[1]
    output_file = sys.argv[2]

    # Check if output file's directory exists
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        print(f"Error: Directory for output file '{output_file}' does not exist.")
        sys.exit(1)

    export_color_grading(project_name, output_file)
