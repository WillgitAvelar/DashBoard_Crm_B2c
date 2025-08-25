
import pandas as pd
from datetime import datetime
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

Base.metadata.create_all(engine)

def process_and_insert_data(file_path):
    df = pd.read_csv(file_path)
    session = Session()
    try:
        for index, row in df.iterrows():
            data = None
            if pd.notna(row['DATA']):
                try:
                    data = datetime.strptime(str(row['DATA']), '%Y-%m-%d').date()
                except ValueError:
                    print(f"Erro ao converter data: {row['DATA']}. Usando None.")
                    data = None

            nome_hotel = str(row['Unnamed: 1']) if pd.notna(row['Unnamed: 1']) else None
            
            valor = None
            if pd.notna(row['VALOR']):
                try:
                    # Remove 'R$' and replace comma with dot for conversion
                    valor_str = str(row['VALOR']).replace('R$', '').replace(',', '.').strip()
                    valor = float(valor_str)
                except ValueError:
                    print(f"Erro ao converter valor: {row['VALOR']}. Usando None.")
                    valor = None

            status = str(row['STATUS']) if pd.notna(row['STATUS']) else None
            status_pagamento = str(row['STATUS PAGAMENTO ']) if pd.notna(row['STATUS PAGAMENTO ']) else None

            # Handle nullable fields for B2C model
            # The 'nome_hotel' column is now nullable, so it's not checked here.
            if data is None or valor is None or status is None or status_pagamento is None:
                print(f"Skipping row {index} due to missing required data: {row.to_dict()}")
                continue

            new_b2c = B2C(
                data=data,
                nome_hotel=nome_hotel,
                valor=valor,
                status=status,
                status_pagamento=status_pagamento
            )
            session.add(new_b2c)
        session.commit()
        print("Dados inseridos com sucesso!")
    except Exception as e:
        session.rollback()
        print(f"Erro durante a inserção de dados: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    process_and_insert_data('DADOS.csv')


