from flask import Blueprint, jsonify, request
from src.models.b2c import B2C
from src import db
from sqlalchemy import func

b2c_bp = Blueprint("b2c", __name__)

@b2c_bp.route("/api/b2c/metrics")
def b2c_metrics():
    data_inicio = request.args.get("dataInicio")
    data_fim = request.args.get("dataFim")

    query = B2C.query

    # filtro por datas
    if data_inicio and data_fim:
        query = query.filter(B2C.data.between(data_inicio, data_fim))

    total_registros = query.count()
    valor_total = db.session.query(func.sum(B2C.valor)).scalar()

    # status registros
    status_registros = (
        db.session.query(B2C.status, func.count(B2C.id))
        .group_by(B2C.status)
        .all()
    )
    status_resumido = {s: c for s, c in status_registros}

    # status pagamento
    status_pagamento = (
        db.session.query(B2C.status_pagamento, func.count(B2C.id))
        .group_by(B2C.status_pagamento)
        .all()
    )
    status_pagamento_dict = {s: c for s, c in status_pagamento}

    # vendas por data
    vendas_por_data = (
        db.session.query(B2C.data, func.sum(B2C.valor))
        .group_by(B2C.data)
        .order_by(B2C.data)
        .all()
    )
    vendas_list = [
        {"data": str(d), "valor_total": float(v or 0)}
        for d, v in vendas_por_data
    ]

    # top hotéis mais vendidos (quantidade e valor)
    hoteis_mais_vendidos = (
        db.session.query(
            B2C.nome_hotel,
            func.count(B2C.id).label("quantidade"),
            func.sum(B2C.valor).label("valor_total")
        )
        .group_by(B2C.nome_hotel)
        .order_by(func.count(B2C.id).desc())
        .limit(5)
        .all()
    )

    hoteis_list = [
        {
            "nome_hotel": h[0],
            "quantidade": int(h[1] or 0),
            "valor_total": float(h[2] or 0)
        }
        for h in hoteis_mais_vendidos
    ]

    return jsonify({
        "total_registros": total_registros,
        "valor_total": float(valor_total or 0),
        "status_registros": status_resumido,
        "status_pagamento": status_pagamento_dict,
        "vendas_por_data": vendas_list,
        "hoteis_mais_vendidos": hoteis_list
    })
