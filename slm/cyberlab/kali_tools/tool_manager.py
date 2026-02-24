from typing import Dict, List, Optional, Any
import re
import json
import subprocess
from pathlib import Path
import yaml
from datetime import datetime

class KaliToolManager:
    """Manager for Kali Linux security tools integration."""
    
    def __init__(self, config_path: Optional[str] = None):
        self.tools_config = self._load_config(config_path)
        self.tool_paths = self._find_tool_paths()
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load tools configuration."""
        default_config = {
            "tools_paths": {
                "nmap": "/usr/bin/nmap",
                "metasploit": "/usr/bin/msfconsole",
                "wireshark": "/usr/bin/wireshark",
                "burpsuite": "/usr/bin/burpsuite",
                "sqlmap": "/usr/bin/sqlmap",
                "hydra": "/usr/bin/hydra",
                "john": "/usr/bin/john",
                "aircrack-ng": "/usr/bin/aircrack-ng",
                "nikto": "/usr/bin/nikto",
                "gobuster": "/usr/bin/gobuster",
                "wpscan": "/usr/bin/wpscan",
                "hashcat": "/usr/bin/hashcat"
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path) as f:
                return yaml.safe_load(f)
        return default_config
    
    def _find_tool_paths(self) -> Dict[str, str]:
        """Find actual paths of Kali tools."""
        paths = {}
        for tool, default_path in self.tools_config["tools_paths"].items():
            # Try default path first
            if Path(default_path).exists():
                paths[tool] = default_path
                continue
                
            # Try to find in common locations
            common_paths = [
                "/usr/bin",
                "/usr/local/bin",
                "/opt/kali/bin",
                "C:\\Program Files\\Kali",
                "C:\\kali",
                str(Path.home() / "kali")
            ]
            
            for path in common_paths:
                tool_path = Path(path) / tool
                if tool_path.exists():
                    paths[tool] = str(tool_path)
                    break
        
        return paths
    
    def is_tool_available(self, tool_name: str) -> bool:
        """Check if a specific tool is available."""
        return tool_name in self.tool_paths
    
    def get_tool_path(self, tool_name: str) -> Optional[str]:
        """Get the path for a specific tool."""
        return self.tool_paths.get(tool_name)
    
    def execute_tool(self, 
                    tool_name: str, 
                    arguments: List[str],
                    capture_output: bool = True) -> Dict[str, Any]:
        """Execute a Kali tool with given arguments."""
        if not self.is_tool_available(tool_name):
            return {
                "success": False,
                "error": f"Tool {tool_name} not found"
            }
        
        try:
            cmd = [self.tool_paths[tool_name]] + arguments
            process = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                check=True
            )
            
            return {
                "success": True,
                "output": process.stdout,
                "command": " ".join(cmd)
            }
            
        except subprocess.CalledProcessError as e:
            return {
                "success": False,
                "error": str(e),
                "output": e.output,
                "command": " ".join(cmd)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "command": " ".join(cmd)
            }
    
    def get_tool_help(self, tool_name: str) -> str:
        """Get help documentation for a tool."""
        if not self.is_tool_available(tool_name):
            return f"Tool {tool_name} not found"
            
        result = self.execute_tool(tool_name, ["--help"])
        return result.get("output", "Help not available")
    
    def list_available_tools(self) -> List[str]:
        """List all available Kali tools."""
        return list(self.tool_paths.keys())
    
    def get_tool_category(self, tool_name: str) -> str:
        """Get the category of a tool."""
        categories = {
            "nmap": "Information Gathering",
            "wireshark": "Sniffing & Spoofing",
            "metasploit": "Exploitation Tools",
            "burpsuite": "Web Applications",
            "sqlmap": "Database Assessment",
            "hydra": "Password Attacks",
            "john": "Password Attacks",
            "aircrack-ng": "Wireless Attacks",
            "nikto": "Vulnerability Analysis",
            "gobuster": "Web Applications",
            "wpscan": "Web Applications",
            "hashcat": "Password Attacks"
        }
        return categories.get(tool_name, "Uncategorized")
