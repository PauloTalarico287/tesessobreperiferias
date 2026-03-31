"""
scraper.py — Coleta teses e dissertações do Catálogo de Teses da CAPES
sobre periferias urbanas e temas correlatos.
"""

import json
import time
import hashlib
import os
import requests
from datetime import datetime

# Termos de busca monitorados
SEARCH_TERMS = [
    "periferia",
    "periferias urbanas",
    "favela",
    "periferias",
]

# Arquivo de saída
OUTPUT_FILE = "docs/data.json"

# API do Catálogo de Teses da CAPES (endpoint de busca)
CAPES_API = "https://catalogodeteses.capes.gov.br/catalogo-teses/rest/busca"

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/json",
    "Origin": "https://catalogodeteses.capes.gov.br",
    "Referer": "https://catalogodeteses.capes.gov.br/",
    "User-Agent": "Mozilla/5.0 (compatible; PeriferiasWatch/1.0)",
}


def gerar_id(item: dict) -> str:
    """Gera um ID único baseado em título + autor."""
    chave = f"{item.get('tituloTese', '')}{item.get('autor', '')}"
    return hashlib.md5(chave.encode()).hexdigest()


def buscar_termo(termo: str, pagina: int = 1, tamanho: int = 20) -> dict:
    """Faz uma requisição à API da CAPES para um termo específico."""
    payload = {
        "query": termo,
        "filtros": [],
        "pagina": pagina,
        "tamanho": tamanho,
    }
    try:
        resp = requests.post(CAPES_API, headers=HEADERS, json=payload, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        print(f"  Erro ao buscar '{termo}' (página {pagina}): {e}")
        return {}


def formatar_trabalho(raw: dict, termo_origem: str) -> dict:
    """Converte o objeto da CAPES para o formato do site."""
    return {
        "id": gerar_id(raw),
        "titulo": raw.get("tituloTese", "Sem título"),
        "autor": raw.get("autor", "Autor desconhecido"),
        "orientador": raw.get("orientador", ""),
        "instituicao": raw.get("instituicao", ""),
        "programa": raw.get("nomePrograma", ""),
        "nivel": raw.get("nivelTese", ""),          # Mestrado / Doutorado
        "ano": raw.get("ano", ""),
        "area": raw.get("grandeArea", ""),
        "resumo": raw.get("resumo", ""),
        "palavras_chave": raw.get("palavrasChave", ""),
        "termo_origem": termo_origem,
        "biblioteca_url": raw.get("urlBibliotecaDigital", ""),
        "coletado_em": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def carregar_existentes() -> dict:
    """Carrega o JSON já salvo (se existir) e indexa por ID."""
    if not os.path.exists(OUTPUT_FILE):
        return {}
    with open(OUTPUT_FILE, encoding="utf-8") as f:
        dados = json.load(f)
    return {item["id"]: item for item in dados.get("trabalhos", [])}


def salvar(trabalhos: list, novos_ids: list):
    """Salva o JSON final com metadados de atualização."""
    os.makedirs("docs", exist_ok=True)
    saida = {
        "atualizado_em": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "total": len(trabalhos),
        "novos_nesta_coleta": len(novos_ids),
        "termos_monitorados": SEARCH_TERMS,
        "trabalhos": sorted(trabalhos, key=lambda x: str(x.get("ano", "")), reverse=True),
    }
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(saida, f, ensure_ascii=False, indent=2)
    print(f"\n✓ {len(trabalhos)} trabalhos salvos em '{OUTPUT_FILE}'")
    print(f"  → {len(novos_ids)} novos nesta coleta")


def coletar():
    print("=== Periferia Watch — Coleta CAPES ===")
    print(f"Termos: {SEARCH_TERMS}\n")

    existentes = carregar_existentes()
    todos = dict(existentes)  # id → trabalho
    novos_ids = []

    for termo in SEARCH_TERMS:
        print(f"🔍 Buscando: '{termo}'")
        pagina = 1
        total_paginas = 1  # será atualizado na primeira resposta

        while pagina <= total_paginas:
            dados = buscar_termo(termo, pagina=pagina)
            if not dados:
                break

            # A CAPES retorna o total de registros; calculamos as páginas
            total_registros = dados.get("totalDeRegistros", 0)
            tamanho = 20
            total_paginas = min((total_registros // tamanho) + 1, 5)  # máx 5 páginas / termo

            resultados = dados.get("teses", [])
            print(f"  Página {pagina}/{total_paginas} — {len(resultados)} resultados")

            for raw in resultados:
                trabalho = formatar_trabalho(raw, termo)
                wid = trabalho["id"]
                if wid not in todos:
                    todos[wid] = trabalho
                    novos_ids.append(wid)

            pagina += 1
            time.sleep(1)  # respeita o servidor

        time.sleep(2)

    salvar(list(todos.values()), novos_ids)


if __name__ == "__main__":
    coletar()
