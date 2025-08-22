// ===================================================================
//   SCRIPT.JS - VERSÃO FINAL COMPLETA E CORRIGIDA
// ===================================================================

let currentTab = 'leads';
let currentFilters = { dataInicio: '', dataFim: '' };
let charts = {};
let editingId = null;
let allB2cData = [];

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
  if (!dateString) return '-';
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
  document.getElementById('addLeadBtn')?.addEventListener('click', () => openModal('lead'));
  document.getElementById('addB2cBtn')?.addEventListener('click', () => openModal('b2c'));
  document.getElementById('exportPdfBtn')?.addEventListener('click', exportToPDF);
  document.getElementById('leadModal')?.addEventListener('click', (e) => { if (e.target === e.currentTarget) closeModal('lead'); });
  document.getElementById('b2cModal')?.addEventListener('click', (e) => { if (e.target === e.currentTarget) closeModal('b2c'); });
  document.getElementById('closeLeadModal')?.addEventListener('click', () => closeModal('lead'));
  document.getElementById('closeB2cModal')?.addEventListener('click', () => closeModal('b2c'));
  document.getElementById('cancelLeadBtn')?.addEventListener('click', () => closeModal('lead'));
  document.getElementById('cancelB2cBtn')?.addEventListener('click', () => closeModal('b2c'));
  document.getElementById('leadForm')?.addEventListener('submit', handleLeadSubmit);
  document.getElementById('b2cForm')?.addEventListener('submit', handleB2cSubmit);
  document.getElementById('toggleLeadsBtn')?.addEventListener('click', () => {
    const container = document.getElementById('leadsTableContainer');
    if(container) container.style.display = container.style.display === 'none' ? 'block' : 'none';
  });
  document.getElementById('toggleB2cBtn')?.addEventListener('click', () => {
    const container = document.getElementById('b2cTableContainer');
    if(container) container.style.display = container.style.display === 'none' ? 'block' : 'none';
  });

  const chartZoomModal = document.getElementById('chartZoomModal');
  const closeZoomBtn = document.getElementById('closeChartZoomModal');
  closeZoomBtn?.addEventListener('click', () => chartZoomModal.classList.remove('active'));
  chartZoomModal?.addEventListener('click', (e) => { if (e.target === chartZoomModal) chartZoomModal.classList.remove('active'); });

  document.querySelectorAll('.chart-container canvas').forEach(canvas => {
    canvas.addEventListener('click', () => {
        const chartKey = Object.keys(charts).find(key => charts[key].canvas === canvas);
        if (charts[chartKey]) openChartZoom(charts[chartKey]);
    });
  });

  const hotelSearchBtn = document.getElementById('hotelSearchBtn');
  const hotelSearchInput = document.getElementById('hotelSearchInput');
  hotelSearchBtn?.addEventListener('click', handleHotelSearch);
  hotelSearchInput?.addEventListener('keypress', (e) => { if (e.key === 'Enter') handleHotelSearch(); });
}

// ================== Navegação e Filtros ==================
function switchTab(tabName) {
  if (!tabName) return;
  currentTab = tabName;
  document.querySelectorAll('.nav-tab').forEach(tab => tab.classList.toggle('active', tab.dataset.tab === tabName));
  document.getElementById('leads-content').style.display = (tabName === 'leads') ? 'grid' : 'none';
  document.getElementById('b2c-content').style.display = (tabName === 'b2c') ? 'grid' : 'none';
  loadData();
}

function setDefaultDates() {
  const today = new Date(); 
  const firstDayOfYear = new Date(today.getFullYear(), 0, 1); 
  const inicioInput = document.getElementById('dataInicio');
  const fimInput = document.getElementById('dataFim');
  if (inicioInput) inicioInput.value = formatDate(firstDayOfYear);
  if (fimInput) fimInput.value = formatDate(today);
  currentFilters.dataInicio = inicioInput?.value || '';
  currentFilters.dataFim = fimInput?.value || '';
}

