// script.js - VERSÃO FINAL, COMPLETA E CORRIGIDA

let currentTab = 'leads';
let currentFilters = { 
  dataInicio: '', 
  dataFim: '',
  hotelSearch: '',
  myResortsHotelSearch: ''
};
let charts = {};
let editingId = null;

// ================== Inicialização Principal ==================
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  setDefaultDates();
  switchTab('leads');
});

// ================== Funções Auxiliares (Helpers) ==================
function formatDate(d) {
  if (!d) return '';
  const dt = d instanceof Date ? d : new Date(d + 'T00:00:00');
  return dt.toISOString().split('T')[0];
}

function formatDateBR(dateString) {
  if (!dateString || dateString.includes('Invalid')) return 'Data Inválida';
  const date = new Date(dateString + 'T00:00:00');
  return date.toLocaleDateString('pt-BR', { timeZone: 'UTC' });
}

function formatCurrency(value) {
  const v = Number(value) || 0;
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v);
}

// ================== Configuração Centralizada de Eventos ==================
function setupEventListeners() {
  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.addEventListener('click', () => switchTab(tab.dataset.tab));
  });
  document.getElementById('applyFilterBtn')?.addEventListener('click', applyFilters);
  document.getElementById('clearFilterBtn')?.addEventListener('click', clearFilters);
  
  // Botões de Adicionar
  document.getElementById('addLeadBtn')?.addEventListener('click', () => openModal('lead'));
  document.getElementById('addB2cBtn')?.addEventListener('click', () => openModal('b2c'));
  document.getElementById('addMyResortsBtn')?.addEventListener('click', () => openModal('my_resorts'));

  document.getElementById('exportPdfBtn')?.addEventListener('click', exportToPDF);
  
  // Modais
  document.getElementById('leadModal')?.addEventListener('click', (e) => { if (e.target === e.currentTarget) closeModal('lead'); });
  document.getElementById('b2cModal')?.addEventListener('click', (e) => { if (e.target === e.currentTarget) closeModal('b2c'); });
  document.getElementById('my_resortsModal')?.addEventListener('click', (e) => { if (e.target === e.currentTarget) closeModal('my_resorts'); });
  
  // Botões de Fechar/Cancelar Modais
  document.getElementById('closeLeadModal')?.addEventListener('click', () => closeModal('lead'));
  document.getElementById('closeB2cModal')?.addEventListener('click', () => closeModal('b2c'));
  document.getElementById('closeMyResortsModal')?.addEventListener('click', () => closeModal('my_resorts'));
  document.getElementById('cancelLeadBtn')?.addEventListener('click', () => closeModal('lead'));
  document.getElementById('cancelB2cBtn')?.addEventListener('click', () => closeModal('b2c'));
  document.getElementById('cancelMyResortsBtn')?.addEventListener('click', () => closeModal('my_resorts'));

  // Submissão de Formulários
  document.getElementById('leadForm')?.addEventListener('submit', handleLeadSubmit);
  document.getElementById('b2cForm')?.addEventListener('submit', handleB2cSubmit);
  document.getElementById('my_resortsForm')?.addEventListener('submit', handleMyResortsSubmit);
  
  // Botões de Mostrar/Esconder Tabela
  document.getElementById('toggleLeadsBtn')?.addEventListener('click', () => toggleTableVisibility('leadsTableContainer'));
  document.getElementById('toggleB2cBtn')?.addEventListener('click', () => toggleTableVisibility('b2cTableContainer'));
  document.getElementById('toggleMyResortsBtn')?.addEventListener('click', () => toggleTableVisibility('myResortsTableContainer'));

  // Filtros de Hotel
  document.getElementById('hotelSearchBtn')?.addEventListener('click', applyFilters);
  document.getElementById('hotelSearchInput')?.addEventListener('keypress', (e) => { if (e.key === 'Enter') applyFilters(); });
  document.getElementById('myResortsHotelSearchBtn')?.addEventListener('click', applyFilters);
  document.getElementById('myResortsHotelSearchInput')?.addEventListener('keypress', (e) => { if (e.key === 'Enter') applyFilters(); });

  // Listener para fechar o modal de zoom
  document.getElementById('closeChartZoomModal')?.addEventListener('click', () => {
    const modal = document.getElementById('chartZoomModal');
    if (modal) modal.classList.remove('active');
  });
}

