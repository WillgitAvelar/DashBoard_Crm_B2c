from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__, static_folder='src/static')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/api/leads')
def get_leads():
    return jsonify([])

@app.route('/api/leads/metrics')
def get_leads_metrics():
    return jsonify({
        'total_leads': 0,
        'entrada_leads_ask_suite': 0,
        'fila_atendimento': 0,
        'atendimento': 0,
        'qualificacao': 0,
        'oportunidade': 0,
        'aguardando_pagamento': 0
    })

@app.route('/api/b2c')
def get_b2c():
    return jsonify([])

@app.route('/api/b2c/metrics')
def get_b2c_metrics():
    return jsonify({
        'total_registros': 0,
        'total_valor': 0,
        'valor_medio': 0,
        'hoteis_mais_vendidos': [],
        'hoteis_menos_vendidos': [],
        'status_registros': [],
        'status_pagamento': []
    })

if __name__ == '__main__':
    print("Iniciando servidor Flask simples...")
    app.run(host='0.0.0.0', port=5000, debug=False)

