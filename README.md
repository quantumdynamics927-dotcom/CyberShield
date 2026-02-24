
# CyberLab Assistant - Asistente Offline de Análisis de Seguridad

Un asistente de línea de comandos basado en SLM para análisis de logs, scans y generación de reportes de seguridad, diseñado para funcionar completamente offline en entornos Kali/Parrot.

## Características

- 🔍 **Análisis de Salidas**

  - Nmap, dirb/gobuster, nikto
  - Logs de sistema y seguridad
  - Wireshark/tcpdump
  - Metasploit

- 📊 **Capacidades**

  - Explicación detallada de hallazgos
  - Resumen de vulnerabilidades
  - Sugerencia de siguientes pasos
  - Generación de playbooks

- 🛠 **Características Técnicas**

  - Funciona 100% offline
  - Integración con pipes Unix
  - Cache local persistente
  - Respuestas en español

## Instalación

```bash

# Clonar repositorio

git clone https://github.com/your-repo/cyberlab-assistant
cd cyberlab-assistant

# Instalar

sudo ./install.sh

# Verificar instalación

explain --version

```text

## Uso

### Análisis de Escaneos

```bash

# Analizar salida de nmap

nmap -sV 192.168.1.0/24 | explain

# Guardar análisis en archivo

nmap -sV -sC target.com | explain > reporte.txt

```text

### Análisis de Logs

```bash

# Analizar logs de autenticación

tail -f /var/log/auth.log | explain

# Analizar capturas de red

tcpdump -r capture.pcap | explain

```text

### Generación de Playbooks

```bash

# Generar siguientes pasos basados en hallazgos

cat nmap_results.txt | next-steps

# Sugerir comandos adicionales

dirb http://target.com | next-steps --format commands

```text

## Configuración

El asistente se puede configurar editando `/etc/cyberlab-assistant/config.json`:

```json

{
  "cache_dir": "/tmp/cyberlab-cache",
  "response_format": "detailed",
  "language": "es",
  "max_context": 2048
}

```text

## Contribuir

Las contribuciones son bienvenidas. Por favor, revisa CONTRIBUTING.md para más detalles.

## Licencia

Este proyecto está licenciado bajo MIT License - ver LICENSE.md para detalles.
# CyberShield