function toggleTableVisibility(containerId) {
    const container = document.getElementById(containerId);
    if(container) container.style.display = container.style.display === 'none' ? 'block' : 'none';
}

// ================== Navegação e Filtros ==================
function switchTab(tabName) {
  if (!tabName) return;
  currentTab = tabName;
  document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.toggle('active', tab.dataset.tab === tabName));
  document.querySelectorAll('.tab-content').forEach(content => {
    content.style.display = 'none';
  });
  
  const activeContent = document.getElementById(`${tabName}-content`);
  if (activeContent) {
    activeContent.style.display = 'block';
  }
  
  loadData();
}

function setDefaultDates() {
  const today = new Date(); 
  const firstDayOfYear = new Date(today.getFullYear(), 0, 1); 
  const inicioInput = document.getElementById('dataInicio');
  const fimInput = document.getElementById('dataFim');
  if (inicioInput) inicioInput.value = formatDate(firstDayOfYear);
  if (fimInput) fimInput.value = formatDate(today);
  
  document.getElementById('hotelSearchInput').value = '';
  document.getElementById('myResortsHotelSearchInput').value = '';

  currentFilters.dataInicio = inicioInput?.value || '';
  currentFilters.dataFim = fimInput?.value || '';
  currentFilters.hotelSearch = '';
  currentFilters.myResortsHotelSearch = '';
}

function applyFilters() {
  currentFilters.dataInicio = document.getElementById('dataInicio').value;
  currentFilters.dataFim = document.getElementById('dataFim').value;
  currentFilters.hotelSearch = document.getElementById('hotelSearchInput').value;
  currentFilters.myResortsHotelSearch = document.getElementById('myResortsHotelSearchInput').value;

  if (currentFilters.dataInicio && currentFilters.dataFim && currentFilters.dataInicio > currentFilters.dataFim) {
    showToast('Data de início não pode ser maior que a data de fim.', 'error');
    return;
  }

  loadData();
  showToast('Filtros aplicados com sucesso!', 'success');
}

function clearFilters() {
  setDefaultDates();
  applyFilters();
  showToast('Filtros limpos.', 'info');
}

// ================== Carregamento de Dados (API) ==================
async function loadData() {
  showLoading(true);
  try {
    if (currentTab === 'leads') await loadLeadsData();
    else if (currentTab === 'b2c') await loadB2cData();
    else if (currentTab === 'my_resorts') await loadMyResortsData();
  } catch (err) {
    console.error('Erro ao carregar dados:', err);
    showToast('Falha ao carregar dados. Verifique o console.', 'error');
  } finally {
    showLoading(false);
  }
}

async function loadLeadsData() {
  const params = new URLSearchParams({ data_inicio: currentFilters.dataInicio, data_fim: currentFilters.dataFim });
  const resp = await fetch(`/api/leads?${params}`);
  if (!resp.ok) throw new Error('Erro ao buscar dados de Leads');
  const leads = await resp.json();
  const metrics = calculateLeadsMetrics(leads);
  updateLeadsMetrics(metrics);
  updateLeadsTable(leads);
  updateLeadsCharts(metrics);
}

async function loadB2cData() {
  const params = new URLSearchParams({ data_inicio: currentFilters.dataInicio, data_fim: currentFilters.dataFim, hotel: currentFilters.hotelSearch });
  const resp = await fetch(`/api/b2c?${params}`);
  if (!resp.ok) throw new Error('Erro ao buscar dados B2C');
  const data = await resp.json();
  const metrics = calculateGenericMetrics(data);
  updateB2cMetrics(metrics);
  updateB2cTable(data);
  updateB2cCharts(metrics);
}

