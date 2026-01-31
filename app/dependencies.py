import os
from minio import Minio
from app.core.database import Environment
#node_env = os.environ.get('NODE_ENV')
node_env = Environment().tipo #os.environ.get('VITE_AMBIENTE')
print(node_env)
def connectMinio():
    endpoit = "54.233.210.68:6001" 
    if node_env == 'production':
        endpoit='barcarena-minio:9000'
    client = Minio(
        endpoint=endpoit,
        access_key="minioadmin",
        secret_key="minioadmin",
        secure=False
    )
    return client