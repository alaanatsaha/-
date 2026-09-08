from __future__ import annotations

"""
ORM models.

Card and Employer hold the configurable "policy" data — the values a
policy/product team would actually change over time. Keeping them as DB
rows (rather than hard-coded constants) means an admin screen or a
direct DB edit can update limits/DPR caps later without a code deploy.

Assessment stores every submitted study and its computed result, so the
report generator (Word/PDF) can regenerate a document for any past
assessment by id, and so the branch can keep a history of studies.
"""
import datetime
import enum
from typing import Optional

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Sector(str, enum.Enum):
    government = "government"
    private = "private"


class AssessmentStatus(str, enum.Enum):
    eligible = "eligible"
    not_eligible = "not_eligible"


class AuditLog(Base):
    """Immutable operational trail for review and incident investigation."""

    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow, nullable=False
    )
    action: Mapped[str] = mapped_column(String(80), nullable=False)
    actor: Mapped[str] = mapped_column(String(160), default="anonymous", nullable=False)
    assessment_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    ip_address: Mapped[str] = mapped_column(String(64), default="unknown", nullable=False)
    user_agent: Mapped[str] = mapped_column(String(512), default="", nullable=False)


class Card(Base):
    """A credit card product (Platinum / World / World Elite / ...)."""

    __tablename__ = "cards"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)  # e.g. "world"
    name: Mapped[str] = mapped_column(String(80))                   # e.g. "World"
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    credit_limit: Mapped[float] = mapped_column(Float)
    monthly_burden: Mapped[float] = mapped_column(Float)
    is_demo_value: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    assessments: Mapped[list["Assessment"]] = relationship(back_populates="card")


class Employer(Base):
    """
    A sector/employer profile that carries the underwriting rules that
    apply to it: whether salary transfer is required, whether a
    salary-transfer guarantor is accepted instead, and the maximum DPR.
    """

    __tablename__ = "employers"

    id: Mapped[str] = mapped_column(String(40), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    sector: Mapped[Sector] = mapped_column(Enum(Sector))
    salary_transfer_required: Mapped[bool] = mapped_column(Boolean, default=True)
    guarantor_allowed: Mapped[bool] = mapped_column(Boolean, default=False)
    max_dpr: Mapped[float] = mapped_column(Float)
    is_demo_value: Mapped[bool] = mapped_column(Boolean, default=True)

    assessments: Mapped[list["Assessment"]] = relationship(back_populates="employer")


class Assessment(Base):
    """A single preliminary eligibility study submitted by a branch employee."""

    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime, default=datetime.datetime.utcnow
    )

    # Customer-entered data
    customer_name: Mapped[str] = mapped_column(String(160))
    age: Mapped[int] = mapped_column(Integer)
    account_number: Mapped[str] = mapped_column(String(60))
    salary: Mapped[float] = mapped_column(Float)
    other_income: Mapped[float] = mapped_column(Float, default=0)
    existing_facilities: Mapped[float] = mapped_column(Float, default=0)
    salary_transferred: Mapped[bool] = mapped_column(Boolean, default=True)
    guarantor_available: Mapped[bool] = mapped_column(Boolean, default=False)
    notes: Mapped[str] = mapped_column(Text, default="")

    card_id: Mapped[str] = mapped_column(ForeignKey("cards.id"))
    employer_id: Mapped[str] = mapped_column(ForeignKey("employers.id"))

    # Computed results (stored so the report can be regenerated later
    # without re-running the rules engine against possibly-changed policy data)
    approved_income: Mapped[float] = mapped_column(Float)
    total_monthly_burden: Mapped[float] = mapped_column(Float)
    dpr: Mapped[float] = mapped_column(Float)
    max_dpr_applied: Mapped[float] = mapped_column(Float)
    status: Mapped[AssessmentStatus] = mapped_column(Enum(AssessmentStatus))
    decision_summary: Mapped[str] = mapped_column(Text)

    card: Mapped["Card"] = relationship(back_populates="assessments")
    employer: Mapped["Employer"] = relationship(back_populates="assessments")
