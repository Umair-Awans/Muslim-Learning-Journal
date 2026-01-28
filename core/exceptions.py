from typing import Optional


class AppError(Exception):
    """Base class for all application-level errors."""
    pass


class DataError(AppError):
    """Base class for data-related errors."""
    pass


class DataCorruptionError(DataError):
    """Raised when persisted data is unreadable or corrupted."""
    error_message = (
                "Your learning journal data file appears to be corrupted.\n\n"
                "The application will now exit to prevent data loss."
            )

    def __init__(self, message: Optional[str] = None, file_path: Optional[str] = None):
        self.file_path = file_path
        if message is None:
            message = self.error_message
        super().__init__(message)
