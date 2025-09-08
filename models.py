from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, date

db = SQLAlchemy()

class Lead(db.Model):
    __tablename__ = 'leads'
    
    id = db.Column(db.Integer, primary_key=True)
    data_entrada = db.Column(db.Date, nullable=False, default=date.today)
    entrada_leads_ask_suite = db.Column(db.Integer, default=0)
    fila_atendimento = db.Column(db.Integer, default=0)
    atendimento = db.Column(db.Integer, default=0)
    qualificacao = db.Column(db.Integer, default=0)
    oportunidade = db.Column(db.Integer, default=0)
    aguardando_pagamento = db.Column(db.Integer, default=0)
    
    def to_dict(self):
        return {
            'id': self.id,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None,
            'entrada_leads_ask_suite': self.entrada_leads_ask_suite,
            'fila_atendimento': self.fila_atendimento,
            'atendimento': self.atendimento,
            'qualificacao': self.qualificacao,
            'oportunidade': self.oportunidade,
            'aguardando_pagamento': self.aguardando_pagamento
        }

class B2C(db.Model):
    __tablename__ = 'b2c'
    
    id = db.Column(db.Integer, primary_key=True)
    id_externo = db.Column(db.String(100), unique=True, nullable=True)
    data = db.Column(db.Date, nullable=False, default=date.today)
    nome_hotel = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, default=0.0)
    forma_pagamento = db.Column(db.String(50), default='Não Informado')
    usou_cupom = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='Pendente')
    status_pagamento = db.Column(db.String(50), default='Pendente')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_externo': self.id_externo,
            'data': self.data.isoformat() if self.data else None,
            'nome_hotel': self.nome_hotel,
            'valor': self.valor,
            'forma_pagamento': self.forma_pagamento,
            'usou_cupom': self.usou_cupom,
            'status': self.status,
            'status_pagamento': self.status_pagamento
        }



class MyResorts(db.Model):
    __tablename__ = 'my_resorts'
    
    id = db.Column(db.Integer, primary_key=True)
    id_externo = db.Column(db.String(100), unique=True, nullable=True)
    data = db.Column(db.Date, nullable=False, default=date.today)
    nome_hotel = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, default=0.0)
    forma_pagamento = db.Column(db.String(50), default='Não Informado')
    usou_cupom = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(50), default='Pendente')
    status_pagamento = db.Column(db.String(50), default='Pendente')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_externo': self.id_externo,
            'data': self.data.isoformat() if self.data else None,
            'nome_hotel': self.nome_hotel,
            'valor': self.valor,
            'forma_pagamento': self.forma_pagamento,
            'usou_cupom': self.usou_cupom,
            'status': self.status,
            'status_pagamento': self.status_pagamento
        }


