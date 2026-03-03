import json

START_DATE = "2026-02-24"
END_DATE = "2026-03-30"


def carregar_json(nome_arquivo):
    with open(nome_arquivo, encoding="utf-8") as f:
        return json.load(f)


def gerar_ofertas():
    turma_alunos = carregar_json("json/turmas_estudantes_ids.json")
    escolas_docentes = carregar_json("json/escolas_docentes.json")
    escolas_itinerarios = carregar_json("json/escolas_itinerarios.json")
    escolas_turmas = carregar_json("json/escolas_turmas_filtrado.json")

    ofertas = []
    relatorio = {}

    for school_id, turmas in escolas_turmas.items():

        school_id_str = str(school_id)

        docentes = escolas_docentes.get(school_id_str, [])
        itinerarios = escolas_itinerarios.get(school_id_str, [])

        total_escola = 0
        total_unidades = sum(len(i["curricular_units"]) for i in itinerarios)

        for turma_id in turmas:

            alunos = turma_alunos.get(str(turma_id), [])

            for itinerario in itinerarios:
                itinerary_id = itinerario["itinerary_id"]

                for unidade in itinerario["curricular_units"]:

                    payload = {
                        "start_date": START_DATE,
                        "end_date": END_DATE,
                        "class_group": turma_id,
                        "itinerary": itinerary_id,
                        "curricular_unit": unidade,
                        "moderators": [],
                        "editor_teachers": docentes,
                        "students_people": alunos
                    }

                    ofertas.append(payload)
                    total_escola += 1

        relatorio[school_id] = {
            "turmas": len(turmas),
            "itinerarios": len(itinerarios),
            "total_unidades": total_unidades,
            "ofertas_geradas": total_escola
        }

    return ofertas, relatorio


def mostrar_relatorio(ofertas, relatorio):
    print("\n📊 RELATÓRIO POR ESCOLA\n")

    for escola, dados in relatorio.items():
        print(
            f"🏫 Escola {escola} → "
            f"{dados['turmas']} turmas × "
            f"{dados['itinerarios']} itinerários "
            f"(total unidades: {dados['total_unidades']}) "
            f"= {dados['ofertas_geradas']} ofertas"
        )

    print(f"\n🔥 TOTAL GERAL: {len(ofertas)} ofertas\n")


def salvar_ofertas(ofertas):
    with open("ofertas_payload.json", "w", encoding="utf-8") as f:
        json.dump(ofertas, f, indent=2)

    print("✅ Arquivo 'ofertas_payload.json' salvo com sucesso!")


if __name__ == "__main__":
    ofertas, relatorio = gerar_ofertas()
    mostrar_relatorio(ofertas, relatorio)
    salvar_ofertas(ofertas)