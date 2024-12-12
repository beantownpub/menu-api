import json
import os
import botocore.session

from api.libs.logging import init_logger

LOG = init_logger(os.environ.get("LOG_LEVEL").strip())
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION").strip()
AWS_SECRET_NAME = os.environ.get("AWS_SECRET_NAME").strip()
CHARSET = "UTF-8"


def get_secret(aws_secrets_manager="disabled"):
  if aws_secrets_manager == "enabled":
    secretsmanager_client = botocore.session.get_session().create_client("secretsmanager", region_name=AWS_REGION)
    data = secretsmanager_client.get_secret_value(SecretId=AWS_SECRET_NAME)
    secret = json.loads(data["SecretString"])
  else:
    secret = {
      'user': os.environ.get("DATABASE_USERNAME"),
      'password': os.environ.get("DATABASE_PASSWORD"),
      'host': os.environ.get("DATABASE_HOST"),
      'db': os.environ.get("DATABASE_NAME"),
      'port': os.environ.get("DATABASE_PORT")
    }
  return secret
