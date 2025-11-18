from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime
import os

app = Flask(__name__)

# Conexão com MongoDB local (ou ajuste para Atlas se for usar online)
client = MongoClient('mongodb://localhost:27017/')
db = client['shina_db']            # nome do banco de dados
sensores = db['sensores']          # coleção para dados dos sensores
configuracao = db['configuracao']  # coleção para parâmetros/configuração

# Rota para receber e salvar dados dos sensores via POST
@app.route('/api/sensores', methods=['POST'])
def salvar_dados_sensor():
    dados = request.get_json()
    dados['dataRegistro'] = datetime.now()
    sensores.insert_one(dados)
    return jsonify({'mensagem': 'Dados salvos!'}), 201

# Rota para listar os últimos 50 registros dos sensores via GET
@app.route('/api/sensores', methods=['GET'])
def listar_dados_sensores():
    data = list(sensores.find({}, {"_id": 0}).sort("dataRegistro", -1).limit(50))
    return jsonify(data), 200

# Rota para salvar a configuração via POST
@app.route('/api/configuracao', methods=['POST'])
def salvar_configuracao():
    conf = request.get_json()
    conf['dataRegistro'] = datetime.now()
    configuracao.insert_one(conf)
    return jsonify({'mensagem': 'Configuração salva!'}), 201

# Rota para obter a última configuração via GET
@app.route('/api/configuracao', methods=['GET'])
def obter_configuracao():
    conf = configuracao.find_one(sort=[('dataRegistro', -1)], projection={"_id": 0})
    return jsonify(conf if conf else {}), 200

@app.route("/api/recomendacao", methods=["POST"])
def recomendar_acoes():
    dados = request.get_json()
    temperatura = dados.get("temperatura", None)
    ph = dados.get("ph", None)
    mensagem = ""
    if temperatura and temperatura > 24:
        mensagem += "Atenção: temperatura acima do ideal. "
    if ph and ph < 6.5:
        mensagem += "Atenção: pH abaixo do recomendado. "
    if not mensagem:
        mensagem = "Tudo dentro dos parâmetros ideais!"
    return jsonify({"recomendacao": mensagem}), 200

# ---- ESTE BLOCO VAI EXATAMENTE NO FINAL ----
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
