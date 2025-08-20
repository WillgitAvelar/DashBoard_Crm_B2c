# src/routes/export.py

from flask import Blueprint, request, make_response
from fpdf import FPDF
from .. import db
from ..models.lead import Lead
from ..models.b2c import B2C
from datetime import datetime
import io  # <-- Importe a biblioteca de I/O em memória

export_bp = Blueprint('export_bp', __name__)

# Função auxiliar para garantir que o texto seja compatível com o PDF
def encode_text(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

@export_bp.route('/export/pdf', methods=['GET'])
def export_pdf():
    try:
        tipo_relatorio = request.args.get('tipo', 'leads')
        
        class PDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 12)
                titulo = f'Relatorio de {tipo_relatorio.capitalize()}'
                self.cell(0, 10, encode_text(titulo), 0, 1, 'C')
                self.ln(10)

            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                pagina = f'Pagina {self.page_no()}'
                self.cell(0, 10, encode_text(pagina), 0, 0, 'C')

        pdf = PDF()
        pdf.add_page()
        pdf.set_font('Arial', '', 10)

        # Lógica para preencher o PDF (Leads ou B2C)
        if tipo_relatorio == 'leads':
            dados = Lead.query.all()
            headers = ['ID', 'Data Entrada', 'Ask Suite', 'Fila', 'Atendimento', 'Qualificacao', 'Oportunidade', 'Pagamento']
            col_widths = [10, 25, 25, 20, 25, 25, 25, 25]
            
            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, encode_text(header), 1)
            pdf.ln()

            for item in dados:
                pdf.cell(col_widths[0], 10, str(item.id), 1)
                pdf.cell(col_widths[1], 10, item.data_entrada.strftime('%d/%m/%Y'), 1)
                pdf.cell(col_widths[2], 10, str(item.entrada_leads_ask_suite), 1)
                pdf.cell(col_widths[3], 10, str(item.fila_atendimento), 1)
                pdf.cell(col_widths[4], 10, str(item.atendimento), 1)
                pdf.cell(col_widths[5], 10, str(item.qualificacao), 1)
                pdf.cell(col_widths[6], 10, str(item.oportunidade), 1)
                pdf.cell(col_widths[7], 10, str(item.aguardando_pagamento), 1)
                pdf.ln()

        elif tipo_relatorio == 'b2c':
            dados = B2C.query.all()
            headers = ['ID', 'Data', 'Hotel', 'Valor', 'Status', 'Pgto Status']
            col_widths = [10, 25, 60, 25, 30, 30]

            for i, header in enumerate(headers):
                pdf.cell(col_widths[i], 10, encode_text(header), 1)
            pdf.ln()

            for item in dados:
                pdf.cell(col_widths[0], 10, str(item.id), 1)
                pdf.cell(col_widths[1], 10, item.data.strftime('%d/%m/%Y'), 1)
                pdf.cell(col_widths[2], 10, encode_text(item.nome_hotel), 1)
                pdf.cell(col_widths[3], 10, encode_text(f'R$ {item.valor:.2f}'), 1)
                pdf.cell(col_widths[4], 10, encode_text(item.status), 1)
                pdf.cell(col_widths[5], 10, encode_text(item.status_pagamento), 1)
                pdf.ln()

        # --- A CORREÇÃO FINAL E DEFINITIVA ---
        # 1. Crie um buffer de bytes em memória
        buffer = io.BytesIO()
        # 2. Salve o PDF nesse buffer
        pdf.output(buffer)
        # 3. Pegue o conteúdo do buffer (que é garantidamente do tipo bytes)
        pdf_output = buffer.getvalue()
        
        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=relatorio_{tipo_relatorio}.pdf'
        
        return response

    except Exception as e:
        print(f"Erro ao exportar PDF: {e}")
        return "Erro ao gerar PDF", 500
