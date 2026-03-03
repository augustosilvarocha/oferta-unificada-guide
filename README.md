# 📚 Scripts de Automação – Oferta Unificada RIEH

Conjunto de scripts Python para automatizar a criação de turmas, busca de dados e geração de ofertas regulares no sistema RIEH (`administrativo.rieh.nees.ufal.br`), como parte do fluxo de criação da **Oferta Unificada**.

---

## 📁 Estrutura dos Arquivos

```
.
├── auth.py                         # Autenticação e obtenção de token JWT
├── buscar_ids_por_inep.py          # Busca IDs de escolas pelo código INEP
├── buscar_ids_por_nome.py          # Busca IDs de escolas pelo nome
├── gerar_json_docentes.py          # Mapeia docentes por escola
├── buscar_itinerarios.py           # Busca itinerários e unidades curriculares por escola
├── criar_turmas.py                 # Cria turmas nas escolas
├── gerar_ofertas_payload.py        # Gera os payloads das ofertas regulares
├── enviar_ofertas.py               # Envia as ofertas para a API
└── json/
    ├── ids_escolas_por_inep.json
    └── ids_escolas_por_nome.json
```

---

## 🔐 Autenticação — `auth.py`

Obtém um token JWT para autenticação nas requisições à API.

**Como usar:**
Substitua `username` e `password` pelas credenciais válidas do sistema antes de executar qualquer script.

```python
username = "seu_cpf"
password = "sua_senha"
```

O token é gerado via `POST /api/token/` e retornado pela função `obter_token()`, que é importada pelos demais scripts.

---

## 🏫 Busca de IDs de Escolas

### `buscar_ids_por_inep.py`
Busca o ID interno de cada escola a partir do seu **código INEP**.

- Edite a lista `INEPS` com os códigos desejados.
- O resultado é salvo em `json/ids_escolas_por_inep.json`.

### `buscar_ids_por_nome.py`
Busca o ID interno de cada escola a partir do seu **nome**.

- Edite a lista `ESCOLAS` com os nomes das escolas.
- O resultado é salvo em `json/ids_escolas_por_nome.json`.

---

## 👩‍🏫 Mapeamento de Docentes — `gerar_json_docentes.py`

Consulta todos os docentes da API e gera um JSON mapeando quais professores pertencem a cada escola.

- Edite `ID_SCHOOLS` com os IDs das escolas a considerar.
- O resultado é salvo em `escolas_docentes.json`.

> ⚠️ Este script aponta para o ambiente de **homologação** (`rieh-hmg`). Ajuste a `BASE_URL` se necessário.

---

## 📋 Busca de Itinerários — `buscar_itinerarios.py`

Para cada escola, busca os itinerários formativos e suas respectivas unidades curriculares.

- Edite `ID_SCHOOLS` com os IDs das escolas.
- Inclui retry automático em caso de erros de servidor (500, 502, 503, 504).
- O resultado é salvo em `escolas_itinerarios_unidades.json`.

---

## 🏷️ Criação de Turmas — `criar_turmas.py`

Cria 5 turmas por escola com base no mapeamento `itineraries_by_school` (escola → itinerário).

- Os códigos das turmas seguem o padrão `escola-{N}-t-{1..5}`.
- Ano de referência configurável via `REFERENCE_YEAR` (padrão: `2026`).

> O dicionário `itineraries_by_school` deve ser preenchido com os IDs corretos de escolas e itinerários antes da execução.

---

## 📦 Geração de Payloads de Ofertas — `gerar_ofertas_payload.py`

Cruza os dados de turmas, alunos, docentes e itinerários para montar os payloads das ofertas regulares.

**Arquivos de entrada necessários:**
| Arquivo | Descrição |
|---|---|
| `turmas_estudantes_ids.json` | Mapa de turma → lista de alunos |
| `escolas_docentes.json` | Mapa de escola → lista de docentes |
| `escolas_itinerarios.json` | Mapa de escola → itinerários e unidades |
| `escolas_turmas_filtrado.json` | Mapa de escola → lista de turmas |

Configure as datas no topo do arquivo:
```python
START_DATE = "2026-02-24"
END_DATE   = "2026-03-30"
```

O resultado é salvo em `ofertas_payload.json` e um relatório por escola é exibido no terminal.

---

## 🚀 Envio de Ofertas — `enviar_ofertas.py`

Lê o `ofertas_payload.json` e envia cada oferta via `POST /api/offers/`.

- Possui **retry automático** em caso de timeout (até 3 tentativas por oferta).
- Falhas são registradas em `ofertas_falhas.json` ao final da execução.
- Exibe progresso em tempo real no terminal.

Parâmetros configuráveis:
```python
TIMEOUT         = 120   # segundos por requisição
RETRY_LIMIT     = 3     # tentativas em caso de timeout
SLEEP_BETWEEN   = 0.5   # intervalo entre requisições (segundos)
```

---

## 🔄 Fluxo Completo

```
1. auth.py                    → Configura credenciais
2. buscar_ids_por_inep.py     → Obtém IDs das escolas
   buscar_ids_por_nome.py     ↗
3. gerar_json_docentes.py     → Mapeia professores por escola
4. buscar_itinerarios.py      → Busca itinerários e unidades curriculares
5. criar_turmas.py            → Cria as turmas nas escolas
6. gerar_ofertas_payload.py   → Gera os payloads das ofertas
7. enviar_ofertas.py          → Envia as ofertas para a API
8. [Manual] Criação da Oferta Unificada via interface do sistema
```

> O **Passo 8** deve ser realizado manualmente pela interface web: `Meu Painel de Atividades → Ofertas Unificadas → + Nova oferta unificada`.

---

## ⚙️ Requisitos

- Python 3.8+
- Biblioteca `requests`

```bash
pip install requests
```

---

## ⚠️ Observações

- Todos os itinerários utilizados nas turmas devem estar **clonados para a escola correspondente** antes da criação das ofertas.
- Todas as ofertas regulares devem estar **sincronizadas** antes da criação da Oferta Unificada.
- Após a criação da Oferta Unificada, **não é possível** alterar a oferta base nem adicionar/remover ofertas vinculadas.