"""
PDF assessment report generator, using reportlab.

Arabic needs two things reportlab does not do on its own:
1. Shaping/reordering — handled by `arabic_reshaper` + `python-bidi`
   (see `_ar()`), which convert plain Arabic text into the correctly
   joined, visually-ordered presentation-form string reportlab can
   lay out left-to-right like any other string.
2. A font that actually has glyphs for those presentation-form
   codepoints — most bundled PDF fonts don't. This module ships GNU
   FreeSerif (`fonts/FreeSerif.ttf`, `fonts/FreeSerifBold.ttf`), which
   has full Arabic presentation-form coverage and is redistributable
   (GNU GPL v3 with the font-embedding exception, see fonts/LICENSE.txt).
"""
import io
import os

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    SimpleDocTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    Image,
)
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_RIGHT

from ..models import Assessment
from ..rules_engine import ASSUMPTIONS
from .word_report import build_report_data

_FONTS_DIR = os.path.join(os.path.dirname(__file__), "fonts")
_FONT_REGULAR = "PIBArabic"
_FONT_BOLD = "PIBArabic-Bold"
_fonts_registered = False


def _ensure_fonts_registered() -> None:
    """Register the bundled Arabic-capable TTF fonts with reportlab, once."""
    global _fonts_registered
    if _fonts_registered:
        return
    pdfmetrics.registerFont(TTFont(_FONT_REGULAR, os.path.join(_FONTS_DIR, "FreeSerif.ttf")))
    pdfmetrics.registerFont(TTFont(_FONT_BOLD, os.path.join(_FONTS_DIR, "FreeSerifBold.ttf")))
    _fonts_registered = True

PIB_BLUE_DARK = colors.HexColor("#003B70")
PIB_BLUE = colors.HexColor("#075B91")
PIB_BLUE_LIGHT = colors.HexColor("#EAF3F9")
PIB_GOLD = colors.HexColor("#F4C400")
INK = colors.HexColor("#18324A")
MUTED = colors.HexColor("#627588")
DANGER = colors.HexColor("#A23B34")
ROW_BG = colors.HexColor("#F7F8F9")
_LOGO_PATH = os.path.join(_FONTS_DIR, "pib-logo.png")


def _ar(text: str) -> str:
    """
    Reshape/reorder Arabic (and mixed Arabic/Latin/number) text so
    reportlab — which does no bidi or letter-joining itself — lays it
    out correctly. Non-Arabic strings pass through unchanged.
    """
    import arabic_reshaper
    from bidi.algorithm import get_display

    return get_display(arabic_reshaper.reshape(text))


