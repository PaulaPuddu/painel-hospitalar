# Painel Inteligente de Acesso Hospitalar

Painel interativo de análise do **Vazio Assistencial** no estado de São Paulo, desenvolvido como Challenge Oracle + FIAP — Turma 1TSCO.

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://painel-hospitalar-hvhm8xhtr23cjzzxufa9a.streamlit.app)

---

## Sobre o projeto

O **Vazio Assistencial** ocorre quando municípios não possuem oferta hospitalar suficiente, obrigando pacientes a se deslocar para outras cidades para se internar. Este painel transforma dados públicos do SIH/SUS, CNES e IBGE em informação visual acionável para gestores de saúde pública.

**Período analisado:** fevereiro, junho, agosto e dezembro de 2024  
**Abrangência:** Estado de São Paulo

---

## Painéis

| # | Painel | Descrição |
|---|--------|-----------|
| 1 | **Visão Geral** | KPIs macro, mapa geográfico dos municípios críticos e ranking dos maiores exportadores de pacientes |
| 2 | **Vazio Assistencial** | Fluxo origem-destino (Sankey), classificação dos municípios por criticidade e análise de evasão |
| 3 | **Perfil de Atendimento** | Diagnósticos (CID-10) que mais pressionam o sistema: volume, permanência média e custo |
| 4 | **Consultor de Dados IA** | Perguntas em linguagem natural respondidas com dados reais via Oracle Select AI |

### Filtros globais
Todos os painéis respondem aos mesmos filtros na barra lateral:
- **UF** — São Paulo (SP)
- **Município** — multiselect com todos os municípios com ≥ 100 internações
- **CID Grupo** — 22 capítulos do CID-10 em português

---

## Stack tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Interface | Streamlit (Python) |
| Banco de dados | Oracle Autonomous Database — Lakehouse (Always Free) |
| IA / NLP | Oracle Select AI + Cohere Command-R |
| Visualizações | Plotly (mapa, Sankey, barras) |
| Driver | python-oracledb (Thin mode + Oracle Wallet) |
| Cloud | Oracle Cloud Infrastructure — região `sa-saopaulo-1` |

---

## Fontes de dados

- **SIH/SUS** — Sistema de Informações Hospitalares do SUS (internações)
- **CNES** — Cadastro Nacional de Estabelecimentos de Saúde (hospitais)
- **IBGE 2022** — Estimativas populacionais por município

---

## Executar localmente

### Pré-requisitos
- Python 3.10+
- Oracle Wallet configurado na pasta `wallet/`
- Arquivo `.streamlit/secrets.toml` com as credenciais (ver abaixo)

### Instalação

```bash
pip install -r requirements.txt
```

### Configuração dos secrets

Crie o arquivo `.streamlit/secrets.toml`:

```toml
DB_USER = "seu_usuario"
DB_PASSWORD = "sua_senha"
DB_DSN = "seu_dsn"
WALLET_DIR = "wallet"
WALLET_PASSWORD = "sua_wallet_password"
```

### Executar

```bash
streamlit run painel_hospitalar.py
```

---

## Deploy

O app está publicado no **Streamlit Cloud** e conectado a este repositório. Qualquer push na branch `main` atualiza o app automaticamente.

---

## Equipe

**Challenge Oracle + FIAP · Turma 1TSCO · 2024**
