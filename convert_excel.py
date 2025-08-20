import pandas as pd

try:
    df = pd.read_excel('DADOS.xlsx')
    df.to_csv('DADOS.csv', index=False)
    print('DADOS.xlsx convertido para DADOS.csv com sucesso!')
except Exception as e:
    print(f'Erro ao converter arquivo: {e}')
