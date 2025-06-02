# 📄 Documentação Técnica – Sistema de Felicitações de Aniversário

# Para rodar:
Estar na mesma pasta do scheduler.py
- python scheduler.py

- Stack: Python, Docker, Pytest, etc.

## 📌 Visão Geral

Este sistema automatiza o envio de **e-mails personalizados de aniversário** com base nos dados de funcionários ativos do sistema **TOTVS (via API RM)** e imagens armazenadas por CPF. O envio é feito por meio da **API da Microsoft Graph**, utilizando a conta institucional `wfsolar`.

---

## 🔄 Fluxo Geral do Sistema

1. **Coleta de dados de funcionários ativos** via API TOTVS.
2. **Tratamento de dados**:
   - Remoção de partículas do nome (`de`, `da`, `das`, `do`, `dos`).
   - Formatação da data de nascimento.
3. **Verificação de aniversariantes do dia atual** (ou data informada).
4. **Busca de imagens por CPF** em pastas mensais.
5. **Geração de e-mail com imagens inline (quando disponíveis)**.
6. **Envio do e-mail** para um destinatário pré-configurado usando a API Microsoft Graph.

---

## 🧩 Tecnologias Utilizadas

| Componente            | Descrição                                              |
|-----------------------|--------------------------------------------------------|
| **Flask**             | Framework web utilizado para expor o endpoint REST     |
| **Python**            | Linguagem principal da aplicação                       |
| **TOTVS API (RM)**    | Fonte de dados de funcionários ativos                  |
| **Microsoft Graph API** | Envio de e-mails com anexos e HTML                  |
| **Requests**          | Requisições HTTP para integração com APIs              |
| **dotenv / os.getenv**| Variáveis de ambiente para credenciais e configurações |

---

## ⚙️ Endpoints

### `POST /enviar-felicitacoes`

**Objetivo**: Enviar um e-mail contendo os aniversariantes do dia.

#### Corpo da Requisição (opcional):
```json
{
  "data": "dd-mm"  // opcional. Se omitido, a data atual do sistema será usada.
}
```
## ✅ Respostas da API

- **200 OK**: E-mail enviado ou nenhum aniversariante encontrado.
- **400 Bad Request**: Caso a data esteja malformada.
- **500 Internal Server Error**: Falha na autenticação ou envio.

---

## 📚 Estrutura das Funções

### `get_active_employees()`

- Consulta a API TOTVS com autenticação via `client_id`, `client_secret`, `username`, `password`.
- Filtra somente **funcionários ativos** (sem `demissionDate`).
- Extrai e formata:
  - `name` (com formatação curta).
  - `birthdate` no formato `dd-mm`.
  - `employeeCpf`.

### `formatar_nome_curto(nome: str)`

- Remove preposições comuns (`de`, `da`, `das`, `do`, `dos`) para uma apresentação mais amigável no e-mail.

### `get_aniversariantes_com_imagem(token, data_desejada)`

- Verifica os aniversariantes pela data `dd-mm`.
- Procura por uma imagem de perfil em uma pasta organizada por mês (`imagens/06/12345678900.jpg`).
- Retorna metadados e imagem em base64 para inclusão no e-mail.

### `enviar_email_por_data()`

- Controlador principal exposto como rota do Flask.
- Usa a data atual se nenhuma for fornecida.
- Monta HTML com nome e imagem dos aniversariantes.
- Envia via Microsoft Graph API com as credenciais do e-mail `wfsolar`.

---

## 📁 Organização dos Arquivos de Imagem

- Imagens devem estar em diretórios nomeados pelo **mês numérico** (`01`, `02`, ..., `12`).
- Os arquivos devem estar nomeados pelo **CPF do colaborador**, ex: `12345678900.jpg`.

### Estrutura de exemplo:
```
imagens/
├── 06/
│ ├── 12345678900.jpg
│ └── 98765432100.jpg
```


---

## 🔐 Variáveis de Ambiente Necessárias

| Nome                                       | Descrição                                                |
|--------------------------------------------|-----------------------------------------------------------|
| `PROTHEUS_URL`                             | URL da API de funcionários ativos do TOTVS               |
| `PROTHEUS_USER` / `PROTHEUS_PASS`          | Credenciais da API TOTVS                                 |
| `PROTHEUS_CLIENT_ID` / `PROTHEUS_CLIENT_SECRET` | Autenticação OAuth para TOTVS                      |
| `PROTHEUS_COMPANY_ID` / `PROTHEUS_BRANCH_ID` | IDs da empresa e filial TOTVS                        |
| `EMAIL_REMETENTE`                          | E-mail usado como remetente no envio (ex: `wfsolar`)     |
| `EMAIL_DESTINO`                            | E-mail institucional que recebe os comunicados           |
| `MICROSOFT_CLIENT_ID` / `MICROSOFT_CLIENT_SECRET` | Credenciais do app no Azure                        |
| `MICROSOFT_TENANT_ID`                      | Tenant ID da organização no Azure                        |
| `MICROSOFT_SCOPE`                          | Escopo da API Graph (`Mail.Send`)                        |

---

## 📅 Automação Recomendada

Para envio diário automático, utilizar **cron job** ou agendador de tarefas no servidor:

```bash
curl -X POST http://localhost:5000/enviar-felicitacoes
```

## 🛠️ Futuras Melhorias

- Dashboard com aniversariantes do mês.

- Envio para múltiplos destinatários ou canais (ex: Slack, Teams).

- Log de aniversários enviados (evitar duplicidade).

- Inclusão de BD pra gravar logs. 