import logging
import sys
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def log_info(msg: str, *args, **kwargs):
    parts = [msg]
    parts += [str(arg) for arg in args]
    parts += [f"{key}={value}" for key, value in kwargs.items()]
    full_msg = " ".join(parts)
    logger.info(full_msg)


def log_debug(msg: str, *args, **kwargs):
    parts = [msg]
    parts += [str(arg) for arg in args]
    parts += [f"{key}={value}" for key, value in kwargs.items()]
    full_msg = " ".join(parts)
    logger.debug(full_msg)


def log_success(msg: str, *args, **kwargs):
    parts = [msg]
    parts += [str(arg) for arg in args]
    parts += [f"{key}={value}" for key, value in kwargs.items()]
    full_msg = " ".join(parts)
    logger.info(f"SUCCESS: {full_msg}")


def log_warning(msg: str, *args, **kwargs):
    parts = [msg]
    parts += [str(arg) for arg in args]
    parts += [f"{key}={value}" for key, value in kwargs.items()]
    full_msg = " ".join(parts)
    logger.warning(full_msg)


def log_error(msg: str, *args, **kwargs):
    parts = [msg]
    parts += [str(arg) for arg in args]
    parts += [f"{key}={value}" for key, value in kwargs.items()]
    full_msg = " ".join(parts)
    logger.error(full_msg)