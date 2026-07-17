import logging
import logging.handlers
from typing import Optional


class SingletonLogger:
    """Singleton logger wrapper around Python's logging module."""

    _instance: "SingletonLogger" = None
    _configured: bool = False

    def __new__(cls, name: Optional[str] = None, *, level: int = logging.INFO, logfile: Optional[str] = None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._logger = logging.getLogger(name or "decentro")
            cls._instance._logger.setLevel(level)
            cls._instance._configure(level=level, logfile=logfile)
        return cls._instance

    def _configure(self, *, level: int, logfile: Optional[str]) -> None:
        if self._configured:
            return

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)

        if logfile:
            file_handler = logging.handlers.RotatingFileHandler(
                logfile,
                maxBytes=10 * 1024 * 1024,
                backupCount=5,
                encoding="utf-8",
            )
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)

        self._logger.propagate = False
        self._configured = True

    @property
    def logger(self) -> logging.Logger:
        """Return the underlying configured Python logger."""
        return self._logger

    def set_level(self, level: int) -> None:
        """Update the logger level at runtime."""
        self._logger.setLevel(level)
        for handler in self._logger.handlers:
            handler.setLevel(level)

    def add_file_handler(self, logfile: str, level: Optional[int] = None) -> None:
        """Add a rotating file handler to the singleton logger."""
        if not level:
            level = self._logger.level

        formatter = logging.Formatter(
            fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = logging.handlers.RotatingFileHandler(
            logfile,
            maxBytes=10 * 1024 * 1024,
            backupCount=5,
            encoding="utf-8",
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        self._logger.addHandler(file_handler)

    def get_logger(self) -> logging.Logger:
        """Return the configured logger for use in application code."""
        return self._logger


def get_logger(name: Optional[str] = None, *, level: int = logging.INFO, logfile: Optional[str] = None) -> logging.Logger:
    """Get the singleton logger instance.

    Args:
        name: Optional logger name. Uses the same logger name for every call.
        level: Logging level for the logger.
        logfile: Optional rotating file path.

    Returns:
        The shared logger instance.
    """
    return SingletonLogger(name, level=level, logfile=logfile).get_logger()
