"""
Initial reference data for Card and Employer.

Marked per-row with `is_demo_value`:
- Card names (Platinum / World / World Elite) reflect products actually
  listed on the bank's public cards page — the card LIMIT and MONTHLY
  BURDEN figures here are still Demo placeholders for development.
- Employer salary-transfer / guarantor conditions mirror what's
  published on the World card's terms page. The specific max-DPR
  percentages (25% / 40%) are Demo placeholders, not a published number.

Replace the demo values (or add rows) once the bank provides the
official internal policy document — no code changes needed, just data.
"""
from sqlalchemy.orm import Session

from .models import Card, Employer, Sector


def seed(db: Session) -> None:
    if db.query(Card).count() == 0:
        db.add_all(
            [
                Card(
                    id="platinum",
                    name="Platinum",
                    currency="USD",
                    credit_limit=3000,
                    monthly_burden=150,
                    is_demo_value=True,
                    display_order=1,
                ),
                Card(
                    id="world",
                    name="World",
                    currency="USD",
                    credit_limit=5000,
                    monthly_burden=250,
                    is_demo_value=True,
                    display_order=2,
                ),
                Card(
                    id="world_elite",
                    name="World Elite",
                    currency="USD",
                    credit_limit=7000,
                    monthly_burden=350,
                    is_demo_value=True,
                    display_order=3,
                ),
            ]
        )

    if db.query(Employer).count() == 0:
        db.add_all(
            [
                Employer(
                    id="gov_general",
                    name="قطاع حكومي - نموذج",
                    sector=Sector.government,
                    salary_transfer_required=True,
                    guarantor_allowed=False,
                    max_dpr=25,
                    is_demo_value=True,
                ),
                Employer(
                    id="private_general",
                    name="قطاع خاص - نموذج",
                    sector=Sector.private,
                    salary_transfer_required=True,
                    guarantor_allowed=True,
                    max_dpr=40,
                    is_demo_value=True,
                ),
            ]
        )

    db.commit()