function applyFilters() {
  const dataInicio = document.getElementById('dataInicio').value;
  const dataFim = document.getElementById('dataFim').value;
  if (dataInicio && dataFim && dataInicio > dataFim) {
    showToast('Data de início não pode ser maior que a data de fim.', 'error');
    return;
  }
  currentFilters.dataInicio = dataInicio;
  currentFilters.dataFim = dataFim;
  loadData();
  showToast('Filtros aplicados com sucesso!', 'success');
}

function clearFilters() {
  document.getElementById('dataInicio').value = '';
  document.getElementById('dataFim').value = '';
  setDefaultDates();
  loadData();
  showToast('Filtros limpos.', 'info');
}

// ================== Carregamento de Dados (API) ==================
async function loadData() {
  showLoading(true);
  try {
    if (currentTab === 'leads') await loadLeadsData();
    else await loadB2cData();
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
  updateLeadsMetrics(calculateLeadsMetrics(leads));
  updateLeadsTable(leads || []);
  updateLeadsCharts(calculateDailyLeadsMetrics(leads));
}

async function loadB2cData() {
  const params = new URLSearchParams({ data_inicio: currentFilters.dataInicio, data_fim: currentFilters.dataFim });
  const resp = await fetch(`/api/b2c?${params}`);
  if (!resp.ok) throw new Error('Erro ao buscar dados B2C');
  const data = await resp.json();
  allB2cData = data || [];
  const metrics = calculateB2cMetrics(allB2cData);
  updateB2cMetrics(metrics);
  updateB2cTable(allB2cData);
  updateB2cCharts(allB2cData, metrics);
}

// ================== Cálculo de Métricas ==================
function calculateLeadsMetrics(leads) {
  const metrics = { totalLeads: 0, leadsAskSuite: 0, leadsFilaAtendimento: 0, leadsAtendimento: 0, leadsQualificacao: 0, leadsOportunidade: 0, leadsAguardandoPagamento: 0 };
  if (!Array.isArray(leads)) return metrics;
  leads.forEach(lead => {
    metrics.totalLeads++;
    metrics.leadsAskSuite += Number(lead.entrada_leads_ask_suite) || 0;
    metrics.leadsFilaAtendimento += Number(lead.fila_atendimento) || 0;
    metrics.leadsAtendimento += Number(lead.atendimento) || 0;
    metrics.leadsQualificacao += Number(lead.qualificacao) || 0;
    metrics.leadsOportunidade += Number(lead.oportunidade) || 0;
    metrics.leadsAguardandoPagamento += Number(lead.aguardando_pagamento) || 0;
  });
  return metrics;
}

function calculateDailyLeadsMetrics(leads) {
    const dailyData = {};
    (leads || []).forEach(lead => {
      const date = lead.data_entrada;
      if (!date) return;
      if (!dailyData[date]) { dailyData[date] = { askSuite: 0, filaAtendimento: 0, atendimento: 0, qualificacao: 0, oportunidade: 0, aguardandoPagamento: 0 }; }
      dailyData[date].askSuite += Number(lead.entrada_leads_ask_suite) || 0;
      dailyData[date].filaAtendimento += Number(lead.fila_atendimento) || 0;
      dailyData[date].atendimento += Number(lead.atendimento) || 0;
      dailyData[date].qualificacao += Number(lead.qualificacao) || 0;
      dailyData[date].oportunidade += Number(lead.oportunidade) || 0;
      dailyData[date].aguardandoPagamento += Number(lead.aguardando_pagamento) || 0;
    });
    const totals = { askSuite: 0, filaAtendimento: 0, atendimento: 0, qualificacao: 0, oportunidade: 0, aguardandoPagamento: 0 };
    Object.values(dailyData).forEach(dayData => {
      totals.askSuite += dayData.askSuite;
      totals.filaAtendimento += dayData.filaAtendimento;
      totals.atendimento += dayData.atendimento;
      totals.qualificacao += dayData.qualificacao;
      totals.oportunidade += dayData.oportunidade;
      totals.aguardandoPagamento += dayData.aguardandoPagamento;
    });
    return { ...totals, dailyData, totalDays: Object.keys(dailyData).length || 1 };
}

function calculateB2cMetrics(data) {
  const metrics = { 
    total_registros: 0, 
    total_valor: 0, 
    total_confirmados: 0, 
    total_pendentes: 0, 
    total_cancelados: 0, 
    hoteis_stats: {}, 
    status_pagamento_stats: {},
    forma_pagamento_stats: {},
    cupom_stats: { 'Sim': 0, 'Não': 0 } 
  };

  if (!Array.isArray(data)) return metrics;

  data.forEach(item => {
    metrics.total_registros++;
    metrics.total_valor += Number(item.valor) || 0;
    
    const status = (item.status || 'pendente').toLowerCase();
    if (status === 'confirmado' || status === 'ativo') metrics.total_confirmados++;
    else if (status === 'cancelado') metrics.total_cancelados++;
    else if (status === 'pendente') metrics.total_pendentes++;
    
    const statusPag = item.status_pagamento || 'Não Informado';
    metrics.status_pagamento_stats[statusPag] = (metrics.status_pagamento_stats[statusPag] || 0) + 1;

    const formaPag = item.forma_pagamento || 'Não Informado';
    metrics.forma_pagamento_stats[formaPag] = (metrics.forma_pagamento_stats[formaPag] || 0) + 1;

    if (item.usou_cupom === true || item.usou_cupom === 'true') {
        metrics.cupom_stats['Sim']++;
    } else {
        metrics.cupom_stats['Não']++;
    }

    if (item.nome_hotel) {
      if (!metrics.hoteis_stats[item.nome_hotel]) { metrics.hoteis_stats[item.nome_hotel] = { nome_hotel: item.nome_hotel, valor_total: 0, quantidade: 0 }; }
      metrics.hoteis_stats[item.nome_hotel].valor_total += Number(item.valor) || 0;
      metrics.hoteis_stats[item.nome_hotel].quantidade++;
    }
  });

  metrics.hoteis_mais_vendidos = Object.values(metrics.hoteis_stats);
  metrics.status_pagamento = Object.entries(metrics.status_pagamento_stats).map(([status, qtd]) => ({ status_pagamento: status, quantidade: qtd }));
  metrics.forma_pagamento = Object.entries(metrics.forma_pagamento_stats).map(([forma, qtd]) => ({ forma_pagamento: forma, quantidade: qtd }));
  
  return metrics;
}

// ================== Atualização da UI (Métricas e Tabelas) ==================
function updateLeadsMetrics(metrics) {
  document.getElementById('totalLeads').textContent = metrics.totalLeads || 0;
  document.getElementById('leadsAskSuite').textContent = metrics.leadsAskSuite || 0;
  document.getElementById('leadsFilaAtendimento').textContent = metrics.leadsFilaAtendimento || 0;
  document.getElementById('leadsAtendimento').textContent = metrics.leadsAtendimento || 0;
  document.getElementById('leadsQualificacao').textContent = metrics.leadsQualificacao || 0;
  document.getElementById('leadsOportunidade').textContent = metrics.leadsOportunidade || 0;
  document.getElementById('leadsAguardandoPagamento').textContent = metrics.leadsAguardandoPagamento || 0;
}

function updateB2cMetrics(metrics) {
  document.getElementById('totalB2cRegistros').textContent = metrics.total_registros || 0;
  document.getElementById('totalB2cValor').textContent = formatCurrency(metrics.total_valor || 0);
}

function updateLeadsTable(leads) {
  const tbody = document.getElementById('leadsTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';
  (leads || []).forEach(lead => {
    const row = document.createElement('tr');
    row.innerHTML = `<td>${formatDateBR(lead.data_entrada)}</td><td>${lead.entrada_leads_ask_suite || '-'}</td><td>${lead.fila_atendimento || '-'}</td><td>${lead.atendimento || '-'}</td><td>${lead.qualificacao || '-'}</td><td>${lead.oportunidade || '-'}</td><td>${lead.aguardando_pagamento || '-'}</td><td><div class="action-buttons"><button class="btn btn-primary" data-id="${lead.id}" data-action="edit-lead"><i class="fas fa-edit"></i></button><button class="btn btn-danger" data-id="${lead.id}" data-action="delete-lead"><i class="fas fa-trash"></i></button></div></td>`;
    tbody.appendChild(row);
  });
  addTableActionListeners(tbody);
}

// ================== Atualização da UI (Métricas e Tabelas) ==================
// ... (outras funções de atualização) ...

function updateB2cTable(b2cData) {
  const tbody = document.getElementById('b2cTableBody');
  if (!tbody) return;
  
  // ========================================================
  //      ADICIONE APENAS ESTA LINHA DE CÓDIGO AQUI
  // ========================================================
  const sortedData = [...b2cData].sort((a, b) => new Date(b.data) - new Date(a.data));
  // ========================================================

  tbody.innerHTML = '';
  
  // Altere a linha abaixo para usar a nova variável 'sortedData'
  (sortedData || []).forEach(item => {
    const statusClass = (item.status || 'pendente').toLowerCase().replace(/\s+/g, '-');
    const pagClass = (item.status_pagamento || 'nao-informado').toLowerCase().replace(/\s+/g, '-');
    const row = document.createElement('tr');
    row.innerHTML = `
      <td>${formatDateBR(item.data)}</td>
      <td>${item.nome_hotel || '-'}</td>
      <td>${formatCurrency(item.valor || 0)}</td>
      <td><span class="status-badge status-${statusClass}">${item.status || 'Pendente'}</span></td>
      <td><span class="status-badge status-${pagClass}">${item.status_pagamento || 'Não Informado'}</span></td>
      <td>
        <div class="action-buttons">
          <button class="btn btn-primary" data-id="${item.id}" data-action="edit-b2c"><i class="fas fa-edit"></i></button>
          <button class="btn btn-danger" data-id="${item.id}" data-action="delete-b2c"><i class="fas fa-trash"></i></button>
        </div>
      </td>`;
    tbody.appendChild(row);
  });
  addTableActionListeners(tbody);
}


function addTableActionListeners(tbody) {
    tbody.querySelectorAll('button[data-action]').forEach(btn => {
        btn.removeEventListener('click', delegatedClickHandler); 
        btn.addEventListener('click', delegatedClickHandler);
    });
}

function delegatedClickHandler(e) {
  const btn = e.currentTarget;
  const id = btn.dataset.id;
  const action = btn.dataset.action;
  if (!action || !id) return;
  const actions = {
    'edit-lead': () => editLead(id),
    'delete-lead': () => deleteLead(id),
    'edit-b2c': () => editB2c(id),
    'delete-b2c': () => deleteB2c(id),
  };
  if (actions[action]) actions[action]();
}

// ================== Gráficos (Chart.js) ==================
function createOrUpdateChart(chartId, chartConfig) {
    const canvas = document.getElementById(chartId);
    if (!canvas) return;
    const chartKey = chartId.replace('Chart', '');
    if (charts[chartKey]) charts[chartKey].destroy();
    charts[chartKey] = new Chart(canvas.getContext("2d"), chartConfig);
}

function updateLeadsCharts(dailyMetrics) {
    const days = Object.keys(dailyMetrics.dailyData || {});
    const lastDay = days.length > 0 ? days[days.length - 1] : null;
    const dataDay = lastDay ? dailyMetrics.dailyData[lastDay] : { askSuite: 0, filaAtendimento: 0, atendimento: 0, qualificacao: 0, oportunidade: 0, aguardandoPagamento: 0 };
    const funnelLabels = ['Ask Suite', 'Fila Atendimento', 'Atendimento', 'Qualificação', 'Oportunidade', 'Aguardando Pagamento'];
    const funnelValues = [ dataDay.askSuite, dataDay.filaAtendimento, dataDay.atendimento, dataDay.qualificacao, dataDay.oportunidade, dataDay.aguardandoPagamento ];
    
    createOrUpdateChart('leadsFunnelChart', {
      type: 'bar',
      data: { 
        labels: funnelLabels, 
        datasets: [{ 
          label: lastDay ? `Leads do dia ${formatDateBR(lastDay)}` : 'Nenhum dado no período', 
          data: funnelValues, 
          backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'], 
          borderRadius: 5 
        }]
      },
      options: {
        indexAxis: 'y', 
        responsive: true, 
        maintainAspectRatio: false,
        plugins: { 
          legend: { display: false }, 
          title: { display: true, text: 'Funil de Leads (Dia Mais Recente)', font: { size: 16 }, padding: 15 }, 
          tooltip: { callbacks: { label: (c) => `${c.label}: ${c.parsed.x} leads` } } 
        },
        scales: { 
          x: { beginAtZero: true, title: { display: true, text: 'Quantidade' } }, 
          y: { grid: { display: false } } 
        }
      }
    });
}

function updateB2cCharts(b2cData, metrics) {
    const topHoteisValor = [...metrics.hoteis_mais_vendidos].sort((a, b) => b.valor_total - a.valor_total).slice(0, 5);
    createOrUpdateChart('topHoteisChart', {
        type: "doughnut",
        data: { labels: topHoteisValor.map(h => h.nome_hotel || "N/A"), datasets: [{ data: topHoteisValor.map(h => h.valor_total || 0), backgroundColor: ["#42a5f5", "#ab47bc", "#ffa726", "#66bb6a", "#ef5350"] }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "right" } } }
    });

    createOrUpdateChart('statusChart', {
        type: "pie",
        data: { labels: ["Confirmados", "Pendentes", "Cancelados"], datasets: [{ data: [metrics.total_confirmados, metrics.total_pendentes, metrics.total_cancelados], backgroundColor: ["#4caf50", "#ffc107", "#f44336"], borderColor: '#ffffff', borderWidth: 2 }] },
        options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "top" } } }
    });

    createOrUpdateChart('statusPagamentoChart', {
        type: "bar",
        data: { labels: metrics.status_pagamento.map(s => s.status_pagamento), datasets: [{ label: "Quantidade", data: metrics.status_pagamento.map(s => s.quantidade), backgroundColor: "#4facfe" }] },
        options: { responsive: true, maintainAspectRatio: false, indexAxis: "y", plugins: { legend: { display: false } } }
    });

    if (metrics.forma_pagamento) {
        createOrUpdateChart('formaPagamentoChart', {
            type: 'doughnut',
            data: {
                labels: metrics.forma_pagamento.map(item => item.forma_pagamento),
                datasets: [{
                    label: 'Formas de Pagamento',
                    data: metrics.forma_pagamento.map(item => item.quantidade),
                    backgroundColor: ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f', '#9b59b6', '#1abc9c'],
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
        });
    }

    if (metrics.cupom_stats) {
        createOrUpdateChart('cupomChart', {
            type: 'pie',
            data: {
                labels: ['Usou Cupom', 'Não Usou Cupom'],
                datasets: [{
                    label: 'Uso de Cupons',
                    data: [metrics.cupom_stats['Sim'], metrics.cupom_stats['Não']],
                    backgroundColor: ['#27ae60', '#c0392b'],
                    borderColor: '#ffffff',
                    borderWidth: 2
                }]
            },
            options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'top' } } }
        });
    }

    const topHoteisQtd = [...metrics.hoteis_mais_vendidos].sort((a, b) => b.quantidade - a.quantidade).slice(0, 5);
    createOrUpdateChart('topHoteisQtdChart', {
        type: "bar",
        data: { labels: topHoteisQtd.map(h => h.nome_hotel || "N/A"), datasets: [{ label: "Quantidade de Vendas", data: topHoteisQtd.map(h => h.quantidade || 0), backgroundColor: "#42a5f5" }] },
        options: {
            responsive: true, maintainAspectRatio: false,
            plugins: { legend: { display: false }, tooltip: { callbacks: { label: (ctx) => `${ctx.raw} vendas` } } },
            scales: { y: { beginAtZero: true, title: { display: true, text: "Vendas" } }, x: { title: { display: true, text: "Hotéis" } } }
        }
    });
}

