from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta
import os

# Configuração do SQLAlchemy
# Assumindo que o main.py está na raiz do projeto e o instance/project.db está lá
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
DATABASE_URL = f"sqlite:///{os.path.join(INSTANCE_DIR, 'project.db')}"

engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

# Definição dos modelos (copiado de main.py para garantir consistência)
class B2C(Base):
    __tablename__ = 'b2_c'
    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    nome_hotel = Column(String(200), nullable=False)
    valor = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    status_pagamento = Column(String(50), nullable=False)

class Lead(Base):
    __tablename__ = 'lead'
    id = Column(Integer, primary_key=True)
    data_entrada = Column(Date, nullable=False)
    entrada_leads_ask_suite = Column(Integer)
    fila_atendimento = Column(Integer)
    atendimento = Column(Integer)
    qualificacao = Column(Integer)
    oportunidade = Column(Integer)
    aguardando_pagamento = Column(Integer)

# Cria as tabelas se não existirem
Base.metadata.create_all(engine)

def populate_db():
    session = Session()

    # Limpa dados existentes para evitar duplicação em execuções repetidas
    session.query(Lead).delete()
    session.query(B2C).delete()
    session.commit()

    # Adiciona dados de exemplo para Leads
    today = datetime.now().date()
    for i in range(1, 11):
        lead = Lead(
            data_entrada=today - timedelta(days=i),
            entrada_leads_ask_suite=10 + i,
            fila_atendimento=5 + i,
            atendimento=3 + i,
            qualificacao=2 + i,
            oportunidade=1 + i,
            aguardando_pagamento=0 + i
        )
        session.add(lead)

    # Adiciona dados de exemplo para B2C
    hotels = ["Hotel A", "Hotel B", "Hotel C", "Hotel D", "Hotel E"]
    statuses = ["Confirmado", "Pendente", "Cancelado"]
    payment_statuses = ["Pago", "Pendente", "Atrasado"]

    for i in range(1, 16):
        b2c = B2C(
            data=today - timedelta(days=i),
            nome_hotel=hotels[i % len(hotels)],
            valor=round(100.00 + i * 10.50, 2),
            status=statuses[i % len(statuses)],
            status_pagamento=payment_statuses[i % len(payment_statuses)]
        )
        session.add(b2c)

    session.commit()
    session.close()
    print("Banco de dados populado com sucesso!")

if __name__ == "__main__":
    populate_db()


