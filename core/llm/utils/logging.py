import logging
import logging.handlers

from ..settings import settings


class FileFilter(logging.Filter):
    def filter(self, record):
        if record.args and isinstance(record.args, dict):
            if record.args.get("file", False) is True:
                return True
        return False


def do_file_logging(logger: logging.Logger, level=logging.INFO):
    logger.setLevel(level)
    for log_handler in settings.logging.handlers:
        log_formatter = logging.Formatter(
            "%(asctime)s - %(name)s [%(process)s] [%(levelname)s] %(message)s"
        )
        filter = FileFilter()
        if log_handler.type == "file":
            file_handler = logging.FileHandler(filename=log_handler.path)
            file_handler.setLevel(level)
            file_handler.setFormatter(log_formatter)
            file_handler.addFilter(filter)
            logger.addHandler(file_handler)
        elif log_handler.type == "rotating_file":
            kwargs = {}
            if log_handler.max_bytes:
                kwargs["maxBytes"] = log_handler.max_bytes
            if log_handler.backup_count:
                kwargs["backupCount"] = log_handler.backup_count
            rotating_file_handler = logging.handlers.RotatingFileHandler(
                filename=log_handler.path, **kwargs
            )
            rotating_file_handler.setLevel(level)
            rotating_file_handler.setFormatter(log_formatter)
            rotating_file_handler.addFilter(filter)
            logger.addHandler(rotating_file_handler)