// ================== Processamento de Dados para Gráficos ==================
function processTimelineData(data, dateField, valueField = null) {
  const grouped = {};
  (data || []).forEach(item => {
    if (!item[dateField]) return;
    const dateStr = String(item[dateField]).split('T')[0];
    if (!grouped[dateStr]) grouped[dateStr] = 0;
    grouped[dateStr] += valueField ? (Number(item[valueField]) || 0) : 1;
  });
  const sortedDates = Object.keys(grouped).sort((a, b) => new Date(a) - new Date(b));
  return { labels: sortedDates.map(date => formatDateBR(date)), data: sortedDates.map(date => grouped[date]) };
}

// ================== Modais (Adicionar/Editar) ==================
function openModal(type, data = null) {
  editingId = data ? data.id : null;
  const modalId = `${type}Modal`;
  const modal = document.getElementById(modalId);
  if (!modal) return;
  document.getElementById(`${type}ModalTitle`).textContent = data ? `Editar ${type.toUpperCase()}` : `Adicionar ${type.toUpperCase()}`;
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
  } else if (type === 'b2c') {
    if (data) {
      form.data.value = formatDate(data.data);
      form.nome_hotel.value = data.nome_hotel || '';
      form.valor.value = data.valor || '';
      form.forma_pagamento.value = data.forma_pagamento || 'Não Informado';
      form.usou_cupom.value = data.usou_cupom ? 'true' : 'false';
      form.status.value = data.status || '';
      form.status_pagamento.value = data.status_pagamento || '';
    } else {
      form.data.value = formatDate(new Date());
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
  const formData = new FormData(e.target);
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
  const formData = new FormData(e.target);
  const data = {
    data: formData.get('data'),
    nome_hotel: formData.get('nome_hotel'),
    valor: parseFloat(formData.get('valor').replace(',', '.')) || 0,
    forma_pagamento: formData.get('forma_pagamento'),
    usou_cupom: formData.get('usou_cupom') === 'true',
    status: formData.get('status'),
    status_pagamento: formData.get('status_pagamento'),
  };
  await saveData('b2c', data, editingId);
}

async function saveData(type, data, id) {
  const endpoint = type === 'lead' ? 'leads' : 'b2c';
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
      const errData = await resp.json().catch(() => ({}));
      throw new Error(errData.error || `Erro ${resp.status} ao salvar.`);
    }
    closeModal(type);
    loadData();
    showToast(`${type.toUpperCase()} ${id ? 'atualizado' : 'criado'} com sucesso!`, 'success');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    showLoading(false);
  }
}

