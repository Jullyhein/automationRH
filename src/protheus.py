#checar se os dados dos funcionários estão no protheus e com base nele trabalhar o envio do aniversário.

import os
import requests
import logging
from datetime import datetime
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def get_active_employees():
    API_URL = os.getenv("PROTHEUS_URL")
    USER = os.getenv("PROTHEUS_USER")
    PASS = os.getenv("PROTHEUS_PASS")

    HEADERS = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "client_id": os.getenv("PROTHEUS_CLIENT_ID"),
        "client_secret": os.getenv("PROTHEUS_CLIENT_SECRET"),
        "product": "RM",
        "companyId": os.getenv("PROTHEUS_COMPANY_ID"),
        "branchId": os.getenv("PROTHEUS_BRANCH_ID")
    }

    # Autenticação via Basic Auth se necessário
    auth = (USER, PASS) if USER and PASS else None

    response = requests.get(API_URL, headers=HEADERS, auth=auth)

    if response.status_code != 200:
        raise Exception(f"Erro na requisição: {response.status_code} - {response.text}")
    
    try:
        data = response.json()
    except ValueError:
        raise Exception("Resposta não é um JSON válido.")

    # ✅ Verifica se a resposta está aninhada em alguma chave (ex: 'employees' ou 'value')
    if isinstance(data, dict):
        # Ajuste conforme o nome correto da chave na API
        for key in ['employees', 'value', 'items', 'data']:
            if key in data and isinstance(data[key], list):
                data = data[key]
                break

    if not isinstance(data, list):
        raise Exception("Formato inesperado: esperado uma lista de funcionários.")

    active_employees = []
    for employee in data:
        if isinstance(employee, dict) and not employee.get("demissionDate"):
            raw_birthdate = employee.get("birthDate")
            formatted_birthdate = None
            if raw_birthdate:
                try:
                    dt = datetime.strptime(raw_birthdate[:10], "%Y-%m-%d")
                    formatted_birthdate = dt.strftime("%d-%m")
                except Exception as e:
                    print(f"Erro ao formatar data de nascimento: {raw_birthdate} -> {e}")

            filtered = {
                "name": employee.get("name"),
                "birthdate": formatted_birthdate,
                "employeeCpf": employee.get("employeeCpf")
            }
            active_employees.append(filtered)

    return active_employees


def buscar_aniversariantes_hoje(data_desejada=None):
    #today = datetime.today().strftime("%d-%m")
    if data_desejada is None:
        data_desejada = datetime.today().strftime("%d-%m")

    logging.info(f"🔎 Procurando aniversariantes para a data: {data_desejada}")
    employees = get_active_employees()
    logging.debug(f"Total de funcionários ativos: {len(employees)}")

    aniversariantes = []
    for emp in employees:
        logging.debug(f"Analisando funcionário: {emp['name']} - Nasc: {emp['birthdate']}")
        if emp["birthdate"] == data_desejada:
            logging.info(f"🎉 Aniversariante encontrado: {emp['name']} - CPF: {emp['employeeCpf']}")
            aniversariantes.append(emp["employeeCpf"])

    return aniversariantes

def buscar_aniversariantes_mes(mes_desejado="06"):
    """
    Lista CPFs dos funcionários ativos que fazem aniversário no mês especificado (formato: "MM").
    """
    logging.info(f"🔎 Procurando aniversariantes para o mês: {mes_desejado}")
    employees = get_active_employees()
    logging.debug(f"Total de funcionários ativos: {len(employees)}")

    aniversariantes_mes = []
    for emp in employees:
        nascimento = emp.get("birthdate")  # formato esperado: "dd-mm"
        if nascimento and nascimento[3:5] == mes_desejado:
            logging.info(f"🎉 Aniversariante de junho: {emp['name']} - CPF: {emp['employeeCpf']}")
            aniversariantes_mes.append({
                "name": emp["name"],
                "birthdate": nascimento,
                "employeeCpf": emp["employeeCpf"]
            })

    return aniversariantes_mes



# Permite rodar direto no terminal
if __name__ == "__main__":
    aniversariantes_junho = buscar_aniversariantes_mes("06")

    for pessoa in aniversariantes_junho:
        print(f"{pessoa['name']} - {pessoa['birthdate']} - CPF: {pessoa['employeeCpf']}")
