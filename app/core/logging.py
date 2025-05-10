import logging
import sys
from pythonjsonlogger import jsonlogger
from pathlib import Path
from .config import get_settings

settings = get_settings()

def setup_logging():
    # Створення директорії для логів
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Налаштування формату логування
    if settings.LOG_FORMAT == "json":
        formatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(levelname)s %(name)s %(message)s'
        )
    else:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    # Налаштування файлового логування
    file_handler = logging.FileHandler(
        log_dir / "bot.log",
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Налаштування консольного логування
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Налаштування кореневого логера
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    root_logger.addHandler(file_handler)
    root_logger.addHandler(console_handler)

    # Налаштування логера для aiogram
    aiogram_logger = logging.getLogger("aiogram")
    aiogram_logger.setLevel(settings.LOG_LEVEL)

    return root_logger 