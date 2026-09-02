import os
import subprocess
def run_python_file(
    working_directory: str, file_path: str, args: list[str] | None = None
) -> str:
    try:
        working_dir_abs = os.path.abspath(working_directory)
        target_file = os.path.abspath(os.path.join(working_dir_abs, file_path))
        valid_target_file = os.path.commonpath([working_dir_abs, target_file]) == working_dir_abs
        if not valid_target_file:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        if not os.path.isfile(target_file):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        if not file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", target_file]
        if args is not None:
            command.extend(args)
        complete_process = subprocess.run(args=command, cwd=working_dir_abs, text=True, timeout=30, capture_output=True)
        
        output_string = ""
        
        if complete_process.returncode != 0:
            output_string += f"Process exited with code {complete_process.returncode}\n"
        elif complete_process.stdout == "" and complete_process.stderr == "":
            output_string += "No output produced\n"
        else:
            output_string += f"STDOUT:\n{complete_process.stdout}\nSTDERR:\n{complete_process.stderr}"

        return output_string
    except Exception as e:
        return f"Error: executing Python file: {e}"
    
schema_run_python_file = {
    "type": "function",
    "function": {
        "name": "run_python_file",
        "description": "Executes a specified Python file relative to the working directory, optionally with command-line arguments, and returns the output or error messages",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the Python file to execute, relative to the working directory",
                },
                "args": {
                    "type": "array",
                    "items": {
                        "type": "string",
                    },
                    "description": "Optional list of command-line arguments to pass to the Python file",
                },
            },
        },
    },
}

    