"""
Exemplo de código que diciona alunos em turmas: para cada escola, distribui 50 alunos por turma.
Usa estudantes_cpfs.json (CPFs por escola) e escolas_turmas_filtrado.json (IDs das turmas por escola).
POST /api/classes/{id}/add_students/ com body {"students_cpf_list": ["cpf1", ...]}.
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
ARQUIVO_CPFS = "json/estudantes_cpfs copy.json"
ARQUIVO_TURMAS = "json/escolas_turmas_filtrado.json"
ALUNOS_POR_TURMA = 50

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


def adicionar_alunos_turma(turma_id, cpfs, tokens):
    """
    POST /api/classes/{turma_id}/add_students/ com students_cpf_list.
    Retorna (True, None) em sucesso, (False, mensagem) em erro.
    """
    access, refresh = tokens[0], tokens[1]
    headers = {"Authorization": f"Bearer {access}", "Content-Type": "application/json"}
    csrf = session.cookies.get("csrftoken")
    if csrf:
        headers["X-CSRFTOKEN"] = csrf
    url = f"{base_url}/api/classes/{turma_id}/add_students/"
    payload = {"students_cpf_list": cpfs}

    def fazer_request():
        return session.post(url, json=payload, headers=headers)

    try:
        r = fazer_request()
        if token_invalido_ou_expirado(r):
            with lock_token:
                novo = renovar_token(refresh)
                tokens[0] = novo
                headers["Authorization"] = f"Bearer {novo}"
            r = fazer_request()
        if r.status_code in (200, 201):
            return True, None
        return False, f"{r.status_code} - {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def main():
    USERNAME = "xxxxxx"
    PASSWORD = "xxxxxx"

    print("Carregando JSONs...")
    with open(ARQUIVO_CPFS, "r", encoding="utf-8") as f:
        cpfs_por_escola = json.load(f)
    with open(ARQUIVO_TURMAS, "r", encoding="utf-8") as f:
        turmas_por_escola = json.load(f)

    # Escolas que têm CPFs e turmas
    escolas_cpfs = set(cpfs_por_escola.keys())
    escolas_turmas = set(turmas_por_escola.keys())
    escolas = sorted(escolas_cpfs & escolas_turmas, key=int)
    if not escolas:
        print("Nenhuma escola em comum entre os dois arquivos.")
        return

    # Monta lista (turma_id, lista_de_50_cpfs) para cada escola
    tarefas = []
    for escola_id in escolas:
        cpfs = cpfs_por_escola[escola_id]
        turmas = turmas_por_escola[escola_id]
        if len(turmas) != 5:
            print(f"⚠️ Escola {escola_id}: esperadas 5 turmas, encontradas {len(turmas)}. Pulando.")
            continue
        # Divide os primeiros 250 CPFs em 5 grupos de 50
        for i in range(5):
            inicio = i * ALUNOS_POR_TURMA
            fim = inicio + ALUNOS_POR_TURMA
            chunk = cpfs[inicio:fim]
            if len(chunk) < ALUNOS_POR_TURMA:
                print(f"⚠️ Escola {escola_id} turma {turmas[i]}: só {len(chunk)} CPFs (esperados {ALUNOS_POR_TURMA}).")
            tarefas.append((escola_id, turmas[i], chunk))

    total = len(tarefas)
    print(f"🔑 Obtendo token...")
    access, refresh = obter_tokens(USERNAME, PASSWORD)
    tokens = [access, refresh]
    ok_count = 0
    err_count = 0
    _write = getattr(tqdm, "write", None) or print

    print(f"📋 Adicionando {ALUNOS_POR_TURMA} alunos em cada uma das {total} turmas ({len(escolas)} escolas).")
    print()

    with tqdm(total=total, unit="turma", desc="Turmas", ncols=100) as pbar:
        for escola_id, turma_id, cpfs in tarefas:
            sucesso, msg = adicionar_alunos_turma(turma_id, cpfs, tokens)
            pbar.update(1)
            if sucesso:
                ok_count += 1
                pbar.set_postfix(ok=ok_count, erros=err_count, escola=escola_id, refresh=False)
            else:
                err_count += 1
                _write(f"❌ Escola {escola_id} turma {turma_id} | {msg}")
                pbar.set_postfix(ok=ok_count, erros=err_count, escola=escola_id, refresh=False)

    print()
    print(f"✅ Turmas preenchidas: {ok_count}  |  ❌ Erros: {err_count}  |  Total: {total}")


if __name__ == "__main__":
    main()
