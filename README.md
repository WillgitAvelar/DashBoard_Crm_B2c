# Projeto B2C Dashboard

Este projeto processa dados de uma planilha Excel (447 linhas) e os integra ao formulário B2C, tratando campos vazios como NULL.

## Estrutura do Projeto

```
projeto_b2c_completo/
├── main.py                 # Aplicação Flask principal
├── static/                 # Arquivos estáticos (CSS, JS, imagens)
│   ├── script.js
│   ├── styles.css
│   └── logo.png
├── templates/              # Templates HTML
│   └── index.html
├── instance/               # Banco de dados SQLite
│   └── project.db
├── src/                    # Código fonte organizado
├── process_data.py         # Script para processar e inserir dados
├── clear_b2c_table.py      # Script para limpar tabela B2C
├── check_db.py             # Script para verificar dados no banco
├── DADOS.csv               # Dados convertidos para CSV
└── DADOS.xlsx              # Planilha original
```

## Dados Processados

- **Total de registros inseridos**: 622 registros
- **Campos vazios tratados como NULL**: Sim
- **Campos obrigatórios**: data, valor, status, status_pagamento
- **Campo opcional**: nome_hotel (pode ser NULL)

## Como Executar

1. Instale as dependências:
```bash
pip install flask sqlalchemy pandas openpyxl fpdf2
```

2. Execute a aplicação:
```bash
python3 main.py
```

3. Acesse no navegador:
```
http://localhost:5000
```

## Scripts Auxiliares

- `process_data.py`: Processa a planilha DADOS.xlsx e insere no banco
- `clear_b2c_table.py`: Limpa todos os registros da tabela B2C
- `check_db.py`: Verifica quantos registros existem no banco

## API Endpoints

- `GET /api/b2c`: Lista todos os registros B2C
- `POST /api/b2c`: Cria novo registro B2C
- `GET /api/b2c/<id>`: Obtém registro específico
- `PUT /api/b2c/<id>`: Atualiza registro específico
- `DELETE /api/b2c/<id>`: Remove registro específico
- `GET /api/b2c/metrics`: Obtém métricas dos registros

## Funcionalidades

- Dashboard com visualização de dados
- Filtros por data
- Exportação para PDF
- Formulários para adicionar/editar registros
- Gráficos e métricas
- Interface responsiva

## Observações

- Campos vazios na planilha são tratados como NULL no banco de dados
- O campo `nome_hotel` pode ser NULL para registros sem hotel especificado
- A aplicação está otimizada para economizar créditos durante o processamento
- Todos os 447 registros da planilha foram processados com sucesso