async function editLead(id) {
    await loadSingleItemForEdit('leads', 'lead', id);
}

async function editB2c(id) {
    await loadSingleItemForEdit('b2c', 'b2c', id);
}

async function loadSingleItemForEdit(endpoint, type, id) {
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

async function deleteLead(id) {
    await deleteItem('leads', id);
}

async function deleteB2c(id) {
    await deleteItem('b2c', id);
}

async function deleteItem(type, id) {
  if (!confirm(`Tem certeza que deseja deletar este item?`)) return;
  showLoading(true);
  try {
    const resp = await fetch(`/api/${type}/${id}`, { method: 'DELETE' });
    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({}));
      throw new Error(errData.error || `Erro ao deletar item.`);
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
  showLoading(true);
  try {
    const params = new URLSearchParams({ data_inicio: currentFilters.dataInicio, data_fim: currentFilters.dataFim, tipo: currentTab });
    const resp = await fetch(`/api/export/pdf?${params}`);
    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({}));
      throw new Error(errData.error || 'Erro ao gerar o PDF.');
    }
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = url;
    a.download = `relatorio-${currentTab}-${new Date().toISOString().split('T')[0]}.pdf`;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(url);
    a.remove();
    showToast('Relatório PDF gerado com sucesso!', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  } finally {
    showLoading(false);
  }
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
  
  const icons = {
    success: 'fa-check-circle',
    error: 'fa-exclamation-circle',
    warning: 'fa-exclamation-triangle',
    info: 'fa-info-circle'
  };
  
  toast.innerHTML = `<i class="fas ${icons[type] || icons.info}"></i><span>${message}</span>`;
  container.appendChild(toast);
  
  setTimeout(() => {
    toast.classList.add('show');
  }, 100);

  setTimeout(() => {
    toast.classList.remove('show');
    toast.classList.add('hide');
    
    toast.addEventListener('transitionend', () => {
      toast.remove();
    }, { once: true });

  }, 5000);
}

