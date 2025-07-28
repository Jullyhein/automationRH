import os
import requests
import base64
import os
import requests
import logging
from datetime import datetime
from dotenv import load_dotenv
import time
from protheus import buscar_aniversariantes_hoje, get_active_employees

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
TENANT_ID = os.getenv("TENANT_ID")
DRIVE_ID = os.getenv("DRIVE_ID")
FOLDER_BASE = os.getenv("FOLDER_BASE") 

MESES_PT = [
    "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

MES_ATUAL = MESES_PT[datetime.now().month - 1]

FOLDER_PATH = f"{FOLDER_BASE}/{MES_ATUAL}"
GRAPH_URL = f"https://graph.microsoft.com/v1.0/drives/{DRIVE_ID}/root:/{FOLDER_PATH}:/children"
IMAGEM_PADRAO = "https://uploaddeimagens.com.br/images/004/893/374/full/Design_sem_nome_%281%29.png"

# --- Obter token da API Microsoft Graph ---
def get_access_token():
    url = f"https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }
    response = requests.post(url, headers=headers, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


logging.basicConfig(
level=logging.INFO,
format="%(asctime)s [%(levelname)s] %(message)s"
)

def normalizar_cpf(cpf):
    return "".join(filter(str.isdigit, str(cpf)))

def listar_conteudo_pasta(token):
    headers = {"Authorization": f"Bearer {token}"}

    # Chamada original para listar os arquivos
    response = requests.get(GRAPH_URL, headers=headers)
    response.raise_for_status()
    dados = response.json()

    imagens_dict = {}

    for item in dados.get("value", []):
        if "file" in item and item["name"].lower().endswith(('.jpg', '.jpeg', '.png')):
            nome_arquivo = item["name"]
            nome_base = nome_arquivo.rsplit(".", 1)[0]
            cpf = normalizar_cpf(nome_base.strip())
            item_id = item["id"]
            drive_id = item["parentReference"]["driveId"]


            #logging.debug(f"📂 Arquivo encontrado: {nome_arquivo}")
            #logging.debug(f"🧾 Extraído CPF: {cpf}")

            conteudo_url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"
            res_img = requests.get(conteudo_url, headers=headers)
            if res_img.status_code == 200:
                imagem_bytes = res_img.content
                extensao = nome_arquivo.split(".")[-1].lower()
                mime_type = f"image/{'jpeg' if extensao in ['jpg', 'jpeg'] else 'png'}"
                imagem_base64 = base64.b64encode(imagem_bytes).decode('utf-8')
                imagens_dict[cpf] = f"data:{mime_type};base64,{imagem_base64}"
            else:
                print(f"⚠️ Não foi possível baixar a imagem {nome_arquivo} - Status: {res_img.status_code}")
    for cpf_key in imagens_dict.keys():
        logging.debug(f"🔎 Imagem disponível para CPF: {cpf_key}")
    return imagens_dict

def formatar_nome_curto(nome_completo):
    nomes = nome_completo.strip().split()
    primeiros = nomes[:2]
    return " ".join([n.capitalize() for n in primeiros])

inicio = time.time()
EXTENSOES_SUPORTADAS = [".jpg", ".jpeg", ".png"]
def get_aniversariantes_com_imagem(token, data_desejada=None):
    cpfs_hoje = buscar_aniversariantes_hoje(data_desejada)
    logging.info(f"⏱️ Tempo para obter aniversariantes: {time.time() - inicio:.2f}s")
    if not cpfs_hoje:
        logging.info("Nenhum aniversariante encontrado para hoje.")
        return []

    imagens_dict = listar_conteudo_pasta(token)  # dict com base64
    employees = get_active_employees()
    aniversariantes_final = []

    for emp in employees:
        cpf = normalizar_cpf(emp.get("employeeCpf"))
        if cpf in cpfs_hoje:
            nome_formatado = formatar_nome_curto(emp.get("name", ""))
            imagem_base64 = imagens_dict.get(cpf, None)
            aniversariante = {
                "name": nome_formatado,
                "cpf": cpf,
                "image_base64": imagem_base64,
                "filename": f"{cpf}.png",
                "metodo": "inline" if imagem_base64 else "sem imagem"
            }
            aniversariante["tem_imagem"] = bool(imagem_base64)
            aniversariantes_final.append(aniversariante)

    return aniversariantes_final


def formatar_nome_curto(nome_completo):
    """Retorna o primeiro e último nome, ignorando partículas como 'de', 'da', 'dos'."""
    ignorar = {"de", "da", "das", "do", "dos"}
    partes = [parte.capitalize() for parte in nome_completo.strip().split() if parte.lower() not in ignorar]
    if len(partes) >= 2:
        return f"{partes[0]} {partes[-1]}"
    return " ".join(partes)


if __name__ == "__main__":
    token = get_access_token()
    imagens_dict = listar_conteudo_pasta(token)

    for cpf, base64_img in imagens_dict.items():
        print(f"{cpf} → {base64_img[:100]}...")