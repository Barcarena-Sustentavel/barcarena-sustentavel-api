# Configuração de ambiente
## Dependências
* FastApi: `pip install "fastapi[standard]"`
* Poetry: `sudo curl -sSL https://install.python-poetry.org | python3 -`
* Alembic: `pip install alembic`

## Configurando Docker
* Baixar imagem: `sudo docker compose up -d barcarena-sustentavel-postgresql` 
* Executar imagem: `sudo docker exec -it barcarena-sustentavel-postgresql bash`

## Configurando banco
* Configuração de usuário e banco:`psql -U barcarena_sustentavel -d barcarena_sustentavel`
* Schema do banco: `CREATE SCHEMA barcarena_sustentavel AUTHORIZATION barcarena_sustentavel;`
  
