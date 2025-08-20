// script.js — versão completa (corrigida para Totais por Período)
// - Corrige sintaxe do Chart.js (fechamentos e vírgulas)
// - Remove duplicação de funções
// - Funil agora mostra TOTAl por período (não média)

let currentTab = 'leads';
let currentFilters = { dataInicio: '', dataFim: '' };
let charts = {};
let editingId = null;

// Inicialização
document.addEventListener('DOMContentLoaded', () => {
  setupEventListeners();
  setDefaultDates();
  switchTab('leads');
});

/* ============== Helpers ============== */
function formatDate(d) {
  if (!d) return '';
  const dt = d instanceof Date ? d : new Date(d + 'T00:00:00');
  return dt.toISOString().split('T')[0];
}

function formatDateBR(dateString) {
  if (!dateString) return '-';
  if (typeof dateString === 'number') {
    const date = new Date(dateString);
    return date.toLocaleDateString('pt-BR', { timeZone: 'UTC' });
  }
  const date = new Date(dateString + 'T00:00:00');
  return date.toLocaleDateString('pt-BR', { timeZone: 'UTC' });
}

function formatCurrency(value) {
  const v = Number(value) || 0;
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(v);
}



/* ============ Tabs & Filtros ============ */
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
}

function switchTab(tabName) {
  if (!tabName) return;
  currentTab = tabName;

  document.querySelectorAll('.nav-tab').forEach(tab => {
    tab.classList.toggle('active', tab.dataset.tab === tabName);
  });

  const leadsContent = document.getElementById('leads-content');
  const b2cContent = document.getElementById('b2c-content');
  if (leadsContent) leadsContent.style.display = (tabName === 'leads') ? 'grid' : 'none';
  if (b2cContent) b2cContent.style.display = (tabName === 'b2c') ? 'grid' : 'none';

  loadData();
}

function setDefaultDates() {
  const today = new Date();
  const first = new Date(today.getFullYear(), today.getMonth(), 1);
  const inicio = document.getElementById('dataInicio');
  const fim = document.getElementById('dataFim');
  if (inicio && !inicio.value) inicio.value = formatDate(first);
  if (fim && !fim.value) fim.value = formatDate(today);
  currentFilters.dataInicio = inicio?.value || '';
  currentFilters.dataFim = fim?.value || '';
}

function applyFilters() {
  const inicioEl = document.getElementById('dataInicio');
  const fimEl = document.getElementById('dataFim');
  const dataInicio = inicioEl?.value ? formatDate(inicioEl.value) : '';
  const dataFim = fimEl?.value ? formatDate(fimEl.value) : '';
  if (dataInicio && dataFim && dataInicio > dataFim) {
    showToast('Data de início não pode ser maior que data de fim', 'error');
    return;
  }
  currentFilters.dataInicio = dataInicio;
  currentFilters.dataFim = dataFim;
  loadData();
  showToast('Filtros aplicados', 'success');
}

function clearFilters() {
  const inicioEl = document.getElementById('dataInicio');
  const fimEl = document.getElementById('dataFim');
  if (inicioEl) inicioEl.value = '';
  if (fimEl) fimEl.value = '';
  currentFilters.dataInicio = '';
  currentFilters.dataFim = '';
  setDefaultDates();
  loadData();
  showToast('Filtros limpos', 'info');
}

/* ============== Load Data ============== */
async function loadData() {
  showLoading(true);
  try {
    if (currentTab === 'leads') {
      await loadLeadsData();
    } else {
      await loadB2cData();
    }
  } catch (err) {
    console.error('Erro ao carregar dados:', err);
    showToast('Erro ao carregar dados', 'error');
  } finally {
    showLoading(false);
  }
}

async function loadLeadsData() {
  const params = new URLSearchParams();
  if (currentFilters.dataInicio) params.append('data_inicio', currentFilters.dataInicio);
  if (currentFilters.dataFim) params.append('data_fim', currentFilters.dataFim);

  const resp = await fetch(`/api/leads?${params}`);
  if (!resp.ok) throw new Error('Erro ao buscar leads');
  const leads = await resp.json();

  const metrics = calculateLeadsMetrics(leads);
  const dailyMetrics = calculateDailyLeadsMetrics(leads);

  updateLeadsMetrics(metrics);
  updateLeadsTable(leads || []);
  updateLeadsCharts(dailyMetrics);
}

