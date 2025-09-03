from flask_sqlalchemy import SQLAlchemy
from datetime import date

# Criamos a instância do banco de dados aqui.
# Ela será conectada ao seu app principal depois.
db = SQLAlchemy()

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
        return {c.name: getattr(self, c.name).strftime('%Y-%m-%d') if isinstance(getattr(self, c.name), date) else getattr(self, c.name) for c in self.__table__.columns}

class B2C(db.Model):
    __tablename__ = 'b2_c'
    id = db.Column(db.Integer, primary_key=True)
    id_externo = db.Column(db.String(100), nullable=True, unique=True)
    data = db.Column(db.Date, nullable=False)
    nome_hotel = db.Column(db.String(200))
    valor = db.Column(db.Float)
    status = db.Column(db.String(50)) # Agora aceita 'Status do ID', 'Edição', 'Expirado', 'Confirmado', 'Aguardando Pagamento', 'Cancelado'
    status_pagamento = db.Column(db.String(50)) # Agora aceita 'Não informado', 'Aprovado', 'Pendente', 'Atrasado', 'Cancelado'
    usou_cupom = db.Column(db.Boolean, default=False)
    forma_pagamento = db.Column(db.String(50)) # Agora aceita 'Não informado', 'Pix', 'Crédito', 'Débito', 'Boleto', 'Depósito Bancário', 'Faturado'

    def to_dict(self):
        return {c.name: getattr(self, c.name).strftime('%Y-%m-%d') if isinstance(getattr(self, c.name), date) else getattr(self, c.name) for c in self.__table__.columns}