import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(log_dir, exist_ok=True)

# Create log file name with date
log_file = os.path.join(log_dir, 'app.log')

# Set up logger
logging.basicConfig(
    filename=log_file,
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Optional: also log to terminal
console = logging.StreamHandler()
console.setLevel(logging.INFO)
formatter = logging.Formatter('[%(levelname)s] %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)

# You can now import logging and use:
# logging.info("message")
# logging.error("message")
# logging.debug("message")
