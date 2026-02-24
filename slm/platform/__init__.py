"""CyberLab platform module - Platform-specific utilities."""

import sys
import os
from typing import Optional, Dict, Any


def get_platform() -> str:
    """Get the current platform.

    Returns:
        'windows', 'linux', or 'darwin'
    """
    if sys.platform == "win32":
        return "windows"
    elif sys.platform == "darwin":
        return "darwin"
    else:
        return "linux"


def is_windows() -> bool:
    """Check if running on Windows."""
    return sys.platform == "win32"


def is_linux() -> bool:
    """Check if running on Linux."""
    return sys.platform.startswith("linux")


def is_macos() -> bool:
    """Check if running on macOS."""
    return sys.platform == "darwin"


def normalize_path(path: str) -> str:
    """Normalize a path for the current platform.

    Args:
        path: Path to normalize

    Returns:
        Normalized path
    """
    if is_windows():
        # Convert forward slashes to backslashes on Windows
        return path.replace("/", "\\")
    return path


def get_shell() -> str:
    """Get the default shell for the current platform.

    Returns:
        Shell command (e.g., 'powershell', 'cmd', 'bash')
    """
    if is_windows():
        # Check if PowerShell is available
        if os.environ.get("PSModulePath"):
            return "powershell"
        return "cmd"
    return "bash"


def get_path_separator() -> str:
    """Get the path separator for the current platform.

    Returns:
        Path separator character
    """
    return "\\" if is_windows() else "/"


def get_line_ending() -> str:
    """Get the line ending for the current platform.

    Returns:
        Line ending string
    """
    return "\r\n" if is_windows() else "\n"


__all__ = [
    "get_platform",
    "is_windows",
    "is_linux",
    "is_macos",
    "normalize_path",
    "get_shell",
    "get_path_separator",
    "get_line_ending",
]
