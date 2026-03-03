import requests
import json
from auth import obter_token

BASE_URL = "https://administrativo.rieh-hmg.nees.ufal.br"
TEACHERS_URL = f"{BASE_URL}/api/teachers/?limit=100"

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


def gerar_json_docentes():
    token = obter_token()

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}"
    }

    resultado = {school_id: [] for school_id in ID_SCHOOLS}

    url = TEACHERS_URL
    total_docentes = 0

    while url:
        response = requests.get(url, headers=headers, timeout=60)

        if response.status_code != 200:
            print("Erro ao buscar docentes:", response.status_code)
            print(response.text)
            return

        data = response.json()

        for teacher in data["results"]:
            teacher_id = teacher["id"]

            for school_id in teacher["schools"]:
                if school_id in ID_SCHOOLS:
                    resultado[school_id].append(teacher_id)
                    total_docentes +=1

        url = data["next"]

    resultado = {k: v for k, v in resultado.items() if v}

    with open("escolas_docentes.json", "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=4)

    print("✅ JSON de docentes criado com sucesso!")
    print("\n📊 RESUMO DOCENTES")
    print(f"👥 Total de vínculos encontrados: {total_docentes}")


if __name__ == "__main__":
    gerar_json_docentes()