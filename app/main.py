from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import employees, leaves

app = FastAPI(title="HRMS 0.1", version="0.1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(employees.router)
app.include_router(leaves.router)

@app.get("/")
def root():
    return {"ok": True, "service": "HRMS 0.1"}
