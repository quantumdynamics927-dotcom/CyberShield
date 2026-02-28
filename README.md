# CyberShield – Offline Security Analysis Assistant

A command-line assistant (SLM-based) for analyzing logs, scan outputs, and generating security reports. Designed to run completely offline.

---

## Features

### Output Analysis
- Nmap, dirb/gobuster, Nikto
- System and security logs
- Wireshark/tcpdump captures
- Metasploit output

### Capabilities
- Detailed explanation of findings
- Vulnerability summaries
- Suggestions for next steps
- Playbook generation

### Technical Characteristics
- 100% offline operation
- Integration with Unix pipes
- Persistent local cache
- Modular and extensible design

---

## Installation

```bash
# Clone the repository
git clone https://github.com/quantumdynamics927-dotcom/CyberShield
cd CyberShield

# Install dependencies
sudo ./install.sh

# Verify installation
explain --version
```

---

## Usage

### Scan Analysis

```bash
# Analyze Nmap output
nmap -sV 192.168.1.0/24 | explain

# Save analysis to a file
nmap -sV -sC target.com | explain > report.txt
```

### Log Analysis

```bash
# Analyze authentication logs
tail -f /var/log/auth.log | explain

# Analyze network captures
tcpdump -r capture.pcap | explain
```

### Playbook Generation

```bash
# Generate next steps based on findings
cat nmap_results.txt | next-steps

# Suggest additional commands
dirb http://target.com | next-steps --format commands
```

---

## Configuration

Edit the config file at:

```
/etc/cyberlab-assistant/config.json
```

Example:

```json
{
  "cache_dir": "/tmp/cyberlab-cache",
  "response_format": "detailed",
  "language": "en",
  "max_context": 2048
}
```

---

## Requirements

- Kali Linux / Parrot OS (recommended)
- Python 3.8+
- Common Kali tools: nmap, dirb, gobuster, nikto, tcpdump

---

## Contributing

Contributions are welcome! Please open an issue or pull request with improvements, new analysis patterns, or additional tool integrations.

---

## Disclaimer

This tool is intended for **legal and authorized use only**, such as lab environments, CTFs, and penetration testing engagements with explicit written permission. Misuse is the sole responsibility of the user.

---

## License

MIT License – see `LICENSE.md` for details.
