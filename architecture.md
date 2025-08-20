# Arquitetura do Sistema

## Visão Geral
O sistema será construído como uma aplicação web, dividida em duas partes principais: um backend robusto para manipulação de dados e lógica de negócios, e um frontend interativo para a interface do usuário e visualização de dados.

## Backend (API e Lógica de Negócios)
- **Tecnologia Principal**: Flask (Python)
- **Funções**: Gerenciamento de dados (Leads e B2C), cálculo de métricas, processamento de requisições do frontend, geração de relatórios PDF.
- **Banco de Dados**: SQLite para desenvolvimento e testes. Para produção, PostgreSQL é recomendado para maior escalabilidade e robustez.
- **ORM**: SQLAlchemy para interação com o banco de dados, permitindo modelagem de dados Pythonic e abstração de SQL.
- **Estrutura de Dados**: 
    - **Leads**: Data de entrada, Entrada de Leads Ask Suite, Fila de Atendimento, Atendimento, Qualificação, Oportunidade, Aguardando Pagamento.
    - **B2C**: Data, Nome do Hotel, Valor, Status, Status de Pagamento.

## Frontend (Interface do Usuário e Visualização)
- **Tecnologia Principal**: HTML, CSS, JavaScript puro (Vanilla JS).
- **Funções**: Renderização do dashboard, formulários de entrada de dados, exibição de gráficos e tabelas, interação com a API do backend.
- **Bibliotecas de Gráficos**: Chart.js para a criação de gráficos interativos e visualmente atraentes.
- **Design**: Responsivo, garantindo uma experiência de usuário consistente em diferentes dispositivos (desktops, tablets, smartphones).

## Geração de Relatórios PDF
- **Tecnologia**: Uma biblioteca Python como `ReportLab` ou `WeasyPrint` será utilizada para gerar os relatórios PDF. A escolha final dependerá da facilidade de integração com gráficos e da capacidade de incluir marca d'água e identidade visual.

## Persistência e Segurança
- Os dados serão armazenados no banco de dados escolhido (SQLite/PostgreSQL).
- A segurança será abordada através de boas práticas de desenvolvimento web, como validação de entrada de dados e, se necessário, autenticação de usuário para acesso ao sistema (a ser definida em fases posteriores).

## Fluxo de Dados
1. O usuário interage com o frontend (preenche formulários, aplica filtros).
2. O frontend envia requisições (GET/POST) para a API do Flask.
3. O backend processa as requisições, interage com o banco de dados, calcula métricas.
4. O backend retorna os dados processados para o frontend.
5. O frontend atualiza o dashboard com os novos dados e visualizações.
6. Para relatórios PDF, o frontend envia uma requisição ao backend, que gera o PDF e o disponibiliza para download.


