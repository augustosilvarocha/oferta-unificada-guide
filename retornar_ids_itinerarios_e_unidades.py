import requests
import json
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from auth import obter_token


BASE_URL = "https://administrativo.rieh.nees.ufal.br"
ITINERARIES_URL = f"{BASE_URL}/api/itineraries/"
OUTPUT_FILE = "escolas_itinerarios_unidades.json"


ID_SCHOOLS = [
    14529,14530,14531,14532,14533,14534,14535,14536,14537,14538,
    14539,14540,14541,14542,14543,14544,14545,14546,14547,14548,
    14549,14550,14551,14552,14553,14554,14555,14556,14557,14558,
    14559,14560,14561,14562,14563,14564,14565,14566,14567,14568,
    14569,14570,14571,14572,14573,14574,14575,14576,14577,14578,
    14579,14580,14581,14582,14583,14584,14585,14586,14587,14588,
    14589,14590,14591,14592,14593,14594,14595,14596,14597,14598,
    14599,14600,14601,14602,14603,14604,14605,14606,14607,14608,
    14609,14610,14611,14612,14613,14614,14615,14616,14617,14618,
    14619,14620,14621,14622,14623,14624,14625,14626,14627,14628
]


def criar_sessao():
    session = requests.Session()

    retry = Retry(
        total=5,
        backoff_factor=2,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET"]
    )

    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)

    return session


def buscar_itinerarios(ids):
    token = obter_token()

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    session = criar_sessao()
    resultado = {}

    for school_id in ids:
        url = f"{ITINERARIES_URL}?id_school={school_id}&limit=100"
        itinerarios = []

        print(f"\n🔎 Buscando escola {school_id}...")

        while url:
            try:
                response = session.get(url, headers=headers, timeout=60)
            except requests.exceptions.RequestException as e:
                print(f"⚠️ Erro de conexão escola {school_id}: {e}")
                break

            if response.status_code != 200:
                print(f"❌ Erro HTTP {response.status_code} escola {school_id}")
                break

            data = response.json()

            for item in data.get("results", []):
                itinerarios.append({
                    "itinerary_id": item["id"],
                    "curricular_units": item.get("curricular_units", [])
                })

            url = data.get("next")

        resultado[str(school_id)] = itinerarios
        print(f"✅ Escola {school_id} → {len(itinerarios)} itinerários")

        time.sleep(0.3)

    return resultado


if __name__ == "__main__":
    dados = buscar_itinerarios(ID_SCHOOLS)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)

    print(f"\n📄 Arquivo gerado: {OUTPUT_FILE}")