import requests
import xml.etree.ElementTree as ET

from core.graph import Graph
from tools.nmap import run_scan

OLLAMA_URL = "http://localhost:11434/v1/chat/completions"
MODEL = "gpt-oss:120b-cloud"


def _ollama_chat(system_msg: str, user_msg: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": user_msg},
        ],
        "max_tokens": 1500,
    }
    r = requests.post(OLLAMA_URL, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]


def generate_report(target: str) -> str:
    """
    Run scans via tools.nmap and format a concise report.
    Includes service/version info for port 22.
    """
    scan_data = run_scan(target)

    # Parse the version-scan XML for port 22 details
    port22_info = ""
    try:
        root = ET.fromstring(scan_data["port22_version_scan"])
        for host in root.findall("host"):
            for port in host.findall("./ports/port"):
                if port.get("portid") == "22":
                    service = port.find("service")
                    if service is None:
                        continue
                    name = service.get("name", "unknown")
                    version = (
                        (service.get("product", "") + " " + service.get("version", ""))
                        .strip()
                    )
                    extra = service.get("extrainfo", "")
                    port22_info = f"Port 22: {name} {version}".strip()
                    if extra:
                        port22_info += f" ({extra})"
    except ET.ParseError:
        port22_info = "Port 22 version data unavailable."

    base_report = (
        f"Nmap Scan Report for {target}\n"
        f"{'-'*40}\n"
        f"{scan_data['syn_scan']}\n"
        f"{'-'*20}\n"
        f"{port22_info}\n"
    )

    # Send to LLM for higher-level analysis
    ai_report = _ollama_chat(
        "You are a cybersecurity analyst. Summarize and assess this nmap scan.",
        base_report,
    )
    return ai_report


# ----------------------------------------------------------------------
# Metatron pipeline stages
# ----------------------------------------------------------------------
def recon(target: str):
    print(f"[{target}] Reconnaissance: gathering info…")


def scan(target: str):
    print(f"[{target}] Scanning: running nmap scans…")


def analyze(target: str):
    print(f"[{target}] Analyzing: generating AI security report…")
    report = generate_report(target)
    print(report)


def report_stage(target: str):
    # For now, just a placeholder – in future you can save to file/DB.
    print(f"[{target}] Reporting stage completed.")


def run_agent(target: str):
    """
    Build a static graph (recon → scan → analyze → report) and walk it.
    """
    g = Graph()

    g.set_handler("recon", recon)
    g.set_handler("scan", scan)
    g.set_handler("analyze", analyze)
    g.set_handler("report", report_stage)

    g.walk(target)