async function loadB2cData() {
  const params = new URLSearchParams();
  if (currentFilters.dataInicio) params.append('data_inicio', currentFilters.dataInicio);
  if (currentFilters.dataFim) params.append('data_fim', currentFilters.dataFim);

  // Busca registros
const resp = await fetch(`/api/b2c?${params}`);

  if (!resp.ok) throw new Error('Erro ao buscar B2C');
  const data = await resp.json();

  // Busca métricas
  const metrics = calculateB2cMetrics(data);

  updateB2cMetrics(metrics);
  updateB2cTable(data || []);
  updateB2cCharts(data || [], metrics);
}

/* ============= Métricas ============= */
function calculateLeadsMetrics(leads) {
  const metrics = {
    totalLeads: 0,
    leadsAskSuite: 0,
    leadsFilaAtendimento: 0,
    leadsAtendimento: 0,
    leadsQualificacao: 0,
    leadsOportunidade: 0,
    leadsAguardandoPagamento: 0,
  };
  if (!leads || !Array.isArray(leads)) return metrics;
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
    if (!dailyData[date]) {
      dailyData[date] = { askSuite: 0, filaAtendimento: 0, atendimento: 0, qualificacao: 0, oportunidade: 0, aguardandoPagamento: 0 };
    }
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
  return {
    ...totals,
    dailyData,
    totalDays: Object.keys(dailyData).length || 1,
  };
}

function calculateB2cMetrics(data) {
  const metrics = {
    total_registros: 0,
    total_valor: 0,
    total_confirmados: 0,
    total_pendentes: 0,
    total_cancelados: 0,
    total_pagos: 0,
    hoteis_mais_vendidos: [],
    status_pagamento: [],
  };
  if (!data || !Array.isArray(data)) return metrics;
  const hotelStats = {};
  const statusPagamentoStats = {};
  data.forEach(item => {
    if (!item.nome_hotel && !item.valor && !item.status_pagamento) return;
    metrics.total_registros++;
    if (item.valor && typeof item.valor === 'number') metrics.total_valor += item.valor;
    const status = item.status || 'ATIVO';
    if (status === 'CONFIRMADO') metrics.total_confirmados++;
    else if (status === 'CANCELADO') metrics.total_cancelados++;
    else metrics.total_pendentes++;
    const statusPag = item.status_pagamento || 'NÃO INFORMADO';
    if (statusPag === 'PAGO') metrics.total_pagos++;
    statusPagamentoStats[statusPag] = (statusPagamentoStats[statusPag] || 0) + 1;
    if (item.nome_hotel && item.valor > 0) {
      const hotelName = item.nome_hotel;
      if (!hotelStats[hotelName]) hotelStats[hotelName] = { nome_hotel: hotelName, valor_total: 0, quantidade: 0 };
      hotelStats[hotelName].valor_total += item.valor;
      hotelStats[hotelName].quantidade++;
    }
  });
  metrics.hoteis_mais_vendidos = Object.values(hotelStats).sort((a, b) => b.valor_total - a.valor_total).slice(0, 5);
  metrics.status_pagamento = Object.entries(statusPagamentoStats).map(([status, quantidade]) => ({ status_pagamento: status, quantidade }));
  return metrics;
}

/* ============= Atualização UI ============= */
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
    row.innerHTML = `
      <td>${formatDateBR(lead.data_entrada)}</td>
      <td>${lead.entrada_leads_ask_suite || '-'}</td>
      <td>${lead.fila_atendimento || '-'}</td>
      <td>${lead.atendimento || '-'}</td>
      <td>${lead.qualificacao || '-'}</td>
      <td>${lead.oportunidade || '-'}</td>
      <td>${lead.aguardando_pagamento || '-'}</td>
      <td>
        <div class="action-buttons">
          <button class="btn btn-primary" data-id="${lead.id}" data-action="edit-lead"><i class="fas fa-edit"></i></button>
          <button class="btn btn-danger" data-id="${lead.id}" data-action="delete-lead"><i class="fas fa-trash"></i></button>
        </div>
      </td>`;
    tbody.appendChild(row);
  });
  tbody.querySelectorAll('button[data-action]').forEach(btn => {
    btn.removeEventListener('click', delegatedClickHandler);
    btn.addEventListener('click', delegatedClickHandler);
  });
}

