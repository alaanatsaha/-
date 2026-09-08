from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/api/employers", tags=["employers"])


@router.get("", response_model=list[schemas.EmployerOut])
def list_employers(db: Session = Depends(get_db)):
    return db.query(models.Employer).order_by(models.Employer.name).all()
