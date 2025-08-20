from flask import Flask, render_template, jsonify, request, make_response
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
from fpdf import FPDF
import os
import io

app = Flask(__name__)# main.py

# Adicione o 'os' para manipulação de caminhos
import os

# ... (outros imports)

# Define o caminho para a pasta raiz do projeto
project_root = os.path.abspath(os.path.dirname(__file__))

# Configura o Flask para usar a pasta raiz como pasta de templates
app = Flask(__name__, template_folder=project_root)

# ... (resto do seu código)

# Configuração do SQLAlchemy
DATABASE_URL = "sqlite:///instance/project.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Definição dos modelos
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), nullable=False)

class B2C(Base):
    __tablename__ = 'b2_c'
    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    nome_hotel = Column(String(200), nullable=True)
    valor = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    status_pagamento = Column(String(50), nullable=False)

class Lead(Base):
    __tablename__ = 'lead'
    id = Column(Integer, primary_key=True)
    data_entrada = Column(Date, nullable=False)
    entrada_leads_ask_suite = Column(Integer)
    fila_atendimento = Column(Integer)
    atendimento = Column(Integer)
    qualificacao = Column(Integer)
    oportunidade = Column(Integer)
    aguardando_pagamento = Column(Integer)

# Cria as tabelas se não existirem
Base.metadata.create_all(engine)

# Função auxiliar para garantir que o texto seja compatível com o PDF
def encode_text(text):
    return str(text).encode('latin-1', 'replace').decode('latin-1')

# Rotas
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/leads", methods=["GET", "POST"])
def leads_api():
    session = Session()
    try:
        if request.method == "GET":
            # Aplicar filtros de data se fornecidos
            query = session.query(Lead)
            data_inicio = request.args.get('data_inicio')
            data_fim = request.args.get('data_fim')
            
            if data_inicio:
                query = query.filter(Lead.data_entrada >= datetime.strptime(data_inicio, "%Y-%m-%d").date())
            if data_fim:
                query = query.filter(Lead.data_entrada <= datetime.strptime(data_fim, "%Y-%m-%d").date())
            
            leads_data = query.all()
            leads_list = []
            for lead in leads_data:
                leads_list.append({
                    "id": lead.id,
                    "data_entrada": lead.data_entrada.strftime("%Y-%m-%d"),
                    "entrada_leads_ask_suite": lead.entrada_leads_ask_suite,
                    "fila_atendimento": lead.fila_atendimento,
                    "atendimento": lead.atendimento,
                    "qualificacao": lead.qualificacao,
                    "oportunidade": lead.oportunidade,
                    "aguardando_pagamento": lead.aguardando_pagamento
                })
            return jsonify(leads_list)
        elif request.method == "POST":
            data = request.get_json()
            new_lead = Lead(
                data_entrada=datetime.strptime(data["data_entrada"], "%Y-%m-%d").date(),
                entrada_leads_ask_suite=int(data.get("entrada_leads_ask_suite") or 0) if data.get("entrada_leads_ask_suite") else None,
                fila_atendimento=int(data.get("fila_atendimento") or 0) if data.get("fila_atendimento") else None,
                atendimento=int(data.get("atendimento") or 0) if data.get("atendimento") else None,
                qualificacao=int(data.get("qualificacao") or 0) if data.get("qualificacao") else None,
                oportunidade=int(data.get("oportunidade") or 0) if data.get("oportunidade") else None,
                aguardando_pagamento=int(data.get("aguardando_pagamento") or 0) if data.get("aguardando_pagamento") else None
            )
            session.add(new_lead)
            session.commit()
            lead_id = new_lead.id
            return jsonify({"message": "Lead criado com sucesso", "id": lead_id}), 201
    finally:
        session.close()

