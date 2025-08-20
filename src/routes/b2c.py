from flask import Blueprint, request, jsonify
from src.models.b2c import B2C
from src.extensions import db
from collections import Counter

b2c_bp = Blueprint("b2c", __name__)

@b2c_bp.route("/api/b2c", methods=["GET"])
def get_b2c():
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")

    query = B2C.query
    if data_inicio:
        query = query.filter(B2C.data >= data_inicio)
    if data_fim:
        query = query.filter(B2C.data <= data_fim)

    registros = query.all()
    return jsonify([item.to_dict() for item in registros])


@b2c_bp.route("/api/b2c/metrics", methods=["GET"])
def get_b2c_metrics():
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")

    query = B2C.query
    if data_inicio:
        query = query.filter(B2C.data >= data_inicio)
    if data_fim:
        query = query.filter(B2C.data <= data_fim)

    registros = query.all()

    total_registros = len(registros)
    total_valor = sum([r.valor or 0 for r in registros])

    # --- Mapeamento corrigido ---
    total_confirmados = 0
    total_cancelados = 0
    total_pendentes = 0

    for r in registros:
        status = (r.status or "").strip().lower()

        if status in ["confirmado", "confirmados", "ativo"]:
            total_confirmados += 1
        elif status in ["cancelado", "cancelados"]:
            total_cancelados += 1
        elif status in ["pendente", "pendentes"]:
            total_pendentes += 1
        else:
            # Caso apareça um novo status, entra como pendente
            total_pendentes += 1

    # --- Status detalhado (para debug e flexibilidade futura) ---
    status_counts = Counter([(r.status or "NÃO INFORMADO").strip().upper() for r in registros])
    status_detalhado = [{"status": k, "quantidade": v} for k, v in status_counts.items()]

    # --- Status de pagamento ---
    pagamento_counts = Counter([(r.status_pagamento or "NÃO INFORMADO").strip().upper() for r in registros])
    status_pagamento_list = [{"status_pagamento": k, "quantidade": v} for k, v in pagamento_counts.items()]

    # --- Hotéis mais vendidos ---
    hotel_stats = {}
    for r in registros:
        if r.nome_hotel and r.valor:
            if r.nome_hotel not in hotel_stats:
                hotel_stats[r.nome_hotel] = {"nome_hotel": r.nome_hotel, "valor_total": 0, "quantidade": 0}
            hotel_stats[r.nome_hotel]["valor_total"] += r.valor
            hotel_stats[r.nome_hotel]["quantidade"] += 1
    hoteis_mais_vendidos = sorted(hotel_stats.values(), key=lambda x: x["valor_total"], reverse=True)[:5]

    return jsonify({
        "total_registros": total_registros,
        "total_valor": total_valor,
        "status_resumido": {
            "confirmados": total_confirmados,
            "cancelados": total_cancelados,
            "pendentes": total_pendentes
        },
        "status_detalhado": status_detalhado,
        "status_pagamento": status_pagamento_list,
        "hoteis_mais_vendidos": hoteis_mais_vendidos
    })
