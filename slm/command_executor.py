from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
import subprocess
import shlex
import os
import sys
from typing import Optional, Dict, Any, List
import json

# Import platform utilities
from slm.platform import is_windows, get_shell

class CommandFormatter:
    """Format and validate system commands."""

    @staticmethod
    def format_command(command: str) -> str:
        """Format a command string for the current platform."""
        if is_windows():
            # Convert forward slashes to backslashes on Windows
            from slm.platform.windows import convert_command
            return convert_command(command)
        return command
    
    @staticmethod
    def validate_command(command: str) -> bool:
        """Validate if a command is safe to execute."""
        # List of dangerous commands/patterns
        dangerous_patterns = [
            "rm -rf",
            "del /f",
            "format",
            ">",  # redirections
            "2>",
            "&",  # command chaining
            "|",  # pipes
            ";",  # command separator
            "mkfs",
            "dd"
        ]
        
        return not any(pattern in command.lower() for pattern in dangerous_patterns)

class SecurityContext:
    """Manage security context for command execution."""
    
    def __init__(self):
        self.allowed_paths: List[str] = []
        self.allowed_commands: List[str] = []
        self.security_level: str = "strict"
    
    def is_command_allowed(self, command: str) -> bool:
        """Check if a command is allowed in current security context."""
        cmd = shlex.split(command)[0]
        return (
            cmd in self.allowed_commands or
            self.security_level == "permissive"
        )
    
    def is_path_allowed(self, path: str) -> bool:
        """Check if a path is allowed in current security context."""
        path = os.path.abspath(path)
        return (
            any(path.startswith(allowed) for allowed in self.allowed_paths) or
            self.security_level == "permissive"
        )

class CommandExecutor:
    """Execute system commands safely."""
    
    def __init__(self):
        self.console = Console()
        self.formatter = CommandFormatter()
        self.security = SecurityContext()
    
    def execute(self, command: str) -> Dict[str, Any]:
        """Execute a system command and return results."""
        # Format command for current platform
        formatted_cmd = self.formatter.format_command(command)
        
        # Validate command
        if not self.formatter.validate_command(formatted_cmd):
            return {
                "success": False,
                "error": "Command contains dangerous patterns"
            }
        
        # Check security context
        if not self.security.is_command_allowed(formatted_cmd):
            return {
                "success": False,
                "error": "Command not allowed by security policy"
            }
        
        try:
            # Display command
            self.console.print(
                Panel(
                    Syntax(formatted_cmd, "bash", theme="monokai"),
                    title="Executing Command",
                    border_style="blue"
                )
            )
            
            # Execute command
            process = subprocess.Popen(
                formatted_cmd,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Capture output
            stdout, stderr = process.communicate()
            
            # Format result
            result = {
                "success": process.returncode == 0,
                "return_code": process.returncode,
                "stdout": stdout.strip(),
                "stderr": stderr.strip() if stderr else None
            }
            
            # Display output
            if result["success"]:
                if stdout:
                    self.console.print(
                        Panel(
                            stdout,
                            title="Output",
                            border_style="green"
                        )
                    )
            else:
                if stderr:
                    self.console.print(
                        Panel(
                            stderr,
                            title="Error",
                            border_style="red"
                        )
                    )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

def main():
    """Test the command executor."""
    executor = CommandExecutor()
    
    # Configure security context
    executor.security.security_level = "strict"
    executor.security.allowed_commands = [
        "dir",
        "ls",
        "pwd",
        "cd",
        "python",
        "pip"
    ]
    executor.security.allowed_paths = [
        os.getcwd(),
        os.path.expanduser("~")
    ]
    
    # Test command execution
    test_commands = [
        "dir" if sys.platform == "win32" else "ls",
        "pwd" if sys.platform != "win32" else "cd",
        "python --version"
    ]
    
    for cmd in test_commands:
        print(f"\nTesting command: {cmd}")
        result = executor.execute(cmd)
        print("Result:", json.dumps(result, indent=2))

if __name__ == "__main__":
    main()
