FROM python:3.10-slim

WORKDIR /app

# Copiar os arquivos de dependências
COPY pyproject.toml poetry.lock /app/

# Instalar o Poetry
RUN pip install --no-cache-dir poetry

# Verificar a versão do Poetry
RUN poetry --version

# Configurar o Poetry e instalar as dependências
RUN poetry config virtualenvs.create false && poetry install --without dev --no-interaction --no-ansi --no-root

# Copiar o restante do código da aplicação
COPY . /app

# Expor a porta 8000
EXPOSE 8000

# Comando para rodar o aplicativo
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
