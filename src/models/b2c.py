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
    # Em seu arquivo de modelo (ex: src/models/b2c.py)

from src import db # ou de onde quer que seu 'db' venha
from sqlalchemy import Column, Integer, String, Float, Date, Boolean # Adicione Boolean

class B2C(db.Model):
    __tablename__ = 'b2c'
    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    nome_hotel = Column(String(150), nullable=False)
    valor = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, default='ATIVO')
    status_pagamento = Column(String(50), nullable=False, default='Pendente')
    
    # --- NOVAS COLUNAS ADICIONADAS AQUI ---
    usou_cupom = Column(Boolean, default=False)
    forma_pagamento = Column(String(50), default='Não Informado')
    # ------------------------------------

    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.isoformat(),
            'nome_hotel': self.nome_hotel,
            'valor': self.valor,
            'status': self.status,
            'status_pagamento': self.status_pagamento,
            # --- ADICIONE AO DICIONÁRIO DE RETORNO ---
            'usou_cupom': self.usou_cupom,
            'forma_pagamento': self.forma_pagamento
        }

