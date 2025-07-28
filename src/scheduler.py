#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import logging
from dotenv import load_dotenv
from executa_envio_data import executar_envio_por_data

# Redireciona erros para arquivo de log
sys.stderr = open("stderr.log", "w", encoding="utf-8", errors="replace")

# Carrega variáveis de ambiente do .env
load_dotenv()

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def tarefa_enviar_felicitacoes():
    try:
        resultado = executar_envio_por_data()
        logging.info(f"✅ Tarefa executada com sucesso: {resultado}")
    except Exception as e:
        logging.error(f"❌ Erro ao executar envio automático: {str(e)}")

if __name__ == "__main__":
    logging.info("🚀 Iniciando tarefa de envio de felicitações...")
    tarefa_enviar_felicitacoes()
