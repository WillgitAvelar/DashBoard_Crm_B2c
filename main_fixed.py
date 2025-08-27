import os
from flask import Flask, jsonify, render_template, request
from datetime import datetime, date

# Importa os modelos do arquivo models.py
from models import db, Lead, B2C

# --- Configuração Inicial ---
basedir = os.path.abspath(os.path.dirname(__file__))
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'project.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# --- Rota Principal da Interface ---
@app.route("/")
def index():
    return render_template("index.html")

# ===================================================================
#   ROTA DA API PARA LEADS - COM FILTRO DE DATA
# ===================================================================
@app.route("/api/leads", methods=["GET", "POST"])
def leads_api():
    if request.method == "GET":
        query = Lead.query

        # <<< A LÓGICA DO FILTRO É APLICADA AQUI >>>
        data_inicio_str = request.args.get('data_inicio')
        data_fim_str = request.args.get('data_fim')

        if data_inicio_str:
            try:
                data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
                query = query.filter(Lead.data_entrada >= data_inicio)
            except (ValueError, TypeError):
                pass # Ignora filtro se a data for inválida

        if data_fim_str:
            try:
                data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
                query = query.filter(Lead.data_entrada <= data_fim)
            except (ValueError, TypeError):
                pass # Ignora filtro se a data for inválida

        leads_data = query.order_by(Lead.data_entrada.desc()).all()
        return jsonify([lead.to_dict() for lead in leads_data])

    if request.method == "POST":
        # ... (Sua lógica de POST para criar um novo lead) ...
        data = request.get_json()
        try:
            new_lead = Lead(
                data_entrada=datetime.strptime(data["data_entrada"], "%Y-%m-%d").date(),
                entrada_leads_ask_suite=data.get("entrada_leads_ask_suite"),
                fila_atendimento=data.get("fila_atendimento"),
                atendimento=data.get("atendimento"),
                qualificacao=data.get("qualificacao"),
                oportunidade=data.get("oportunidade"),
                aguardando_pagamento=data.get("aguardando_pagamento")
            )
            db.session.add(new_lead)
            db.session.commit()
            return jsonify(new_lead.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Erro ao criar lead: {e}"}), 500
    
    return jsonify({"error": "Método não permitido"}), 405


# ===================================================================
#   ROTA DA API PARA B2C - COM FILTRO DE DATA E HOTEL
# ===================================================================
@app.route("/api/b2c", methods=["GET", "POST"])
def b2c_api():
    if request.method == "GET":
        query = B2C.query

        # <<< A LÓGICA DO FILTRO É APLICADA AQUI >>>
        data_inicio_str = request.args.get('data_inicio')
        data_fim_str = request.args.get('data_fim')
        hotel_str = request.args.get('hotel') # Filtro de hotel

        if data_inicio_str:
            try:
                data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d").date()
                query = query.filter(B2C.data >= data_inicio)
            except (ValueError, TypeError):
                pass

        if data_fim_str:
            try:
                data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d").date()
                query = query.filter(B2C.data <= data_fim)
            except (ValueError, TypeError):
                pass
        
        if hotel_str:
            # Usa 'ilike' para busca case-insensitive (não diferencia maiúsculas/minúsculas)
            query = query.filter(B2C.nome_hotel.ilike(f'%{hotel_str}%'))

        b2c_data = query.order_by(B2C.data.desc()).all()
        return jsonify([item.to_dict() for item in b2c_data])

    if request.method == "POST":
        # LÓGICA CORRIGIDA PARA CRIAR UM NOVO B2C
        data = request.get_json()
        try:
            # Verifica se o ID externo já existe (se fornecido)
            id_externo = data.get("id_externo")
            if id_externo:
                existing_item = B2C.query.filter_by(id_externo=id_externo).first()
                if existing_item:
                    return jsonify({"error": f"O ID Externo '{id_externo}' já está em uso."}), 409

            new_b2c = B2C(
                id_externo=id_externo,
                data=datetime.strptime(data["data"], "%Y-%m-%d").date(),
                nome_hotel=data.get("nome_hotel"),
                valor=float(data.get("valor", 0)),
                status=data.get("status"),
                status_pagamento=data.get("status_pagamento"),
                forma_pagamento=data.get("forma_pagamento"),
                usou_cupom=data.get("usou_cupom", False)
            )
            db.session.add(new_b2c)
            db.session.commit()
            return jsonify(new_b2c.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                return jsonify({"error": f"O ID Externo '{data.get('id_externo')}' já está em uso."}), 409
            return jsonify({"error": f"Erro ao criar B2C: {e}"}), 500

    return jsonify({"error": "Método não permitido"}), 405


# ... (O RESTO DAS SUAS ROTAS DE DETALHE /api/leads/<id> e /api/b2c/<id> CONTINUAM AQUI) ...
# ... (E A SEÇÃO if __name__ == "__main__": TAMBÉM) ...

@app.route("/api/leads/<int:id>", methods=["GET", "PUT", "DELETE"])
def lead_detail_api(id):
    """Obtém, atualiza ou deleta um lead específico."""
    lead = Lead.query.get_or_404(id)
    
    if request.method == "GET":
        return jsonify(lead.to_dict())

    if request.method == "PUT":
        data = request.get_json()
        try:
            lead.data_entrada = datetime.strptime(data["data_entrada"], "%Y-%m-%d").date()
            lead.entrada_leads_ask_suite = data.get("entrada_leads_ask_suite")
            lead.fila_atendimento = data.get("fila_atendimento")
            lead.atendimento = data.get("atendimento")
            lead.qualificacao = data.get("qualificacao")
            lead.oportunidade = data.get("oportunidade")
            lead.aguardando_pagamento = data.get("aguardando_pagamento")
            db.session.commit()
            return jsonify(lead.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Erro ao atualizar lead: {e}"}), 500

    if request.method == "DELETE":
        try:
            db.session.delete(lead)
            db.session.commit()
            return jsonify({"message": "Lead deletado com sucesso"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Erro ao deletar lead: {e}"}), 500

@app.route("/api/b2c/<int:id>", methods=["GET", "PUT", "DELETE"])
def b2c_detail_api(id):
    """Obtém, atualiza ou deleta um registro B2C específico."""
    b2c_item = B2C.query.get_or_404(id)

    if request.method == "GET":
        return jsonify(b2c_item.to_dict())

    if request.method == "PUT":
        data = request.get_json()
        try:
            id_externo = data.get("id_externo")
            if id_externo:
                existing_item = B2C.query.filter(B2C.id_externo == id_externo, B2C.id != id).first()
                if existing_item:
                    return jsonify({"error": f"O ID Externo '{id_externo}' já pertence a outro registro."}), 409

            b2c_item.id_externo = id_externo
            b2c_item.data = datetime.strptime(data["data"], "%Y-%m-%d").date()
            b2c_item.nome_hotel = data.get("nome_hotel")
            b2c_item.valor = float(data.get("valor", 0))
            b2c_item.status = data.get("status")
            b2c_item.status_pagamento = data.get("status_pagamento")
            b2c_item.forma_pagamento = data.get("forma_pagamento")
            b2c_item.usou_cupom = data.get("usou_cupom", False)
            db.session.commit()
            return jsonify(b2c_item.to_dict())
        except Exception as e:
            db.session.rollback()
            if 'UNIQUE constraint failed' in str(e):
                 return jsonify({"error": f"O ID Externo '{data.get('id_externo')}' já está em uso."}), 409
            return jsonify({"error": f"Erro ao atualizar B2C: {e}"}), 500

    if request.method == "DELETE":
        try:
            db.session.delete(b2c_item)
            db.session.commit()
            return jsonify({"message": "Item B2C deletado com sucesso"}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": f"Erro ao deletar B2C: {e}"}), 500


# --- Execução do Aplicativo ---
if __name__ == "__main__":
    instance_path = os.path.join(basedir, 'instance')
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)
    
    with app.app_context():
        db.create_all()
        
    app.run(debug=True, host='0.0.0.0', port=5000)