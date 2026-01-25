from pymongo.errors import DuplicateKeyError
from app.core.errors import NotFound, Conflict
from app.repositories.employees_repo import EmployeesRepo
from app.core.audit import audit

class EmployeesService:
    def list(self, request, query: dict, skip: int, limit: int, sort):
        repo = EmployeesRepo()
        items = repo.list(query, skip, limit, sort)
        total = repo.count(query)
        return items, total

    def get(self, request, id: str):
        repo = EmployeesRepo()
        doc = repo.get(id)
        if not doc:
            raise NotFound("Employee not found")
        return doc

    def create(self, request, data: dict):
        repo = EmployeesRepo()
        try:
            doc = repo.create(data)
        except DuplicateKeyError:
            raise Conflict("employee_code already exists", {"field": "employee_code"})
        audit(request, "CREATE", "employee", doc["id"], {"employee_code": doc.get("employee_code")})
        return doc

    def update(self, request, id: str, data: dict):
        repo = EmployeesRepo()
        matched, doc = repo.update(id, data)
        if matched == 0 or not doc:
            raise NotFound("Employee not found")
        audit(request, "UPDATE", "employee", id, {"employee_code": doc.get("employee_code")})
        return doc

    def delete(self, request, id: str):
        repo = EmployeesRepo()
        deleted = repo.delete(id)
        if deleted == 0:
            raise NotFound("Employee not found")
        audit(request, "DELETE", "employee", id)
        return True