function updateB2cTable(b2cData) {
  const tbody = document.getElementById('b2cTableBody');
  if (!tbody) return;
  tbody.innerHTML = '';
  (b2cData || []).forEach(item => {
    if (!item.nome_hotel && !item.valor && !item.status_pagamento) return;
    const row = document.createElement('tr');
    const statusPagamento = item.status_pagamento || 'NÃO INFORMADO';
    row.innerHTML = `
      <td>${formatDateBR(item.data)}</td>
      <td>${item.nome_hotel || '-'}</td>
      <td>${formatCurrency(item.valor || 0)}</td>
      <td><span class="status-badge status-${(item.status || 'ATIVO').toLowerCase().replace(/\s+/g, '-')}">${item.status || 'ATIVO'}</span></td>
      <td><span class="status-badge status-${statusPagamento.toLowerCase().replace(/\s+/g, '-')}">${statusPagamento}</span></td>
      <td>
        <div class="action-buttons">
          <button class="btn btn-primary" data-id="${item.id}" data-action="edit-b2c"><i class="fas fa-edit"></i></button>
          <button class="btn btn-danger" data-id="${item.id}" data-action="delete-b2c"><i class="fas fa-trash"></i></button>
        </div>
      </td>`;
    tbody.appendChild(row);
  });
  tbody.querySelectorAll('button[data-action]').forEach(btn => {
    btn.removeEventListener('click', delegatedClickHandler);
    btn.addEventListener('click', delegatedClickHandler);
  });
}

function delegatedClickHandler(e) {
  const btn = e.currentTarget;
  const id = btn.getAttribute('data-id');
  const action = btn.getAttribute('data-action');
  if (!action) return;
  if (action === 'edit-lead') editLead(Number(id));
  if (action === 'delete-lead') deleteLead(Number(id));
  if (action === 'edit-b2c') editB2c(Number(id));
  if (action === 'delete-b2c') deleteB2c(Number(id));
}

/* =============== Gráficos (Chart.js) =============== */
const ctx = document.getElementById('leadsFunnelChart').getContext('2d');

// Exemplo de dados de UM DIA (pega do backend/tabela)
const funnelLabels = ['Ask Suite', 'Fila Atendimento', 'Atendimento', 'Qualificação', 'Oportunidade', 'Aguardando Pagamento'];
const funnelValues = [193, 39, 9, 4, 0, 2]; // valores do dia atual

function updateLeadsCharts(dailyMetrics) {
  const ctx = document.getElementById('leadsFunnelChart');
  if (!ctx) return;

  if (charts.leadsFunnel) charts.leadsFunnel.destroy();

  // Pega o último dia disponível (ou hoje, se não houver)
  const days = Object.keys(dailyMetrics.dailyData || {});
  const lastDay = days.length > 0 ? days[days.length - 1] : null;
  const dataDay = lastDay ? dailyMetrics.dailyData[lastDay] : {
    askSuite: 0, filaAtendimento: 0, atendimento: 0,
    qualificacao: 0, oportunidade: 0, aguardandoPagamento: 0
  };

  const funnelLabels = ['Ask Suite', 'Fila Atendimento', 'Atendimento', 'Qualificação', 'Oportunidade', 'Aguardando Pagamento'];
  const funnelValues = [
    dataDay.askSuite, dataDay.filaAtendimento, dataDay.atendimento,
    dataDay.qualificacao, dataDay.oportunidade, dataDay.aguardandoPagamento
  ];

  charts.leadsFunnel = new Chart(ctx.getContext('2d'), {
    type: 'bar',
    data: {
      labels: funnelLabels,
      datasets: [{
        label: lastDay ? `Leads do dia ${formatDateBR(lastDay)}` : 'Dia Atual',
        data: funnelValues,
        backgroundColor: ['#667eea', '#764ba2', '#f093fb', '#f5576c', '#4facfe', '#00f2fe'],
        borderRadius: 8,
        borderWidth: 2,
        borderColor: '#ffffff',
      }],
    },
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false },
        title: { 
          display: true, 
          text: 'Leads por Etapa - Dia Atual', 
          font: { size: 18, weight: 'bold' }, 
          padding: 20 
        },
        tooltip: { callbacks: { label: (ctx) => `${ctx.label}: ${ctx.parsed.x} leads` } },
      },
      scales: {
        x: { beginAtZero: true, title: { display: true, text: 'Quantidade de Leads', font: { size: 14, weight: 'bold' } } },
        y: { title: { display: true, text: 'Etapas do Funil', font: { size: 14, weight: 'bold' } }, grid: { display: false } }
      }
    }
  });
}


