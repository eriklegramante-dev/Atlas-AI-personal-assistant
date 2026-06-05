import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from config.settings import settings

LOGS_DIR = settings.BASE_PATH / "logs"
LOGS_DIR.mkdir(exist_ok=True)

LOG_FILE_PATH = LOGS_DIR / "atlas.log"

class CustomFormatter(logging.Formatter):
    """Formatador personalizado para trazer cores e clareza no terminal do Ubuntu."""
    
    grey = "\x1b[38;20m"
    cyan = "\x1b[36;20m"
    yellow = "\x1b[33;20m"
    red = "\x1b[31;20m"
    bold_red = "\x1b[31;1m"
    reset = "\x1b[0m"
    
    log_format = "%(asctime)s - [%(levelname)s] - (%(filename)s:%(lineno)d) - %(message)s"

    FORMATS = {
        logging.DEBUG: grey + log_format + reset,
        logging.INFO: cyan + log_format + reset,
        logging.WARNING: yellow + log_format + reset,
        logging.ERROR: red + log_format + reset,
        logging.CRITICAL: bold_red + log_format + reset
    }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt, datefmt="%Y-%m-%d %H:%M:%S")
        return formatter.format(record)


def setup_logger() -> logging.Logger:
    """Configura o sistema central de logs da ATLAS."""
    
    numeric_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    
    logger = logging.getLogger("ATLAS")
    logger.setLevel(numeric_level)
    
    if logger.hasHandlers():
        return logger

    console_handler = logging.StreamHandler()
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(CustomFormatter())
    logger.addHandler(console_handler)

    file_handler = RotatingFileHandler(
        LOG_FILE_PATH, 
        maxBytes=5 * 1024 * 1024, 
        backupCount=3, 
        encoding="utf-8"
    )
    file_handler.setLevel(numeric_level)
    
    file_formatter = logging.Formatter(
        "%(asctime)s - [%(levelname)s] - (%(filename)s:%(lineno)d) - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)

    return logger

logger = setup_logger()