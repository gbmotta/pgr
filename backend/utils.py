"""
Utilitários - Sistema PGR

Funções auxiliares para upload, PDF, email, etc.
"""
import os
import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile
import aiofiles
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

# Configurações de upload
UPLOAD_DIR = Path(__file__).parent.parent / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)


async def save_upload_file(file: UploadFile, process_id: int) -> tuple[str, int]:
    """
    Salva arquivo enviado e retorna (filename, file_size).
    
    Args:
        file: Arquivo enviado
        process_id: ID do processo
    
    Returns:
        Tuple com (filename, file_size)
    """
    # Criar diretório do processo
    process_dir = UPLOAD_DIR / str(process_id)
    process_dir.mkdir(exist_ok=True)
    
    # Gerar nome único
    ext = Path(file.filename).suffix
    unique_filename = f"{uuid.uuid4()}{ext}"
    file_path = process_dir / unique_filename
    
    # Salvar arquivo
    async with aiofiles.open(file_path, 'wb') as f:
        content = await file.read()
        await f.write(content)
        file_size = len(content)
    
    # Retornar caminho relativo
    relative_path = f"{process_id}/{unique_filename}"
    return relative_path, file_size


def generate_pdf_report(process_data: dict, output_path: str):
    """
    Gera relatório PDF de um processo.
    
    Args:
        process_data: Dados do processo
        output_path: Caminho para salvar o PDF
    """
    doc = SimpleDocTemplate(output_path, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    # Estilos personalizados
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        textColor=colors.HexColor('#34495e'),
        spaceAfter=30,
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#2c3e50'),
        spaceAfter=12,
    )
    
    # Título
    story.append(Paragraph("Relatório de Processo Administrativo", title_style))
    story.append(Spacer(1, 0.5*cm))
    
    # Dados do processo
    story.append(Paragraph("Dados do Processo", heading_style))
    
    data = [
        ["Protocolo:", process_data.get('protocol_number', 'N/A')],
        ["Requerente:", process_data.get('applicant_name', 'N/A')],
        ["Tipo:", process_data.get('type_name', 'N/A')],
        ["Status:", process_data.get('status_label', 'N/A')],
        ["Data de Criação:", process_data.get('created_date', 'N/A')],
    ]
    
    if process_data.get('applicant_registration'):
        data.append(["Matrícula:", process_data['applicant_registration']])
    if process_data.get('financial_effective_date'):
        data.append(["Efeito Financeiro:", process_data['financial_effective_date']])
    if process_data.get('parecer'):
        data.append(["Parecer:", process_data['parecer']])
    
    table = Table(data, colWidths=[5*cm, 12*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.grey),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('BACKGROUND', (1, 0), (1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    story.append(table)
    story.append(Spacer(1, 1*cm))
    
    # Documentos
    if process_data.get('documents'):
        story.append(Paragraph("Documentos", heading_style))
        doc_data = [["Documento", "Obrigatório", "Fornecido", "Data"]]
        for doc in process_data['documents']:
            doc_data.append([
                doc.get('name', 'N/A'),
                "Sim" if doc.get('required') else "Não",
                "Sim" if doc.get('provided') else "Não",
                doc.get('provided_date', '-') or '-'
            ])
        doc_table = Table(doc_data, colWidths=[8*cm, 3*cm, 3*cm, 4*cm])
        doc_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(doc_table)
        story.append(Spacer(1, 1*cm))
    
    # Prazos
    if process_data.get('deadlines'):
        story.append(Paragraph("Prazos", heading_style))
        deadline_data = [["Prazo", "Data de Vencimento", "Status"]]
        for deadline in process_data['deadlines']:
            status_text = "Cumprido" if deadline.get('closed') else "Pendente"
            if not deadline.get('closed'):
                due_date = datetime.fromisoformat(deadline['due_date'].replace('Z', '+00:00'))
                if due_date.date() < datetime.now().date():
                    status_text = "Vencido"
            deadline_data.append([
                deadline.get('name', 'N/A'),
                deadline.get('due_date', 'N/A'),
                status_text
            ])
        deadline_table = Table(deadline_data, colWidths=[8*cm, 5*cm, 5*cm])
        deadline_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
        ]))
        story.append(deadline_table)
    
    # Rodapé
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph(
        f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}",
        styles['Normal']
    ))
    
    doc.build(story)


async def send_email(to_email: str, subject: str, body: str, html_body: Optional[str] = None):
    """
    Envia email via SMTP.
    
    Args:
        to_email: Email destinatário
        subject: Assunto
        body: Corpo em texto
        html_body: Corpo em HTML (opcional)
    """
    smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER")
    smtp_password = os.getenv("SMTP_PASSWORD")
    
    if not smtp_user or not smtp_password:
        print(f"[EMAIL] Configuração SMTP não encontrada. Email não enviado para {to_email}")
        return
    
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = smtp_user
    msg['To'] = to_email
    
    part1 = MIMEText(body, 'plain', 'utf-8')
    msg.attach(part1)
    
    if html_body:
        part2 = MIMEText(html_body, 'html', 'utf-8')
        msg.attach(part2)
    
    try:
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
        print(f"[EMAIL] Email enviado para {to_email}")
    except Exception as e:
        print(f"[EMAIL] Erro ao enviar email: {e}")