function updateB2cCharts(b2cData, metrics) {
  // Top Hotéis
  const topHoteisCanvas = document.getElementById("topHoteisChart");
  if (topHoteisCanvas) {
    if (charts.topHoteis) charts.topHoteis.destroy();
    const hotelStats = {};
    b2cData.forEach(item => {
      if (item.nome_hotel && item.valor > 0) {
        const hotelName = item.nome_hotel;
        if (!hotelStats[hotelName]) hotelStats[hotelName] = { nome_hotel: hotelName, valor_total: 0, quantidade: 0 };
        hotelStats[hotelName].valor_total += item.valor;
        hotelStats[hotelName].quantidade++;
      }
    });
    const hoteis_mais_vendidos = Object.values(hotelStats).sort((a, b) => b.valor_total - a.valor_total).slice(0, 5);
    const labels = hoteis_mais_vendidos.map(h => h.nome_hotel);
    const dataVals = hoteis_mais_vendidos.map(h => h.valor_total);
    charts.topHoteis = new Chart(topHoteisCanvas.getContext("2d"), {
      type: "doughnut",
      data: { labels, datasets: [{ data: dataVals, backgroundColor: ["#667eea", "#764ba2", "#f093fb", "#f5576c", "#4facfe"] }] },
      options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: "top" } } },
    });
  }

  // Status dos registros (Confirmado/Cancelado/Pendente)
  const statusCanvas = document.getElementById("statusChart");
  if (statusCanvas) {
    if (charts.status) charts.status.destroy();
    let total_confirmados = 0;
    let total_cancelados = 0;
    let total_pendentes = 0;
    b2cData.forEach(item => {
      const status = item.status || "ATIVO";
      if (status === "CONFIRMADO") total_confirmados++;
      else if (status === "CANCELADO") total_cancelados++;
      else total_pendentes++;
    });
    const labels = ["Confirmados", "Pendentes", "Cancelados"];
    const dataVals = [total_confirmados, total_pendentes, total_cancelados];
    charts.status = new Chart(statusCanvas.getContext("2d"), {
      type: "pie",
      data: {
        labels,
        datasets: [{
          data: dataVals,
          backgroundColor: ["#4caf50", "#ffc107", "#f44336"]
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "top" } }
      }
    });
  }

  // Status de pagamento
  const statusPagamentoCanvas = document.getElementById("statusPagamentoChart");
  if (statusPagamentoCanvas) {
    if (charts.statusPagamento) charts.statusPagamento.destroy();
    const statusPagamentoStats = {};
    b2cData.forEach(item => {
      const statusPag = item.status_pagamento || "NÃO INFORMADO";
      statusPagamentoStats[statusPag] = (statusPagamentoStats[statusPag] || 0) + 1;
    });
    const status_pagamento = Object.entries(statusPagamentoStats).map(([status, quantidade]) => ({ status_pagamento: status, quantidade }));
    const labels = status_pagamento.map(s => s.status_pagamento);
    const dataVals = status_pagamento.map(s => s.quantidade);
    charts.statusPagamento = new Chart(statusPagamentoCanvas.getContext("2d"), {
      type: "bar",
      data: { labels, datasets: [{ label: "Quantidade", data: dataVals, backgroundColor: "#4facfe" }] },
      options: { responsive: true, maintainAspectRatio: false, indexAxis: "y", plugins: { legend: { display: false } } },
    });
  }

  // Timeline de vendas (R$)
  const vendasCanvas = document.getElementById("vendasTimelineChart");
  if (vendasCanvas) {
    if (charts.vendasTimeline) charts.vendasTimeline.destroy();
    const vendasData = processTimelineData(b2cData, "data", "valor");
    charts.vendasTimeline = new Chart(vendasCanvas.getContext("2d"), {
      type: "line",
      data: {
        labels: vendasData.labels,
        datasets: [{
          label: "Vendas (R$)",
          data: vendasData.data,
          borderColor: "#4facfe",
          backgroundColor: "rgba(79, 172, 254, 0.1)",
          fill: true,
          tension: 0.4,
        }],
      },
      options: { responsive: true, maintainAspectRatio: false, scales: { y: { beginAtZero: true, ticks: { callback: (v) => formatCurrency(v) } } } },
    });
  }
}

