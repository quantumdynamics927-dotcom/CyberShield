#!/bin/bash
# CyberLab Assistant - Security Hardening Script
# Run as: sudo ./harden_system.sh

set -e

echo "=========================================="
echo "CyberLab Security Hardening Script"
echo "=========================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root: sudo $0"
    exit 1
fi

echo "[1/5] Updating system..."
apt update && apt upgrade -y

echo "[2/5] Hardening SSH..."
cat > /etc/ssh/sshd_config.d/hardening.conf << 'EOF'
# SSH Hardening Configuration

# Disable root login
PermitRootLogin no

# Disable password authentication
PasswordAuthentication no
PermitEmptyPasswords no

# Use strong ciphers
Ciphers chacha20-poly1305@openssh.com,aes256-gcm@openssh.com,aes128-gcm@openssh.com,aes256-ctr,aes192-ctr,aes128-ctr

# Use strong MACs
MACs hmac-sha2-512-etm@openssh.com,hmac-sha2-256-etm@openssh.com

# Use strong key exchange
KexAlgorithms curve25519-sha256,ecdh-sha2-nistp256

# Disable unused authentication methods
ChallengeResponseAuthentication no
KerberosAuthentication no
GSSAPIAuthentication no

# Security options
X11Forwarding no
AllowTcpForwarding no
AllowAgentForwarding no

# Timeout settings
ClientAliveInterval 300
ClientAliveCountMax 2
LoginGraceTime 60

# Disable empty passwords
IgnoreRhosts yes
HostbasedAuthentication no

# Logging
SyslogFacility AUTH
LogLevel VERBOSE
EOF

echo "[3/5] Securing MySQL..."
# If MySQL is installed
if command -v mysql &> /dev/null; then
    # Backup MySQL config
    cp /etc/mysql/mysql.conf.d/mysqld.cnf /etc/mysql/mysql.conf.d/mysqld.cnf.bak

    # Add security configuration
    cat >> /etc/mysql/mysql.conf.d/mysqld.cnf << 'EOF'

# Security Hardening
bind-address = 127.0.0.1
local_infile = 0
skip_symbolic_links = 1
secure_file_priv = /var/lib/mysql-files
EOF

    echo "MySQL secured. Run 'sudo mysql_secure_installation' for additional setup."
else
    echo "MySQL not found - skipping"
fi

echo "[4/5] Setting up firewall..."
# Install ufw if not present
if ! command -v ufw &> /dev/null; then
    apt install -y ufw
fi

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow specific ports
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS

# Enable firewall
echo "y" | ufw enable

echo "[5/5] Installing fail2ban..."
apt install -y fail2ban

# Configure fail2ban
cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 3600
findtime = 600
maxretry = 5
destemail = admin@localhost
action = %(action_mwl)s

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
EOF

systemctl enable fail2ban
systemctl restart fail2ban

# Restart services
echo "Restarting services..."
systemctl restart sshd
systemctl restart mysql 2>/dev/null || true

echo "=========================================="
echo "Hardening complete!"
echo "=========================================="
echo ""
echo "Recommended next steps:"
echo "1. Set up SSH key authentication"
echo "2. Configure fail2ban email notifications"
echo "3. Set up log monitoring"
echo "4. Regular security updates: apt update && apt upgrade"
echo ""
echo "To check status:"
echo "  ufw status"
echo "  fail2ban-client status"
echo "  systemctl status sshd"
