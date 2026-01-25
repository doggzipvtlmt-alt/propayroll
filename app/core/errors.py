class AppError(Exception):
    status_code = 400
    code = "BAD_REQUEST"

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

class NotFound(AppError):
    status_code = 404
    code = "NOT_FOUND"

class Conflict(AppError):
    status_code = 409
    code = "CONFLICT"

class InvalidId(AppError):
    status_code = 400
    code = "INVALID_ID"

class DatabaseDown(AppError):
    status_code = 503
    code = "DATABASE_DOWN"

class InvalidPagination(AppError):
    status_code = 400
    code = "INVALID_PAGINATION"

class InvalidDate(AppError):
    status_code = 400
    code = "INVALID_DATE"
