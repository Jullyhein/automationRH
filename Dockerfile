# Usa imagem base com Python
FROM python:3.11-slim

# Cria diretório de trabalho
WORKDIR /app

# Copia os arquivos
COPY . .

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta usada pela aplicação Flask
EXPOSE 5000

# Comando para rodar a aplicação
CMD ["python", "src/scheduler.py"]
