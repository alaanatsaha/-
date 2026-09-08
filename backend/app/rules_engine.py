from __future__ import annotations

"""
Rules Engine
============

This is the one file that encodes the bank's underwriting logic. Every
other module (API routes, report generator) only ever calls
`RulesEngine.run(...)` and reads the `AssessmentOutcome` it returns —
none of them know *how* eligibility is decided.

Design:
- Each business rule is its own small class implementing `Rule.evaluate()`.
- `RulesEngine` runs every registered rule in order and combines them.
- Adding a new rule = add one class + register it in `default_rules()`.
  No other file needs to change.

The concrete numbers used here (credit-card monthly burden, max DPR per
sector, salary-transfer / guarantor requirement) come from the `Card`
and `Employer` rows in the database, NOT from hard-coded constants —
see backend/app/seed_data.py for where those starting values live and
which ones are officially published vs. demo placeholders.
"""
from dataclasses import dataclass, field

from .models import Card, Employer


@dataclass
class AssessmentContext:
    """Everything a rule might need to evaluate, in one place."""

    age: int
    salary: float
    other_income: float
    existing_facilities: float
    salary_transferred: bool
    guarantor_available: bool
    card: Card
    employer: Employer

    # Computed once up-front, reused by multiple rules
    approved_income: float = field(init=False)
    card_monthly_burden: float = field(init=False)
    total_monthly_burden: float = field(init=False)
    dpr: float = field(init=False)

    def __post_init__(self):
        self.approved_income = self.salary + self.other_income
        self.card_monthly_burden = self.card.monthly_burden
        self.total_monthly_burden = self.card_monthly_burden + self.existing_facilities
        self.dpr = (
            (self.total_monthly_burden / self.approved_income) * 100
            if self.approved_income > 0
            else 100.0
        )


@dataclass
class RuleCheck:
    key: str
    label: str
    passed: bool
    detail: str


class Rule:
    """Base class for a single underwriting rule."""

    key: str = "rule"
    label: str = "Rule"

    def evaluate(self, ctx: AssessmentContext) -> RuleCheck:
        raise NotImplementedError


class MinimumAgeRule(Rule):
    key = "age"
    label = "الحد الأدنى للعمر"
    MIN_AGE = 18

    def evaluate(self, ctx: AssessmentContext) -> RuleCheck:
        passed = ctx.age >= self.MIN_AGE
        detail = "مستوفى" if passed else f"العمر أقل من الحد الأدنى ({self.MIN_AGE} سنة)"
        return RuleCheck(self.key, self.label, passed, detail)


class SalaryTransferRule(Rule):
    """
    Mirrors the published condition on the bank's card pages: salary
    transfer is required, OR — if not transferred — a salary-transfer
    guarantor may be provided instead (where the employer profile
    allows a guarantor at all).
    """

    key = "salary_transfer"
    label = "تحويل الراتب / ضمان بديل"

    def evaluate(self, ctx: AssessmentContext) -> RuleCheck:
        if not ctx.employer.salary_transfer_required:
            return RuleCheck(self.key, self.label, True, "غير مطلوب لهذه الجهة")

        if ctx.salary_transferred:
            return RuleCheck(self.key, self.label, True, "الراتب محوَّل للبنك")

        if ctx.employer.guarantor_allowed and ctx.guarantor_available:
            return RuleCheck(self.key, self.label, True, "متوفر عبر كفيل محوِّل راتب")

        detail = (
            "الراتب غير محوَّل ولا يوجد كفيل محوِّل راتب"
            if ctx.employer.guarantor_allowed
            else "الراتب غير محوَّل، ولا يُقبل كفيل بديل لهذه الجهة"
        )
        return RuleCheck(self.key, self.label, False, detail)


class DebtBurdenRatioRule(Rule):
    """
    DPR = total monthly burden (existing facilities + new card burden)
    divided by approved monthly income, must stay at or below the
    employer/sector's maximum.
    """

    key = "dpr"
    label = "نسبة عبء الدين (DPR)"

    def evaluate(self, ctx: AssessmentContext) -> RuleCheck:
        passed = ctx.dpr <= ctx.employer.max_dpr
        detail = f"{ctx.dpr:.2f}% من الحد الأقصى {ctx.employer.max_dpr:.0f}%"
        return RuleCheck(self.key, self.label, passed, detail)


@dataclass
class AssessmentOutcome:
    status: str  # "eligible" | "not_eligible"
    decision_summary: str
    checks: list[RuleCheck]
    context: AssessmentContext


class RulesEngine:
    """Runs a configured list of rules against a context and combines them."""

    def __init__(self, rules: list[Rule] | None = None):
        self.rules = rules if rules is not None else self.default_rules()

    @staticmethod
    def default_rules() -> list[Rule]:
        return [
            SalaryTransferRule(),
            DebtBurdenRatioRule(),
            MinimumAgeRule(),
        ]

    def run(self, ctx: AssessmentContext) -> AssessmentOutcome:
        checks = [rule.evaluate(ctx) for rule in self.rules]
        eligible = all(c.passed for c in checks)

        if eligible:
            summary = "الطلب يجتاز قواعد التقييم الأولي التجريبية ويمكن رفعه للجهة المختصة للمراجعة النهائية."
        else:
            failed_labels = "، ".join(c.label for c in checks if not c.passed)
            summary = f"فشل في: {failed_labels}"

        return AssessmentOutcome(
            status="eligible" if eligible else "not_eligible",
            decision_summary=summary,
            checks=checks,
            context=ctx,
        )


# Assumptions surfaced to the UI / reports so nothing reads as an
# official bank policy that hasn't actually been confirmed.
ASSUMPTIONS = [
    "قيم عبء البطاقات الشهرية في هذا الإصدار افتراضية للتطوير (Demo)، وليست بالضرورة القيم الفعلية.",
    "حدود DPR القطاعية (حكومي/خاص) في هذا الإصدار افتراضية للتطوير، إلى حين توفر السياسة الداخلية الرسمية.",
    "هذه النتيجة أولية وليست قرارًا ائتمانيًا نهائيًا؛ القرار النهائي يخضع لسياسات وإجراءات البنك المعتمدة.",
]
