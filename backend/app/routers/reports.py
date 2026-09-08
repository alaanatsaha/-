from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload

from .. import models
from ..database import get_db
from ..audit import record_event
from ..reports.word_report import generate_word_report
from ..reports.pdf_report import generate_pdf_report

router = APIRouter(prefix="/api/assessments", tags=["reports"])


def _get_assessment_or_404(db: Session, assessment_id: int) -> models.Assessment:
    assessment = (
        db.query(models.Assessment)
        .options(joinedload(models.Assessment.card), joinedload(models.Assessment.employer))
        .filter(models.Assessment.id == assessment_id)
        .first()
    )
    if not assessment:
        raise HTTPException(status_code=404, detail="الدراسة غير موجودة")
    return assessment


@router.get("/{assessment_id}/report.docx")
def download_word_report(request: Request, assessment_id: int, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
    content = generate_word_report(assessment)
    record_event(db, request, "word_report_downloaded", assessment_id)
    filename = f"pib-assessment-{assessment_id}.docx"
    return Response(
        content=content,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{assessment_id}/report.pdf")
def download_pdf_report(request: Request, assessment_id: int, db: Session = Depends(get_db)):
    assessment = _get_assessment_or_404(db, assessment_id)
    content = generate_pdf_report(assessment)
    record_event(db, request, "pdf_report_downloaded", assessment_id)
    filename = f"pib-assessment-{assessment_id}.pdf"
    return Response(
        content=content,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
