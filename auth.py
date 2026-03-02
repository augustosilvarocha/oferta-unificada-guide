import os
import requests

BASE_URL = "https://administrativo.rieh.nees.ufal.br"

url_token = BASE_URL + "/api/token/"

def obter_token():
    username = "xxxxxx"
    password = "xxxxxx"

    if not username or not password:
        raise ValueError("Variáveis de ambiente RIEH_CPF e RIEH_SENHA não estão definidas.")

    data = {"username": username, "password": password}
    response = requests.post(url_token, json=data)

    if response.status_code != 200:
        raise Exception(f"Erro ao obter token: {response.text}")

    return response.json().get("access")