async function loadMyResortsData() {
  const params = new URLSearchParams({ data_inicio: currentFilters.dataInicio, data_fim: currentFilters.dataFim, hotel: currentFilters.myResortsHotelSearch });
  const resp = await fetch(`/api/my_resorts?${params}`);
  if (!resp.ok) throw new Error('Erro ao buscar dados de My Resorts');
  const data = await resp.json();
  const metrics = calculateGenericMetrics(data);
  updateMyResortsMetrics(metrics);
  updateMyResortsTable(data);
  updateMyResortsCharts(metrics);
}

// ================== Cálculo de Métricas ==================
function calculateLeadsMetrics(leads) {
  const defaultMetrics = { entrada_leads_ask_suite: 0, fila_atendimento: 0, atendimento: 0, qualificacao: 0, oportunidade: 0, aguardando_pagamento: 0 };
  if (!Array.isArray(leads) || leads.length === 0) {
    return defaultMetrics;
  }
  const sortedLeads = [...leads].sort((a, b) => new Date(b.data_entrada) - new Date(a.data_entrada));
  const latestLead = sortedLeads[0];
  return {
    entrada_leads_ask_suite: Number(latestLead.entrada_leads_ask_suite) || 0,
    fila_atendimento: Number(latestLead.fila_atendimento) || 0,
    atendimento: Number(latestLead.atendimento) || 0,
    qualificacao: Number(latestLead.qualificacao) || 0,
    oportunidade: Number(latestLead.oportunidade) || 0,
    aguardando_pagamento: Number(latestLead.aguardando_pagamento) || 0
  };
}

function calculateGenericMetrics(data) {
  const metrics = { 
    total_registros: 0, 
    total_valor: 0, 
    status_stats: { 'Confirmado': 0, 'Pendente': 0, 'Cancelado': 0, 'Negado': 0, 'Reservado': 0 },
    hoteis_stats: {}, 
    status_pagamento_stats: {}, 
    forma_pagamento_stats: {},
    cupom_stats: { 'Sim': 0, 'Não': 0 } 
  };

  if (!Array.isArray(data)) return metrics;

  data.forEach(item => {
    metrics.total_registros++;
    metrics.total_valor += Number(item.valor) || 0;
    if (metrics.status_stats.hasOwnProperty(item.status || 'Pendente')) {
        metrics.status_stats[item.status || 'Pendente']++;
    }
    metrics.status_pagamento_stats[item.status_pagamento || 'Não Informado'] = (metrics.status_pagamento_stats[item.status_pagamento || 'Não Informado'] || 0) + 1;
    metrics.forma_pagamento_stats[item.forma_pagamento || 'Não Informado'] = (metrics.forma_pagamento_stats[item.forma_pagamento || 'Não Informado'] || 0) + 1;
    metrics.cupom_stats[item.usou_cupom ? 'Sim' : 'Não']++;
    
    // BLOCO CORRIGIDO
    if (item.nome_hotel) {
      if (!metrics.hoteis_stats[item.nome_hotel]) { 
        metrics.hoteis_stats[item.nome_hotel] = { nome_hotel: item.nome_hotel, valor_total: 0, quantidade: 0 }; 
      }
      metrics.hoteis_stats[item.nome_hotel].valor_total += Number(item.valor) || 0;
      metrics.hoteis_stats[item.nome_hotel].quantidade++; // Esta linha foi adicionada
    }
  });

  metrics.hoteis_mais_vendidos = Object.values(metrics.hoteis_stats);
  metrics.status_pagamento = Object.entries(metrics.status_pagamento_stats).map(([status, qtd]) => ({ status_pagamento: status, quantidade: qtd }));
  metrics.forma_pagamento = Object.entries(metrics.forma_pagamento_stats).map(([forma, qtd]) => ({ forma_pagamento: forma, quantidade: qtd }));
  
  return metrics;
}


