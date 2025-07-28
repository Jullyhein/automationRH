from datetime import datetime
import logging
import os
import requests
from graphutils import formatar_nome_curto, get_access_token, get_aniversariantes_com_imagem


def executar_envio_por_data(data_desejada=None):
    if not data_desejada:
        #data_desejada = "26-07"
        data_desejada = datetime.now().strftime("%d-%m")

    logging.info(f"📅 Data desejada: {data_desejada}")

    try:
        token = get_access_token()
        logging.info("✅ Token obtido com sucesso.")
    except Exception as e:
        logging.error(f"❌ Erro ao obter token: {str(e)}")
        raise Exception(f"Erro ao obter token: {str(e)}")

    aniversariantes = get_aniversariantes_com_imagem(token, data_desejada)
    logging.info(f"🔍 {len(aniversariantes)} aniversariante(s) encontrado(s) para {data_desejada}.")

    if not aniversariantes:
        logging.warning(f"⚠️ Nenhum aniversariante encontrado para {data_desejada}.")
        return f"Nenhum aniversariante encontrado para {data_desejada}."

    remetente_email = os.getenv("EMAIL_REMETENTE")
    email_destino = os.getenv("EMAIL_DESTINO")

    if not remetente_email or not email_destino:
        logging.error("❌ EMAIL_REMETENTE ou EMAIL_DESTINO não definido.")
        raise Exception("Configuração de e-mail inválida.")

    url_envio = f"https://graph.microsoft.com/v1.0/users/{remetente_email}/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    assunto = f"🎉 Felicitações de Aniversário – {data_desejada}"
    corpo_html = f"""
        <h2>🎉 Aniversariantes de {data_desejada}</h2>
        <p>🎈 Hoje é dia de celebrar as vidas incríveis que fazem parte da nossa jornada!</p>
    """

    attachments = []

    for idx, pessoa in enumerate(aniversariantes):
        nome = formatar_nome_curto(pessoa["name"])
        filename = pessoa["filename"]

        logging.info(f"📷 Processando aniversariante: {nome} - {filename}")
        corpo_html += f"""
        <div style="margin-bottom: 30px;">
            <p><strong>{nome}</strong></p>
        """

        if pessoa.get("metodo") == "inline":
            cid = f"fotoaniversario{idx}"
            corpo_html += f'<img src="cid:{cid}" width="300" /><br>'

            imagem_base64_limpa = pessoa["image_base64"].split(",")[1] if "," in pessoa["image_base64"] else pessoa["image_base64"]

            attachments.append({
                "@odata.type": "#microsoft.graph.fileAttachment",
                "name": filename,
                "contentBytes": imagem_base64_limpa,
                "contentId": cid,
                "isInline": True
            })
        else:
            logging.warning(f"⚠️ Aniversariante {nome} não possui imagem.")
            corpo_html += "<p>🎈 Sem imagem disponível</p>"

        corpo_html += "</div>"

    payload = {
        "message": {
            "subject": assunto,
            "body": {
                "contentType": "html",
                "content": corpo_html
            },
            "toRecipients": [
                {"emailAddress": {"address": email_destino}}
            ],
            "attachments": attachments
        }
    }

    logging.debug("📦 Payload pronto para envio.")

    try:
        res = requests.post(url_envio, headers=headers, json=payload)
        logging.info(f"📨 Requisição enviada. Status: {res.status_code}")
        if res.status_code == 202:
            logging.info(f"✅ E-mail enviado com sucesso para {email_destino}")
            return f"E-mail enviado com {len(aniversariantes)} aniversariantes."
        else:
            raise Exception(f"Erro ao enviar e-mail: {res.text}")
    except Exception as e:
        logging.error(f"❌ Exceção ao tentar enviar o e-mail: {str(e)}")
        raise
