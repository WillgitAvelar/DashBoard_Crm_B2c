from flask import Blueprint, jsonify, request
from src.models.b2c import B2C  # Verifique se o caminho do modelo está correto
from src import db              # Verifique se o caminho do db está correto
from sqlalchemy import func
from datetime import datetime

b2c_bp = Blueprint("b2c", __name__)

# ===================================================================
#   ROTA PARA BUSCAR TODOS OS REGISTROS B2C (com filtros de data)
# ===================================================================
@b2c_bp.route("/api/b2c", methods=['GET'])
def get_all_b2c():
    data_inicio_str = request.args.get('data_inicio')
    data_fim_str = request.args.get('data_fim')
    
    query = B2C.query

    if data_inicio_str and data_fim_str:
        try:
            data_inicio = datetime.strptime(data_inicio_str, '%Y-%m-%d').date()
            data_fim = datetime.strptime(data_fim_str, '%Y-%m-%d').date()
            query = query.filter(B2C.data.between(data_inicio, data_fim))
        except ValueError:
            return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    registros = query.order_by(B2C.data.desc()).all()
    return jsonify([r.to_dict() for r in registros])

# ===================================================================
#   ROTA PARA BUSCAR UM ÚNICO REGISTRO B2C POR ID
# ===================================================================
@b2c_bp.route("/api/b2c/<int:id>", methods=['GET'])
def get_b2c_by_id(id):
    registro = B2C.query.get_or_404(id)
    return jsonify(registro.to_dict())

# ===================================================================
#   ROTA PARA CRIAR UM NOVO REGISTRO B2C (com os novos campos)
# ===================================================================
@b2c_bp.route("/api/b2c", methods=['POST'])
def create_b2c():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição sem dados"}), 400

    novo_registro = B2C(
        data=datetime.strptime(data['data'], '%Y-%m-%d').date(),
        nome_hotel=data['nome_hotel'],
        valor=data['valor'],
        status=data['status'],
        status_pagamento=data['status_pagamento'],
        # --- RECEBENDO OS NOVOS DADOS ---
        usou_cupom=data.get('usou_cupom', False),
        forma_pagamento=data.get('forma_pagamento', 'Não Informado')
    )
    db.session.add(novo_registro)
    db.session.commit()
    return jsonify(novo_registro.to_dict()), 201

# ===================================================================
#   ROTA PARA ATUALIZAR UM REGISTRO B2C (com os novos campos)
# ===================================================================
@b2c_bp.route("/api/b2c/<int:id>", methods=['PUT'])
def update_b2c(id):
    item = B2C.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição sem dados"}), 400

    item.data = datetime.strptime(data['data'], '%Y-%m-%d').date()
    item.nome_hotel = data['nome_hotel']
    item.valor = data['valor']
    item.status = data['status']
    item.status_pagamento = data['status_pagamento']
    # --- ATUALIZANDO OS NOVOS DADOS ---
    item.usou_cupom = data.get('usou_cupom', item.usou_cupom)
    item.forma_pagamento = data.get('forma_pagamento', item.forma_pagamento)
    
    db.session.commit()
    return jsonify(item.to_dict())

# ===================================================================
#   ROTA PARA DELETAR UM REGISTRO B2C
# ===================================================================
@b2c_bp.route("/api/b2c/<int:id>", methods=['DELETE'])
def delete_b2c(id):
    item = B2C.query.get_or_404(id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Registro deletado com sucesso"}), 200


# ===================================================================
#   SUA ROTA DE MÉTRICAS (EXISTENTE)
#   (Não precisa de alterações, mas a mantemos aqui)
# ===================================================================
@b2c_bp.route("/api/b2c/metrics")
def b2c_metrics():
    data_inicio = request.args.get("dataInicio")
    data_fim = request.args.get("dataFim")

    query = B2C.query

    if data_inicio and data_fim:
        query = query.filter(B2C.data.between(data_inicio, data_fim))

    total_registros = query.count()
    valor_total_query = db.session.query(func.sum(B2C.valor)).select_from(query.subquery())
    valor_total = valor_total_query.scalar() or 0

    status_registros_query = db.session.query(B2C.status, func.count(B2C.id)).select_from(query.subquery()).group_by(B2C.status)
    status_resumido = {s: c for s, c in status_registros_query.all()}

    status_pagamento_query = db.session.query(B2C.status_pagamento, func.count(B2C.id)).select_from(query.subquery()).group_by(B2C.status_pagamento)
    status_pagamento_dict = {s: c for s, c in status_pagamento_query.all()}

    vendas_por_data_query = db.session.query(B2C.data, func.sum(B2C.valor)).select_from(query.subquery()).group_by(B2C.data).order_by(B2C.data)
    vendas_list = [{"data": str(d), "valor_total": float(v or 0)} for d, v in vendas_por_data_query.all()]

    hoteis_mais_vendidos_query = (
        db.session.query(
            B2C.nome_hotel,
            func.count(B2C.id).label("quantidade"),
            func.sum(B2C.valor).label("valor_total")
        )
        .select_from(query.subquery())
        .group_by(B2C.nome_hotel)
        .order_by(func.count(B2C.id).desc())
        .limit(5)
    )
    hoteis_list = [{"nome_hotel": h[0], "quantidade": int(h[1] or 0), "valor_total": float(h[2] or 0)} for h in hoteis_mais_vendidos_query.all()]

    return jsonify({
        "total_registros": total_registros,
        "valor_total": float(valor_total),
        "status_registros": status_resumido,
        "status_pagamento": status_pagamento_dict,
        "vendas_por_data": vendas_list,
        "hoteis_mais_vendidos": hoteis_list
    })
