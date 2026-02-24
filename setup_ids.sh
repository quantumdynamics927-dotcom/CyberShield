#!/bin/bash
# CyberLab Assistant - Intrusion Detection Setup
# Run as: sudo ./setup_ids.sh

set -e

echo "=========================================="
echo "CyberLab Intrusion Detection Setup"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo $0"
    exit 1
fi

echo "[1/4] Installing rkhunter..."
apt update
apt install -y rkhunter

echo "[2/4] Installing chkrootkit..."
apt install -y chkrootkit

echo "[3/4] Configuring rkhunter..."
# Update rkhunter
rkhunter --update

# Set up weekly cron job
cat > /etc/cron.weekly/rkhunter << 'EOF'
#!/bin/bash
rkhunter --check --cronjob --report-warnings-only
EOF
chmod +x /etc/cron.weekly/rkhunter

echo "[4/4] Running initial scan..."
echo ""
echo "--- rkhunter scan ---"
rkhunter --check --sk --propupd

echo ""
echo "--- chkrootkit scan ---"
chkrootkit

echo "=========================================="
echo "Intrusion Detection Setup Complete!"
echo "=========================================="
echo ""
echo "To run scans manually:"
echo "  sudo rkhunter --check"
echo "  sudo chkrootkit"
echo ""
echo "To update rkhunter database:"
echo "  sudo rkhunter --update"
echo "  sudo rkhunter --propupd"
echo ""
echo "Check logs:"
echo "  sudo cat /var/log/rkhunter.log"
