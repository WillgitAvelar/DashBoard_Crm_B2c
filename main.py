# main.py - VERSÃO FINAL, COMPLETA E FUNCIONAL

import os
from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# --- 1. INICIALIZAÇÃO DO FLASK E CONFIGURAÇÃO ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
instance_path = os.path.join(basedir, 'instance')
if not os.path.exists(instance_path):
    os.makedirs(instance_path)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(instance_path, 'project.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# --- 2. DEFINIÇÃO DOS MODELOS DO BANCO DE DADOS ---
class Lead(db.Model):
    __tablename__ = 'leads'
    id = db.Column(db.Integer, primary_key=True)
    data_entrada = db.Column(db.Date, nullable=False)
    entrada_leads_ask_suite = db.Column(db.Integer, default=0)
    fila_atendimento = db.Column(db.Integer, default=0)
    atendimento = db.Column(db.Integer, default=0)
    qualificacao = db.Column(db.Integer, default=0)
    oportunidade = db.Column(db.Integer, default=0)
    aguardando_pagamento = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {
            "id": self.id, "data_entrada": self.data_entrada.isoformat(),
            "entrada_leads_ask_suite": self.entrada_leads_ask_suite,
            "fila_atendimento": self.fila_atendimento, "atendimento": self.atendimento,
            "qualificacao": self.qualificacao, "oportunidade": self.oportunidade,
            "aguardando_pagamento": self.aguardando_pagamento
        }

class B2C(db.Model):
    __tablename__ = 'b2c'
    id = db.Column(db.Integer, primary_key=True)
    id_externo = db.Column(db.String(100), unique=True, nullable=True)
    data = db.Column(db.Date, nullable=False)
    nome_hotel = db.Column(db.String(200), nullable=True)
    valor = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    status_pagamento = db.Column(db.String(50), nullable=False)
    forma_pagamento = db.Column(db.String(50), nullable=False)
    usou_cupom = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {
            "id": self.id, "id_externo": self.id_externo,
            "data": self.data.isoformat(), "nome_hotel": self.nome_hotel,
            "valor": self.valor, "status": self.status,
            "status_pagamento": self.status_pagamento,
            "forma_pagamento": self.forma_pagamento, "usou_cupom": self.usou_cupom
        }


# --- 3. ROTAS DA APLICAÇÃO ---
@app.route("/")
def index():
    return render_template("index.html")

# --- ROTAS DA API PARA LEADS ---
@app.route("/api/leads", methods=["GET", "POST"])
def leads_api():
    if request.method == "GET":
        try:
            query = Lead.query
            data_inicio_str = request.args.get("data_inicio")
            if data_inicio_str:
                data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
                query = query.filter(Lead.data_entrada >= data_inicio)
            data_fim_str = request.args.get("data_fim")
            if data_fim_str:
                data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
                query = query.filter(Lead.data_entrada <= data_fim)
            leads = query.order_by(Lead.data_entrada.desc()).all()
            return jsonify([lead.to_dict() for lead in leads])
        except Exception as e:
            return jsonify({"error": f"Erro ao buscar leads: {e}"}), 500

    if request.method == "POST":
        data = request.get_json()
        try:
            new_lead = Lead(
                data_entrada=datetime.strptime(data["data_entrada"], "%Y-%m-%d").date(),
                entrada_leads_ask_suite=data.get("entrada_leads_ask_suite", 0),
                fila_atendimento=data.get("fila_atendimento", 0),
                atendimento=data.get("atendimento", 0),
                qualificacao=data.get("qualificacao", 0),
                oportunidade=data.get("oportunidade", 0),
                aguardando_pagamento=data.get("aguardando_pagamento", 0)
            )
            db.session.add(new_lead)
            db.session.commit()
            db.session.refresh(new_lead)
            return jsonify(new_lead.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Erro ao salvar o lead: {e}"}), 500
    return jsonify({"error": "Método não permitido"}), 405

@app.route("/api/leads/<int:id>", methods=["GET", "PUT", "DELETE"])
def lead_detail_api(id):
    lead = Lead.query.get_or_404(id)
    if request.method == "GET":
        return jsonify(lead.to_dict())
    if request.method == "PUT":
        data = request.get_json()
        try:
            lead.data_entrada = datetime.strptime(data.get('data_entrada'), "%Y-%m-%d").date()
            lead.entrada_leads_ask_suite = data.get('entrada_leads_ask_suite', lead.entrada_leads_ask_suite)
            lead.fila_atendimento = data.get('fila_atendimento', lead.fila_atendimento)
            lead.atendimento = data.get('atendimento', lead.atendimento)
            lead.qualificacao = data.get('qualificacao', lead.qualificacao)
            lead.oportunidade = data.get('oportunidade', lead.oportunidade)
            lead.aguardando_pagamento = data.get('aguardando_pagamento', lead.aguardando_pagamento)
            db.session.commit()
            return jsonify(lead.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Erro ao atualizar o lead: {e}"}), 500
    if request.method == "DELETE":
        try:
            db.session.delete(lead)
            db.session.commit()
            return jsonify({"message": "Lead deletado com sucesso"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Erro ao deletar o lead: {e}"}), 500
    return jsonify({"error": "Método não permitido"}), 405

# --- ROTAS DA API PARA B2C ---
@app.route("/api/b2c", methods=["GET", "POST"])
def b2c_api():
    if request.method == "GET":
        try:
            query = B2C.query
            data_inicio_str = request.args.get("data_inicio")
            if data_inicio_str:
                data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
                query = query.filter(B2C.data >= data_inicio)
            data_fim_str = request.args.get("data_fim")
            if data_fim_str:
                data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
                query = query.filter(B2C.data <= data_fim)
            hotel_str = request.args.get("hotel")
            if hotel_str:
                query = query.filter(B2C.nome_hotel.ilike(f"%{hotel_str}%"))
            b2c_items = query.order_by(B2C.data.desc()).all()
            return jsonify([item.to_dict() for item in b2c_items])
        except Exception as e:
            return jsonify({"error": f"Erro ao buscar B2C: {e}"}), 500

    if request.method == "POST":
        data = request.get_json()
        try:
            new_b2c = B2C(
                id_externo=data.get('id_externo'),
                data=datetime.strptime(data["data"], "%Y-%m-%d").date(),
                nome_hotel=data.get("nome_hotel"), valor=float(data.get("valor", 0)),
                status=data.get("status"), status_pagamento=data.get("status_pagamento"),
                forma_pagamento=data.get("forma_pagamento"), usou_cupom=data.get("usou_cupom", False)
            )
            db.session.add(new_b2c)
            db.session.commit()
            db.session.refresh(new_b2c)
            return jsonify(new_b2c.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Erro ao salvar o B2C: {e}"}), 500
    return jsonify({"error": "Método não permitido"}), 405

@app.route("/api/b2c/<int:id>", methods=["GET", "PUT", "DELETE"])
def b2c_detail_api(id):
    b2c_item = B2C.query.get_or_404(id)
    if request.method == "GET":
        return jsonify(b2c_item.to_dict())
    if request.method == "PUT":
        data = request.get_json()
        try:
            b2c_item.id_externo = data.get('id_externo', b2c_item.id_externo)
            b2c_item.data = datetime.strptime(data.get('data'), "%Y-%m-%d").date()
            b2c_item.nome_hotel = data.get('nome_hotel', b2c_item.nome_hotel)
            b2c_item.valor = float(data.get('valor', b2c_item.valor))
            b2c_item.status = data.get('status', b2c_item.status)
            b2c_item.status_pagamento = data.get('status_pagamento', b2c_item.status_pagamento)
            b2c_item.forma_pagamento = data.get('forma_pagamento', b2c_item.forma_pagamento)
            b2c_item.usou_cupom = data.get('usou_cupom', b2c_item.usou_cupom)
            db.session.commit()
            return jsonify(b2c_item.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Erro ao atualizar o B2C: {e}"}), 500
    if request.method == "DELETE":
        try:
            db.session.delete(b2c_item)
            db.session.commit()
            return jsonify({"message": "Registro B2C deletado com sucesso"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Erro ao deletar o B2C: {e}"}), 500
    return jsonify({"error": "Método não permitido"}), 405


# --- 4. EXECUÇÃO DO APLICATIVO ---
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True, host='0.0.0.0', port=5000)
