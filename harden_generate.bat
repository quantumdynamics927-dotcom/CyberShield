@echo off
REM CyberLab Assistant - Security Hardening Script Generator
REM This script generates the hardening script for Linux systems

echo ==========================================
echo CyberLab Security Hardening Script Generator
echo ==========================================
echo.

set /p TARGET_HOST="Enter target Linux host IP: "
set /p SSH_USER="Enter SSH username: "

echo.
echo Generating hardening script...
echo.

REM Create the hardening script content
(
echo @echo off
echo echo ==========================================
echo echo CyberLab Security Hardening Script
echo echo ==========================================
echo.
echo rem Run these commands on the target Linux system:
echo.
echo rem Update system:
echo sudo apt update ^&^& sudo apt upgrade -y
echo.
echo rem SSH Hardening:
echo sudo cat ^> /etc/ssh/sshd_config.d/hardening.conf ^<^< EOF
echo # Disable root login
echo PermitRootLogin no
echo # Disable password auth
echo PasswordAuthentication no
echo # Strong ciphers
echo Ciphers chacha20-poly1305@openssh.com^,aes256-gcm@openssh.com^,aes128-gcm@openssh.com
echo # Strong MACs
echo MACs hmac-sha2-512-etm@openssh.com^,hmac-sha2-256-etm@openssh.com
echo # Strong key exchange
echo KexAlgorithms curve25519-sha256^,ecdh-sha2-nistp256
echo X11Forwarding no
echo AllowTcpForwarding no
echo ClientAliveInterval 300
echo EOF
echo sudo systemctl restart sshd
echo.
echo rem MySQL Hardening:
echo sudo sed -i 's/^bind-address.*/bind-address = 127.0.0.1/' /etc/mysql/mysql.conf.d/mysqld.cnf
echo sudo systemctl restart mysql
echo.
echo rem Firewall:
echo sudo ufw default deny incoming
echo sudo ufw default allow outgoing
echo sudo ufw allow 22/tcp
echo sudo ufw allow 80/tcp
echo sudo ufw allow 443/tcp
echo sudo ufw --force enable
echo.
echo rem Fail2Ban:
echo sudo apt install -y fail2ban
echo sudo systemctl enable fail2ban
echo sudo systemctl start fail2ban
echo.
echo echo Hardening complete!
) > harden_%TARGET_HOST%.bat

echo Generated: harden_%TARGET_HOST%.bat
echo.
echo To use:
echo 1. Copy the commands to your Linux system
echo 2. Or use: ssh %SSH_USER%@%TARGET_HOST% "sudo bash -c '...'"
echo.
pause
