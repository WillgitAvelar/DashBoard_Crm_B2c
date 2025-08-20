from src.extensions import db

class B2C(db.Model):
    __tablename__ = "b2_c"

    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    nome_hotel = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="ATIVO")
    status_pagamento = db.Column(db.String(50), default="NÃO INFORMADO")

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
