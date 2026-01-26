from datetime import datetime, timezone
from app.core.db import connect, ensure_indexes
from app.core.permissions import ROLE_PERMISSIONS
from app.core.crypto import hash_secret

def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def ensure_company(db):
    company = db.companies.find_one({"name": "Doggzi Pvt Ltd"})
    if company:
        return company
    doc = {
        "name": "Doggzi Pvt Ltd",
        "legal_name": "Doggzi Private Limited",
        "gstin": "29ABCDE1234F1Z5",
        "pan": "ABCDE1234F",
        "address": "Bengaluru, India",
        "phone": "+91-99999-00000",
        "email": "contact@doggzi.example",
        "currency": "INR",
        "timezone": "Asia/Kolkata",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    res = db.companies.insert_one(doc)
    return db.companies.find_one({"_id": res.inserted_id})


def ensure_roles(db, company_id: str):
    for key, perms in ROLE_PERMISSIONS.items():
        existing = db.roles.find_one({"company_id": company_id, "key": key})
        if existing:
            continue
        db.roles.insert_one({
            "company_id": company_id,
            "key": key,
            "name": key.title(),
            "permissions": perms,
            "created_at": now_iso(),
            "updated_at": now_iso(),
        })


def ensure_user(db, company_id: str, full_name: str, email: str, role_key: str, pin: str | None = None, dob: str | None = None):
    existing = db.users.find_one({"company_id": company_id, "email": email})
    if existing:
        return existing
    pin_meta = hash_secret(pin) if pin else {}
    res = db.users.insert_one({
        "company_id": company_id,
        "full_name": full_name,
        "email": email,
        "phone": None,
        "role_key": role_key,
        "status": "active",
        "dob": dob,
        "pin_hash": pin_meta.get("hash"),
        "pin_salt": pin_meta.get("salt"),
        "pin_iterations": pin_meta.get("iterations"),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    })
    return db.users.find_one({"_id": res.inserted_id})


def ensure_employee(db, company_id: str, employee_code: str, full_name: str, user_id: str | None = None, dob: str | None = None):
    existing = db.employees.find_one({"company_id": company_id, "employee_code": employee_code})
    if existing:
        return existing
    res = db.employees.insert_one({
        "company_id": company_id,
        "employee_code": employee_code,
        "full_name": full_name,
        "email": None,
        "phone": None,
        "department": "Engineering",
        "designation": "Engineer",
        "status": "active",
        "user_id": user_id,
        "dob": dob,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    })
    return db.employees.find_one({"_id": res.inserted_id})


def ensure_vault_item(db, company_id: str, owner_user_id: str):
    existing = db.vault_items.find_one({"company_id": company_id, "owner_user_id": owner_user_id})
    if existing:
        return existing
    password_meta = hash_secret("Sup3rSecret!")
    notes_meta = hash_secret("Banking PIN stored securely")
    res = db.vault_items.insert_one({
        "company_id": company_id,
        "owner_user_id": owner_user_id,
        "title": "Personal Bank",
        "username": "employee.one",
        "url": "https://bank.example.com",
        "tags": ["finance", "personal"],
        "password_hash": password_meta.get("hash"),
        "password_salt": password_meta.get("salt"),
        "password_iterations": password_meta.get("iterations"),
        "notes_hash": notes_meta.get("hash"),
        "notes_salt": notes_meta.get("salt"),
        "notes_iterations": notes_meta.get("iterations"),
        "created_at": now_iso(),
        "updated_at": now_iso(),
    })
    return db.vault_items.find_one({"_id": res.inserted_id})


def ensure_notifications(db, company_id: str, user_id: str):
    if db.notifications.count_documents({"company_id": company_id}) > 0:
        return
    db.notifications.insert_one({
        "company_id": company_id,
        "user_id": user_id,
        "title": "Welcome",
        "message": "Welcome to Doggzi Office OS!",
        "type": "success",
        "read": False,
        "created_at": now_iso(),
    })


def ensure_approvals(db, company_id: str, user_id: str):
    if db.approvals.count_documents({"company_id": company_id}) > 0:
        return
    db.approvals.insert_one({
        "company_id": company_id,
        "entity_type": "expense",
        "entity_id": "EXP-0001",
        "workflow_key": "expense_default",
        "current_step": 1,
        "status": "pending",
        "requested_by_user_id": user_id,
        "decided_by_user_id": None,
        "decision_comment": "",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    })


def ensure_leave_request(db, company_id: str, employee_code: str, employee_name: str, requested_by_user_id: str):
    if db.leave_requests.count_documents({"company_id": company_id}) > 0:
        return
    leave_doc = {
        "company_id": company_id,
        "employee_id": employee_code,
        "employee_name": employee_name,
        "leave_type": "Annual",
        "start_date": "2024-06-10",
        "end_date": "2024-06-12",
        "reason": "Family event",
        "status": "pending",
        "approver_comment": "",
        "requested_by_user_id": requested_by_user_id,
        "created_at": now_iso(),
        "updated_at": now_iso(),
    }
    res = db.leave_requests.insert_one(leave_doc)
    db.approvals.insert_one({
        "company_id": company_id,
        "entity_type": "leave",
        "entity_id": str(res.inserted_id),
        "workflow_key": "leave_default",
        "current_step": 1,
        "status": "pending",
        "requested_by_user_id": requested_by_user_id,
        "decided_by_user_id": None,
        "decision_comment": "",
        "created_at": now_iso(),
        "updated_at": now_iso(),
    })


def main():
    db = connect()
    ensure_indexes()

    company = ensure_company(db)
    company_id = str(company["_id"])

    ensure_roles(db, company_id)

    md_user = ensure_user(db, company_id, "Meera Doggzi", "md@doggzi.example", "MD", pin="1234")
    hr_user = ensure_user(db, company_id, "Harsha HR", "hr@doggzi.example", "HR", pin="2345")
    finance_user = ensure_user(db, company_id, "Finley Finance", "finance@doggzi.example", "FINANCE", pin="3456")
    admin_user = ensure_user(db, company_id, "Aarav Admin", "admin@doggzi.example", "ADMIN", pin="4567")
    emp_one = ensure_user(db, company_id, "Esha Employee", "employee1@doggzi.example", "EMPLOYEE", dob="1994-04-12")
    emp_two = ensure_user(db, company_id, "Ravi Employee", "employee2@doggzi.example", "EMPLOYEE", dob="1992-09-08")

    ensure_employee(db, company_id, "EMP-1001", "Esha Employee", str(emp_one["_id"]), dob="1994-04-12")
    ensure_employee(db, company_id, "EMP-1002", "Ravi Employee", str(emp_two["_id"]), dob="1992-09-08")
    ensure_employee(db, company_id, "EMP-9001", "Harsha HR", str(hr_user["_id"]))

    ensure_vault_item(db, company_id, str(emp_one["_id"]))
    ensure_notifications(db, company_id, str(hr_user["_id"]))
    ensure_approvals(db, company_id, str(md_user["_id"]))
    ensure_leave_request(db, company_id, "EMP-1001", "Esha Employee", str(emp_one["_id"]))

    print("Seed complete")
    print("Companies:", db.companies.count_documents({}))
    print("Roles:", db.roles.count_documents({}))
    print("Users:", db.users.count_documents({}))
    print("Employees:", db.employees.count_documents({}))
    print("Vault items:", db.vault_items.count_documents({}))
    print("Notifications:", db.notifications.count_documents({}))
    print("Approvals:", db.approvals.count_documents({}))
    print("Leave requests:", db.leave_requests.count_documents({}))


if __name__ == "__main__":
    main()
