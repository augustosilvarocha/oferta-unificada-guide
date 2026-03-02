import requests
import json
import time
from auth import obter_token

BASE_URL = "https://administrativo.rieh.nees.ufal.br"
SCHOOLS_URL = f"{BASE_URL}/api/schools/"
OUTPUT_FILE = "json/ids_escolas_por_inep.json"

INEPS = [
12000094,
12000108
]


def buscar_ids():
    token = obter_token()

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    resultado = {}

    for inep in INEPS:
        url = f"{SCHOOLS_URL}?code={inep}"

        response = requests.get(url, headers=headers)
        data = response.json()
        resultados = data.get("results", data)

        if resultados:
            resultado[inep] = resultados[0]["id"]
            print(f"{inep} -> {resultados[0]['id']}")

        time.sleep(0.2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    buscar_ids()