@app.route("/api/leads/<int:lead_id>", methods=["GET", "PUT", "DELETE"])
def lead_detail_api(lead_id):
    session = Session()
    try:
        lead = session.get(Lead, lead_id)
        if not lead:
            return jsonify({"error": "Lead não encontrado"}), 404

        if request.method == "GET":
            lead_data = {
                "id": lead.id,
                "data_entrada": lead.data_entrada.strftime("%Y-%m-%d"),
                "entrada_leads_ask_suite": lead.entrada_leads_ask_suite,
                "fila_atendimento": lead.fila_atendimento,
                "atendimento": lead.atendimento,
                "qualificacao": lead.qualificacao,
                "oportunidade": lead.oportunidade,
                "aguardando_pagamento": lead.aguardando_pagamento
            }
            return jsonify(lead_data)
        elif request.method == "PUT":
            data = request.get_json()
            lead.data_entrada = datetime.strptime(data["data_entrada"], "%Y-%m-%d").date()
            lead.entrada_leads_ask_suite = int(data.get("entrada_leads_ask_suite") or 0) if data.get("entrada_leads_ask_suite") else None
            lead.fila_atendimento = int(data.get("fila_atendimento") or 0) if data.get("fila_atendimento") else None
            lead.atendimento = int(data.get("atendimento") or 0) if data.get("atendimento") else None
            lead.qualificacao = int(data.get("qualificacao") or 0) if data.get("qualificacao") else None
            lead.oportunidade = int(data.get("oportunidade") or 0) if data.get("oportunidade") else None
            lead.aguardando_pagamento = int(data.get("aguardando_pagamento") or 0) if data.get("aguardando_pagamento") else None
            session.commit()
            return jsonify({"message": "Lead atualizado com sucesso"})
        elif request.method == "DELETE":
            session.delete(lead)
            session.commit()
            return jsonify({"message": "Lead deletado com sucesso"}), 204
    finally:
        session.close()

@app.route("/api/b2c", methods=["GET", "POST"])
def b2c_api():
    session = Session()
    try:
        if request.method == "GET":
            # Aplicar filtros de data se fornecidos
            query = session.query(B2C)
            data_inicio = request.args.get('data_inicio')
            data_fim = request.args.get('data_fim')
            
            if data_inicio:
                query = query.filter(B2C.data >= datetime.strptime(data_inicio, "%Y-%m-%d").date())
            if data_fim:
                query = query.filter(B2C.data <= datetime.strptime(data_fim, "%Y-%m-%d").date())
            
            b2c_data = query.all()
            b2c_list = []
            for item in b2c_data:
                b2c_list.append({
                    "id": item.id,
                    "data": item.data.strftime("%Y-%m-%d"),
                    "nome_hotel": item.nome_hotel,
                    "valor": item.valor,
                    "status": item.status,
                    "status_pagamento": item.status_pagamento
                })
            return jsonify(b2c_list)
        elif request.method == "POST":
            data = request.get_json()
            new_b2c = B2C(
                data=datetime.strptime(data["data"], "%Y-%m-%d").date(),
                nome_hotel=data["nome_hotel"],
                valor=float(data["valor"]),
                status=data["status"],
                status_pagamento=data["status_pagamento"]
            )
            session.add(new_b2c)
            session.commit()
            b2c_id = new_b2c.id
            return jsonify({"message": "B2C criado com sucesso", "id": b2c_id}), 201
    finally:
        session.close()

@app.route("/api/b2c/<int:b2c_id>", methods=["GET", "PUT", "DELETE"])
def b2c_detail_api(b2c_id):
    session = Session()
    try:
        b2c_item = session.get(B2C, b2c_id)
        if not b2c_item:
            return jsonify({"error": "Registro B2C não encontrado"}), 404

        if request.method == "GET":
            b2c_data = {
                "id": b2c_item.id,
                "data": b2c_item.data.strftime("%Y-%m-%d"),
                "nome_hotel": b2c_item.nome_hotel,
                "valor": b2c_item.valor,
                "status": b2c_item.status,
                "status_pagamento": b2c_item.status_pagamento
            }
            return jsonify(b2c_data)
        elif request.method == "PUT":
            data = request.get_json()
            b2c_item.data = datetime.strptime(data["data"], "%Y-%m-%d").date()
            b2c_item.nome_hotel = data["nome_hotel"]
            b2c_item.valor = float(data["valor"])
            b2c_item.status = data["status"]
            b2c_item.status_pagamento = data["status_pagamento"]
            session.commit()
            return jsonify({"message": "Registro B2C atualizado com sucesso"})
        elif request.method == "DELETE":
            session.delete(b2c_item)
            session.commit()
            return jsonify({"message": "Registro B2C deletado com sucesso"}), 204
    finally:
        session.close()