/* ========== Processamento timeline ========== */
function processTimelineData(data, dateField, valueField = null) {
  const grouped = {};
  (data || []).forEach(item => {
    if (!item[dateField]) return;
    let dateStr;
    if (typeof item[dateField] === 'number') {
      const date = new Date(item[dateField]);
      dateStr = date.toISOString().split('T')[0];
    } else {
      dateStr = String(item[dateField]).split('T')[0];
    }
    if (!grouped[dateStr]) grouped[dateStr] = 0;
    grouped[dateStr] += valueField ? (Number(item[valueField]) || 0) : 1;
  });
  const sorted = Object.keys(grouped).sort((a, b) => new Date(a) - new Date(b));
  return { labels: sorted.map(s => formatDateBR(s)), data: sorted.map(s => grouped[s]) };
}

/* ================= Modais ================= */
function openModal(type, data = null) {
  editingId = data ? data.id : null;
  if (type === 'lead') {
    const modal = document.getElementById('leadModal');
    document.getElementById('leadModalTitle').textContent = data ? 'Editar Lead' : 'Adicionar Lead';
    const form = document.getElementById('leadForm');
    form.reset();
    if (data) {
      document.getElementById('leadDataEntrada').value = data.data_entrada ? formatDate(data.data_entrada) : '';
      document.getElementById('leadAskSuite').value = data.entrada_leads_ask_suite || '';
      document.getElementById('leadFilaAtendimento').value = data.fila_atendimento || '';
      document.getElementById('leadAtendimento').value = data.atendimento || '';
      document.getElementById('leadQualificacao').value = data.qualificacao || '';
      document.getElementById('leadOportunidade').value = data.oportunidade || '';
      document.getElementById('leadAguardandoPagamento').value = data.aguardando_pagamento || '';
    } else {
      document.getElementById('leadDataEntrada').value = formatDate(new Date());
    }
    modal?.classList.add('active');
  }
  if (type === 'b2c') {
    const modal = document.getElementById('b2cModal');
    document.getElementById('b2cModalTitle').textContent = data ? 'Editar B2C' : 'Adicionar B2C';
    const form = document.getElementById('b2cForm');
    form.reset();
    if (data) {
      document.getElementById('b2cData').value = data.data ? formatDate(data.data) : '';
      document.getElementById('b2cNomeHotel').value = data.nome_hotel || '';
      document.getElementById('b2cValor').value = data.valor || '';
      document.getElementById('b2cStatus').value = data.status || '';
      document.getElementById('b2cStatusPagamento').value = data.status_pagamento || '';
    } else {
      document.getElementById('b2cData').value = formatDate(new Date());
    }
    modal?.classList.add('active');
  }
}

function closeModal(type) {
  editingId = null;
  if (type === 'lead') document.getElementById('leadModal')?.classList.remove('active');
  if (type === 'b2c') document.getElementById('b2cModal')?.classList.remove('active');
}

/* ================= CRUD ================= */
async function handleLeadSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form).entries());
  try {
    showLoading(true);
    const url = editingId !== null ? `/api/leads/${editingId}` : '/api/leads';
    const method = editingId !== null ? 'PUT' : 'POST';
    const resp = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(data) });
    if (!resp.ok) {
      const errData = await resp.json().catch(() => ({ error: 'Erro desconhecido ao salvar lead' }));
      throw new Error(errData.error);
    }
    closeModal('lead');
    loadData();
    showToast(editingId !== null ? 'Lead atualizado com sucesso' : 'Lead criado com sucesso', 'success');
  } catch (err) {
    showToast(err.message, 'error');
  } finally { showLoading(false); }
}

async function handleB2cSubmit(e) {
  e.preventDefault();
  const form = e.target;
  const data = Object.fromEntries(new FormData(form).entries());
  if (data.valor) data.valor = data.valor.replace(',', '.');
  const b2cData = { 
    data: data.data, 
    nome_hotel: data.nome_hotel, 
    valor: parseFloat(data.valor), 
    status: data.status, 
    status_pagamento: data.status_pagamento 
  };
  try {
    showLoading(true);
    const url = editingId !== null ? `/api/b2c/${editingId}` : '/api/b2c';
    const method = editingId !== null ? 'PUT' : 'POST';
    const resp = await fetch(url, { method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(b2cData) });
    if (!resp.ok) {
      const errData = await resp.json().catch(() => null);
      const msg = errData?.error || resp.statusText || 'Erro ao salvar B2C';
      throw new Error(msg);
    }
    closeModal('b2c');
    loadData();
    showToast(editingId !== null ? 'B2C atualizado com sucesso' : 'B2C criado com sucesso', 'success');
  } catch (err) {
    console.error('handleB2cSubmit error:', err);
    showToast(err.message, 'error');
  } finally { showLoading(false); }
}

