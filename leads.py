from flask import Blueprint, request, jsonify
from src.models.lead import Lead, db
from datetime import datetime, date
from sqlalchemy import func

leads_bp = Blueprint('leads', __name__)

@leads_bp.route('/leads', methods=['GET'])
def get_leads():
    """Retorna todos os leads com filtro opcional por data"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Lead.query
        
        if data_inicio:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            query = query.filter(Lead.data_entrada >= data_inicio_obj)
            
        if data_fim:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            query = query.filter(Lead.data_entrada <= data_fim_obj)
            
        leads = query.order_by(Lead.data_entrada.desc()).all()
        return jsonify([lead.to_dict() for lead in leads])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@leads_bp.route('/leads', methods=['POST'])
def create_lead():
    """Cria um novo lead"""
    try:
        data = request.get_json()
        
        # Converte a string de data para objeto date
        data_entrada = datetime.strptime(data['data_entrada'], '%Y-%m-%d').date() if data.get('data_entrada') else date.today()
        
        lead = Lead(
            data_entrada=data_entrada,
            entrada_leads_ask_suite=data.get('entrada_leads_ask_suite'),
            fila_atendimento=data.get('fila_atendimento'),
            atendimento=data.get('atendimento'),
            qualificacao=data.get('qualificacao'),
            oportunidade=data.get('oportunidade'),
            aguardando_pagamento=data.get('aguardando_pagamento')
        )
        
        db.session.add(lead)
        db.session.commit()
        
        return jsonify(lead.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@leads_bp.route('/leads/<int:lead_id>', methods=['PUT'])
def update_lead(lead_id):
    """Atualiza um lead existente"""
    try:
        lead = Lead.query.get_or_404(lead_id)
        data = request.get_json()
        
        if 'data_entrada' in data:
            lead.data_entrada = datetime.strptime(data['data_entrada'], '%Y-%m-%d').date()
        if 'entrada_leads_ask_suite' in data:
            lead.entrada_leads_ask_suite = data['entrada_leads_ask_suite']
        if 'fila_atendimento' in data:
            lead.fila_atendimento = data['fila_atendimento']
        if 'atendimento' in data:
            lead.atendimento = data['atendimento']
        if 'qualificacao' in data:
            lead.qualificacao = data['qualificacao']
        if 'oportunidade' in data:
            lead.oportunidade = data['oportunidade']
        if 'aguardando_pagamento' in data:
            lead.aguardando_pagamento = data['aguardando_pagamento']
            
        db.session.commit()
        return jsonify(lead.to_dict())
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@leads_bp.route('/leads/<int:lead_id>', methods=['DELETE'])
def delete_lead(lead_id):
    """Deleta um lead"""
    try:
        lead = Lead.query.get_or_404(lead_id)
        db.session.delete(lead)
        db.session.commit()
        return jsonify({'message': 'Lead deletado com sucesso'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@leads_bp.route('/leads/metrics', methods=['GET'])
def get_leads_metrics():
    """Retorna métricas dos leads com filtro opcional por data"""
    try:
        data_inicio = request.args.get('data_inicio')
        data_fim = request.args.get('data_fim')
        
        query = Lead.query
        
        if data_inicio:
            data_inicio_obj = datetime.strptime(data_inicio, '%Y-%m-%d').date()
            query = query.filter(Lead.data_entrada >= data_inicio_obj)
            
        if data_fim:
            data_fim_obj = datetime.strptime(data_fim, '%Y-%m-%d').date()
            query = query.filter(Lead.data_entrada <= data_fim_obj)
        
        total_leads = query.count()
        
        # Contagem por status/etapa
        metrics = {
            'total_leads': total_leads,
            'entrada_leads_ask_suite': query.filter(Lead.entrada_leads_ask_suite.isnot(None)).count(),
            'fila_atendimento': query.filter(Lead.fila_atendimento.isnot(None)).count(),
            'atendimento': query.filter(Lead.atendimento.isnot(None)).count(),
            'qualificacao': query.filter(Lead.qualificacao.isnot(None)).count(),
            'oportunidade': query.filter(Lead.oportunidade.isnot(None)).count(),
            'aguardando_pagamento': query.filter(Lead.aguardando_pagamento.isnot(None)).count()
        }
        
        return jsonify(metrics)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

