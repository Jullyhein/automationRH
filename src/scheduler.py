import logging
import schedule
import time
from main import app, executar_envio_por_data

# Configura o logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def tarefa_enviar_felicitacoes():
    try:
        with app.app_context():
            resultado = executar_envio_por_data()
            logging.info(f"✅ Tarefa executada: {resultado}")
    except Exception as e:
        logging.error(f"❌ Erro ao executar envio automático: {str(e)}")

# 🕒 Agendar a execução diária às 11:52 (ou outro horário desejado)
schedule.every().day.at("07:10").do(tarefa_enviar_felicitacoes)

logging.info("📆 Scheduler iniciado. Aguardando horário programado...")

# 🔁 Loop para manter o scheduler ativo
while True:
    schedule.run_pending()
    time.sleep(60)
