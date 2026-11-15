import io
import re
import unicodedata
from datetime import datetime
from xml.sax.saxutils import escape

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from src.database.export_pdf import get_pdf_data
from src.utils.security import CurrentUser, get_current_user
from src.utils.validation import Id, LongText

router = APIRouter(prefix="/export_pdf")


class ExportPDFRequest(BaseModel):
    id_patient: Id
    text: LongText


def _e(value) -> str:
    """Escapa texto para Paragraph de reportlab (interpreta marcado tipo XML)."""
    return escape("" if value is None else str(value))


def _safe_filename(*parts: str) -> str:
    raw = "_".join(p for p in parts if p)
    ascii_only = unicodedata.normalize("NFKD", raw).encode("ascii", "ignore").decode()
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", ascii_only).strip("_")
    return f"consulta_{cleaned or 'paciente'}.pdf"


@router.post("/")
def export_pdf(req: ExportPDFRequest, user: CurrentUser = Depends(get_current_user)):
    patient, employee = get_pdf_data(user, req.id_patient)
    if not patient:
        raise HTTPException(status_code=404, detail="No encontrado")

    # Generate PDF in memory
    buffer = io.BytesIO()
    
    # Page setup
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=54,
        bottomMargin=54
    )
    
    styles = getSampleStyleSheet()
    
    # Custom color palette for premium design
    primary_color = colors.HexColor("#0f172a")    # Slate 900
    secondary_color = colors.HexColor("#0284c7")  # Sky 600
    text_color = colors.HexColor("#334155")       # Slate 700
    light_bg = colors.HexColor("#f8fafc")         # Slate 50
    border_color = colors.HexColor("#e2e8f0")     # Slate 200
    
    # Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=primary_color,
        spaceAfter=2
    )
    
    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=15
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        textColor=secondary_color,
        spaceBefore=10,
        spaceAfter=4
    )
    
    meta_label_style = ParagraphStyle(
        'MetaLabel',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        textColor=primary_color
    )
    
    meta_val_style = ParagraphStyle(
        'MetaValue',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        textColor=text_color
    )
    
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10.5,
        textColor=text_color,
        leading=15,
        spaceAfter=8
    )
    
    story = []
    
    # Header brand block
    story.append(Paragraph("SYS-GEST-CLINIC", title_style))
    story.append(Paragraph("Sistema de Gestión y Control Clínico | Morelia, Michoacán", subtitle_style))
    
    # Date block
    current_date = datetime.now().strftime("%d/%m/%Y")
    date_style = ParagraphStyle(
        'DateStyle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        alignment=2, # Right aligned
        textColor=text_color
    )
    story.append(Paragraph(f"Fecha: {current_date}", date_style))
    story.append(Spacer(1, 10))
    
    # Patient meta table
    doctor_fullname = f"Dra. {_e(patient['doctor_name'])} {_e(patient['doctor_last_name'])}" if patient['doctor_name'] else "No asignada"
    sender_name = _e(patient['doctor_sender']) or "No especificado"
    aseguradora = _e(patient['aseguradora']) or "Ninguna"
    
    meta_data = [
        [
            Paragraph("Paciente:", meta_label_style),
            Paragraph(f"{_e(patient['name'])} {_e(patient['last_name'])}", meta_val_style),
            Paragraph("Médico a cargo:", meta_label_style),
            Paragraph(doctor_fullname, meta_val_style)
        ],
        [
            Paragraph("Teléfono:", meta_label_style),
            Paragraph(_e(patient['phone']), meta_val_style),
            Paragraph("Médico remitente:", meta_label_style),
            Paragraph(sender_name, meta_val_style)
        ],
        [
            Paragraph("Aseguradora:", meta_label_style),
            Paragraph(aseguradora, meta_val_style),
            Paragraph("Atendido por:", meta_label_style),
            Paragraph(f"{_e(employee['name'])} {_e(employee['last_name'])}" if employee else "Sistema", meta_val_style)
        ]
    ]
    
    # Total width of content = 504 units (612 - 54*2)
    meta_table = Table(meta_data, colWidths=[80, 172, 102, 150])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_bg),
        ('BOX', (0,0), (-1,-1), 1, border_color),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor("#f1f5f9")),
    ]))
    
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    # Title section
    story.append(Paragraph("VALORACIÓN / NOTA DE CONSULTA", section_heading))
    
    # Underline line
    line_table = Table([[""]], colWidths=[504])
    line_table.setStyle(TableStyle([
        ('LINEBELOW', (0,0), (-1,-1), 1.5, secondary_color),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0),
        ('TOPPADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(line_table)
    story.append(Spacer(1, 12))
    
    # Consultation details text
    notes_lines = req.text.split('\n')
    for line in notes_lines:
        if line.strip() == "":
            story.append(Spacer(1, 6))
        else:
            story.append(Paragraph(_e(line), body_style))
            
    story.append(Spacer(1, 45))
    
    # Signatures
    sig_data = [
        ["", ""],
        ["_______________________________________", "_______________________________________"],
        ["Firma del Médico / Terapeuta", "Firma del Paciente"]
    ]
    sig_table = Table(sig_data, colWidths=[252, 252])
    sig_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'BOTTOM'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TEXTCOLOR', (0,1), (-1,-1), text_color),
        ('FONTNAME', (0,2), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,2), (-1,-1), 8.5),
    ]))
    story.append(sig_table)
    
    doc.build(story)
    buffer.seek(0)
    
    filename = _safe_filename(patient['name'], patient['last_name'])
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{filename}"', "Cache-Control": "no-store"}
    )
