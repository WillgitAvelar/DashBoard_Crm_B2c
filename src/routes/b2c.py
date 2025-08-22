from flask import Blueprint, jsonify, request
from src.models.b2c import B2C  
from src import db             
from sqlalchemy import func
from datetime import datetime

b2c_bp = Blueprint("b2c", __name__)

@b2c_bp.route("/api/b2c", methods=["GET"])
def get_all_b2c():
    """
    Busca todos os registros B2C, aplicando filtros de data se fornecidos.
    Retorna uma lista de dicionários usando o método to_dict() do modelo.
    """
    query = B2C.query

    data_inicio = request.args.get('data_inicio')
    data_fim = request.args.get('data_fim')
    if data_inicio and data_fim:
        try:
            start_date = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            end_date = datetime.strptime(data_fim, '%Y-%m-%d').date()
            query = query.filter(B2C.data.between(start_date, end_date))
        except ValueError:
            return jsonify({"error": "Formato de data inválido. Use YYYY-MM-DD."}), 400

    all_items = query.order_by(B2C.data.desc()).all()
    
    results = [item.to_dict() for item in all_items]
    
    return jsonify(results)


@b2c_bp.route("/api/b2c", methods=['POST'])
def create_b2c():
    """
    Cria um novo registro B2C a partir dos dados JSON recebidos.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição sem dados"}), 400

    try:
        novo_registro = B2C(
            data=datetime.strptime(data['data'], '%Y-%m-%d').date(),
            nome_hotel=data['nome_hotel'],
            valor=data['valor'],
            status=data['status'],
            status_pagamento=data['status_pagamento'],
            usou_cupom=data.get('usou_cupom', False),
            forma_pagamento=data.get('forma_pagamento', 'Não Informado')
        )
        db.session.add(novo_registro)
        db.session.commit()
        return jsonify(novo_registro.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao criar registro: {str(e)}"}), 500


@b2c_bp.route("/api/b2c/<int:id>", methods=['GET'])
def get_b2c_by_id(id):
    """
    Busca e retorna um único registro B2C pelo seu ID.
    """
    registro = B2C.query.get_or_404(id)
    return jsonify(registro.to_dict())


@b2c_bp.route("/api/b2c/<int:id>", methods=['PUT'])
def update_b2c(id):
    """
    Atualiza um registro B2C existente com os dados JSON recebidos.
    """
    item = B2C.query.get_or_404(id)
    data = request.get_json()
    if not data:
        return jsonify({"error": "Requisição sem dados"}), 400

    try:
        item.data = datetime.strptime(data['data'], '%Y-%m-%d').date()
        item.nome_hotel = data.get('nome_hotel', item.nome_hotel)
        item.valor = data.get('valor', item.valor)
        item.status = data.get('status', item.status)
        item.status_pagamento = data.get('status_pagamento', item.status_pagamento)
        item.usou_cupom = data.get('usou_cupom', item.usou_cupom)
        item.forma_pagamento = data.get('forma_pagamento', item.forma_pagamento)
        
        db.session.commit()
        return jsonify(item.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao atualizar registro: {str(e)}"}), 500
@b2c_bp.route("/api/b2c/<int:id>", methods=['DELETE'])
def delete_b2c(id):
    """
    Deleta um registro B2C pelo seu ID.
    """
    item = B2C.query.get_or_404(id)
    try:
        db.session.delete(item)
        db.session.commit()
        return jsonify({"message": "Registro deletado com sucesso"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Erro ao deletar registro: {str(e)}"}), 500
@b2c_bp.route("/api/b2c/metrics")
def b2c_metrics():
      return jsonify({
        "total_registros": 0,
        "valor_total": 0,
        "status_registros": {},
        "status_pagamento": {},
        "vendas_por_data": [],
        "hoteis_mais_vendidos": []
    })
