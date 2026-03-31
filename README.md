# Periferia Watch 📚

Monitor automático de teses e dissertações sobre periferias urbanas, favelas e habitação popular no Brasil. Os dados são coletados semanalmente do [Catálogo de Teses e Dissertações da CAPES](https://catalogodeteses.capes.gov.br) e publicados como site estático no GitHub Pages.

## Como funciona

```
GitHub Actions (toda segunda-feira, 06h UTC)
    └── executa scripts/scraper.py
         └── consulta a API da CAPES
              └── salva resultados em docs/data.json
                   └── GitHub Pages publica o site automaticamente
```

## Termos monitorados

- periferia
- periferias urbanas
- favela
- periferias

## Como publicar o seu próprio

### 1. Fork este repositório

Clique em **Fork** no canto superior direito da página do GitHub.

### 2. Ative o GitHub Pages

Vá em **Settings → Pages** e configure:
- **Source:** `Deploy from a branch`
- **Branch:** `main` — pasta `/docs`

Clique em **Save**. Em alguns minutos seu site estará em:
```
https://<seu-usuario>.github.io/<nome-do-repositorio>/
```

### 3. Rode a primeira coleta manualmente

Vá em **Actions → Coleta Semanal — Periferia Watch → Run workflow**.

Aguarde alguns minutos — o scraper vai popular o `docs/data.json` com os trabalhos encontrados.

### 4. Personalize os termos de busca (opcional)

Edite o arquivo `scripts/scraper.py` e altere a lista `SEARCH_TERMS`:

```python
SEARCH_TERMS = [
    "periferia",
    "periferias urbanas",
    "favela",
    "periferias",
    # adicione outros termos aqui
]
```

## Estrutura do projeto

```
periferia-watch/
├── .github/
│   └── workflows/
│       └── coleta.yml       # Agendamento automático (GitHub Actions)
├── docs/
│   ├── index.html           # Site público (GitHub Pages)
│   └── data.json            # Dados coletados (atualizado automaticamente)
└── scripts/
    └── scraper.py           # Script de coleta da CAPES
```

## Requisitos para rodar localmente

```bash
pip install requests
python scripts/scraper.py
```

## Licença

MIT — use, adapte e compartilhe.
