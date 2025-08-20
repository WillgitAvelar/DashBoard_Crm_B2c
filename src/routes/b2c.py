from flask import Blueprint, request, jsonify
from src.models.b2c import B2C
from src.extensions import db

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
    total_confirmados = sum(1 for r in registros if r.status == "CONFIRMADO")
    total_cancelados = sum(1 for r in registros if r.status == "CANCELADO")
    total_pendentes = total_registros - total_confirmados - total_cancelados
    total_pagos = sum(1 for r in registros if r.status_pagamento == "PAGO")

    # hotéis mais vendidos
    hotel_stats = {}
    for r in registros:
        if r.nome_hotel and r.valor:
            if r.nome_hotel not in hotel_stats:
                hotel_stats[r.nome_hotel] = {"nome_hotel": r.nome_hotel, "valor_total": 0, "quantidade": 0}
            hotel_stats[r.nome_hotel]["valor_total"] += r.valor
            hotel_stats[r.nome_hotel]["quantidade"] += 1
    hoteis_mais_vendidos = sorted(hotel_stats.values(), key=lambda x: x["valor_total"], reverse=True)[:5]

    # status de pagamento
    status_pagamento = {}
    for r in registros:
        status = r.status_pagamento or "NÃO INFORMADO"
        status_pagamento[status] = status_pagamento.get(status, 0) + 1
    status_pagamento_list = [{"status_pagamento": k, "quantidade": v} for k, v in status_pagamento.items()]

    return jsonify({
        "total_registros": total_registros,
        "total_valor": total_valor,
        "total_confirmados": total_confirmados,
        "total_cancelados": total_cancelados,
        "total_pendentes": total_pendentes,
        "total_pagos": total_pagos,
        "hoteis_mais_vendidos": hoteis_mais_vendidos,
        "status_pagamento": status_pagamento_list
    })
