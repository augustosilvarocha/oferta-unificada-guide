"""
Gera um JSON com id da turma -> lista de IDs dos estudantes da turma.
Pagina GET /api/classes/?limit=50 seguindo "next" e filtra só as turmas cujos IDs estão em escolas_turmas_filtrado.json.
A API retorna: { "count", "next", "previous", "results": [ { "id", "students": [627573, 627574, ...] }, ... ] }.
"""

import json
import threading

import requests

try:
    from tqdm import tqdm
except ImportError:
    def tqdm(iterable, **kwargs):
        return iterable

# ========== CONFIGURAÇÃO ==========
ARQUIVO_TURMAS_IDS = "json/escolas_turmas_filtrado.json"
ARQUIVO_SAIDA = "json/turmas_estudantes_ids.json"
LIMIT_POR_PAGINA = 50

base_url = "https://administrativo.rieh-hmg.nees.ufal.br"
url_token = base_url + "/api/token/"
url_refresh = base_url + "/api/token/refresh/"

session = requests.Session()
lock_token = threading.Lock()

API_HEADERS = {"Accept": "application/json", "Content-Type": "application/json"}


def obter_tokens(username, password):
    data = {"username": username, "password": password}
    r = session.post(url_token, json=data, headers=API_HEADERS)
    r.raise_for_status()
    d = r.json()
    return d["access"], d["refresh"]


def renovar_token(refresh_token):
    headers = dict(API_HEADERS)
    csrf = session.cookies.get("csrftoken")
    if csrf:
        headers["X-CSRFTOKEN"] = csrf
    r = session.post(url_refresh, json={"refresh": refresh_token}, headers=headers)
    if r.status_code != 200:
        raise RuntimeError(f"Falha ao renovar token: {r.status_code} - {r.text}")
    body = r.json()
    if "access" not in body:
        raise RuntimeError(f"Resposta do refresh sem 'access': {body}")
    return body["access"]

 
def token_invalido_ou_expirado(response):
    if response.status_code not in (401, 403):
        return False
    texto = (response.text or "").lower()
    return "expirado" in texto or "token_not_valid" in texto or ("token" in texto and "inválido" in texto)


def get_com_token(url, tokens, params=None):
    access, refresh = tokens[0], tokens[1]
    headers = {"Authorization": f"Bearer {access}", **API_HEADERS}
    # Se url já tiver query string (ex: next), não envia params
    r = session.get(url, headers=headers, params=params if params else None, timeout=30)
    if token_invalido_ou_expirado(r):
        with lock_token:
            novo = renovar_token(refresh)
            tokens[0] = novo
            headers["Authorization"] = f"Bearer {novo}"
        r = session.get(url, headers=headers, params=params if params else None, timeout=30)
    return r


def extrair_ids_estudantes(turma_obj):
    """API retorna students: [627573, 627574, ...] (lista de IDs)."""
    students = turma_obj.get("students") or []
    return [s for s in students if isinstance(s, (int, float))]


def main():
    USERNAME = "xxxxxx"
    PASSWORD = "xxxxxx"

    print("Carregando IDs das turmas desejadas...")
    with open(ARQUIVO_TURMAS_IDS, "r", encoding="utf-8") as f:
        turmas_por_escola = json.load(f)
    ids_desejados = set()
    for lista in turmas_por_escola.values():
        ids_desejados.update(lista)
    ids_desejados = sorted(ids_desejados)
    print(f"  {len(ids_desejados)} turmas para buscar (IDs em {ARQUIVO_TURMAS_IDS}).")

    print("🔑 Obtendo token...")
    access, refresh = obter_tokens(USERNAME, PASSWORD)
    tokens = [access, refresh]

    # 1) Paginar listagem seguindo "next" (limit=50 por página)
    print("Listando turmas (limit=50 por página)...")
    turmas_encontradas = {}
    url = f"{base_url}/api/classes/"
    params = {"limit": LIMIT_POR_PAGINA, "offset": 0}
    while True:
        r = get_com_token(url, tokens, params=params)
        if r.status_code != 200:
            print(f"Erro listagem: {r.status_code} - {r.text[:200]}")
            break
        data = r.json()
        results = data.get("results", data if isinstance(data, list) else [])
        if not results:
            break
        for t in results:
            tid = t.get("id")
            if tid is not None and tid in ids_desejados:
                turmas_encontradas[tid] = t
        next_url = data.get("next") if isinstance(data, dict) else None
        if not next_url:
            break
        url = next_url
        params = None  # next já traz query string na URL

    # Turmas que não apareceram na listagem: GET /api/classes/{id}/
    faltando = [i for i in ids_desejados if i not in turmas_encontradas]
    if faltando:
        print(f"  {len(faltando)} IDs não na listagem; buscando detalhe...")
        for tid in tqdm(faltando, desc="Detalhe"):
            r = get_com_token(f"{base_url}/api/classes/{tid}/", tokens)
            if r.status_code == 200:
                turmas_encontradas[tid] = r.json()

    # 2) Montar saida: id_turma -> lista de IDs dos estudantes
    saida = {}
    for tid in ids_desejados:
        obj = turmas_encontradas.get(tid)
        if not obj:
            saida[str(tid)] = []
            continue
        saida[str(tid)] = extrair_ids_estudantes(obj)

    with open(ARQUIVO_SAIDA, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)

    print(f"✅ Salvo em {ARQUIVO_SAIDA} ({len(saida)} turmas).")


if __name__ == "__main__":
    main()
