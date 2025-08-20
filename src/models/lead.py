from src.extensions import db

class Lead(db.Model):
    __tablename__ = "lead"

    id = db.Column(db.Integer, primary_key=True)
    data_entrada = db.Column(db.Date, nullable=False)
    entrada_leads_ask_suite = db.Column(db.Integer, default=0)
    fila_atendimento = db.Column(db.Integer, default=0)
    atendimento = db.Column(db.Integer, default=0)
    qualificacao = db.Column(db.Integer, default=0)
    oportunidade = db.Column(db.Integer, default=0)
    aguardando_pagamento = db.Column(db.Integer, default=0)

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