// ================== Atualização da UI (Métricas e Tabelas) ==================
function updateLeadsMetrics(metrics) {
  document.getElementById('leadsAskSuite').textContent = metrics.entrada_leads_ask_suite || 0;
  document.getElementById('leadsFilaAtendimento').textContent = metrics.fila_atendimento || 0;
  document.getElementById('leadsAtendimento').textContent = metrics.atendimento || 0;
  document.getElementById('leadsQualificacao').textContent = metrics.qualificacao || 0;
  document.getElementById('leadsOportunidade').textContent = metrics.oportunidade || 0;
  document.getElementById('leadsAguardandoPagamento').textContent = metrics.aguardando_pagamento || 0;
}

function updateB2cMetrics(metrics) {
  document.getElementById('totalB2cRegistros').textContent = metrics.total_registros || 0;
  document.getElementById('totalB2cValor').textContent = formatCurrency(metrics.total_valor || 0);
}

function updateMyResortsMetrics(metrics) {
  document.getElementById('totalMyResortsRegistros').textContent = metrics.total_registros || 0;
  document.getElementById('totalMyResortsValor').textContent = formatCurrency(metrics.total_valor || 0);
}

function updateLeadsTable(leads) {
  const tbody = document.getElementById('leadsTableBody');
  if (!tbody) return;
  const sortedLeads = [...leads].sort((a, b) => new Date(b.data_entrada) - new Date(a.data_entrada));
  tbody.innerHTML = ''; 
  sortedLeads.forEach(lead => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${formatDateBR(lead.data_entrada)}</td>
      <td>${lead.entrada_leads_ask_suite || '-'}</td>
      <td>${lead.fila_atendimento || '-'}</td>
      <td>${lead.atendimento || '-'}</td>
      <td>${lead.qualificacao || '-'}</td>
      <td>${lead.oportunidade || '-'}</td>
      <td>${lead.aguardando_pagamento || '-'}</td>
      <td><div class="action-buttons"><button class="btn btn-primary" data-id="${lead.id}" data-action="edit-lead"><i class="fas fa-edit"></i></button><button class="btn btn-danger" data-id="${lead.id}" data-action="delete-lead"><i class="fas fa-trash"></i></button></div></td>`;
    tbody.appendChild(row);
  });
  addTableActionListeners(tbody);
}

function updateB2cTable(b2cData) {
  const tbody = document.getElementById('b2cTableBody');
  if (!tbody) return;
  const sortedData = [...b2cData].sort((a, b) => new Date(b.data) - new Date(a.data));
  tbody.innerHTML = '';
  sortedData.forEach(item => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${item.id_externo || '-'}</td>
      <td>${formatDateBR(item.data)}</td>
      <td>${item.nome_hotel || '-'}</td>
      <td>${formatCurrency(item.valor || 0)}</td>
      <td>${item.forma_pagamento || 'Não Informado'}</td>
      <td><span class="status-badge ${item.usou_cupom ? 'status-confirmado' : 'status-cancelado'}">${item.usou_cupom ? 'Sim' : 'Não'}</span></td>
      <td><span class="status-badge status-${(item.status || 'pendente').toLowerCase().replace(/\s+/g, '-')}">${item.status || 'Pendente'}</span></td>
      <td><span class="status-badge status-${(item.status_pagamento || 'pendente').toLowerCase().replace(/\s+/g, '-')}">${item.status_pagamento || 'Pendente'}</span></td>
      <td><div class="action-buttons"><button class="btn btn-primary" data-id="${item.id}" data-action="edit-b2c"><i class="fas fa-edit"></i></button><button class="btn btn-danger" data-id="${item.id}" data-action="delete-b2c"><i class="fas fa-trash"></i></button></div></td>`;
    tbody.appendChild(row);
  });
  addTableActionListeners(tbody);
}

