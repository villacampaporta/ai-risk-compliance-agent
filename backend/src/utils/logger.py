import logging
import sys

# Configuración básica del logger para salida en stdout
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_event(event: str, data: dict):
    logging.info(f"{event}: {data}")
