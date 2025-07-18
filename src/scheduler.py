#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from flask import Flask
from flask import app
from executa_envio_data import executar_envio_por_data
sys.stderr = open("stderr.log", "w", encoding="utf-8", errors="replace")

import os
import schedule
import time
import subprocess
import smtplib
import datetime
import logging
from email.mime.text import MIMEText
from dotenv import load_dotenv


app = Flask(__name__)
# Carrega variáveis de ambiente
load_dotenv()

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

if __name__ == "__main__":
    logging.info("🚀 Executando tarefa de felicitações...")
    tarefa_enviar_felicitacoes()