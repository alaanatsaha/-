"""
Word (.docx) assessment report generator, using python-docx.

Kept deliberately separate from the PDF generator: they share the same
data (an `Assessment` ORM row) but each library has its own layout
model, so trying to share drawing code between them would fight both
APIs. `build_report_data()` is the shared step — it turns the ORM row
into plain dicts/strings so neither generator touches SQLAlchemy directly.
"""
import io
import os

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor, Cm, Inches

from ..models import Assessment
from ..rules_engine import ASSUMPTIONS

PIB_BLUE_DARK = RGBColor(0x00, 0x3B, 0x70)
PIB_BLUE = RGBColor(0x07, 0x5B, 0x91)
PIB_BLUE_LIGHT = "EAF3F9"
PIB_GOLD = RGBColor(0xF4, 0xC4, 0x00)
INK = RGBColor(0x18, 0x32, 0x4A)
MUTED = RGBColor(0x62, 0x75, 0x88)
DANGER = RGBColor(0xA2, 0x3B, 0x34)
_LOGO_PATH = os.path.join(os.path.dirname(__file__), "fonts", "pib-logo.png")
_FONT_NAME = "PIBFontRG"


def build_report_data(assessment: Assessment) -> dict:
    """Flatten the ORM row (+ its relationships) into plain data for rendering."""
    status_ar = "مؤهل مبدئيًا" if assessment.status.value == "eligible" else "غير مؤهل مبدئيًا"
    return {
        "id": assessment.id,
        "created_at": assessment.created_at.strftime("%Y-%m-%d %H:%M"),
        "status_ar": status_ar,
        "eligible": assessment.status.value == "eligible",
        "decision_summary": assessment.decision_summary,
        "customer_name": assessment.customer_name,
        "age": assessment.age,
        "account_number": assessment.account_number,
        "card_name": assessment.card.name,
        "card_limit": assessment.card.credit_limit,
        "card_currency": assessment.card.currency,
        "employer_name": assessment.employer.name,
        "salary": assessment.salary,
        "other_income": assessment.other_income,
        "approved_income": assessment.approved_income,
        "existing_facilities": assessment.existing_facilities,
        "card_monthly_burden": assessment.card.monthly_burden,
        "total_monthly_burden": assessment.total_monthly_burden,
        "dpr": assessment.dpr,
        "max_dpr": assessment.max_dpr_applied,
        "notes": assessment.notes or "",
    }


