from datetime import datetime, timedelta
from app.core.db import require_db
from app.core.security import require_company_id, require_user_id

class DashboardService:
    def summary(self, request):
        db = require_db()
        company_id = require_company_id(request)
        require_user_id(request)
        headcount = db.employees.count_documents({"company_id": company_id})
        active = db.employees.count_documents({"company_id": company_id, "status": "active"})
        pending_leaves = db.leave_requests.count_documents({"company_id": company_id, "status": "pending"})

        # attendance "today" based on date string YYYY-MM-DD
        today = datetime.now().strftime("%Y-%m-%d")
        present_today = db.attendance.count_documents({"company_id": company_id, "date": today, "status": "present"})

        # new joiners last 30 days (string compare works only if YYYY-MM-DD; we assume that)
        cutoff = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        new_joiners = db.employees.count_documents({"company_id": company_id, "join_date": {"$gte": cutoff}})

        # birthday count (only if dob exists in YYYY-MM-DD); keep simple
        upcoming_birthdays = 0

        return {
            "headcount": headcount,
            "active_count": active,
            "present_today_count": present_today,
            "pending_leaves_count": pending_leaves,
            "new_joiners_30d_count": new_joiners,
            "upcoming_birthdays_30d_count": upcoming_birthdays,
        }
