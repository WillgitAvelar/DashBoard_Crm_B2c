from flask import Blueprint, request, jsonify
from src.models.b2c import B2C, db
from datetime import datetime, date
from sqlalchemy import func, desc

b2c_bp = Blueprint('b2c', __name__)

@b2c_bp.route('/b2c', methods=['GET'])
def get_b2c():
    """Retorna todos os registros B2C com filtro opcional por data"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = B2C.query
        
        if data_inicio:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            query = query.filter(B2C.data >= data_inicio_obj)
            
        if data_fim:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            query = query.filter(B2C.data <= data_fim_obj)
            
        b2c_records = query.order_by(B2C.data.desc()).all()
        return jsonify([record.to_dict() for record in b2c_records])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@b2c_bp.route('/b2c', methods=['POST'])
def create_b2c():
    """Cria um novo registro B2C"""
    try:
        data = request.get_json()
        
        # Converte a string de data para objeto date
        data_obj = datetime.strptime(data['data'], '%Y-%m-%d').date() if data.get('data') else date.today()
        
        b2c_record = B2C(
            data=data_obj,
            nome_hotel=data['nome_hotel'],
            valor=float(data['valor']),
            status=data['status'],
            status_pagamento=data['status_pagamento']
        )
        
        db.session.add(b2c_record)
        db.session.commit()
        
        return jsonify(b2c_record.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@b2c_bp.route('/b2c/<int:b2c_id>', methods=['PUT'])
def update_b2c(b2c_id):
    """Atualiza um registro B2C existente"""
    try:
        b2c_record = B2C.query.get_or_404(b2c_id)
        data = request.get_json()
        
        if 'data' in data:
            b2c_record.data = datetime.strptime(data['data'], '%Y-%m-%d').date()
        if 'nome_hotel' in data:
            b2c_record.nome_hotel = data['nome_hotel']
        if 'valor' in data:
            b2c_record.valor = float(data['valor'])
        if 'status' in data:
            b2c_record.status = data['status']
        if 'status_pagamento' in data:
            b2c_record.status_pagamento = data['status_pagamento']
            
        db.session.commit()
        return jsonify(b2c_record.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@b2c_bp.route('/b2c/<int:b2c_id>', methods=['DELETE'])
def delete_b2c(b2c_id):
    """Deleta um registro B2C"""
    try:
        b2c_record = B2C.query.get_or_404(b2c_id)
        db.session.delete(b2c_record)
        db.session.commit()
        return jsonify({'message': 'Registro B2C deletado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@b2c_bp.route('/b2c/metrics', methods=['GET'])
def get_b2c_metrics():
    """Retorna métricas dos dados B2C com filtro opcional por data"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = B2C.query
        
        if data_inicio:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            query = query.filter(B2C.data >= data_inicio_obj)
            
        if data_fim:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            query = query.filter(B2C.data <= data_fim_obj)
        
        # Métricas básicas
        total_registros = query.count()
        total_valor = query.with_entities(func.sum(B2C.valor)).scalar() or 0
        valor_medio = query.with_entities(func.avg(B2C.valor)).scalar() or 0
        
        # Hotéis mais vendidos (top 5)
        hoteis_mais_vendidos = db.session.query(
            B2C.nome_hotel,
            func.count(B2C.id).label('quantidade'),
            func.sum(B2C.valor).label('valor_total')
        ).filter(
            query.whereclause if query.whereclause is not None else True
        ).group_by(B2C.nome_hotel).order_by(desc('valor_total')).limit(5).all()
        
        # Hotéis menos vendidos (bottom 5)
        hoteis_menos_vendidos = db.session.query(
            B2C.nome_hotel,
            func.count(B2C.id).label('quantidade'),
            func.sum(B2C.valor).label('valor_total')
        ).filter(
            query.whereclause if query.whereclause is not None else True
        ).group_by(B2C.nome_hotel).order_by('valor_total').limit(5).all()
        
        # Status dos registros
        status_count = db.session.query(
            B2C.status,
            func.count(B2C.id).label('quantidade')
        ).filter(
            query.whereclause if query.whereclause is not None else True
        ).group_by(B2C.status).all()
        
        # Status de pagamento
        status_pagamento_count = db.session.query(
            B2C.status_pagamento,
            func.count(B2C.id).label('quantidade')
        ).filter(
            query.whereclause if query.whereclause is not None else True
        ).group_by(B2C.status_pagamento).all()
        
        metrics = {
            'total_registros': total_registros,
            'total_valor': float(total_valor),
            'valor_medio': float(valor_medio),
            'hoteis_mais_vendidos': [
                {
                    'nome_hotel': hotel[0],
                    'quantidade': hotel[1],
                    'valor_total': float(hotel[2])
                } for hotel in hoteis_mais_vendidos
            ],
            'hoteis_menos_vendidos': [
                {
                    'nome_hotel': hotel[0],
                    'quantidade': hotel[1],
                    'valor_total': float(hotel[2])
                } for hotel in hoteis_menos_vendidos
            ],
            'status_registros': [
                {
                    'status': status[0],
                    'quantidade': status[1]
                } for status in status_count
            ],
            'status_pagamento': [
                {
                    'status_pagamento': status[0],
                    'quantidade': status[1]
                } for status in status_pagamento_count
            ]
        }
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

