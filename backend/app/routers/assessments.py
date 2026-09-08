import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..database import get_db
from ..audit import record_event
from ..excel_export import append_assessment, get_export_path
from ..rules_engine import ASSUMPTIONS, AssessmentContext, RulesEngine

router = APIRouter(prefix="/api/assessments", tags=["assessments"])
logger = logging.getLogger(__name__)

_engine = RulesEngine()


def _get_card_or_404(db: Session, card_id: str) -> models.Card:
    card = db.get(models.Card, card_id)
    if not card:
        raise HTTPException(status_code=404, detail="البطاقة غير موجودة")
    return card


def _get_employer_or_404(db: Session, employer_id: str) -> models.Employer:
    employer = db.get(models.Employer, employer_id)
    if not employer:
        raise HTTPException(status_code=404, detail="الجهة غير موجودة")
    return employer


def _to_result_schema(assessment: models.Assessment) -> schemas.AssessmentResult:
    checks = _recompute_checks(assessment)
    return schemas.AssessmentResult(
        id=assessment.id,
        created_at=assessment.created_at,
        status=assessment.status.value,
        decision_summary=assessment.decision_summary,
        customer_name=assessment.customer_name,
        age=assessment.age,
        account_number=assessment.account_number,
        card=schemas.CardOut.model_validate(assessment.card),
        employer=schemas.EmployerOut.model_validate(assessment.employer),
        salary=assessment.salary,
        other_income=assessment.other_income,
        approved_income=assessment.approved_income,
        existing_facilities=assessment.existing_facilities,
        card_monthly_burden=assessment.card.monthly_burden,
        total_monthly_burden=assessment.total_monthly_burden,
        dpr=assessment.dpr,
        max_dpr_applied=assessment.max_dpr_applied,
        checks=checks,
        assumptions=ASSUMPTIONS,
    )


def _recompute_checks(assessment: models.Assessment) -> list[schemas.RuleCheckOut]:
    """
    Re-runs the rules engine against the stored inputs so GET responses
    show the same per-rule breakdown as the original POST, without
    persisting the breakdown itself (it's fully derivable from the
    stored inputs + current policy data).
    """
    ctx = AssessmentContext(
        age=assessment.age,
        salary=assessment.salary,
        other_income=assessment.other_income,
        existing_facilities=assessment.existing_facilities,
        salary_transferred=assessment.salary_transferred,
        guarantor_available=assessment.guarantor_available,
        card=assessment.card,
        employer=assessment.employer,
    )
    outcome = _engine.run(ctx)
    return [
        schemas.RuleCheckOut(key=c.key, label=c.label, passed=c.passed, detail=c.detail)
        for c in outcome.checks
    ]


@router.post("", response_model=schemas.AssessmentResult, status_code=201)
def create_assessment(request: Request, payload: schemas.AssessmentRequest, db: Session = Depends(get_db)):
    card = _get_card_or_404(db, payload.card_id)
    employer = _get_employer_or_404(db, payload.employer_id)

    ctx = AssessmentContext(
        age=payload.age,
        salary=payload.salary,
        other_income=payload.other_income,
        existing_facilities=payload.existing_facilities,
        salary_transferred=payload.salary_transferred,
        guarantor_available=payload.guarantor_available,
        card=card,
        employer=employer,
    )
    outcome = _engine.run(ctx)

    assessment = models.Assessment(
        customer_name=payload.customer_name,
        age=payload.age,
        account_number=payload.account_number,
        salary=payload.salary,
        other_income=payload.other_income,
        existing_facilities=payload.existing_facilities,
        salary_transferred=payload.salary_transferred,
        guarantor_available=payload.guarantor_available,
        notes=payload.notes,
        card_id=card.id,
        employer_id=employer.id,
        approved_income=ctx.approved_income,
        total_monthly_burden=ctx.total_monthly_burden,
        dpr=ctx.dpr,
        max_dpr_applied=employer.max_dpr,
        status=models.AssessmentStatus(outcome.status),
        decision_summary=outcome.decision_summary,
    )
    db.add(assessment)
    db.commit()
    db.refresh(assessment)
    record_event(db, request, "assessment_created", assessment.id)

    try:
        append_assessment(assessment)
    except Exception:
        # The database record is authoritative; an export failure must not
        # turn a successful assessment into a failed request.
        logger.exception("Could not append assessment %s to the Excel register", assessment.id)

    return _to_result_schema(assessment)


@router.get("", response_model=list[schemas.AssessmentListItem])
def list_assessments(db: Session = Depends(get_db), limit: int = 50):
    rows = (
        db.query(models.Assessment)
        .order_by(models.Assessment.created_at.desc())
        .limit(min(limit, 200))
        .all()
    )
    return [
        schemas.AssessmentListItem(
            id=a.id,
            created_at=a.created_at,
            customer_name=a.customer_name,
            status=a.status.value,
            dpr=a.dpr,
            card_id=a.card_id,
            employer_id=a.employer_id,
        )
        for a in rows
    ]


@router.get("/export.xlsx", response_class=FileResponse)
def download_assessments_excel(request: Request, db: Session = Depends(get_db)):
    export_path = get_export_path()
    if not export_path.exists():
        raise HTTPException(status_code=404, detail="لم يتم تسجيل أي تقييمات في ملف Excel بعد")
    record_event(db, request, "excel_export_downloaded")
    return FileResponse(
        export_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="assessments.xlsx",
    )


@router.get("/{assessment_id}", response_model=schemas.AssessmentResult)
def get_assessment(assessment_id: int, db: Session = Depends(get_db)):
    assessment = (
        db.query(models.Assessment)
        .options(joinedload(models.Assessment.card), joinedload(models.Assessment.employer))
        .filter(models.Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="الدراسة غير موجودة")
    return _to_result_schema(assessment)
