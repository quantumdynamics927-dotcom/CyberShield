"""Windows-specific platform utilities."""

import sys
import os
import subprocess
from typing import Optional, List, Dict, Any


# Windows tool equivalents for common Unix tools
TOOL_EQUIVALENTS = {
    "ls": "dir",
    "cat": "type",
    "rm": "del",
    "cp": "copy",
    "mv": "move",
    "mkdir": "mkdir",
    "pwd": "cd",
    "which": "where",
    "grep": "findstr",
    "head": "more +1",
    "tail": "more +1",
    "sed": "powershell -Command",
    "awk": "powershell -Command",
    "chmod": "attrib",
    "ps": "tasklist",
    "kill": "taskkill",
    "netstat": "netstat -an",
    "ifconfig": "ipconfig",
    "ping": "ping",
    "traceroute": "tracert",
    "nmap": "nmap",  # Windows nmap available
}


def convert_command(command: str) -> str:
    """Convert a Unix-style command to Windows equivalent.

    Args:
        command: Unix-style command string

    Returns:
        Windows-compatible command
    """
    # Don't convert if nmap is explicitly available (user may have it)
    if "nmap" in command.lower():
        return command

    # Split command into parts
    parts = command.split()
    if not parts:
        return command

    # Check if the command has an equivalent
    cmd_name = parts[0].lower()
    if cmd_name in TOOL_EQUIVALENTS:
        # Replace command name
        parts[0] = TOOL_EQUIVALENTS[cmd_name]

        # Handle special cases
        if cmd_name == "ls":
            # Add /b for bare format
            if "/l" not in command and "-l" not in command:
                parts.append("/b")
        elif cmd_name == "rm":
            # Add /f /s for recursive force delete
            if "-rf" in command or "-r" in command:
                parts.insert(1, "/s")
                parts.insert(2, "/f")
        elif cmd_name == "ps":
            # tasklist with format
            parts.extend(["/fo", "csv", "/nh"])
        elif cmd_name == "grep":
            # findstr is case-insensitive with /i
            parts.insert(1, "/i")

    return " ".join(parts)


def get_powershell_version() -> Optional[str]:
    """Get PowerShell version if available.

    Returns:
        PowerShell version string or None
    """
    try:
        result = subprocess.run(
            ["powershell", "-Command", "$PSVersionTable.PSVersion.ToString()"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def is_powershell_available() -> bool:
    """Check if PowerShell is available.

    Returns:
        True if PowerShell is available
    """
    return get_powershell_version() is not None


def get_windows_version() -> Optional[Dict[str, Any]]:
    """Get Windows version information.

    Returns:
        Dict with Windows version info or None
    """
    if sys.platform != "win32":
        return None

    try:
        import platform
        winver = platform.win32_ver()
        return {
            "version": winver[0],
            "service_pack": winver[1],
            "platform": platform.platform(),
        }
    except Exception:
        pass

    return None


def enable_ansi_support() -> bool:
    """Enable ANSI color support on Windows.

    Returns:
        True if successful
    """
    if sys.platform != "win32":
        return True

    try:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
        return True
    except Exception:
        return False


def get_tool_path(tool_name: str) -> Optional[str]:
    """Get the full path to a tool if available on Windows.

    Args:
        tool_name: Name of the tool

    Returns:
        Full path to tool or None if not found
    """
    if sys.platform != "win32":
        return None

    # Check if tool is in PATH
    try:
        result = subprocess.run(
            ["where", tool_name],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")[0]
    except Exception:
        pass

    return None


def check_tool_available(tool_name: str) -> bool:
    """Check if a tool is available on Windows.

    Args:
        tool_name: Name of the tool

    Returns:
        True if tool is available
    """
    return get_tool_path(tool_name) is not None


__all__ = [
    "TOOL_EQUIVALENTS",
    "convert_command",
    "get_powershell_version",
    "is_powershell_available",
    "get_windows_version",
    "enable_ansi_support",
    "get_tool_path",
    "check_tool_available",
]