@app.route("/api/b2c/metrics", methods=["GET"])
def get_b2c_metrics():
    session = Session()
    try:
        # Aplicar filtros de data se fornecidos
        query = session.query(B2C)
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        if data_inicio:
            query = query.filter(B2C.data >= datetime.strptime(data_inicio, "%Y-%m-%d").date())
        if data_fim:
            query = query.filter(B2C.data <= datetime.strptime(data_fim, "%Y-%m-%d").date())
        
        b2c_data = query.all()
        total_registros = len(b2c_data)
        total_valor = sum(item.valor for item in b2c_data)

        return jsonify({"total_registros": total_registros, "total_valor": total_valor})
    finally:
        session.close()

@app.route("/api/export/pdf", methods=["GET"])
def export_pdf():
    try:
        tipo_relatorio = request.args.get('tipo', 'leads')
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
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

        session = Session()
        try:
            # Lógica para preencher o PDF (Leads ou B2C)
            if tipo_relatorio == 'leads':
                query = session.query(Lead)
                if data_inicio:
                    query = query.filter(Lead.data_entrada >= datetime.strptime(data_inicio, "%Y-%m-%d").date())
                if data_fim:
                    query = query.filter(Lead.data_entrada <= datetime.strptime(data_fim, "%Y-%m-%d").date())
                
                dados = query.all()
                headers = ['ID', 'Data Entrada', 'Ask Suite', 'Fila', 'Atendimento', 'Qualificacao', 'Oportunidade', 'Pagamento']
                col_widths = [10, 25, 25, 20, 25, 25, 25, 25]
                
                for i, header in enumerate(headers):
                    pdf.cell(col_widths[i], 10, encode_text(header), 1)
                pdf.ln()

                for item in dados:
                    pdf.cell(col_widths[0], 10, str(item.id), 1)
                    pdf.cell(col_widths[1], 10, item.data_entrada.strftime('%d/%m/%Y'), 1)
                    pdf.cell(col_widths[2], 10, str(item.entrada_leads_ask_suite or ''), 1)
                    pdf.cell(col_widths[3], 10, str(item.fila_atendimento or ''), 1)
                    pdf.cell(col_widths[4], 10, str(item.atendimento or ''), 1)
                    pdf.cell(col_widths[5], 10, str(item.qualificacao or ''), 1)
                    pdf.cell(col_widths[6], 10, str(item.oportunidade or ''), 1)
                    pdf.cell(col_widths[7], 10, str(item.aguardando_pagamento or ''), 1)
                    pdf.ln()

            elif tipo_relatorio == 'b2c':
                query = session.query(B2C)
                if data_inicio:
                    query = query.filter(B2C.data >= datetime.strptime(data_inicio, "%Y-%m-%d").date())
                if data_fim:
                    query = query.filter(B2C.data <= datetime.strptime(data_fim, "%Y-%m-%d").date())
                
                dados = query.all()
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
        finally:
            session.close()

        # Cria um buffer de bytes em memória
        buffer = io.BytesIO()
        # Salva o PDF nesse buffer
        pdf.output(buffer)
        # Pega o conteúdo do buffer
        pdf_output = buffer.getvalue()
        
        response = make_response(pdf_output)
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename=relatorio_{tipo_relatorio}.pdf'
        
        return response

    except Exception as e:
        print(f"Erro ao exportar PDF: {e}")
        return jsonify({"error": "Erro ao gerar PDF"}), 500

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')

