import os
from minio import Minio
from app.core.database import Environment
node_env = Environment().tipo 
print(node_env)
def connectMinio():
    endpoint = "54.233.210.68:6001" 
    if node_env == 'production':
        endpoint='barcarena-minio:9000'
    client = Minio(
        endpoint=endpoint,
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    return client