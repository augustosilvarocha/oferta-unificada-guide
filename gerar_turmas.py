import requests
import time
from auth import obter_token

BASE_URL = "https://administrativo.rieh.nees.ufal.br"
CLASSES_URL = f"{BASE_URL}/api/classes/"

REFERENCE_YEAR = 2026

itineraries_by_school = {
  "14529": [
    181
  ],
  "14530": [
    183
  ],
  "14531": [
    184
  ],
  "14532": [
    185
  ],
  "14533": [
    186
  ],
  "14534": [
    187
  ],
  "14535": [
    188
  ],
  "14536": [
    189
  ],
  "14537": [
    190
  ],
  "14538": [
    191
  ],
  "14539": [
    192
  ],
  "14540": [
    193
  ],
  "14541": [
    194
  ],
  "14542": [
    195
  ],
  "14543": [
    196
  ],
  "14544": [
    197
  ],
  "14545": [
    198
  ],
  "14546": [
    199
  ],
  "14547": [
    200
  ],
  "14548": [
    201
  ],
  "14549": [
    202
  ],
  "14550": [
    203
  ],
  "14551": [
    204
  ],
  "14552": [
    205
  ],
  "14553": [
    206
  ],
  "14554": [
    207
  ],
  "14555": [
    208
  ],
  "14556": [
    209
  ],
  "14557": [
    210
  ],
  "14558": [
    211
  ],
  "14559": [
    212
  ],
  "14560": [
    213
  ],
  "14561": [
    214
  ],
  "14562": [
    215
  ],
  "14563": [
    216
  ],
  "14564": [
    217
  ],
  "14565": [
    218
  ],
  "14566": [
    219
  ],
  "14567": [
    220
  ],
  "14568": [
    221
  ],
  "14569": [
    222
  ],
  "14570": [
    223
  ],
  "14571": [
    224
  ],
  "14572": [
    225
  ],
  "14573": [
    226
  ],
  "14574": [
    227
  ],
  "14575": [
    228
  ],
  "14576": [
    229
  ],
  "14577": [
    230
  ],
  "14578": [
    231
  ],
  "14579": [
    232
  ],
  "14580": [
    233
  ],
  "14581": [
    234
  ],
  "14582": [
    235
  ],
  "14583": [
    236
  ],
  "14584": [
    237
  ],
  "14585": [
    238
  ],
  "14586": [
    239
  ],
  "14587": [
    240
  ],
  "14588": [
    241
  ],
  "14589": [
    242
  ],
  "14590": [
    243
  ],
  "14591": [
    244
  ],
  "14592": [
    245
  ],
  "14593": [
    246
  ],
  "14594": [
    247
  ],
  "14595": [
    248
  ],
  "14596": [
    249
  ],
  "14597": [
    250
  ],
  "14598": [
    251
  ],
  "14599": [
    252
  ],
  "14600": [
    253
  ],
  "14601": [
    254
  ],
  "14602": [
    255
  ],
  "14603": [
    256
  ],
  "14604": [
    257
  ],
  "14605": [
    258
  ],
  "14606": [
    259
  ],
  "14607": [
    260
  ],
  "14608": [
    261
  ],
  "14609": [
    262
  ],
  "14610": [
    263
  ],
  "14611": [
    264
  ],
  "14612": [
    265
  ],
  "14613": [
    266
  ],
  "14614": [
    267
  ],
  "14615": [
    268
  ],
  "14616": [
    269
  ],
  "14617": [
    270
  ],
  "14618": [
    271
  ],
  "14619": [
    272
  ],
  "14620": [
    273
  ],
  "14621": [
    274
  ],
  "14622": [
    275
  ],
  "14623": [
    276
  ],
  "14624": [
    277
  ],
  "14625": [
    278
  ],
  "14626": [
    279
  ],
  "14627": [
    280
  ],
  "14628": [
    281
  ]
}

def criar_turmas():
    token = obter_token()

    headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    for school_index, (school_id, itineraries) in enumerate(itineraries_by_school.items(), start=1):

        print(f"\n🏫 Criando turmas para escola {school_id}")

        for turma_num in range(1, 6):

            payload = {
                "reference_year": REFERENCE_YEAR,
                "code": f"escola-{school_index}-t-{turma_num}",
                "school": school_id,
                "itineraries": itineraries,
                "students_cpf_list": [],
                "is_eja": False
            }

            response = requests.post(
                CLASSES_URL,
                json=payload,
                headers=headers,
                timeout=120
            )

            if response.status_code in (200, 201):
                print(f"✅ {payload['code']} criada")
            else:
                print(f"❌ Erro {payload['code']} → {response.status_code}")
                print(response.text)

            time.sleep(0.2)


if __name__ == "__main__":
    criar_turmas()