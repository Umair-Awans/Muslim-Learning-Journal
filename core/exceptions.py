from typing import Optional


class AppError(Exception):
    """Base class for all application-level errors."""
    pass


class DataError(AppError):
    """Base class for data-related errors."""
    pass


class DataCorruptionError(DataError):
    """Raised when persisted data is unreadable or corrupted."""
    def __init__(self, message: str, file_path: Optional[str] = None):
        self.file_path = file_path
        super().__init__(message)
