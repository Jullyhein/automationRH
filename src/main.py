from datetime import time
import os
import logging
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_caching import Cache
from executa_envio_data import executar_envio_por_data
from graphutils import get_access_token

app = Flask(__name__)
load_dotenv()

print(os.getenv("EMAIL_DESTINO"))

# Configuração do logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


# Configuração do cache
app.config['CACHE_TYPE'] = 'SimpleCache'
app.config['CACHE_DEFAULT_TIMEOUT'] = 50
cache = Cache(app)


@app.route("/token", methods=["GET"])
def gerar_token():
    try:
        token = get_access_token()
        return jsonify({"token": token})
    except Exception as e:
        return jsonify({"error": f"Erro ao gerar token: {str(e)}"}), 500

@app.route("/enviar-felicitacoes", methods=["POST"])
def enviar_email_por_data():
    req = request.json
    data_desejada = req.get("data")

    try:
        resultado = executar_envio_por_data(data_desejada)
        return jsonify({"message": resultado}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@cache.memoize(timeout=60)
def get_token_cached():
    return get_access_token()

@app.route("/")
@cache.cached(timeout=50)
def index():
    start = time.time()
    time.sleep(2)
    fim = time.time()
    logging.info(f"Tempo de resposta: {fim - start:.2f}s")
    return render_template('aniversariantes.html')
    

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
