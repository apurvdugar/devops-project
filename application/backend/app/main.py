from fastapi import Depends, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from prometheus_fastapi_instrumentator import Instrumentator
from decimal import Decimal

from .config import settings
from .db import Base, engine, get_db
from .loans import calculate_emi, validate_transition
from .models import LoanApplication
from .schemas import LoanCreate, LoanOut, LoanUpdate, StatsOut, StatusUpdate

app = FastAPI(title=settings.app_name, version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
Instrumentator().instrument(app).expose(app, endpoint="/metrics")

@app.on_event("startup")
def startup():
    # Production containers run Alembic before Uvicorn; create_all keeps tests self-contained.
    Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"service": settings.app_name, "version": "1.0.0", "docs": "/docs"}

@app.get("/health")
def health():
    return {"status": "UP"}

@app.get("/ready")
def ready(db: Session = Depends(get_db)):
    db.execute(select(func.count(LoanApplication.id)))
    return {"status": "READY"}

@app.get("/api/loans", response_model=list[LoanOut])
def list_loans(
    status: str | None = Query(default=None),
    loan_type: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    stmt = select(LoanApplication).order_by(LoanApplication.id.desc())
    if status:
        stmt = stmt.where(LoanApplication.status == status)
    if loan_type:
        stmt = stmt.where(LoanApplication.loan_type == loan_type)
    return list(db.scalars(stmt))

@app.get("/api/loans/stats", response_model=StatsOut)
def stats(db: Session = Depends(get_db)):
    rows = db.execute(select(LoanApplication.status, func.count(LoanApplication.id)).group_by(LoanApplication.status)).all()
    counts = {s: c for s, c in rows}
    total = sum(counts.values())
    approved = counts.get("approved", 0)
    pending = counts.get("submitted", 0) + counts.get("under_review", 0)
    disbursed_total = db.execute(
        select(func.coalesce(func.sum(LoanApplication.principal_amount), 0)).where(LoanApplication.status == "disbursed")
    ).scalar_one()
    avg = db.execute(select(func.coalesce(func.avg(LoanApplication.principal_amount), 0))).scalar_one()
    return StatsOut(
        total=total,
        approved=approved,
        pending=pending,
        disbursed_total=Decimal(disbursed_total),
        average_loan_size=Decimal(avg),
    )

@app.get("/api/loans/{loan_id}", response_model=LoanOut)
def get_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.get(LoanApplication, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    return loan

@app.post("/api/loans", response_model=LoanOut, status_code=status.HTTP_201_CREATED)
def create_loan(payload: LoanCreate, db: Session = Depends(get_db)):
    emi = calculate_emi(payload.principal_amount, payload.annual_interest_rate, payload.tenure_months)
    loan = LoanApplication(**payload.model_dump(), status="submitted", emi=emi)
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan

@app.put("/api/loans/{loan_id}", response_model=LoanOut)
def update_loan(loan_id: int, payload: LoanUpdate, db: Session = Depends(get_db)):
    loan = db.get(LoanApplication, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(loan, key, value)
    # Recompute EMI if loan terms changed
    loan.emi = calculate_emi(loan.principal_amount, loan.annual_interest_rate, loan.tenure_months)
    db.commit()
    db.refresh(loan)
    return loan

@app.patch("/api/loans/{loan_id}/status", response_model=LoanOut)
def change_status(loan_id: int, payload: StatusUpdate, db: Session = Depends(get_db)):
    loan = db.get(LoanApplication, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    validate_transition(loan.status, payload.status)
    loan.status = payload.status
    db.commit()
    db.refresh(loan)
    return loan

@app.delete("/api/loans/{loan_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_loan(loan_id: int, db: Session = Depends(get_db)):
    loan = db.get(LoanApplication, loan_id)
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    db.delete(loan)
    db.commit()

