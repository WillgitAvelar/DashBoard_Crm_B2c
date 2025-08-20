
from sqlalchemy import create_engine, Column, Integer, String, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///instance/project.db"
engine = create_engine(DATABASE_URL)
Base = declarative_base()
Session = sessionmaker(bind=engine)

class B2C(Base):
    __tablename__ = 'b2_c'
    id = Column(Integer, primary_key=True)
    data = Column(Date, nullable=False)
    nome_hotel = Column(String(200), nullable=True)
    valor = Column(Float, nullable=False)
    status = Column(String(50), nullable=False)
    status_pagamento = Column(String(50), nullable=False)

Base.metadata.create_all(engine) # Ensure table exists

session = Session()
try:
    session.query(B2C).delete()
    session.commit()
    print("Tabela B2C limpa com sucesso!")
except Exception as e:
    session.rollback()
    print(f"Erro ao limpar a tabela B2C: {e}")
finally:
    session.close()


