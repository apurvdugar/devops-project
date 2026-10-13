from datetime import datetime
from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, EmailStr, Field

LoanType = Literal["personal", "home", "auto", "education"]
LoanStatus = Literal["submitted", "under_review", "approved", "rejected", "disbursed"]


class LoanCreate(BaseModel):
    applicant_name: str = Field(min_length=1, max_length=200)
    email: EmailStr
    loan_type: LoanType
    principal_amount: Decimal = Field(gt=0, le=Decimal("9999999999.99"))
    annual_interest_rate: Decimal = Field(ge=1, le=40)
    tenure_months: int = Field(ge=6, le=360)


class LoanUpdate(BaseModel):
    applicant_name: str | None = Field(default=None, min_length=1, max_length=200)
    email: EmailStr | None = None
    loan_type: LoanType | None = None
    principal_amount: Decimal | None = Field(default=None, gt=0, le=Decimal("9999999999.99"))
    annual_interest_rate: Decimal | None = Field(default=None, ge=1, le=40)
    tenure_months: int | None = Field(default=None, ge=6, le=360)


class StatusUpdate(BaseModel):
    status: LoanStatus


class LoanOut(BaseModel):
    id: int
    applicant_name: str
    email: str
    loan_type: str
    principal_amount: Decimal
    annual_interest_rate: Decimal
    tenure_months: int
    status: str
    emi: Decimal
    created_at: datetime
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)


class StatsOut(BaseModel):
    total: int
    approved: int
    pending: int
    disbursed_total: Decimal
    average_loan_size: Decimal

