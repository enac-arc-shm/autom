import logging
import subprocess

# Configuración del logger
logging.basicConfig(
    filename='systemctl_logs.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_service_status(service_name):
    """Obtiene el estado de un servicio usando systemctl"""
    try:
        result = subprocess.run(['systemctl', 'status', service_name], capture_output=True, text=True)
        if result.returncode == 0:
            logging.info(f"Service {service_name} is running")
        else:
            logging.warning(f"Service {service_name} is not running")
        return result.stdout
    except Exception as e:
        logging.error(f"Error checking status of service {service_name}: {e}")
        return None

def log_service_status(services):
    """Registra el estado de los servicios especificados"""
    for service in services:
        status = get_service_status(service)
        if status:
            logging.info(f"Status of {service}:\n{status}")

if __name__ == "__main__":
    services_to_check = ['sshd', 'virtualbox.service', 'NetworkManager.service']  # Añade los servicios que quieres monitorear
    log_service_status(services_to_check)