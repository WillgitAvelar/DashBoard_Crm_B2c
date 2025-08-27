from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class B2C(Base):
    __tablename__ = 'b2_c'
    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    nome_hotel = Column(String(200), nullable=True)
    valor = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    status_pagamento = Column(String(50), nullable=False)
    forma_pagamento = Column(String(50), nullable=False)
    usou_cupom = Column(String(10), nullable=False)

engine = create_engine('sqlite:///instance/project.db')
Session = sessionmaker(bind=engine)
session = Session()

try:
    count = session.query(B2C).count()
    print(f'Total de registros B2C: {count}')
    
    # Mostrar alguns registros de exemplo
    sample_records = session.query(B2C).limit(5).all()
    print("\nPrimeiros 5 registros:")
    for record in sample_records:
        print(f"ID: {record.id}, Data: {record.data}, Hotel: {record.nome_hotel}, Valor: {record.valor}, Status: {record.status}")
finally:
    session.close()