function updateMyResortsTable(data) {
  const tbody = document.getElementById('myResortsTableBody');
  if (!tbody) return;
  const sortedData = [...data].sort((a, b) => new Date(b.data) - new Date(a.data));
  tbody.innerHTML = '';
  sortedData.forEach(item => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${item.id_externo || '-'}</td>
      <td>${formatDateBR(item.data)}</td>
      <td>${item.nome_hotel || '-'}</td>
      <td>${formatCurrency(item.valor || 0)}</td>
      <td>${item.forma_pagamento || 'Não Informado'}</td>
      <td><span class="status-badge ${item.usou_cupom ? 'status-confirmado' : 'status-cancelado'}">${item.usou_cupom ? 'Sim' : 'Não'}</span></td>
      <td><span class="status-badge status-${(item.status || 'pendente').toLowerCase().replace(/\s+/g, '-')}">${item.status || 'Pendente'}</span></td>
      <td><span class="status-badge status-${(item.status_pagamento || 'pendente').toLowerCase().replace(/\s+/g, '-')}">${item.status_pagamento || 'Pendente'}</span></td>
      <td><div class="action-buttons"><button class="btn btn-primary" data-id="${item.id}" data-action="edit-my_resorts"><i class="fas fa-edit"></i></button><button class="btn btn-danger" data-id="${item.id}" data-action="delete-my_resorts"><i class="fas fa-trash"></i></button></div></td>`;
    tbody.appendChild(row);
  });
  addTableActionListeners(tbody);
}

function addTableActionListeners(tbody) {
    tbody.querySelectorAll('button[data-action]').forEach(btn => {
        btn.addEventListener('click', delegatedClickHandler);
    });
}

function delegatedClickHandler(e) {
  const btn = e.currentTarget;
  const id = btn.dataset.id;
  const action = btn.dataset.action;
  if (!action || !id) return;
  const actions = {
    'edit-lead': () => editItem('leads', 'lead', id),
    'delete-lead': () => deleteItem('leads', id),
    'edit-b2c': () => editItem('b2c', 'b2c', id),
    'delete-b2c': () => deleteItem('b2c', id),
    'edit-my_resorts': () => editItem('my_resorts', 'my_resorts', id),
    'delete-my_resorts': () => deleteItem('my_resorts', id),
  };
  if (actions[action]) actions[action]();
}

// ================== Gráficos (Chart.js) ==================
function createOrUpdateChart(chartId, chartConfig) {
    const canvas = document.getElementById(chartId);
    if (!canvas) return;
    if (charts[chartId]) charts[chartId].destroy();
    const newChart = new Chart(canvas.getContext("2d"), chartConfig);
    charts[chartId] = newChart;
    canvas.onclick = () => openChartZoom(newChart);
}

function updateLeadsCharts(metrics) {
    const funnelLabels = ['Entrada Leads', 'Fila Atendimento', 'Atendimento', 'Qualificação', 'Oportunidade', 'Aguardando Pagamento'];
    const funnelValues = [ metrics.entrada_leads_ask_suite, metrics.fila_atendimento, metrics.atendimento, metrics.qualificacao, metrics.oportunidade, metrics.aguardando_pagamento ];
    createOrUpdateChart('leadsFunnelChart', {
      type: 'bar', data: { labels: funnelLabels, datasets: [{ label: `Funil de Leads`, data: funnelValues, backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'], borderRadius: 5 }] },
      options: { indexAxis: 'y', responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false }, title: { display: true, text: 'Funil de Conversão de Leads', font: { size: 16 }, padding: 15 }, tooltip: { callbacks: { label: (c) => `${c.label}: ${c.parsed.x} leads` } } }, scales: { x: { beginAtZero: true, title: { display: true, text: 'Quantidade' } }, y: { grid: { display: false } } } }
    });
}

function updateB2cCharts(metrics) {
    const commonOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "right" } } };
    const topHoteisValor = [...metrics.hoteis_mais_vendidos].sort((a, b) => b.valor_total - a.valor_total).slice(0, 5);
    createOrUpdateChart('topHoteisChart', { type: "doughnut", data: { labels: topHoteisValor.map(h => h.nome_hotel || "N/A"), datasets: [{ data: topHoteisValor.map(h => h.valor_total || 0), backgroundColor: ["#42a5f5", "#ab47bc", "#ffa726", "#66bb6a", "#ef5350"] }] }, options: commonOptions });
    createOrUpdateChart('statusChart', { type: "pie", data: { labels: Object.keys(metrics.status_stats), datasets: [{ data: Object.values(metrics.status_stats), backgroundColor: ["#4caf50", "#ffc107", "#f44336", "#9e9e9e", "#2196f3"], borderColor: '#ffffff', borderWidth: 2 }] }, options: commonOptions });
    createOrUpdateChart('statusPagamentoChart', { type: "bar", data: { labels: metrics.status_pagamento.map(s => s.status_pagamento), datasets: [{ label: "Quantidade", data: metrics.status_pagamento.map(s => s.quantidade), backgroundColor: "#4facfe" }] }, options: { ...commonOptions, indexAxis: "y", plugins: { legend: { display: false } } } });
    createOrUpdateChart('formaPagamentoChart', { type: 'doughnut', data: { labels: metrics.forma_pagamento.map(item => item.forma_pagamento), datasets: [{ data: metrics.forma_pagamento.map(item => item.quantidade), backgroundColor: ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6', '#1abc9c'], borderColor: '#ffffff', borderWidth: 2 }] }, options: commonOptions });
    createOrUpdateChart('cupomChart', { type: "pie", data: { labels: Object.keys(metrics.cupom_stats), datasets: [{ data: Object.values(metrics.cupom_stats), backgroundColor: ["#4caf50","#f44336"], borderColor: '#ffffff', borderWidth: 2 }] }, options: commonOptions });
    const topHoteisQtd = [...metrics.hoteis_mais_vendidos].sort((a, b) => b.quantidade - a.quantidade).slice(0, 5);
    createOrUpdateChart('topHoteisQtdChart', { type: "bar", data: { labels: topHoteisQtd.map(h => h.nome_hotel || "N/A"), datasets: [{ label: "Quantidade de Vendas", data: topHoteisQtd.map(h => h.quantidade || 0), backgroundColor: "#42a5f5" }] }, options: { ...commonOptions, plugins: { legend: { display: false }, tooltip: { callbacks: { label: (ctx) => `${ctx.raw} vendas` } } }, scales: { y: { beginAtZero: true, title: { display: true, text: "Vendas" } }, x: { title: { display: true, text: "Hotéis" } } } } });
}

function updateMyResortsCharts(metrics) {
    const commonOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "right" } } };
    const topHoteisValor = [...metrics.hoteis_mais_vendidos].sort((a, b) => b.valor_total - a.valor_total).slice(0, 5);
    createOrUpdateChart('myResortsTopHoteisChart', { type: "doughnut", data: { labels: topHoteisValor.map(h => h.nome_hotel || "N/A"), datasets: [{ data: topHoteisValor.map(h => h.valor_total || 0), backgroundColor: ["#42a5f5", "#ab47bc", "#ffa726", "#66bb6a", "#ef5350"] }] }, options: commonOptions });
    createOrUpdateChart('myResortsStatusChart', { type: "pie", data: { labels: Object.keys(metrics.status_stats), datasets: [{ data: Object.values(metrics.status_stats), backgroundColor: ["#4caf50", "#ffc107", "#f44336", "#9e9e9e", "#2196f3"], borderColor: '#ffffff', borderWidth: 2 }] }, options: commonOptions });
    createOrUpdateChart('myResortsStatusPagamentoChart', { type: "bar", data: { labels: metrics.status_pagamento.map(s => s.status_pagamento), datasets: [{ label: "Quantidade", data: metrics.status_pagamento.map(s => s.quantidade), backgroundColor: "#4facfe" }] }, options: { ...commonOptions, indexAxis: "y", plugins: { legend: { display: false } } } });
    createOrUpdateChart('myResortsFormaPagamentoChart', { type: 'doughnut', data: { labels: metrics.forma_pagamento.map(item => item.forma_pagamento), datasets: [{ data: metrics.forma_pagamento.map(item => item.quantidade), backgroundColor: ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6', '#1abc9c'], borderColor: '#ffffff', borderWidth: 2 }] }, options: commonOptions });
    createOrUpdateChart('myResortsCupomChart', { type: "pie", data: { labels: Object.keys(metrics.cupom_stats), datasets: [{ data: Object.values(metrics.cupom_stats), backgroundColor: ["#4caf50","#f44336"], borderColor: '#ffffff', borderWidth: 2 }] }, options: commonOptions });
    const topHoteisQtd = [...metrics.hoteis_mais_vendidos].sort((a, b) => b.quantidade - a.quantidade).slice(0, 5);
    createOrUpdateChart('myResortsTopHoteisQtdChart', { type: "bar", data: { labels: topHoteisQtd.map(h => h.nome_hotel || "N/A"), datasets: [{ label: "Quantidade de Vendas", data: topHoteisQtd.map(h => h.quantidade || 0), backgroundColor: "#42a5f5" }] }, options: { ...commonOptions, plugins: { legend: { display: false }, tooltip: { callbacks: { label: (ctx) => `${ctx.raw} vendas` } } }, scales: { y: { beginAtZero: true, title: { display: true, text: "Vendas" } }, x: { title: { display: true, text: "Hotéis" } } } } });
}

// ================== Modais (Adicionar/Editar) ==================
function openModal(type, data = null) {
  editingId = data ? data.id : null;
  const modal = document.getElementById(`${type}Modal`);
  if (!modal) return;
  document.getElementById(`${type}ModalTitle`).textContent = data ? `Editar ${type.toUpperCase().replace('_', ' ')}` : `Adicionar ${type.toUpperCase().replace('_', ' ')}`;
  const form = document.getElementById(`${type}Form`);
  form.reset();

  if (type === 'lead') {
    if (data) {
      form.data_entrada.value = formatDate(data.data_entrada);
      form.entrada_leads_ask_suite.value = data.entrada_leads_ask_suite || '';
      form.fila_atendimento.value = data.fila_atendimento || '';
      form.atendimento.value = data.atendimento || '';
      form.qualificacao.value = data.qualificacao || '';
      form.oportunidade.value = data.oportunidade || '';
      form.aguardando_pagamento.value = data.aguardando_pagamento || '';
    } else {
      form.data_entrada.value = formatDate(new Date());
    }
  } else if (type === 'b2c' || type === 'my_resorts') {
    if (data) {
      form.id_externo.value = data.id_externo || '';
      form.data.value = formatDate(data.data);
      form.nome_hotel.value = data.nome_hotel || '';
      form.valor.value = data.valor || '';
      form.status.value = data.status || '';
      form.status_pagamento.value = data.status_pagamento || '';
      form.forma_pagamento.value = data.forma_pagamento || 'Não Informado';
      form.usou_cupom.value = data.usou_cupom ? 'true' : 'false';
    } else {
      form.data.value = formatDate(new Date());
      form.forma_pagamento.value = 'Não Informado';
      form.usou_cupom.value = 'false';
    }
  }
  modal.classList.add('active');
}

function closeModal(type) {
  editingId = null;
  const modal = document.getElementById(`${type}Modal`);
  if (modal) modal.classList.remove('active');
}

// ================== Operações CRUD (Salvar, Editar, Deletar) ==================
async function handleLeadSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const data = {
    data_entrada: formData.get('data_entrada'),
    entrada_leads_ask_suite: parseInt(formData.get('entrada_leads_ask_suite'), 10) || 0,
    fila_atendimento: parseInt(formData.get('fila_atendimento'), 10) || 0,
    atendimento: parseInt(formData.get('atendimento'), 10) || 0,
    qualificacao: parseInt(formData.get('qualificacao'), 10) || 0,
    oportunidade: parseInt(formData.get('oportunidade'), 10) || 0,
    aguardando_pagamento: parseInt(formData.get('aguardando_pagamento'), 10) || 0,
  };
  await saveData('lead', data, editingId);
}

async function handleB2cSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const data = {
    id_externo: formData.get('id_externo'),
    data: formData.get('data'),
    nome_hotel: formData.get('nome_hotel'),
    valor: parseFloat(formData.get('valor').replace(',', '.')) || 0,
    status: formData.get('status'),
    status_pagamento: formData.get('status_pagamento'),
    forma_pagamento: formData.get('forma_pagamento'),
    usou_cupom: formData.get('usou_cupom') === 'true'
  };
  await saveData('b2c', data, editingId);
}

async function handleMyResortsSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const formData = new FormData(form);
  const data = {
    id_externo: formData.get('id_externo'),
    data: formData.get('data'),
    nome_hotel: formData.get('nome_hotel'),
    valor: parseFloat(formData.get('valor').replace(',', '.')) || 0,
    status: formData.get('status'),
    status_pagamento: formData.get('status_pagamento'),
    forma_pagamento: formData.get('forma_pagamento'),
    usou_cupom: formData.get('usou_cupom') === 'true'
  };
  await saveData('my_resorts', data, editingId);
}

async function saveData(type, data, id) {
  const endpoint = type === 'lead' ? 'leads' : type;
  const url = id ? `/api/${endpoint}/${id}` : `/api/${endpoint}`;
  const method = id ? 'PUT' : 'POST';
  
  showLoading(true);
  try {
    const resp = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({ error: `Erro ${resp.status} ao salvar.` }));
      throw new Error(errData.error);
    }
    closeModal(type);
    loadData();
    showToast(`${type.toUpperCase().replace('_', ' ')} ${id ? 'atualizado' : 'criado'} com sucesso!`, 'success');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    showLoading(false);
  }
}

async function editItem(endpoint, type, id) {
    showLoading(true);
    try {
        const resp = await fetch(`/api/${endpoint}/${id}`);
        if (!resp.ok) throw new Error(`Não foi possível carregar o item ${id}`);
        const item = await resp.json();
        openModal(type, item);
    } catch (err) {
        console.error(`Erro ao buscar ${type} ${id}:`, err);
        showToast(`Erro ao carregar dados para edição.`, 'error');
    } finally {
        showLoading(false);
    }
}

async function deleteItem(type, id) {
  if (!confirm(`Tem certeza que deseja deletar este item? A ação não pode ser desfeita.`)) return;
  
  showLoading(true);
  try {
    const resp = await fetch(`/api/${type}/${id}`, { method: 'DELETE' });
    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({ error: `Erro ao deletar item.` }));
      throw new Error(errData.error);
    }
    loadData();
    showToast('Item deletado com sucesso!', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    showLoading(false);
  }
}

// ================== Exportação para PDF ==================
async function exportToPDF() {
  showToast('Funcionalidade de exportação para PDF ainda não implementada.', 'info');
}

// ================== Utilitários da UI (Loading, Toasts) ==================
function showLoading(show) {
  const overlay = document.getElementById('loadingOverlay');
  if (overlay) overlay.classList.toggle('active', !!show);
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  
  const icons = { success: 'fa-check-circle', error: 'fa-exclamation-circle', warning: 'fa-exclamation-triangle', info: 'fa-info-circle' };
  
  toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
  container.appendChild(toast);
  
  setTimeout(() => { toast.classList.add('show'); }, 100);

  setTimeout(() => {
    toast.classList.remove('show');
    toast.classList.add('hide');
    toast.addEventListener('transitionend', () => { toast.remove(); }, { once: true });
  }, 5000);
}

// ================== Lógica de Zoom do Gráfico ==================
function openChartZoom(chartInstance) {
    const modal = document.getElementById('chartZoomModal');
    const container = document.getElementById('chartZoomContainer');
    const title = document.getElementById('chartZoomTitle');

    if (!modal || !container || !title || !chartInstance) return;

    title.innerText = chartInstance.options.plugins.title.text || 'Visualização do Gráfico';
    
    container.innerHTML = '<canvas id="zoomCanvas"></canvas>';
    const zoomCanvas = document.getElementById('zoomCanvas');

    new Chart(zoomCanvas.getContext('2d'), {
        type: chartInstance.config.type,
        data: chartInstance.config.data,
        options: {
            ...chartInstance.config.options,
            responsive: true,
            maintainAspectRatio: false
        }
    });

    modal.classList.add('active');
}

