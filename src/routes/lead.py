from flask import Blueprint, request, jsonify
from src.models.lead import Lead
from src.extensions import db

leads_bp = Blueprint("leads", __name__)

@leads_bp.route("/api/leads", methods=["GET"])
def get_leads():
    data_inicio = request.args.get("data_inicio")
    data_fim = request.args.get("data_fim")

    query = Lead.query
    if data_inicio:
        query = query.filter(Lead.data_entrada >= data_inicio)
    if data_fim:
        query = query.filter(Lead.data_entrada <= data_fim)

    leads = query.all()
    return jsonify([lead.to_dict() for lead in leads])
