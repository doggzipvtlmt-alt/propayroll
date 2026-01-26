from app.core.errors import NotFound
from app.core.security import require_company_id, require_user_id
from app.repositories.notifications_repo import NotificationsRepo

class NotificationsService:
    def list(self, request, query: dict, skip: int, limit: int):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        query = {**query, "company_id": company_id, "user_id": user_id}
        repo = NotificationsRepo()
        items = repo.list(query, skip, limit)
        total = repo.count(query)
        return items, total

    def mark_read(self, request, id: str):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        repo = NotificationsRepo()
        matched = repo.mark_read(id, company_id, user_id)
        if matched == 0:
            raise NotFound("Notification not found")
        return True

    def mark_all_read(self, request):
        company_id = require_company_id(request)
        user_id = require_user_id(request)
        repo = NotificationsRepo()
        count = repo.mark_all_read(company_id, user_id)
        return count