async function editLead(id) {
  try {
    showLoading(true);
    let resp = await fetch(`/api/leads/${id}`);
    if (resp.ok) { const lead = await resp.json(); openModal('lead', lead); return; }
    throw new Error('Endpoint de lead individual não encontrado, usando fallback.');
  } catch (e) {
    try {
      const listResp = await fetch(`/api/leads`);
      if (!listResp.ok) throw new Error('Não foi possível buscar a lista de leads');
      const leads = await listResp.json();
      const lead = (leads || []).find(l => Number(l.id) === Number(id));
      if (lead) openModal('lead', lead); else showToast('Lead não encontrado', 'error');
    } catch (err) {
      console.error('editLead fallback error:', err);
      showToast('Erro ao carregar dados do lead', 'error');
    }
  } finally { showLoading(false); }
}

async function editB2c(id) {
  try {
    showLoading(true);
    const resp = await fetch(`/api/b2c/${id}`);
    if (resp.ok) { const item = await resp.json(); openModal('b2c', item); }
    else {
      const listResp = await fetch(`/api/b2c`);
      if (!listResp.ok) throw new Error('Não foi possível buscar a lista B2C');
      const list = await listResp.json();
      const item = (list || []).find(b => Number(b.id) === Number(id));
      if (item) openModal('b2c', item); else showToast('Registro B2C não encontrado', 'error');
    }
  } catch (err) {
    console.error('editB2c error:', err);
    showToast('Erro ao carregar dados do B2C', 'error');
  } finally { showLoading(false); }
}

async function deleteLead(id) {
  if (!confirm('Tem certeza que deseja deletar este lead?')) return;
  try {
    showLoading(true);
    const resp = await fetch(`/api/leads/${id}`, { method: 'DELETE' });
    if (!resp.ok) {
      const errData = await resp.json().catch(() => null);
      const msg = errData?.error || 'Erro ao deletar lead';
      throw new Error(msg);
    }
    loadData();
    showToast('Lead deletado com sucesso', 'success');
  } catch (err) {
    console.error('deleteLead error:', err);
    showToast(err.message, 'error');
  } finally { showLoading(false); }
}

async function deleteB2c(id) {
  if (!confirm('Tem certeza que deseja deletar este registro B2C?')) return;
  try {
    showLoading(true);
    const resp = await fetch(`/api/b2c/${id}`, { method: 'DELETE' });
    if (!resp.ok) {
      const errData = await resp.json().catch(() => null);
      const msg = errData?.error || 'Erro ao deletar B2C';
      throw new Error(msg);
    }
    loadData();
    showToast('Registro B2C deletado com sucesso', 'success');
  } catch (err) {
    console.error('deleteB2c error:', err);
    showToast(err.message, 'error');
  } finally { showLoading(false); }
}

/* =============== Export PDF =============== */
async function exportToPDF() {
  try {
    showLoading(true);
    const params = new URLSearchParams();
    if (currentFilters.dataInicio) params.append('data_inicio', currentFilters.dataInicio);
    if (currentFilters.dataFim) params.append('data_fim', currentFilters.dataFim);
    params.append('tipo', currentTab);
    const resp = await fetch(`/api/export/pdf?${params}`);
    if (!resp.ok) {
      const errData = await resp.json().catch(() => null);
      const msg = errData?.error || 'Erro ao exportar PDF';
      throw new Error(msg);
    }
    const blob = await resp.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url; a.download = `relatorio-${currentTab}-${formatDate(new Date())}.pdf`;
    document.body.appendChild(a); a.click(); window.URL.revokeObjectURL(url); a.remove();
    showToast('Relatório exportado com sucesso', 'success');
  } catch (err) {
    console.error('exportToPDF error:', err);
    showToast(err.message, 'error');
  } finally { showLoading(false); }
}

/* =============== UI Utils =============== */
function showLoading(show) {
  const overlay = document.getElementById('loadingOverlay');
  if (!overlay) return;
  overlay.classList.toggle('active', !!show);
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  if (!container) return;
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.innerHTML = `<i class="${getToastIcon(type)}"></i><span>${message}</span>`;
  container.appendChild(toast);
  setTimeout(() => { toast.classList.add('hide'); setTimeout(() => toast.remove(), 500); }, 5000);
}

function getToastIcon(type) {
  switch (type) {
    case 'success': return 'fas fa-check-circle';
    case 'error': return 'fas fa-exclamation-circle';
    case 'warning': return 'fas fa-exclamation-triangle';
    default: return 'fas fa-info-circle';
  }
}

// Fim do arquivo