def generate_word_report(assessment: Assessment) -> bytes:
    data = build_report_data(assessment)
    doc = Document()

    section = doc.sections[0]
    section.page_width = Cm(21)
    section.page_height = Cm(29.7)

    # ---- Official bank header ----
    header_table = doc.add_table(rows=1, cols=2)
    header_table.alignment = WD_TABLE_ALIGNMENT.CENTER
    logo_cell = header_table.rows[0].cells[0]
    logo_para = logo_cell.paragraphs[0]
    logo_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
    logo_para.add_run().add_picture(_LOGO_PATH, width=Cm(4.3))
    cell = header_table.rows[0].cells[1]
    cell_para = cell.paragraphs[0]
    cell_para.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = cell_para.add_run("تقرير دراسة أولية لأهلية بطاقة ائتمانية")
    run.font.size = Pt(14)
    run.font.bold = True
    run.font.color.rgb = PIB_BLUE_DARK
    run.font.name = _FONT_NAME
    _shade_cell(cell, PIB_BLUE_LIGHT)
    _set_cell_border(header_table.rows[0].cells[0], "F4C400")
    _set_cell_border(header_table.rows[0].cells[1], "F4C400")

    doc.add_paragraph()

    meta = doc.add_paragraph()
    meta.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    meta_run = meta.add_run(
        f"رقم الدراسة: {data['id']}    |    تاريخ الدراسة: {data['created_at']}"
    )
    meta_run.font.size = Pt(10)
    meta_run.font.color.rgb = MUTED

    # ---- Result banner ----
    doc.add_paragraph()
    result_p = doc.add_paragraph()
    result_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    result_run = result_p.add_run(f"النتيجة الأولية: {data['status_ar']}")
    result_run.font.size = Pt(16)
    result_run.font.bold = True
    result_run.font.color.rgb = PIB_BLUE if data["eligible"] else DANGER
    result_run.font.name = _FONT_NAME

    summary_p = doc.add_paragraph()
    summary_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    summary_run = summary_p.add_run(data["decision_summary"])
    summary_run.font.size = Pt(10.5)
    summary_run.font.color.rgb = INK

    # ---- Customer data ----
    _add_section_title(doc, "بيانات العميل")
    _add_kv_table(
        doc,
        [
            ("اسم العميل", data["customer_name"]),
            ("العمر", str(data["age"])),
            ("رقم الحساب", data["account_number"]),
            ("الجهة", data["employer_name"]),
        ],
    )

    # ---- Card & financials ----
    _add_section_title(doc, "البطاقة والبيانات المالية")
    _add_kv_table(
        doc,
        [
            ("البطاقة المطلوبة", f"{data['card_name']} (حد ائتماني {data['card_currency']} {data['card_limit']:,.0f})"),
            ("الراتب الشهري", f"{data['salary']:,.2f} ₪"),
            ("دخل إضافي معتمد", f"{data['other_income']:,.2f} ₪"),
            ("الدخل المعتمد الإجمالي", f"{data['approved_income']:,.2f} ₪"),
            ("الالتزامات الحالية", f"{data['existing_facilities']:,.2f} ₪"),
            ("عبء البطاقة الشهري (Demo)", f"{data['card_monthly_burden']:,.2f} ₪"),
            ("إجمالي العبء الشهري", f"{data['total_monthly_burden']:,.2f} ₪"),
            ("نسبة عبء الدين (DPR)", f"{data['dpr']:.2f}%"),
            ("الحد الأقصى المسموح لـ DPR", f"{data['max_dpr']:.0f}%"),
        ],
    )

    # ---- Notes ----
    if data["notes"]:
        _add_section_title(doc, "ملاحظات الموظف")
        notes_p = doc.add_paragraph()
        notes_p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        notes_run = notes_p.add_run(data["notes"])
        notes_run.font.size = Pt(10.5)

    # ---- Assumptions / disclaimer ----
    _add_section_title(doc, "ملاحظات هامة")
    for line in ASSUMPTIONS:
        p = doc.add_paragraph(style=None)
        p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = p.add_run(f"• {line}")
        r.font.size = Pt(9.5)
        r.font.color.rgb = MUTED

    buffer = io.BytesIO()
    doc.save(buffer)
    return buffer.getvalue()


def _add_section_title(doc: Document, text: str) -> None:
    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    run = p.add_run(text)
    run.font.size = Pt(12.5)
    run.font.bold = True
    run.font.color.rgb = PIB_BLUE_DARK
    run.font.name = _FONT_NAME
    # bottom border as a section divider (avoids using a table as a rule)
    p_format = p.paragraph_format
    p_format.space_after = Pt(4)


def _add_kv_table(doc: Document, rows: list[tuple[str, str]]) -> None:
    table = doc.add_table(rows=len(rows), cols=2)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    col_widths = [Cm(5.5), Cm(11.5)]
    for row_idx, (label, value) in enumerate(rows):
        label_cell = table.rows[row_idx].cells[0]
        value_cell = table.rows[row_idx].cells[1]

        label_cell.width = col_widths[0]
        value_cell.width = col_widths[1]

        _set_cell_text(label_cell, label, bold=True, color=PIB_BLUE_DARK, align_right=True)
        _set_cell_text(value_cell, value, bold=False, color=INK, align_right=True)
        _shade_cell(label_cell, PIB_BLUE_LIGHT)


def _set_cell_text(cell, text, bold=False, color=INK, align_right=True) -> None:
    cell.text = ""
    p = cell.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT if align_right else WD_ALIGN_PARAGRAPH.LEFT
    run = p.add_run(text)
    run.font.size = Pt(10.5)
    run.font.bold = bold
    run.font.color.rgb = color
    run.font.name = _FONT_NAME


def _shade_cell(cell, hex_color: str) -> None:
    """Apply CLEAR shading (never SOLID, which renders black)."""
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    tc_pr = cell._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hex_color)
    tc_pr.append(shd)


def _set_cell_border(cell, color: str) -> None:
    from docx.oxml.ns import qn
    from docx.oxml import OxmlElement

    tc_pr = cell._tc.get_or_add_tcPr()
    borders = OxmlElement("w:tcBorders")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "18")
    bottom.set(qn("w:space"), "0")
    bottom.set(qn("w:color"), color)
    borders.append(bottom)
    tc_pr.append(borders)
