import json
import time
import requests
from auth import obter_token

BASE_URL = "https://administrativo.rieh.nees.ufal.br"
OFFERS_URL = f"{BASE_URL}/api/offers/"

TIMEOUT = 120
RETRY_LIMIT = 3
SLEEP_BETWEEN = 0.5


def carregar_ofertas():
    with open("ofertas_payload.json", encoding="utf-8") as f:
        return json.load(f)


def enviar_ofertas():
    token = obter_token()

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    ofertas = carregar_ofertas()

    total = len(ofertas)
    sucesso = 0
    falhas = []

    print(f"\n🚀 Iniciando envio de {total} ofertas...\n")

    for index, oferta in enumerate(ofertas, start=1):

        tentativa = 0
        enviada = False

        while tentativa < RETRY_LIMIT and not enviada:
            try:
                response = requests.post(
                    OFFERS_URL,
                    json=oferta,
                    headers=headers,
                    timeout=TIMEOUT
                )

                if response.status_code in (200, 201):
                    sucesso += 1
                    enviada = True
                    print(f"✅ [{index}/{total}] Oferta criada")
                else:
                    print(f"❌ [{index}/{total}] Erro {response.status_code}")
                    print(response.text)
                    falhas.append({
                        "index": index,
                        "status": response.status_code,
                        "response": response.text
                    })
                    enviada = True

            except requests.exceptions.ReadTimeout:
                tentativa += 1
                print(f"⏳ Timeout na oferta {index} (tentativa {tentativa})")
                time.sleep(2)

            except requests.exceptions.RequestException as e:
                tentativa += 1
                print(f"⚠️ Erro de conexão na oferta {index}: {e}")
                time.sleep(2)

        time.sleep(SLEEP_BETWEEN)

    print("\n📊 RESULTADO FINAL")
    print(f"✅ Sucesso: {sucesso}")
    print(f"❌ Falhas: {len(falhas)}")

    if falhas:
        with open("ofertas_falhas.json", "w", encoding="utf-8") as f:
            json.dump(falhas, f, indent=2)

        print("📄 Arquivo 'ofertas_falhas.json' salvo com os erros.")


if __name__ == "__main__":
    enviar_ofertas()