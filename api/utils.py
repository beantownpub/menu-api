import os

from flask_httpauth import HTTPBasicAuth

AUTH = HTTPBasicAuth()


@AUTH.verify_password
def verify_password(username, password):
    api_user = os.environ.get("API_USER")
    api_pwd = os.environ.get("API_USER_PWD")
    if username == api_user and password == api_pwd:
        verified = True
    else:
        verified = False
    return verified