def generate_pdf_report(assessment: Assessment) -> bytes:
    _ensure_fonts_registered()
    data = build_report_data(assessment)
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2 * cm,
        leftMargin=2 * cm,
        topMargin=1.5 * cm,
        bottomMargin=1.5 * cm,
    )

    title_style = ParagraphStyle(
        "TitleAr", fontName=_FONT_BOLD, fontSize=15, leading=20, alignment=TA_RIGHT, textColor=PIB_BLUE_DARK
    )
    meta_style = ParagraphStyle("MetaAr", fontName=_FONT_REGULAR, fontSize=9, alignment=TA_RIGHT, textColor=MUTED)
    section_style = ParagraphStyle(
        "SectionAr", fontName=_FONT_BOLD, fontSize=12.5, leading=18, alignment=TA_RIGHT,
        textColor=PIB_BLUE_DARK, spaceBefore=14,
    )
    result_style = ParagraphStyle(
        "ResultAr",
        fontName=_FONT_BOLD,
        fontSize=15,
        alignment=TA_RIGHT,
        textColor=PIB_BLUE if data["eligible"] else DANGER,
        spaceAfter=4,
    )
    body_style = ParagraphStyle("BodyAr", fontName=_FONT_REGULAR, fontSize=10, alignment=TA_RIGHT, textColor=INK, leading=14)
    note_style = ParagraphStyle("NoteAr", fontName=_FONT_REGULAR, fontSize=8.5, alignment=TA_RIGHT, textColor=MUTED, leading=12)

    story = []

    logo = Image(_LOGO_PATH, width=4.3 * cm, height=1.33 * cm)
    report_title = Paragraph(
        _ar("تقرير دراسة أولية لأهلية بطاقة ائتمانية"), title_style
    )
    header = Table([[logo, report_title]], colWidths=[5 * cm, 12 * cm])
    header.setStyle(
        TableStyle(
            [
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ALIGN", (0, 0), (0, 0), "LEFT"),
                ("ALIGN", (1, 0), (1, 0), "RIGHT"),
                ("LINEBELOW", (0, 0), (-1, -1), 2, PIB_GOLD),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.append(header)
    story.append(
        Paragraph(_ar(f"رقم الدراسة: {data['id']} | تاريخ الدراسة: {data['created_at']}"), meta_style)
    )
    story.append(Spacer(1, 10))

    story.append(Paragraph(_ar(f"النتيجة الأولية: {data['status_ar']}"), result_style))
    story.append(Paragraph(_ar(data["decision_summary"]), body_style))

    story.append(Paragraph(_ar("بيانات العميل"), section_style))
    story.append(
        _kv_table(
            [
                ("اسم العميل", data["customer_name"]),
                ("العمر", str(data["age"])),
                ("رقم الحساب", data["account_number"]),
                ("الجهة", data["employer_name"]),
            ]
        )
    )

    story.append(Paragraph(_ar("البطاقة والبيانات المالية"), section_style))
    story.append(
        _kv_table(
            [
                ("البطاقة المطلوبة", f"{data['card_name']} ({data['card_currency']} {data['card_limit']:,.0f})"),
                ("الراتب الشهري", f"{data['salary']:,.2f} \u20aa"),
                ("دخل إضافي معتمد", f"{data['other_income']:,.2f} \u20aa"),
                ("الدخل المعتمد الإجمالي", f"{data['approved_income']:,.2f} \u20aa"),
                ("الالتزامات الحالية", f"{data['existing_facilities']:,.2f} \u20aa"),
                ("عبء البطاقة الشهري (Demo)", f"{data['card_monthly_burden']:,.2f} \u20aa"),
                ("إجمالي العبء الشهري", f"{data['total_monthly_burden']:,.2f} \u20aa"),
                ("نسبة عبء الدين (DPR)", f"{data['dpr']:.2f}%"),
                ("الحد الأقصى المسموح لـ DPR", f"{data['max_dpr']:.0f}%"),
            ]
        )
    )

    if data["notes"]:
        story.append(Paragraph(_ar("ملاحظات الموظف"), section_style))
        story.append(Paragraph(_ar(data["notes"]), body_style))

    story.append(Paragraph(_ar("ملاحظات هامة"), section_style))
    for line in ASSUMPTIONS:
        story.append(Paragraph(_ar(f"• {line}"), note_style))

    doc.build(story, onFirstPage=_draw_page, onLaterPages=_draw_page)
    return buffer.getvalue()


def _kv_table(rows: list[tuple[str, str]]) -> Table:
    label_style = ParagraphStyle("kvLabel", fontName=_FONT_BOLD, fontSize=9.5, alignment=TA_RIGHT, textColor=PIB_BLUE_DARK)
    value_style = ParagraphStyle("kvValue", fontName=_FONT_REGULAR, fontSize=9.5, alignment=TA_RIGHT, textColor=INK)

    table_data = [
        [Paragraph(_ar(value), value_style), Paragraph(_ar(label), label_style)]
        for label, value in rows
    ]

    table = Table(table_data, colWidths=[11.5 * cm, 5.5 * cm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (1, 0), (1, -1), PIB_BLUE_LIGHT),
                ("BACKGROUND", (0, 0), (0, -1), ROW_BG),
                ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#DCE5EC")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#DCE5EC")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return table


def _draw_page(canvas, doc) -> None:
    """Draw the official blue/yellow page frame and a restrained footer."""
    canvas.saveState()
    width, height = A4
    canvas.setFillColor(PIB_BLUE_DARK)
    canvas.rect(0, height - 0.12 * cm, width, 0.12 * cm, stroke=0, fill=1)
    canvas.setFillColor(PIB_GOLD)
    canvas.rect(0, height - 0.2 * cm, width, 0.08 * cm, stroke=0, fill=1)
    canvas.setStrokeColor(colors.HexColor("#DCE5EC"))
    canvas.line(2 * cm, 1.35 * cm, width - 2 * cm, 1.35 * cm)
    canvas.setFont(_FONT_REGULAR, 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawRightString(width - 2 * cm, 0.9 * cm, _ar("البنك الإسلامي الفلسطيني — للاستخدام الداخلي"))
    canvas.drawString(2 * cm, 0.9 * cm, str(doc.page))
    canvas.restoreState()
