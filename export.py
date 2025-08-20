from flask import Blueprint, request, jsonify, make_response
from src.models.lead import Lead, db
from src.models.b2c import B2C
from datetime import datetime, date
from sqlalchemy import func, desc
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.lib.colors import HexColor
import io
import base64
import os

export_bp = Blueprint('export', __name__)

@export_bp.route('/export/pdf', methods=['GET'])
def export_pdf():
    """Exporta relatório em PDF"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        tipo = request.args.get('tipo', 'leads')  # 'leads' ou 'b2c'
        
        # Criar buffer para o PDF
        buffer = io.BytesIO()
        
        # Criar documento PDF
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        story = []
        
        # Adicionar marca d'água
        watermark_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'watermark.png')
        if os.path.exists(watermark_path):
            # Adicionar marca d'água como imagem de fundo
            watermark = Image(watermark_path, width=2*inch, height=2*inch)
            watermark.hAlign = 'CENTER'
            story.append(watermark)
            story.append(Spacer(1, -2*inch))  # Sobrepor o conteúdo na marca d'água
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            textColor=HexColor('#667eea'),
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=16,
            spaceAfter=20,
            textColor=HexColor('#2d3748')
        )
        
        # Título do relatório
        if tipo == 'leads':
            title = "Relatório de Análise de Leads"
        else:
            title = "Relatório de Análise B2C"
            
        story.append(Paragraph(title, title_style))
        
        # Período do relatório
        periodo_text = "Período: "
        if data_inicio and data_fim:
            periodo_text += f"{format_date_br(data_inicio)} a {format_date_br(data_fim)}"
        elif data_inicio:
            periodo_text += f"A partir de {format_date_br(data_inicio)}"
        elif data_fim:
            periodo_text += f"Até {format_date_br(data_fim)}"
        else:
            periodo_text += "Todos os registros"
            
        story.append(Paragraph(periodo_text, styles['Normal']))
        story.append(Spacer(1, 20))
        
        if tipo == 'leads':
            story.extend(generate_leads_report(data_inicio, data_fim, styles))
        else:
            story.extend(generate_b2c_report(data_inicio, data_fim, styles))
        
        # Construir PDF
        doc.build(story)
        
        # Preparar resposta
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=relatorio-{tipo}-{date.today().isoformat()}.pdf'
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generate_leads_report(data_inicio, data_fim, styles):
    """Gera o conteúdo do relatório de leads"""
    story = []
    
    # Filtros de data
    query = Lead.query
    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(Lead.data_entrada >= data_inicio_obj)
    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(Lead.data_entrada <= data_fim_obj)
    
    leads = query.order_by(Lead.data_entrada.desc()).all()
    
    # Métricas
    total_leads = query.count()
    entrada_leads_ask_suite = query.filter(Lead.entrada_leads_ask_suite.isnot(None)).count()
    fila_atendimento = query.filter(Lead.fila_atendimento.isnot(None)).count()
    atendimento = query.filter(Lead.atendimento.isnot(None)).count()
    qualificacao = query.filter(Lead.qualificacao.isnot(None)).count()
    oportunidade = query.filter(Lead.oportunidade.isnot(None)).count()
    aguardando_pagamento = query.filter(Lead.aguardando_pagamento.isnot(None)).count()
    
    # Seção de métricas
    story.append(Paragraph("Métricas Gerais", styles['Heading2']))
    
    metrics_data = [
        ['Métrica', 'Quantidade'],
        ['Total de Leads', str(total_leads)],
        ['Entrada Leads Ask Suite', str(entrada_leads_ask_suite)],
        ['Fila de Atendimento', str(fila_atendimento)],
        ['Em Atendimento', str(atendimento)],
        ['Qualificados', str(qualificacao)],
        ['Oportunidades', str(oportunidade)],
        ['Aguardando Pagamento', str(aguardando_pagamento)]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    
    # Lista de leads
    if leads:
        story.append(Paragraph("Lista de Leads", styles['Heading2']))
        
        leads_data = [['Data', 'Ask Suite', 'Fila Atend.', 'Atendimento', 'Qualificação', 'Oportunidade', 'Aguard. Pag.']]
        
        for lead in leads[:20]:  # Limitar a 20 registros para não sobrecarregar o PDF
            leads_data.append([
                format_date_br(lead.data_entrada.isoformat()) if lead.data_entrada else '-',
                lead.entrada_leads_ask_suite or '-',
                lead.fila_atendimento or '-',
                lead.atendimento or '-',
                lead.qualificacao or '-',
                lead.oportunidade or '-',
                lead.aguardando_pagamento or '-'
            ])
        
        leads_table = Table(leads_data, colWidths=[1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch, 1*inch])
        leads_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#667eea')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(leads_table)
        
        if len(leads) > 20:
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"Mostrando os primeiros 20 registros de {len(leads)} total.", styles['Normal']))
    
    return story

def generate_b2c_report(data_inicio, data_fim, styles):
    """Gera o conteúdo do relatório B2C"""
    story = []
    
    # Filtros de data
    query = B2C.query
    if data_inicio:
        data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
        query = query.filter(B2C.data >= data_inicio_obj)
    if data_fim:
        data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
        query = query.filter(B2C.data <= data_fim_obj)
    
    b2c_records = query.order_by(B2C.data.desc()).all()
    
    # Métricas
    total_registros = query.count()
    total_valor = query.with_entities(func.sum(B2C.valor)).scalar() or 0
    valor_medio = query.with_entities(func.avg(B2C.valor)).scalar() or 0
    
    # Hotéis mais vendidos
    hoteis_mais_vendidos = db.session.query(
        B2C.nome_hotel,
        func.count(B2C.id).label('quantidade'),
        func.sum(B2C.valor).label('valor_total')
    ).filter(
        query.whereclause if query.whereclause is not None else True
    ).group_by(B2C.nome_hotel).order_by(desc('valor_total')).limit(5).all()
    
    # Seção de métricas
    story.append(Paragraph("Métricas Gerais", styles['Heading2']))
    
    metrics_data = [
        ['Métrica', 'Valor'],
        ['Total de Registros', str(total_registros)],
        ['Valor Total', f'R$ {total_valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')],
        ['Valor Médio', f'R$ {valor_medio:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')]
    ]
    
    metrics_table = Table(metrics_data, colWidths=[3*inch, 2*inch])
    metrics_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4fd1c7')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))
    
    story.append(metrics_table)
    story.append(Spacer(1, 20))
    
    # Hotéis mais vendidos
    if hoteis_mais_vendidos:
        story.append(Paragraph("Top 5 Hotéis Mais Vendidos", styles['Heading2']))
        
        hoteis_data = [['Hotel', 'Quantidade', 'Valor Total']]
        for hotel in hoteis_mais_vendidos:
            hoteis_data.append([
                hotel[0],
                str(hotel[1]),
                f'R$ {float(hotel[2]):,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.')
            ])
        
        hoteis_table = Table(hoteis_data, colWidths=[3*inch, 1.5*inch, 1.5*inch])
        hoteis_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4fd1c7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(hoteis_table)
        story.append(Spacer(1, 20))
    
    # Lista de registros B2C
    if b2c_records:
        story.append(Paragraph("Lista de Registros B2C", styles['Heading2']))
        
        b2c_data = [['Data', 'Hotel', 'Valor', 'Status', 'Status Pagamento']]
        
        for record in b2c_records[:20]:  # Limitar a 20 registros
            b2c_data.append([
                format_date_br(record.data.isoformat()) if record.data else '-',
                record.nome_hotel,
                f'R$ {record.valor:,.2f}'.replace(',', 'X').replace('.', ',').replace('X', '.'),
                record.status,
                record.status_pagamento
            ])
        
        b2c_table = Table(b2c_data, colWidths=[1*inch, 2*inch, 1.2*inch, 1*inch, 1.3*inch])
        b2c_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4fd1c7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(b2c_table)
        
        if len(b2c_records) > 20:
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"Mostrando os primeiros 20 registros de {len(b2c_records)} total.", styles['Normal']))
    
    return story

def format_date_br(date_string):
    """Formata data para padrão brasileiro"""
    if not date_string:
        return '-'
    try:
        date_obj = datetime.strptime(date_string, '%Y-%m-%d')
        return date_obj.strftime('%d/%m/%Y')
    except:
        return date_string

