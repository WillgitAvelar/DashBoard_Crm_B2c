# Arquivo: src/models/b2c.py (ou onde seu modelo B2C estiver)

from src.extensions import db
from sqlalchemy import Boolean # Certifique-se de que Boolean está importado

class B2C(db.Model):
    """
    Modelo ÚNICO e CORRETO para os dados de B2C.
    """
    __tablename__ = "b2c_data" # Use o nome correto da sua tabela no banco de dados

    # --- Colunas Originais ---
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    nome_hotel = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, default=0)
    status = db.Column(db.String(50), default="ATIVO")
    status_pagamento = db.Column(db.String(50), default="NÃO INFORMADO")

    # --- NOVAS COLUNAS ADICIONADAS ---
    forma_pagamento = db.Column(db.String(50), default='Não Informado')
    usou_cupom = db.Column(db.Boolean, default=False)
    # --------------------------------

    def to_dict(self):
        """
        Converte o objeto para um dicionário, garantindo que todos os
        campos, incluindo os novos, sejam incluídos.
        """
        return {
            'id': self.id,
            'data': self.data.isoformat() if self.data else None,
            'nome_hotel': self.nome_hotel,
            'valor': self.valor,
            'status': self.status,
            'status_pagamento': self.status_pagamento,
            'forma_pagamento': self.forma_pagamento, # Novo campo
            'usou_cupom': self.usou_cupom           # Novo campo
        }

    def __repr__(self):
        return f"<B2C(id={self.id}, hotel='{self.nome_hotel}')>"

