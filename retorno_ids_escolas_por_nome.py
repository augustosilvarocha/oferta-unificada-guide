import requests
import json
import time
from auth import obter_token

BASE_URL = "https://administrativo.rieh.nees.ufal.br"
SCHOOLS_URL = f"{BASE_URL}/api/schools/"
OUTPUT_FILE = "json/ids_escolas_por_nome.json"

ESCOLAS = [
"EE 8 DE MAIO",
"EE ALVARO MARTINS DOS SANTOS",
"EE BARAO DO RIO BRANCO",
"EE DELFINA NOGUEIRA DE SOUZA",
"EE ELDORADO",
"EE ESTEFANA CENTURION GAMBARRA",
"EE INDIGENA ANTONIO ALVES DE BARROS",
"EE INDIGENA FLAVIANA ALCANTARA FIGUEIREDO",
"EE JAPORA",
"EE JOSE BONIFACIO",
"EE MAL CASTELO BRANCO",
"EE MANOEL DA COSTA LIMA",
"EE PAULO EDUARDO DE SOUZA FIRMO",
"EE SANTIAGO BENITES"
]


def buscar_ids():
    token = obter_token()

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    resultado = {}

    for escola in ESCOLAS:
        url = f"{SCHOOLS_URL}?name={escola}"

        response = requests.get(url, headers=headers)
        data = response.json()
        resultados = data.get("results", data)

        if resultados:
            resultado[escola] = resultados[0]["id"]
            print(f"{escola} -> {resultados[0]['id']}")

        time.sleep(0.2)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    buscar_ids()