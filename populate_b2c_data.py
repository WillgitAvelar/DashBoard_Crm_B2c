#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script para popular o banco de dados com dados B2C reais
Baseado na imagem fornecida pelo usuário
"""

import sys
import os
from datetime import datetime

# Adiciona o diretório raiz ao path para importar os módulos
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src import create_app, db
from src.models.b2c import B2C

# Dados extraídos da imagem fornecida
b2c_data = [
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 5633.74, "data": "13/07/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 3397.00, "data": "13/07/2025"},
    {"nome_hotel": "Buzios Beach Resort by WAM Experience", "valor": 1761.81, "data": "12/07/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 5368.00, "data": "12/07/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "11/07/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 3460.63, "data": "08/07/2025"},
    {"nome_hotel": "Vila Gale Mares Resort - All Inclusive", "valor": 10798.00, "data": "07/07/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 5497.28, "data": "06/07/2025"},
    {"nome_hotel": "Buzios Beach Resort by WAM Experience", "valor": 2606.53, "data": "06/07/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "06/07/2025"},
    {"nome_hotel": "Buzios Beach Resort by WAM Experience", "valor": 2729.00, "data": "06/07/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 4300.00, "data": "04/07/2025"},
    {"nome_hotel": "Hotel Majestic Le Canton", "valor": 3355.02, "data": "03/07/2025"},
    {"nome_hotel": "Majestic Mar Resort All Inclusive", "valor": 12362.00, "data": "03/07/2025"},
    {"nome_hotel": "Portobello Resort All Inclusive", "valor": 5394.00, "data": "02/07/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 10746.00, "data": "02/07/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 5221.50, "data": "28/06/2025"},
    {"nome_hotel": "Casa Bravo All Inclusive Resort", "valor": 3962.72, "data": "29/06/2025"},
    {"nome_hotel": "Buzios Beach Resort by WAM Experience", "valor": 5985.32, "data": "28/06/2025"},
    {"nome_hotel": "Vila Gale Mares Resort - All Inclusive", "valor": 6120.99, "data": "28/06/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1627.35, "data": "27/06/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 4168.00, "data": "27/06/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 5985.01, "data": "27/06/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 4168.86, "data": "25/06/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 5500.24, "data": "25/06/2025"},
    {"nome_hotel": "Thermas Resort Comandatuba - All Inclusive", "valor": 13595.80, "data": "24/06/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "24/06/2025"},
    {"nome_hotel": "Ocean Palace Beach Resort All Inclusive Premium", "valor": 11333.33, "data": "24/06/2025"},
    {"nome_hotel": "Buzios Beach Resort by WAM Experience", "valor": 1296.03, "data": "20/06/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 3505.34, "data": "17/06/2025"},
    {"nome_hotel": "Buzios Beach Resort by WAM Experience", "valor": 5924.00, "data": "17/06/2025"},
    {"nome_hotel": "Vila Gale Mares Resort - All Inclusive", "valor": 6958.62, "data": "17/06/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "15/06/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 4584.64, "data": "15/06/2025"},
    {"nome_hotel": "Hotel Village Le Canton", "valor": 1337.45, "data": "15/06/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 2559.63, "data": "10/06/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 7106.77, "data": "10/06/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "10/06/2025"},
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 5320.00, "data": "07/06/2025"},
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 5431.40, "data": "07/06/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 2559.63, "data": "04/06/2025"},
    {"nome_hotel": "Vila Gale Mares Resort - All Inclusive", "valor": 14024.03, "data": "04/06/2025"},
    {"nome_hotel": "Hotel Village Le Canton", "valor": 1337.45, "data": "30/05/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 2064.83, "data": "28/05/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 4142.33, "data": "28/05/2025"},
    {"nome_hotel": "Pisano Angra dos Reis", "valor": 2380.10, "data": "23/05/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1031.10, "data": "22/05/2025"},
    {"nome_hotel": "Pisano Angra dos Reis", "valor": 5654.70, "data": "19/05/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 3402.00, "data": "17/05/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "17/05/2025"},
    {"nome_hotel": "Majestic Mar Resort All Inclusive", "valor": 7400.00, "data": "12/05/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 5390.00, "data": "11/05/2025"},
    {"nome_hotel": "Vila Gale Cumbuco Resort - All Inclusive", "valor": 14033.83, "data": "04/05/2025"},
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 7204.75, "data": "04/05/2025"},
    {"nome_hotel": "Thermas Resort Comandatuba - All Inclusive", "valor": 17585.00, "data": "04/05/2025"},
    {"nome_hotel": "Grand Palladium Imbassai Resort & Spa", "valor": 7154.32, "data": "01/05/2025"},
    {"nome_hotel": "Arraial d'Ajuda Eco Resort", "valor": 5218.21, "data": "30/04/2025"},
    {"nome_hotel": "Grand Amazon Expedition", "valor": 16112.29, "data": "29/04/2025"},
    {"nome_hotel": "Thermas Resort Comandatuba - All Inclusive", "valor": 17489.12, "data": "27/04/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "27/04/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 2280.11, "data": "27/04/2025"},
    {"nome_hotel": "Vila Gale Cumbuco Resort - All Inclusive", "valor": 12304.08, "data": "27/04/2025"},
    {"nome_hotel": "Vila Gale Touros Resort - All Inclusive", "valor": 5534.84, "data": "27/04/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 5202.72, "data": "27/04/2025"},
    {"nome_hotel": "Vila Gale Alagoas Resort - All Inclusive", "valor": 6548.20, "data": "23/04/2025"},
    {"nome_hotel": "Vila Gale Alagoas Resort - All Inclusive", "valor": 3100.66, "data": "22/04/2025"},
    {"nome_hotel": "Vila Gale Alagoas Resort - All Inclusive", "valor": 7168.00, "data": "22/04/2025"},
    {"nome_hotel": "Vila Gale Alagoas Resort - All Inclusive", "valor": 4500.66, "data": "20/04/2025"},
    {"nome_hotel": "Vila Gale Alagoas Resort - All Inclusive", "valor": 4500.66, "data": "20/04/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1194.11, "data": "20/04/2025"},
    {"nome_hotel": "Vila Gale Alagoas Resort - All Inclusive", "valor": 4500.66, "data": "19/04/2025"},
    {"nome_hotel": "Vila Gale Alagoas Resort - All Inclusive", "valor": 4500.66, "data": "19/04/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 3042.42, "data": "19/04/2025"},
    {"nome_hotel": "Vila Gale Mares Resort - All Inclusive", "valor": 20323.66, "data": "18/04/2025"},
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 4945.03, "data": "18/04/2025"},
    {"nome_hotel": "Vila Gale Mares Resort - All Inclusive", "valor": 6693.47, "data": "17/04/2025"},
    {"nome_hotel": "Grand Oca Maragogi Beach & Leisure Resort", "valor": 4547.47, "data": "05/04/2025"},
    {"nome_hotel": "Vila Gale Collection Douro", "valor": 3427.15, "data": "05/04/2025"},
    {"nome_hotel": "Porto Alto Resort - GAV Resorts", "valor": 3578.41, "data": "05/04/2025"},
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 11154.82, "data": "04/04/2025"},
    {"nome_hotel": "Vila Gale Cumbuco Resort - All Inclusive", "valor": 5096.03, "data": "04/04/2025"},
    {"nome_hotel": "Grand Oca Maragogi Beach & Leisure Resort", "valor": 4370.20, "data": "02/04/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "02/04/2025"},
    {"nome_hotel": "Tivoli Ecoresort Praia do Forte", "valor": 10289.27, "data": "26/03/2025"},
    {"nome_hotel": "Arraial d'Ajuda Eco Resort", "valor": 11154.00, "data": "26/03/2025"},
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 6617.93, "data": "26/03/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 18225.00, "data": "24/03/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "24/03/2025"},
    {"nome_hotel": "Tivoli Ecoresort Praia do Forte", "valor": 7560.00, "data": "23/03/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 11484.00, "data": "23/03/2025"},
    {"nome_hotel": "Thermas Resort Comandatuba - All Inclusive", "valor": 17370.22, "data": "22/03/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 9324.78, "data": "22/03/2025"},
    {"nome_hotel": "Porto Alto Resort - GAV Resorts", "valor": 1571.73, "data": "22/03/2025"},
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 5329.49, "data": "16/03/2025"},
    {"nome_hotel": "Thermas Resort Comandatuba - All Inclusive", "valor": 9348.09, "data": "15/03/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 2249.13, "data": "13/03/2025"},
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 7387.00, "data": "13/03/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "13/03/2025"},
    {"nome_hotel": "Enotel Porto de Galinhas - All Inclusive", "valor": 13268.10, "data": "10/03/2025"},
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 5218.55, "data": "09/03/2025"},
    {"nome_hotel": "Tivoli Ecoresort Praia do Forte", "valor": 19948.29, "data": "08/03/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1279.34, "data": "06/03/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "06/03/2025"},
    {"nome_hotel": "Majestic Mar Resort All Inclusive", "valor": 5119.58, "data": "02/03/2025"},
    {"nome_hotel": "Vila Gale Cumbuco Resort - All Inclusive", "valor": 9353.58, "data": "24/02/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 2724.84, "data": "18/02/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 5328.96, "data": "17/02/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "17/02/2025"},
    {"nome_hotel": "Vila Gale Mares Resort - All Inclusive", "valor": 11209.58, "data": "16/02/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 3374.60, "data": "16/02/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1487.88, "data": "13/02/2025"},
    {"nome_hotel": "Vila Gale Cumbuco Resort - All Inclusive", "valor": 4632.31, "data": "09/02/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "09/02/2025"},
    {"nome_hotel": "Ocean Palace Beach Resort All Inclusive Premium", "valor": 7410.00, "data": "04/02/2025"},
    {"nome_hotel": "Holiday Beach Resort All Inclusive", "valor": 9517.33, "data": "04/02/2025"},
    {"nome_hotel": "Majestic Mar Resort All Inclusive", "valor": 6128.53, "data": "02/02/2025"},
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 7362.31, "data": "02/02/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "02/02/2025"},
    {"nome_hotel": "Beachstar Selection Praia do Forte", "valor": 12429.22, "data": "27/01/2025"},
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 4980.54, "data": "26/01/2025"},
    {"nome_hotel": "Vila Gale Angra Resort - All Inclusive", "valor": 3166.58, "data": "26/01/2025"},
    {"nome_hotel": "Vila Gale Alagoas Resort - All Inclusive", "valor": 6534.72, "data": "24/01/2025"},
    {"nome_hotel": "Casa Bravo All Inclusive Resort", "valor": 10388.26, "data": "22/01/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 2696.48, "data": "22/01/2025"},
    {"nome_hotel": "Santissimo Resort", "valor": 1584.00, "data": "22/01/2025"},
    {"nome_hotel": "Ocean Palace Beach Resort All Inclusive Premium", "valor": 10225.80, "data": "16/01/2025"},
    {"nome_hotel": "Summerville Resort", "valor": 9755.48, "data": "16/01/2025"},
    {"nome_hotel": "Tivoli Ecoresort Praia do Forte", "valor": 5378.25, "data": "15/01/2025"},
    {"nome_hotel": "Portobello Resort & Safari", "valor": 11268.00, "data": "04/01/2025"}
]

def convert_date(date_str):
    """Converte data do formato DD/MM/YYYY para YYYY-MM-DD"""
    day, month, year = date_str.split('/')
    return f"{year}-{month}-{day}"

def populate_b2c_data():
    """Popula o banco de dados com os dados B2C"""
    app = create_app()
    
    with app.app_context():
        # Limpa dados existentes
        B2C.query.delete()
        
        # Status possíveis
        status_options = ['Confirmado', 'Ativo', 'Pendente', 'Cancelado']
        status_pagamento_options = ['Pago', 'Pendente', 'Atrasado']
        
        for i, item in enumerate(b2c_data):
            # Converte a data
            data_convertida = datetime.strptime(convert_date(item['data']), '%Y-%m-%d').date()
            
            # Define status baseado no índice para variedade
            status = status_options[i % len(status_options)]
            status_pagamento = status_pagamento_options[i % len(status_pagamento_options)]
            
            # Cria o registro B2C
            b2c_record = B2C(
                data=data_convertida,
                nome_hotel=item['nome_hotel'],
                valor=item['valor'],
                status=status,
                status_pagamento=status_pagamento
            )
            
            db.session.add(b2c_record)
        
        # Salva todas as alterações
        db.session.commit()
        print(f"✅ {len(b2c_data)} registros B2C foram inseridos com sucesso!")

if __name__ == '__main__':
    populate_b2c_data()

