import json
import os
import botocore.session

from api.libs.logging import init_logger

LOG = init_logger(os.environ.get("LOG_LEVEL").strip())
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION").strip()
AWS_SECRET_NAME = os.environ.get("AWS_SECRET_NAME").strip()
CHARSET = "UTF-8"

secretsmanager_client = botocore.session.get_session().create_client("secretsmanager", region_name=AWS_REGION)

def get_secret():
    data = secretsmanager_client.get_secret_value(SecretId=AWS_SECRET_NAME)
    secret = data["SecretString"]
    return json.loads(secret)
