import logging
import sys

# Basic configuration for logging to stdout with time and level information
logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def log_event(event: str, data: dict):
    logging.info(f"{event}: {data}")
