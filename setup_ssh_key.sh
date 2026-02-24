#!/bin/bash
# CyberLab Assistant - SSH Key Setup
# Run on LOCAL machine before connecting to server

set -e

echo "=========================================="
echo "CyberLab SSH Key Setup"
echo "=========================================="

echo "[1/3] Generating SSH key..."
echo "Press Enter to accept default location or enter custom path"
echo ""

# Generate ED25519 key (most secure)
ssh-keygen -t ed25519 -C "cyberlab@$(hostname)"

echo ""
echo "[2/3] Key generated. Now copy to server:"
echo ""
echo "Syntax: ssh-copy-id user@server-ip"
echo ""
echo "Example:"
echo "  ssh-copy-id admin@192.168.1.100"
echo ""

read -p "Enter server user@ip: " server

if [ -n "$server" ]; then
    ssh-copy-id -i ~/.ssh/id_ed25519.pub "$server"
    echo ""
    echo "[3/3] Testing connection..."
    ssh "$server" "echo 'SSH key login successful!'"
else
    echo "Skipped. Run 'ssh-copy-id user@server' manually."
fi

echo ""
echo "=========================================="
echo "To disable password auth on SERVER, run:"
echo "=========================================="
echo "sudo bash -c 'echo PasswordAuthentication no >> /etc/ssh/sshd_config'"
echo "sudo systemctl restart sshd"
echo ""
echo "IMPORTANT: Test key login BEFORE disabling password auth!"
