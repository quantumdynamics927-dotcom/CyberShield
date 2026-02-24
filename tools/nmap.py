import subprocess
import json  # (kept in case you later parse XML to JSON)

def run_scan(target: str) -> dict:
    """
    Perform a full TCP SYN scan and a service-version/default-script scan on
    port 22. Returns a dict with raw XML outputs.
    """
    # Original SYN scan
    syn_cmd = ["nmap", "-sS", "-T4", "-oX", "-", target]
    syn_output = subprocess.check_output(syn_cmd, text=True)

    # Service/version and default script scan on port 22
    version_cmd = ["nmap", "-sV", "-sC", "-p", "22", "-oX", "-", target]
    version_output = subprocess.check_output(version_cmd, text=True)

    result = {
        "target": target,
        "syn_scan": syn_output,
        "port22_version_scan": version_output,
    }
    return result
