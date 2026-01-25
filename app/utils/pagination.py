from app.core.errors import InvalidPagination

def normalize_pagination(page: int | None, page_size: int | None) -> tuple[int, int, int]:
    page = page or 1
    page_size = page_size or 10
    if page < 1:
        raise InvalidPagination("page must be >= 1")
    if page_size < 1 or page_size > 100:
        raise InvalidPagination("page_size must be between 1 and 100")
    skip = (page - 1) * page_size
    return page, page_size, skip
