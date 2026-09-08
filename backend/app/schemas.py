"""Pydantic request/response models. These are the API's public contract."""
import datetime
from typing import Literal

from pydantic import BaseModel, Field, ConfigDict

from .models import Sector


# ---------- Reference data ----------

class CardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    currency: str
    credit_limit: float
    monthly_burden: float
    is_demo_value: bool
    display_order: int


class EmployerOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    sector: Sector
    salary_transfer_required: bool
    guarantor_allowed: bool
    max_dpr: float
    is_demo_value: bool


# ---------- Assessment request ----------

class AssessmentRequest(BaseModel):
    customer_name: str = Field(min_length=2, max_length=160)
    age: int = Field(ge=18, le=100)
    account_number: str = Field(min_length=3, max_length=60)

    salary: float = Field(gt=0)
    other_income: float = Field(default=0, ge=0)
    existing_facilities: float = Field(default=0, ge=0)

    salary_transferred: bool = True
    guarantor_available: bool = False

    card_id: str
    employer_id: str

    notes: str = Field(default="", max_length=2000)


# ---------- Assessment response ----------

class RuleCheckOut(BaseModel):
    key: str
    label: str
    passed: bool
    detail: str


class AssessmentResult(BaseModel):
    id: int
    created_at: datetime.datetime

    status: Literal["eligible", "not_eligible"]
    decision_summary: str

    customer_name: str
    age: int
    account_number: str

    card: CardOut
    employer: EmployerOut

    salary: float
    other_income: float
    approved_income: float
    existing_facilities: float
    card_monthly_burden: float
    total_monthly_burden: float
    dpr: float
    max_dpr_applied: float

    checks: list[RuleCheckOut]
    assumptions: list[str]

    model_config = ConfigDict(from_attributes=True)


class AssessmentListItem(BaseModel):
    id: int
    created_at: datetime.datetime
    customer_name: str
    status: Literal["eligible", "not_eligible"]
    dpr: float
    card_id: str
    employer_id: str

    model_config = ConfigDict(from_attributes=True)