// ================== Lógica do Filtro de Hotel e Popup ==================
function handleHotelSearch() {
    const searchInput = document.getElementById('hotelSearchInput');
    const searchTerm = searchInput.value.trim().toLowerCase();

    if (!searchTerm) {
        const originalMetrics = calculateB2cMetrics(allB2cData);
        updateB2cMetrics(originalMetrics);
        return;
    }

    const hotelData = allB2cData.filter(item => 
        item.nome_hotel && item.nome_hotel.toLowerCase().includes(searchTerm)
    );

    if (hotelData.length === 0) {
        showToast(`Nenhum hotel encontrado para "${searchInput.value}"`, 'warning');
        const originalMetrics = calculateB2cMetrics(allB2cData);
        updateB2cMetrics(originalMetrics);
        return;
    }
    
    const totalRegistrosHotel = hotelData.length;
    const valorTotalHotel = hotelData.reduce((sum, item) => sum + (Number(item.valor) || 0), 0);
    
    document.getElementById('totalB2cRegistros').textContent = totalRegistrosHotel;
    document.getElementById('totalB2cValor').textContent = formatCurrency(valorTotalHotel);

    const chartZoomModal = document.getElementById('chartZoomModal');
    const chartZoomContainer = document.getElementById('chartZoomContainer');
    const chartZoomTitle = document.getElementById('chartZoomTitle');
    
    const hotelName = hotelData[0].nome_hotel;
    chartZoomTitle.innerText = `Detalhe de Vendas: ${hotelName}`;

    if (charts.zoomChart) {
        charts.zoomChart.destroy();
    }

    let summaryHTML = `
        <div class="popup-summary">
            <div class="summary-item"><strong>Total de Vendas:</strong><span>${totalRegistrosHotel}</span></div>
            <div class="summary-item"><strong>Valor Total Vendido:</strong><span>${formatCurrency(valorTotalHotel)}</span></div>
        </div>
    `;

    let tableHTML = `
        <div class="table-wrapper"><table class="data-table">
            <thead><tr><th>Data da Venda</th><th>Valor</th><th>Forma de Pagamento</th><th>Usou Cupom?</th></tr></thead>
            <tbody>`;

    hotelData.forEach(item => {
        const cupomText = item.usou_cupom ? 'Sim' : 'Não';
        const cupomClass = item.usou_cupom ? 'status-confirmado' : 'status-cancelado';
        tableHTML += `<tr>
            <td>${formatDateBR(item.data)}</td>
            <td>${formatCurrency(item.valor)}</td>
            <td>${item.forma_pagamento || 'Não Informado'}</td>
            <td><span class="status-badge ${cupomClass}">${cupomText}</span></td>
        </tr>`;
    });

    tableHTML += `</tbody></table></div>`;
    chartZoomContainer.innerHTML = summaryHTML + tableHTML;
    chartZoomModal.classList.add('active');
}

function openChartZoom(originalChart) {
    const chartZoomModal = document.getElementById('chartZoomModal');
    const chartZoomContainer = document.getElementById('chartZoomContainer');
    const chartZoomTitle = document.getElementById('chartZoomTitle');

    if (!originalChart) return;

    chartZoomTitle.innerText = originalChart.options.plugins.title.text || 'Visualização do Gráfico';
    
    if (charts.zoomChart) {
        charts.zoomChart.destroy();
    }

    chartZoomContainer.innerHTML = '<canvas id="zoomCanvas"></canvas>';
    const zoomCanvas = document.getElementById('zoomCanvas');

    charts.zoomChart = new Chart(zoomCanvas.getContext('2d'), {
        type: originalChart.config.type,
        data: originalChart.config.data,
        options: { ...originalChart.config.options, maintainAspectRatio: false, responsive: true }
    });
    chartZoomModal.classList.add('active');
}
