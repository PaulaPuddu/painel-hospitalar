"""
============================================================
 PAINEL INTELIGENTE DE ACESSO HOSPITALAR
 Vazio Assistencial — SP 2024  ·  Challenge Oracle + FIAP
============================================================
"""
import os
import requests
import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import oracledb

# ── PAGE CONFIG ─────────────────────────────────────────────
st.set_page_config(
    page_title="Painel Inteligente de Acesso Hospitalar",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── CSS — identidade visual do app.py, mantido integralmente ──
st.markdown("""
<style>
    /* ── SIDEBAR — Marrom café / Chocolate #2B221E */
    [data-testid="stSidebar"] {
        background-color: #2B221E !important;
        border-right: 1px solid rgba(255,255,255,0.06) !important;
    }
    [data-testid="stSidebar"] * { color: #C4B8A8 !important; }

    /* Itens de navegação — layout natural inline (ícone + texto na mesma linha) */
    [data-testid="stSidebar"] [data-testid="stRadio"] label {
        padding: 0.45rem 0.8rem 0.45rem 0.8rem !important;
        border-left: 3px solid transparent !important;
        border-radius: 0 !important;
        margin: 0 !important;
        font-size: 0.92rem !important;
        cursor: pointer;
        transition: color 0.15s, border-color 0.15s;
        align-items: center !important;
    }
    /* Cor do círculo de seleção — âmbar quando selecionado */
    [data-testid="stSidebar"] [data-testid="stRadio"] [data-baseweb="radio"] div {
        border-color: rgba(196,184,168,0.5) !important;
    }
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) [data-baseweb="radio"] div {
        border-color: #C98B32 !important;
        background: #C98B32 !important;
    }
    /* Item selecionado — barra âmbar + texto branco */
    [data-testid="stSidebar"] [data-testid="stRadio"] label:has(input:checked) {
        border-left: 3px solid #C98B32 !important;
        color: #F4F1EA !important;
        font-weight: 600 !important;
    }
    /* Hover */
    [data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
        color: #E8E2D4 !important;
        background: rgba(255,255,255,0.05) !important;
    }
    /* Divisória sutil na sidebar */
    [data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.08) !important; }

    [data-testid="stMetric"] {
        background-color: #E4DDD3; border-radius: 10px;
        padding: 1rem 1.2rem; border: 1px solid #CCC4B8;
    }
    [data-testid="stMetric"] label { font-size: 0.8rem !important; color: #5A6050 !important; }
    [data-testid="stMetricValue"] { font-size: 1.6rem !important; color: #1C241E !important; }

    /* ── HEADER — título direto no fundo, sem bloco */
    .main-header {
        padding: 0.4rem 0 1.3rem 0;
        margin-bottom: 0.5rem;
    }
    .main-header h1 {
        color: #F4F1EA !important; margin: 0;
        font-size: 2.8rem; font-weight: 700; letter-spacing: -0.02em; line-height: 1.1;
    }
    .main-header p  { color: #A8B09A !important; margin: 0.25rem 0 0; font-size: 0.88rem; }
    .badge-critico  { background:#A63A2B; color:#F4F1EA; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:600; }
    .badge-atencao  { background:#C98B32; color:#1C241E; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:600; }
    .badge-adequado { background:#2D7A4D; color:#F4F1EA; padding:3px 12px; border-radius:20px; font-size:0.78rem; font-weight:600; }
    .chat-box {
        background:#2B221E; color:#8DB87A; font-family: monospace;
        font-size:0.82rem; padding:1rem; border-radius:8px;
        white-space: pre-wrap; line-height: 1.6;
    }
    .ai-msg {
        background:#E4DDD3; border:1px solid #CCC4B8;
        border-radius:8px; padding:0.7rem 1rem; font-size:0.9rem; color:#1C241E;
    }
    .insight-box {
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(255,255,255,0.12);
        border-radius: 10px; padding: 1rem 1.2rem;
        font-size: 0.86rem; color: #F4F1EA; line-height: 1.75;
    }
    div[data-testid="column"] { padding: 0 0.3rem; }

    /* Botões de município na classificação — parecem linhas de texto clicáveis */
    .clf-btn button {
        background: transparent !important;
        border: none !important;
        border-bottom: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 0 !important;
        padding: 5px 2px !important;
        text-align: left !important;
        color: #F4F1EA !important;
        font-size: 0.83rem !important;
        font-weight: 400 !important;
        box-shadow: none !important;
    }
    .clf-btn button:hover {
        background: rgba(201,139,50,0.12) !important;
        color: #EDE8D4 !important;
    }

    /* Labels do Sankey — fonte fina, sem borda */
    .js-plotly-plot .plotly .sankey text,
    .js-plotly-plot .plotly text.node-label {
        fill: #E4DDD3 !important;
        font-weight: 400 !important;
        font-family: "Source Sans Pro", sans-serif !important;
    }

    /* Fundo principal — Verde-oliva escuro / Verde militar #3A4B40 */
    [data-testid="stMain"] { background-color: #3A4B40; }
    .block-container { background-color: transparent !important; }

    /* Textos nativos do Streamlit — Off-white suave #F4F1EA */
    [data-testid="stMain"] h1,
    [data-testid="stMain"] h2,
    [data-testid="stMain"] h3,
    [data-testid="stMain"] h4 { color: #F4F1EA !important; }
    [data-testid="stCaptionContainer"] p { color: #A8B09A !important; }
    [data-testid="stMarkdownContainer"] p { color: #F4F1EA; }

    /* ── Botões no conteúdo principal ── */
    [data-testid="stMain"] button {
        background-color: #2E3E32 !important;
        background:       #2E3E32 !important;
        color: #E4DDD3 !important;
        border: 1px solid rgba(196,184,168,0.35) !important;
        border-radius: 8px !important;
        font-size: 0.82rem !important;
        font-weight: 500 !important;
    }
    [data-testid="stMain"] button:hover {
        background-color: #3D5540 !important;
        background:       #3D5540 !important;
        border-color: #C98B32 !important;
        color: #F4F1EA !important;
    }
    /* Botão primário (▶ Perguntar) */
    [data-testid="stMain"] button[kind="primary"] {
        background-color: #C98B32 !important;
        background:       #C98B32 !important;
        color: #1C241E !important;
        border: none !important;
        font-weight: 700 !important;
    }
    [data-testid="stMain"] button[kind="primary"]:hover {
        background-color: #D99C42 !important;
        background:       #D99C42 !important;
    }
</style>
""", unsafe_allow_html=True)


# ── CONSTANTES ──────────────────────────────────────────────
PROFILE    = "PAINEL_APP_GENAI"
CORES_ZONA = {"Crítico": "#A63A2B", "Atenção": "#C98B32", "Adequado": "#2D7A4D"}


# ── CONEXÃO REAL ─────────────────────────────────────────────
@st.cache_resource
def get_connection():
    user       = st.secrets.get("DB_USER",        os.getenv("DB_USER"))
    password   = st.secrets.get("DB_PASSWORD",    os.getenv("DB_PASSWORD"))
    dsn        = st.secrets.get("DB_DSN",          os.getenv("DB_DSN"))
    wallet_dir = st.secrets.get("WALLET_DIR",      os.getenv("WALLET_DIR", "wallet"))
    wallet_pw  = st.secrets.get("WALLET_PASSWORD", os.getenv("WALLET_PASSWORD"))
    return oracledb.connect(
        user=user, password=password, dsn=dsn,
        config_dir=wallet_dir, wallet_location=wallet_dir, wallet_password=wallet_pw,
    )


def garantir_profile(conn):
    with conn.cursor() as cur:
        cur.execute(
            "SELECT COUNT(*) FROM user_cloud_ai_profiles WHERE profile_name = :1",
            [PROFILE],
        )
        if cur.fetchone()[0] == 0:
            cur.execute("""
                BEGIN DBMS_CLOUD_AI.CREATE_PROFILE(
                    profile_name => :pname,
                    attributes   => '{
                      "provider": "oci",
                      "credential_name": "OCI$RESOURCE_PRINCIPAL",
                      "region": "sa-saopaulo-1",
                      "model": "cohere.command-r-08-2024",
                      "oci_apiformat": "COHERE",
                      "object_list": [
                        {"owner":"ADMIN","name":"SIH_INTERNACOES"},
                        {"owner":"ADMIN","name":"POPULACAO_DADOS"},
                        {"owner":"ADMIN","name":"VW_VAZIO_ASSISTENCIAL"}
                      ]
                    }'
                ); END;
            """, pname=PROFILE)
        cur.execute("BEGIN DBMS_CLOUD_AI.SET_PROFILE(:1); END;", [PROFILE])
    conn.commit()


def perguntar_ai(conn, pergunta, action="runsql"):
    with conn.cursor() as cur:
        cur.execute("""
            SELECT DBMS_CLOUD_AI.GENERATE(
                prompt => :p, profile_name => :prof, action => :act
            ) FROM dual
        """, p=pergunta, prof=PROFILE, act=action)
        val = cur.fetchone()[0]
        return val.read() if hasattr(val, "read") else val


def sql_df(conn, sql):
    return pd.read_sql(sql, conn)


# ── QUERIES COM CACHE ────────────────────────────────────────

@st.cache_data(ttl=3600, show_spinner=False)
def load_kpis_dashboard(_conn):
    df = sql_df(_conn, """
        SELECT
          (SELECT COUNT(*) FROM sih_internacoes
            WHERE municipio_residencia LIKE '35%') AS total_internacoes,
          (SELECT ROUND(AVG(taxa_evasao_pct), 1)
             FROM vw_vazio_assistencial
            WHERE total_internacoes >= 100
              AND taxa_evasao_pct < 100
              AND cod_municipio LIKE '35%') AS media_evasao,
          (SELECT COUNT(*) FROM vw_vazio_assistencial
            WHERE taxa_evasao_pct >= 60
              AND total_internacoes >= 100
              AND cod_municipio LIKE '35%') AS municipios_criticos,
          (SELECT ROUND(AVG(taxa_evasao_pct), 1) FROM vw_vazio_assistencial
            WHERE taxa_evasao_pct >= 60
              AND total_internacoes >= 100
              AND cod_municipio LIKE '35%') AS media_evasao_criticos,
          (SELECT SUM(internou_fora) FROM vw_vazio_assistencial
            WHERE cod_municipio LIKE '35%'
              AND total_internacoes >= 100) AS pacientes_viajaram
        FROM dual
    """)
    # CNES: 384 hospitais mapeados (valor confirmado no CLAUDE.md).
    # A coleção JSON não tem SELECT concedido ao usuário painel_app.
    df["HOSPITAIS"] = 384
    return df


@st.cache_data(ttl=3600, show_spinner=False)
def load_vazio_dashboard(_conn):
    return sql_df(_conn, """
        SELECT cod_municipio, nome_municipio, populacao, total_internacoes,
               internou_fora, ROUND(taxa_evasao_pct, 1) AS taxa_evasao_pct
        FROM vw_vazio_assistencial
        WHERE total_internacoes >= 100
          AND taxa_evasao_pct < 100
          AND cod_municipio LIKE '35%'
    """)


@st.cache_data(ttl=86400, show_spinner=False)
def load_coords_sp():
    """
    Carrega centróides dos municípios de SP.
    Fonte: kelvins/municipios-brasileiros (GitHub) — CSV com lat/lng de todos
    os 5.570 municípios do Brasil, filtrado por codigo_uf=35 (SP).
    Retorna DataFrame com colunas: cod6 (6 dígitos), lat, lng.
    """
    try:
        url = (
            "https://raw.githubusercontent.com/kelvins/"
            "municipios-brasileiros/main/csv/municipios.csv"
        )
        df = pd.read_csv(url, dtype={"codigo_ibge": str})
        sp = df[df["codigo_uf"] == 35][["codigo_ibge", "latitude", "longitude"]].copy()
        sp["cod6"] = sp["codigo_ibge"].str[:6]
        sp = sp.rename(columns={"latitude": "lat", "longitude": "lng"})
        return sp[["cod6", "lat", "lng"]].reset_index(drop=True)
    except Exception:
        return pd.DataFrame(columns=["cod6", "lat", "lng"])


@st.cache_data(ttl=3600, show_spinner=False)
def load_kpis_vazio(_conn):
    return sql_df(_conn, """
        SELECT
          (SELECT COUNT(*) FROM vw_vazio_assistencial
            WHERE taxa_evasao_pct >= 60
              AND total_internacoes >= 100
              AND cod_municipio LIKE '35%') AS exportadores,
          (SELECT COUNT(*) FROM (
              SELECT municipio_hospital FROM sih_internacoes
              WHERE municipio_residencia <> municipio_hospital
                AND municipio_hospital LIKE '35%'
              GROUP BY municipio_hospital
              HAVING COUNT(*) >= 500)) AS polos_receptores
        FROM dual
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def load_fluxo_od(_conn):
    return sql_df(_conn, """
        SELECT cod_origem, nome_origem, cod_destino, nome_destino, qtd_pacientes
        FROM (
          SELECT s.municipio_residencia       AS cod_origem,
                 MAX(o.municipio)             AS nome_origem,
                 s.municipio_hospital         AS cod_destino,
                 MAX(d.municipio)             AS nome_destino,
                 COUNT(*)                     AS qtd_pacientes,
                 ROW_NUMBER() OVER (
                   PARTITION BY s.municipio_residencia
                   ORDER BY COUNT(*) DESC
                 ) AS rank_destino
          FROM sih_internacoes s
          LEFT JOIN populacao_dados o
            ON TO_CHAR(s.municipio_residencia) = SUBSTR(TO_CHAR(o.cod_municipio),1,6)
          LEFT JOIN populacao_dados d
            ON TO_CHAR(s.municipio_hospital)   = SUBSTR(TO_CHAR(d.cod_municipio),1,6)
          WHERE s.municipio_residencia <> s.municipio_hospital
            AND s.municipio_residencia LIKE '35%'
          GROUP BY s.municipio_residencia, s.municipio_hospital
        )
        WHERE rank_destino = 1 AND qtd_pacientes >= 50
        ORDER BY qtd_pacientes DESC
        FETCH FIRST 12 ROWS ONLY
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def load_classificacao(_conn):
    # Top 6 por bucket de classificação (até 18 no total), excluindo 100% de evasão
    return sql_df(_conn, """
        SELECT nome_municipio, total_internacoes, taxa_evasao_pct, classificacao
        FROM (
          SELECT nome_municipio,
                 total_internacoes,
                 ROUND(taxa_evasao_pct, 1) AS taxa_evasao_pct,
                 CASE
                   WHEN taxa_evasao_pct >= 60 AND total_internacoes >= 100
                     THEN 'Exportador crítico'
                   WHEN taxa_evasao_pct < 30
                     THEN 'Autossuficiente'
                   ELSE 'Intermediário'
                 END AS classificacao,
                 ROW_NUMBER() OVER (
                   PARTITION BY CASE
                     WHEN taxa_evasao_pct >= 60 AND total_internacoes >= 100 THEN 1
                     WHEN taxa_evasao_pct < 30 THEN 3
                     ELSE 2
                   END
                   ORDER BY taxa_evasao_pct DESC
                 ) AS rn
          FROM vw_vazio_assistencial
          WHERE cod_municipio LIKE '35%'
            AND total_internacoes >= 100
            AND taxa_evasao_pct < 100
        )
        WHERE rn <= 6
        ORDER BY taxa_evasao_pct DESC
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def load_cid_perfil(_conn):
    return sql_df(_conn, """
        SELECT cid_principal,
               COUNT(*)                        AS internacoes,
               ROUND(AVG(dias_permanencia), 1) AS permanencia_media,
               ROUND(SUM(valor_total))         AS custo_total
        FROM sih_internacoes
        WHERE uf = 'SP' AND cid_principal IS NOT NULL
        GROUP BY cid_principal
        ORDER BY internacoes DESC
        FETCH FIRST 50 ROWS ONLY
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def load_cid_perfil_cidades(_conn, cods=()):
    """Perfil CID filtrado por lista de códigos de município (6 dígitos)."""
    if not cods:
        return load_cid_perfil(_conn)
    in_clause = ",".join(f"'{str(c)[:6]}'" for c in cods)
    return sql_df(_conn, f"""
        SELECT cid_principal,
               COUNT(*)                        AS internacoes,
               ROUND(AVG(dias_permanencia), 1) AS permanencia_media,
               ROUND(SUM(valor_total))         AS custo_total
        FROM sih_internacoes
        WHERE cid_principal IS NOT NULL
          AND TO_CHAR(municipio_residencia) IN ({in_clause})
        GROUP BY cid_principal
        ORDER BY internacoes DESC
        FETCH FIRST 50 ROWS ONLY
    """)


def cid_para_capitulo(cid):
    if not cid or len(cid) < 3:
        return "Outros"
    letra = cid[0].upper()
    try:
        num = int(cid[1:3])
    except ValueError:
        return "Outros"
    if letra == "A" or letra == "B":
        return "Infecciosas e parasitárias"
    if letra == "C":
        return "Neoplasias (tumores)"
    if letra == "D":
        return "Neoplasias (tumores)" if num <= 48 else "Doenças do sangue"
    if letra == "E":
        return "Endócrino e metabólico"
    if letra == "F":
        return "Transtornos mentais"
    if letra == "G":
        return "Sistema nervoso"
    if letra == "H":
        return "Olho e anexos" if num <= 59 else "Ouvido"
    if letra == "I":
        return "Aparelho circulatório"
    if letra == "J":
        return "Aparelho respiratório"
    if letra == "K":
        return "Aparelho digestivo"
    if letra == "L":
        return "Pele e tecido subcutâneo"
    if letra == "M":
        return "Osteomuscular"
    if letra == "N":
        return "Geniturinário"
    if letra == "O":
        return "Gravidez e parto"
    if letra == "P":
        return "Perinatal"
    if letra == "Q":
        return "Malformações congênitas"
    if letra == "R":
        return "Sintomas e sinais"
    if letra == "S" or letra == "T":
        return "Lesões e causas externas"
    if letra == "V" or letra == "W" or letra == "X" or letra == "Y":
        return "Causas externas"
    if letra == "Z":
        return "Fatores que influenciam a saúde"
    return "Outros"


# ── Capítulo CID → condição SQL para cid_principal ──────────
_CAP_SQL = {
    "Infecciosas e parasitárias":
        "cid_principal LIKE 'A%' OR cid_principal LIKE 'B%'",
    "Neoplasias (tumores)":
        "cid_principal LIKE 'C%' OR "
        "(cid_principal LIKE 'D%' AND SUBSTR(cid_principal,2,2) <= '48')",
    "Doenças do sangue":
        "cid_principal LIKE 'D%' AND SUBSTR(cid_principal,2,2) > '48'",
    "Endócrino e metabólico":       "cid_principal LIKE 'E%'",
    "Transtornos mentais":          "cid_principal LIKE 'F%'",
    "Sistema nervoso":              "cid_principal LIKE 'G%'",
    "Olho e anexos":
        "cid_principal LIKE 'H%' AND SUBSTR(cid_principal,2,2) <= '59'",
    "Ouvido":
        "cid_principal LIKE 'H%' AND SUBSTR(cid_principal,2,2) > '59'",
    "Aparelho circulatório":        "cid_principal LIKE 'I%'",
    "Aparelho respiratório":        "cid_principal LIKE 'J%'",
    "Aparelho digestivo":           "cid_principal LIKE 'K%'",
    "Pele e tecido subcutâneo":     "cid_principal LIKE 'L%'",
    "Osteomuscular":                "cid_principal LIKE 'M%'",
    "Geniturinário":                "cid_principal LIKE 'N%'",
    "Gravidez e parto":             "cid_principal LIKE 'O%'",
    "Perinatal":                    "cid_principal LIKE 'P%'",
    "Malformações congênitas":      "cid_principal LIKE 'Q%'",
    "Sintomas e sinais":            "cid_principal LIKE 'R%'",
    "Lesões e causas externas":
        "cid_principal LIKE 'S%' OR cid_principal LIKE 'T%'",
    "Causas externas":
        "cid_principal LIKE 'V%' OR cid_principal LIKE 'W%' OR "
        "cid_principal LIKE 'X%' OR cid_principal LIKE 'Y%'",
    "Fatores que influenciam a saúde": "cid_principal LIKE 'Z%'",
}


def capitulos_to_sql(caps):
    """Lista de capítulos CID → fragmento SQL (OR) para WHERE cid_principal."""
    parts = [f"({_CAP_SQL[c]})" for c in caps if c in _CAP_SQL]
    return " OR ".join(parts) if parts else ""


@st.cache_data(ttl=3600, show_spinner=False)
def load_fluxo_od_cid(_conn, cid_filter="", cod_cidades=()):
    """Fluxo OD com filtro opcional de CID e/ou cidades (6 dígitos)."""
    extras = []
    if cid_filter:
        extras.append(f"({cid_filter})")
    if cod_cidades:
        in_cl = ",".join(f"'{c}'" for c in cod_cidades)
        extras.append(f"TO_CHAR(s.municipio_residencia) IN ({in_cl})")
    extra = ("AND " + " AND ".join(extras)) if extras else ""
    return sql_df(_conn, f"""
        SELECT cod_origem, nome_origem, cod_destino, nome_destino, qtd_pacientes
        FROM (
          SELECT s.municipio_residencia       AS cod_origem,
                 MAX(o.municipio)             AS nome_origem,
                 s.municipio_hospital         AS cod_destino,
                 MAX(d.municipio)             AS nome_destino,
                 COUNT(*)                     AS qtd_pacientes,
                 ROW_NUMBER() OVER (
                   PARTITION BY s.municipio_residencia
                   ORDER BY COUNT(*) DESC
                 ) AS rank_destino
          FROM sih_internacoes s
          LEFT JOIN populacao_dados o
            ON TO_CHAR(s.municipio_residencia) = SUBSTR(TO_CHAR(o.cod_municipio),1,6)
          LEFT JOIN populacao_dados d
            ON TO_CHAR(s.municipio_hospital)   = SUBSTR(TO_CHAR(d.cod_municipio),1,6)
          WHERE s.municipio_residencia <> s.municipio_hospital
            AND s.municipio_residencia LIKE '35%'
            {extra}
          GROUP BY s.municipio_residencia, s.municipio_hospital
        )
        WHERE rank_destino = 1 AND qtd_pacientes >= 10
        ORDER BY qtd_pacientes DESC
        FETCH FIRST 12 ROWS ONLY
    """)


@st.cache_data(ttl=3600, show_spinner=False)
def load_viajaram_cid(_conn, cid_filter="", cod_cidades=()):
    """Contagem de pacientes que viajaram, com filtros opcionais de CID e cidades."""
    extras = []
    if cid_filter:
        extras.append(f"({cid_filter})")
    if cod_cidades:
        in_cl = ",".join(f"'{c}'" for c in cod_cidades)
        extras.append(f"TO_CHAR(municipio_residencia) IN ({in_cl})")
    extra = ("AND " + " AND ".join(extras)) if extras else ""
    row = sql_df(_conn, f"""
        SELECT COUNT(*) AS viajaram
        FROM sih_internacoes
        WHERE municipio_residencia LIKE '35%'
          AND municipio_residencia <> municipio_hospital
          {extra}
    """)
    return int(row.iloc[0]["VIAJARAM"])


# ── INICIALIZA CONEXÃO ──────────────────────────────────────
try:
    conn = get_connection()
    garantir_profile(conn)
    conectado = True
except Exception as err:
    conectado = False
    conn = None


# ── SIDEBAR ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## Painel Hospitalar")
    st.markdown("---")
    pagina = st.radio(
        "Navegação",
        [
            "Visão Geral",
            "Vazio Assistencial",
            "Perfil de Atendimento",
            "Select AI",
        ],
        label_visibility="collapsed",
    )
    st.markdown("---")

    # ── Filtros ──────────────────────────────────────────────
    st.markdown(
        "<p style='font-size:0.75rem;font-weight:700;text-transform:uppercase;"
        "letter-spacing:.06em;color:#C4B8A8;margin-bottom:4px;'>Filtros</p>",
        unsafe_allow_html=True,
    )

    uf_sel = st.selectbox("UF", ["SP"], index=0, label_visibility="visible")

    # Carrega lista de municípios para o multiselect
    if "cidades_sp" not in st.session_state and conectado:
        try:
            df_cid = sql_df(conn,
                """SELECT DISTINCT nome_municipio
                   FROM vw_vazio_assistencial
                   WHERE cod_municipio LIKE '35%' AND total_internacoes >= 100
                   ORDER BY nome_municipio"""
            )
            st.session_state["cidades_sp"] = (
                df_cid["NOME_MUNICIPIO"].str.title().tolist()
            )
        except Exception:
            st.session_state["cidades_sp"] = []

    cidades_lista = st.session_state.get("cidades_sp", [])
    if "filtro_cidades" not in st.session_state:
        st.session_state["filtro_cidades"] = []
    cidades_sel = st.multiselect(
        "Município",
        options=cidades_lista,
        key="filtro_cidades",
        placeholder="Todos os municípios",
    )

    _CID_CAPITULOS = [
        "Aparelho circulatório", "Aparelho digestivo", "Aparelho respiratório",
        "Causas externas", "Doenças do sangue", "Endócrino e metabólico",
        "Fatores que influenciam a saúde", "Geniturinário", "Gravidez e parto",
        "Infecciosas e parasitárias", "Lesões e causas externas",
        "Malformações congênitas", "Neoplasias (tumores)", "Osteomuscular",
        "Ouvido", "Olho e anexos", "Perinatal", "Pele e tecido subcutâneo",
        "Sintomas e sinais", "Sistema nervoso", "Transtornos mentais", "Outros",
    ]
    if "filtro_cid" not in st.session_state:
        st.session_state["filtro_cid"] = []
    cid_sel = st.multiselect(
        "CID Grupo",
        options=_CID_CAPITULOS,
        key="filtro_cid",
        placeholder="Todos os grupos CID",
    )

    st.markdown("---")
    if conectado:
        st.success("Banco conectado")
    else:
        st.error("Sem conexão com o banco")
    st.markdown("---")
    st.markdown(
        "<small style='color:#A0C4D8'>Challenge Oracle + FIAP · 1TSCO<br>"
        "Fontes: SIH/SUS · CNES · IBGE</small>",
        unsafe_allow_html=True,
    )

if not conectado:
    st.error("Não foi possível conectar ao banco. Verifique as credenciais.")
    st.stop()


# ════════════════════════════════════════════════════════════
# PÁGINA 1 — VISÃO GERAL
# ════════════════════════════════════════════════════════════
if pagina == "Visão Geral":

    st.markdown("""<div class="main-header">
        <h1>Monitoramento de Internação</h1>
        <p>Visão geral do acesso hospitalar em São Paulo · 4 meses de 2024</p>
    </div>""", unsafe_allow_html=True)

    # ── 4 KPIs ──────────────────────────────────────────────
    try:
        with st.spinner("Carregando indicadores…"):
            kpi_global = load_kpis_dashboard(conn).iloc[0]
            df_vazio_kpi = load_vazio_dashboard(conn)

        # Se há filtro de cidade, recalcula KPIs sobre os dados filtrados
        if cidades_sel:
            df_f = df_vazio_kpi[
                df_vazio_kpi["NOME_MUNICIPIO"].str.title().isin(cidades_sel)
            ]
            total_int       = int(df_f["TOTAL_INTERNACOES"].sum())
            pacientes_viaj  = int(df_f["INTERNOU_FORA"].sum())
            criticos        = int((df_f["TAXA_EVASAO_PCT"] >= 60).sum())
            media_ev_crit   = df_f[df_f["TAXA_EVASAO_PCT"] >= 60]["TAXA_EVASAO_PCT"].mean()
            media_ev_crit   = float(media_ev_crit) if not pd.isna(media_ev_crit) else 0.0
            rodape_int      = f"{', '.join(cidades_sel[:2])}{'…' if len(cidades_sel)>2 else ''}"
        else:
            total_int      = int(kpi_global["TOTAL_INTERNACOES"])
            pacientes_viaj = int(kpi_global["PACIENTES_VIAJARAM"])
            criticos       = int(kpi_global["MUNICIPIOS_CRITICOS"])
            media_ev_crit  = float(kpi_global["MEDIA_EVASAO_CRITICOS"])
            rodape_int     = "SP · fev, jun, ago, dez 2024"

        def kpi_card(col, titulo, valor_html, rodape, accent):
            col.markdown(
                f"""<div style="background:#E4DDD3; border-left:5px solid {accent};
                    border-radius:10px; padding:1rem 1.2rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.25);
                    height:110px; display:flex; flex-direction:column; justify-content:space-between;">
                  <p style="font-size:0.75rem; color:{accent}; margin:0;
                     font-weight:700; text-transform:uppercase; letter-spacing:.04em;">{titulo}</p>
                  <div style="font-size:1.55rem; font-weight:700; color:#1C241E; line-height:1.1;">{valor_html}</div>
                  <p style="font-size:0.73rem; color:#6A7050; margin:0;">{rodape}</p>
                </div>""",
                unsafe_allow_html=True,
            )

        c1, c2, c3, c4 = st.columns(4)
        kpi_card(c1,
            titulo="Hospitais mapeados",
            valor_html="—" if cidades_sel else "384",
            rodape="Sem detalhe por cidade · CNES agregado SP" if cidades_sel else "Fonte: CNES · estabelecimentos SP",
            accent="#2D7A4D",
        )
        kpi_card(c2,
            titulo="Internações analisadas",
            valor_html=f"{total_int:,}".replace(",", "."),
            rodape=rodape_int,
            accent="#C98B32",
        )
        kpi_card(c3,
            titulo="Pacientes que viajaram",
            valor_html=f"{pacientes_viaj:,}".replace(",", "."),
            rodape="Internaram fora do próprio município",
            accent="#A63A2B",
        )
        kpi_card(c4,
            titulo="Municípios críticos",
            valor_html=(
                f"{criticos}"
                f"<span style='font-size:1rem;font-weight:500;margin-left:8px;color:#5A6850;'>"
                f"· {media_ev_crit:.1f}%</span>"
            ),
            rodape="Evasão ≥ 60% · precisam de investimento",
            accent="#5A6850",
        )
    except Exception as e:
        st.warning(f"Erro nos KPIs: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Mapa (esq) + Top 5 (dir) ────────────────────────────
    col_mapa, col_top5 = st.columns([1.5, 1])

    with col_mapa:
        st.markdown("#### Mapa do vazio assistencial — SP")
        try:
            with st.spinner("Carregando mapa…"):
                df_vazio = load_vazio_dashboard(conn)
                coords   = load_coords_sp()

            if coords.empty:
                st.info("Coordenadas indisponíveis. Verifique a conexão de rede.")
            else:
                df_vazio["COD6"] = df_vazio["COD_MUNICIPIO"].astype(str).str[:6]
                # Aplica filtro de município se selecionado
                if cidades_sel:
                    df_vazio = df_vazio[
                        df_vazio["NOME_MUNICIPIO"].str.title().isin(cidades_sel)
                    ]
                df_map = df_vazio.merge(
                    coords, left_on="COD6", right_on="cod6", how="inner"
                ).dropna(subset=["lat", "lng", "TOTAL_INTERNACOES"])

                if df_map.empty:
                    st.warning(
                        "Merge retornou 0 linhas. "
                        "Códigos do banco (amostra): " + str(df_vazio["COD6"].head(3).tolist()) +
                        " · Códigos IBGE (amostra): " + str(coords["cod6"].head(3).tolist())
                    )
                else:
                    df_map["zona"] = df_map["TAXA_EVASAO_PCT"].apply(
                        lambda x: "Crítico" if x >= 60 else ("Atenção" if x >= 30 else "Adequado")
                    )
                    size_max = st.slider(
                        "Tamanho das bolhas", min_value=5, max_value=40, value=15, step=5,
                    )

                    # Legenda de zonas — abaixo do slider
                    st.markdown(
                        "<div style='display:flex;gap:16px;align-items:center;"
                        "padding:0.35rem 0 0.6rem 0;flex-wrap:wrap;'>"
                        "<span class='badge-critico'>Crítico</span>"
                        "<span style='font-size:0.8rem;color:#C4BFA8;margin-right:6px;'>≥ 60%</span>"
                        "<span class='badge-atencao'>Atenção</span>"
                        "<span style='font-size:0.8rem;color:#C4BFA8;margin-right:6px;'>30–59%</span>"
                        "<span class='badge-adequado'>Adequado</span>"
                        "<span style='font-size:0.8rem;color:#C4BFA8;'>&lt; 30%</span>"
                        "</div>",
                        unsafe_allow_html=True,
                    )

                    df_map["tamanho"] = np.log1p(df_map["TOTAL_INTERNACOES"])
                    fig_mapa = px.scatter_mapbox(
                        df_map,
                        lat="lat", lon="lng",
                        size="tamanho",
                        color="zona",
                        color_discrete_map=CORES_ZONA,
                        hover_name="NOME_MUNICIPIO",
                        hover_data={
                            "lat": False, "lng": False, "tamanho": False,
                            "TOTAL_INTERNACOES": ":,",
                            "TAXA_EVASAO_PCT": ":.1f",
                            "POPULACAO": ":,",
                        },
                        size_max=size_max,
                        zoom=6.1,
                        center={"lat": -22.3, "lon": -48.5},
                        mapbox_style="carto-positron",
                        labels={
                            "zona":              "Zona",
                            "TOTAL_INTERNACOES": "Internações",
                            "TAXA_EVASAO_PCT":   "Evasão (%)",
                            "POPULACAO":         "População",
                        },
                    )
                    fig_mapa.update_layout(
                        height=490,
                        margin=dict(l=0, r=0, t=0, b=0),
                        showlegend=False,
                    )
                    st.plotly_chart(fig_mapa, use_container_width=True)
                    st.caption(
                        f"{len(df_map)} municípios · "
                        "Bolha = volume de internações · Cor = zona de evasão"
                    )
        except Exception as e:
            st.warning(f"Erro no mapa: {e}")

    with col_top5:
        st.markdown("<div style='margin-top:155px'></div>", unsafe_allow_html=True)
        st.markdown("#### Top 5 — maior evasão")
        try:
            df_todos = load_vazio_dashboard(conn)
            if cidades_sel:
                df_todos = df_todos[
                    df_todos["NOME_MUNICIPIO"].str.title().isin(cidades_sel)
                ]
            df_top5 = df_todos.head(5)
            for _, row in df_top5.iterrows():
                zona = (
                    "Crítico" if row["TAXA_EVASAO_PCT"] >= 60
                    else "Atenção" if row["TAXA_EVASAO_PCT"] >= 30
                    else "Adequado"
                )
                badge = (
                    "badge-critico" if zona == "Crítico"
                    else "badge-atencao" if zona == "Atenção"
                    else "badge-adequado"
                )
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;"
                    f"align-items:center;padding:6px 0;"
                    f"border-bottom:1px solid rgba(255,255,255,0.08);'>"
                    f"<span style='font-size:0.85rem;color:#F4F1EA;'>"
                    f"{row['NOME_MUNICIPIO']}</span>"
                    f"<span class='{badge}'>{row['TAXA_EVASAO_PCT']:.1f}%</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        except Exception as e:
            st.warning(f"Erro no ranking: {e}")

    # ── Contexto e Insights — ABAIXO do mapa ────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### Contexto e Insights")
    st.markdown("""
    <div class="insight-box">
    <b>O que é o Vazio Assistencial?</b><br>
    Municípios que não conseguem internar seus próprios moradores,
    obrigando-os a buscar atendimento em outras cidades — geralmente
    com maior custo e sofrimento para as famílias.<br><br>
    <b>Padrão identificado em SP:</b><br>
    &bull; Cidades da Grande SP dependem da capital:
    Guarulhos → São Paulo (2.317 pacientes) · Osasco → São Paulo (1.656) · Carapicuíba → São Paulo (813)<br>
    &bull; Polos regionais absorvem pacientes de dezenas de cidades:
    Santo André (58 cidades), Santos (29), Mogi das Cruzes (71), Catanduva (~90)<br><br>
    <i>Explore as próximas páginas para aprofundar a análise.</i>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# PÁGINA 2 — VAZIO ASSISTENCIAL
# ════════════════════════════════════════════════════════════
elif pagina == "Vazio Assistencial":

    st.markdown("""<div class="main-header">
        <h1>Vazio Assistencial</h1>
        <p>Quem exporta pacientes — e para onde eles vão? · SP 2024</p>
    </div>""", unsafe_allow_html=True)

    # ── 4 KPIs ──────────────────────────────────────────────
    try:
        with st.spinner("Carregando indicadores…"):
            kpi1_g      = load_kpis_dashboard(conn).iloc[0]
            kpi2_g      = load_kpis_vazio(conn).iloc[0]
            df_od_all   = load_fluxo_od(conn)
            df_vazio_p2 = load_vazio_dashboard(conn)

        cid_sql_p2  = capitulos_to_sql(cid_sel)
        _cods_p2    = ()

        if cidades_sel:
            df_f2 = df_vazio_p2[df_vazio_p2["NOME_MUNICIPIO"].str.title().isin(cidades_sel)]
            _cods_p2 = tuple(str(c)[:6] for c in df_f2["COD_MUNICIPIO"].tolist())
            if cid_sql_p2:
                viajaram_v     = load_viajaram_cid(conn, cid_filter=cid_sql_p2, cod_cidades=_cods_p2)
                exportadores_v = "—"
                polos_v        = "—"
            else:
                viajaram_v     = int(df_f2["INTERNOU_FORA"].sum())
                exportadores_v = int((df_f2["TAXA_EVASAO_PCT"] >= 60).sum())
                polos_v        = "—"
            rodape_viaj = f"Filtrado: {', '.join(cidades_sel[:2])}{'…' if len(cidades_sel)>2 else ''}"
        elif cid_sql_p2:
            viajaram_v     = load_viajaram_cid(conn, cid_filter=cid_sql_p2)
            exportadores_v = "—"
            polos_v        = "—"
            rodape_viaj    = f"CID: {', '.join(cid_sel[:2])}{'…' if len(cid_sel)>2 else ''}"
        else:
            viajaram_v     = int(kpi1_g["PACIENTES_VIAJARAM"])
            exportadores_v = int(kpi2_g["EXPORTADORES"])
            polos_v        = f"{int(kpi2_g['POLOS_RECEPTORES'])}"
            rodape_viaj    = "Internaram fora do próprio município"

        if cid_sql_p2 or _cods_p2:
            df_od = load_fluxo_od_cid(conn, cid_filter=cid_sql_p2, cod_cidades=_cods_p2)
        else:
            df_od = df_od_all

        maior_rota = "—"
        rota_rodape = ""
        if not df_od.empty:
            r = df_od.iloc[0]
            o = str(r["NOME_ORIGEM"]).title() if r["NOME_ORIGEM"] else "?"
            d = str(r["NOME_DESTINO"]).title() if r["NOME_DESTINO"] else "?"
            maior_rota  = f"{o} → {d}"
            rota_rodape = f"{int(r['QTD_PACIENTES']):,} pacientes · principal fluxo"

        def kpi_card(col, titulo, valor_html, rodape, accent):
            col.markdown(
                f"""<div style="background:#E4DDD3; border-left:5px solid {accent};
                    border-radius:10px; padding:1rem 1.2rem;
                    box-shadow:0 2px 8px rgba(0,0,0,0.25);
                    height:110px; display:flex; flex-direction:column; justify-content:space-between;">
                  <p style="font-size:0.75rem; color:{accent}; margin:0;
                     font-weight:700; text-transform:uppercase; letter-spacing:.04em;">{titulo}</p>
                  <div style="font-size:1.55rem; font-weight:700; color:#1C241E; line-height:1.1;">{valor_html}</div>
                  <p style="font-size:0.73rem; color:#6A7050; margin:0;">{rodape}</p>
                </div>""",
                unsafe_allow_html=True,
            )

        c1, c2, c3, c4 = st.columns(4)
        kpi_card(c1,
            titulo="Pacientes que viajaram",
            valor_html=f"{viajaram_v:,}".replace(",", "."),
            rodape=rodape_viaj,
            accent="#A63A2B",
        )
        kpi_card(c2,
            titulo="Municípios exportadores",
            valor_html=f"{exportadores_v}",
            rodape="Evasão ≥ 60% — precisam de investimento",
            accent="#5A6850",
        )
        kpi_card(c3,
            titulo="Polos receptores",
            valor_html=polos_v,
            rodape="Absorvem ≥ 500 pacientes de fora",
            accent="#2D7A4D",
        )
        kpi_card(c4,
            titulo="Maior rota de evasão",
            valor_html=f"<span style='font-size:1.1rem;'>{maior_rota}</span>",
            rodape=rota_rodape,
            accent="#C98B32",
        )
    except Exception as e:
        st.warning(f"Erro nos KPIs: {e}")

    st.markdown("<br>", unsafe_allow_html=True)

    col_sk, col_dir = st.columns([1.6, 1])

    # ── SANKEY ──────────────────────────────────────────────
    with col_sk:
        st.markdown("#### Fluxo de pacientes — origem → destino")
        try:
            if cid_sql_p2 or _cods_p2:
                df_od = load_fluxo_od_cid(conn, cid_filter=cid_sql_p2, cod_cidades=_cods_p2)
            else:
                df_od = load_fluxo_od(conn)
                if cidades_sel:
                    _mask = df_od["NOME_ORIGEM"].str.title().isin(cidades_sel)
                    df_od = df_od[_mask] if _mask.any() else df_od
            df_od = df_od.dropna(subset=["NOME_ORIGEM", "NOME_DESTINO"])

            origens  = df_od["NOME_ORIGEM"].str.title().tolist()
            destinos = df_od["NOME_DESTINO"].str.title().tolist()
            nos      = list(dict.fromkeys(origens + destinos))
            idx      = {n: i for i, n in enumerate(nos)}
            set_orig = set(origens)
            set_dest = set(destinos)

            cores_nos = []
            for no in nos:
                if no in set_orig and no not in set_dest:
                    cores_nos.append("#D35436")   # exportador puro — terracota/coral
                elif no in set_dest and no not in set_orig:
                    cores_nos.append("#3B6B55")   # polo puro — verde mar profundo
                else:
                    cores_nos.append("#C98B32")   # ambos — mostarda

            fig_sk = go.Figure(go.Sankey(
                arrangement="snap",
                node=dict(
                    pad=20, thickness=24,
                    line=dict(color="#1C241E", width=1.2),
                    label=nos,
                    color=cores_nos,
                    hovertemplate="%{label}<extra></extra>",
                ),
                link=dict(
                    source=[idx[o] for o in origens],
                    target=[idx[d] for d in destinos],
                    value=df_od["QTD_PACIENTES"].tolist(),
                    color="rgba(217,195,165,0.50)",
                    hovertemplate=(
                        "%{source.label} → %{target.label}<br>"
                        "Pacientes: %{value:,}<extra></extra>"
                    ),
                ),
            ))
            fig_sk.update_layout(
                paper_bgcolor="#2A3A2E",
                font=dict(color="#E4DDD3", size=12, family="Source Sans Pro, sans-serif"),
                height=520,
                margin=dict(l=10, r=10, t=10, b=10),
            )
            st.plotly_chart(fig_sk, use_container_width=True)
            st.caption(
                "🟥 Exportadores (terracota)  ·  🟩 Polos receptores (verde-mar)  ·  🟨 Ambos  ·  "
                f"Top {len(df_od)} fluxos principais"
            )
        except Exception as e:
            st.warning(f"Erro no Sankey: {e}")

    # ── DIREITA: Classificação + Insights ───────────────────
    with col_dir:

        # Classificação
        st.markdown("#### Classificação dos municípios")
        BADGE_MAP = {
            "Exportador crítico": "badge-critico",
            "Intermediário":      "badge-atencao",
            "Autossuficiente":    "badge-adequado",
        }
        try:
            df_class = load_classificacao(conn)
            if cidades_sel:
                df_class = df_class[df_class["NOME_MUNICIPIO"].str.title().isin(cidades_sel)]
            for _, row in df_class.iterrows():
                badge_cls = BADGE_MAP.get(row["CLASSIFICACAO"], "badge-atencao")
                st.markdown(
                    f"<div style='display:flex;justify-content:space-between;"
                    f"align-items:center;padding:5px 0;"
                    f"border-bottom:1px solid rgba(255,255,255,0.07);'>"
                    f"<span style='font-size:0.83rem;color:#F4F1EA'>"
                    f"{str(row['NOME_MUNICIPIO']).title()}</span>"
                    f"<span class='{badge_cls}'>{row['TAXA_EVASAO_PCT']:.0f}%</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )
        except Exception as e:
            st.warning(f"Erro na classificação: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Insights via Select AI narrate (fallback texto fixo)
        st.markdown("#### Contexto e Insights")
        try:
            with st.spinner("Gerando análise…"):
                narrativa = perguntar_ai(
                    conn,
                    "INSTRUÇÕES OBRIGATÓRIAS: responda EXCLUSIVAMENTE em português do Brasil. "
                    "Não escreva nenhuma palavra em inglês. "
                    "Em no máximo 4 frases curtas, resuma os principais padrões "
                    "de vazio assistencial em SP: quais municípios mais exportam "
                    "pacientes, para onde vão e o que isso significa para a saúde pública.",
                    action="narrate",
                )
            st.markdown(
                f"<div class='insight-box'>{narrativa}</div>",
                unsafe_allow_html=True,
            )
        except Exception:
            st.markdown("""
            <div class="insight-box">
            <b>O vazio assistencial em SP</b><br>
            Municípios da Grande SP — como Guarulhos, Osasco e Carapicuíba — dependem
            da capital para a maioria de suas internações. Polos regionais como Santo
            André, Santos e Mogi das Cruzes absorvem pacientes de dezenas de cidades
            menores, operando sob pressão crescente. Cidades que exportam pacientes
            geralmente carecem de estrutura hospitalar especializada, sinalizando onde
            o investimento público é mais urgente.
            </div>
            """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════
# PÁGINA 3 — PERFIL DE ATENDIMENTO
# ════════════════════════════════════════════════════════════
elif pagina == "Perfil de Atendimento":

    st.markdown("""<div class="main-header">
        <h1>Perfil de Atendimento</h1>
        <p>Quais diagnósticos pressionam o sistema hospitalar? · SP 2024</p>
    </div>""", unsafe_allow_html=True)

    # ── Processa dados CID ──────────────────────────────────
    try:
        with st.spinner("Carregando perfil de atendimento…"):
            if cidades_sel:
                _df_vz = load_vazio_dashboard(conn)
                _match  = _df_vz[_df_vz["NOME_MUNICIPIO"].str.title().isin(cidades_sel)]
                _cods   = tuple(str(c)[:6] for c in _match["COD_MUNICIPIO"].tolist())
                df_cid_raw = load_cid_perfil_cidades(conn, cods=_cods)
            else:
                df_cid_raw = load_cid_perfil(conn)

        df_cid_raw["CAPITULO"] = df_cid_raw["CID_PRINCIPAL"].apply(cid_para_capitulo)
        df_cap = (
            df_cid_raw.groupby("CAPITULO", as_index=False)
            .agg(
                INTERNACOES=("INTERNACOES", "sum"),
                PERMANENCIA_MEDIA=("PERMANENCIA_MEDIA", "mean"),
                CUSTO_TOTAL=("CUSTO_TOTAL", "sum"),
            )
            .sort_values("INTERNACOES", ascending=False)
        )
        df_cap["PERMANENCIA_MEDIA"] = df_cap["PERMANENCIA_MEDIA"].round(1)
        df_cap["CUSTO_TOTAL"] = df_cap["CUSTO_TOTAL"].round(0).astype(int)

        if cid_sel:
            df_cap = df_cap[df_cap["CAPITULO"].isin(cid_sel)].reset_index(drop=True)

        if df_cap.empty:
            st.info("Nenhum dado para os grupos CID selecionados.")
        else:
            top_cap   = df_cap.iloc[0]
            max_perm  = df_cap.loc[df_cap["PERMANENCIA_MEDIA"].idxmax()]
            max_custo = df_cap.loc[df_cap["CUSTO_TOTAL"].idxmax()]

            # ── 3 KPI cards ────────────────────────────────────
            def kpi_card(col, titulo, valor_html, rodape, accent):
                col.markdown(
                    f"""<div style="background:#E4DDD3; border-left:5px solid {accent};
                        border-radius:10px; padding:1rem 1.2rem;
                        box-shadow:0 2px 8px rgba(0,0,0,0.25);
                        height:110px; display:flex; flex-direction:column; justify-content:space-between;">
                      <p style="font-size:0.75rem; color:{accent}; margin:0;
                         font-weight:700; text-transform:uppercase; letter-spacing:.04em;">{titulo}</p>
                      <div style="font-size:1.35rem; font-weight:700; color:#1C241E; line-height:1.2;">{valor_html}</div>
                      <p style="font-size:0.73rem; color:#6A7050; margin:0;">{rodape}</p>
                    </div>""",
                    unsafe_allow_html=True,
                )

            c1, c2, c3 = st.columns(3)
            kpi_card(c1,
                titulo="CID Grupo mais internado",
                valor_html=f"<span style='font-size:1.05rem;'>{top_cap['CAPITULO']}</span>",
                rodape=f"{int(top_cap['INTERNACOES']):,} internações".replace(",", "."),
                accent="#2D7A4D",
            )
            perm_val = float(max_perm.get("PERMANENCIA_MEDIA", 0))
            perm_cap = str(max_perm.get("CAPITULO", ""))
            kpi_card(c2,
                titulo="Maior permanência média",
                valor_html=f"{perm_val:.1f} dias",
                rodape=perm_cap,
                accent="#C98B32",
            )
            custo_val = int(max_custo.get("CUSTO_TOTAL", 0))
            custo_cap = str(max_custo.get("CAPITULO", ""))
            kpi_card(c3,
                titulo="Maior custo total",
                valor_html=f"R$ {custo_val:,}".replace(",", "."),
                rodape=custo_cap,
                accent="#5A6850",
            )

            st.markdown("<br>", unsafe_allow_html=True)

            col_bar, col_tab = st.columns([1.3, 1])

            # ── Gráfico de barras horizontais ──────────────────
            with col_bar:
                st.markdown("#### Internações por CID Grupo")
                df_plot = df_cap.head(15).sort_values("INTERNACOES")
                fig_bar = px.bar(
                    df_plot,
                    x="INTERNACOES",
                    y="CAPITULO",
                    orientation="h",
                    color="INTERNACOES",
                    color_continuous_scale=["#2D7A4D", "#C98B32", "#A63A2B"],
                    labels={"INTERNACOES": "Internações", "CAPITULO": ""},
                    text="INTERNACOES",
                )
                fig_bar.update_traces(
                    texttemplate="%{x:,}",
                    textposition="outside",
                    textfont=dict(color="#DDD8C4", size=11),
                )
                fig_bar.update_layout(
                    paper_bgcolor="#3A4B40",
                    plot_bgcolor="#3A4B40",
                    font=dict(color="#DDD8C4"),
                    coloraxis_showscale=False,
                    height=520,
                    margin=dict(l=10, r=60, t=10, b=10),
                    xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                    yaxis=dict(tickfont=dict(size=12, color="#F4F1EA")),
                )
                st.plotly_chart(fig_bar, use_container_width=True)

            # ── Tabela + insight ───────────────────────────────
            with col_tab:
                st.markdown("#### Permanência e Custo")
                df_tab = df_cap[["CAPITULO", "PERMANENCIA_MEDIA", "CUSTO_TOTAL"]].copy()
                df_tab.columns = ["Capítulo", "Perm. média (dias)", "Custo total (R$)"]
                df_tab["Custo total (R$)"] = df_tab["Custo total (R$)"].apply(
                    lambda v: f"R$ {int(v):,}".replace(",", ".")
                )
                st.dataframe(
                    df_tab.reset_index(drop=True),
                    use_container_width=True,
                    height=360,
                    hide_index=True,
                )

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown("#### Conexão com o Vazio Assistencial")
                st.markdown(
                    """<div class="insight-box">
                    <b>Volume alto ≠ custo alto</b><br>
                    Gravidez e parto concentram o maior volume de internações, mas com
                    permanência curta e custo unitário baixo. Já neoplasias e doenças do
                    aparelho circulatório representam menos internações, porém com
                    permanência prolongada e custo elevado.<br><br>
                    <b>Ponte com o vazio:</b> municípios que exportam pacientes tendem a
                    transferir justamente casos de alta complexidade — cirurgias,
                    quimioterapia, cardiologia — que exigem estrutura especializada.
                    Isso confirma que o vazio assistencial não é uniforme: é seletivo nos
                    procedimentos que mais pesam no sistema.
                    </div>""",
                    unsafe_allow_html=True,
                )

    except Exception as e:
        st.error(f"Erro ao carregar perfil de atendimento: {e}")


# ════════════════════════════════════════════════════════════
# PÁGINA 4 — SELECT AI
# ════════════════════════════════════════════════════════════
elif pagina == "Select AI":

    st.markdown("""<div class="main-header">
        <h1>Consultor de Dados IA</h1>
        <p>Perguntas em português respondidas com dados reais do SIH/SUS · Oracle Select AI</p>
    </div>""", unsafe_allow_html=True)

    SUGESTOES = [
        "Quais municípios mais enviam pacientes para fora?",
        "Quais municípios com mais de 50 mil habitantes têm maior evasão?",
        "Qual a permanência média por município?",
        "Quais são os principais destinos de Guarulhos?",
        "Qual o custo médio por internação em cada município?",
        "Quais municípios têm mais de 70% de evasão?",
    ]

    # ── Sugestões clicáveis ─────────────────────────────────
    st.markdown("#### Sugestões de perguntas")
    cols_sug = st.columns(3)
    for i, sug in enumerate(SUGESTOES):
        if cols_sug[i % 3].button(sug, key=f"sug_{i}", use_container_width=True):
            st.session_state["pergunta_ai"] = sug
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Caixa de pergunta ───────────────────────────────────
    pergunta = st.text_area(
        "Sua pergunta",
        value=st.session_state.get("pergunta_ai", ""),
        placeholder="Ex.: Quais municípios têm taxa de evasão acima de 60%?",
        height=80,
        label_visibility="collapsed",
    )

    col_btn, col_clear = st.columns([1, 5])
    executar = col_btn.button("▶ Perguntar", type="primary", use_container_width=True)
    if col_clear.button("Limpar", use_container_width=False):
        for _k in ["pergunta_ai", "ai_sql", "ai_resultado", "ai_narrativa", "ai_resultado_erro"]:
            st.session_state.pop(_k, None)
        st.rerun()

    if executar and pergunta.strip():
        st.session_state["pergunta_ai"] = pergunta
        for _k in ["ai_sql", "ai_resultado", "ai_narrativa", "ai_resultado_erro"]:
            st.session_state.pop(_k, None)

        with st.status("Processando sua pergunta…", expanded=True) as _status:
            st.write("🔍  Interpretando pergunta e gerando SQL…")
            try:
                st.session_state["ai_sql"] = perguntar_ai(conn, pergunta, action="showsql")
                st.write("✅  SQL gerado")
            except Exception as _e:
                st.session_state["ai_sql"] = f"-- Erro: {_e}"
                st.write(f"⚠️  Erro ao gerar SQL: {_e}")

            st.write("⚙️  Executando consulta no banco de dados…")
            try:
                st.session_state["ai_resultado"] = perguntar_ai(conn, pergunta, action="runsql")
                st.write("✅  Dados obtidos")
            except Exception as _e:
                st.session_state["ai_resultado"] = None
                st.session_state["ai_resultado_erro"] = str(_e)
                st.write(f"⚠️  Erro na execução: {_e}")

            st.write("📝  Gerando análise em português…")
            try:
                _prompt_pt = (
                    "INSTRUÇÕES OBRIGATÓRIAS: responda EXCLUSIVAMENTE em português do Brasil. "
                    "Não escreva nenhuma palavra em inglês. Use linguagem clara e direta. "
                    f"Pergunta: {pergunta}"
                )
                st.session_state["ai_narrativa"] = perguntar_ai(conn, _prompt_pt, action="narrate")
                st.write("✅  Análise concluída")
            except Exception as _e:
                st.session_state["ai_narrativa"] = None
                st.write(f"⚠️  Análise indisponível: {_e}")

            _status.update(label="Consulta finalizada!", state="complete", expanded=False)

    # ── Resultados ──────────────────────────────────────────
    if st.session_state.get("ai_sql"):
        st.markdown("<br>", unsafe_allow_html=True)

        # ── Resposta em português ────────────────────────────
        narrativa = st.session_state.get("ai_narrativa")
        if narrativa:
            st.markdown("#### Resposta")
            st.markdown(
                f"<div class='insight-box' style='font-size:0.92rem;line-height:1.8;'>"
                f"{narrativa}</div>",
                unsafe_allow_html=True,
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # ── Botões de exportação ─────────────────────────────
        st.markdown(
            "<p style='font-size:0.73rem;font-weight:700;text-transform:uppercase;"
            "letter-spacing:.06em;color:#A8B09A;margin-bottom:6px;'>Exportar resultado</p>",
            unsafe_allow_html=True,
        )
        _e1, _e2, _e3, _ = st.columns([1, 1, 1, 4])
        if _e1.button("📄  PDF",     key="exp_pdf",   use_container_width=True):
            st.toast("Exportação em PDF disponível em breve", icon="ℹ️")
        if _e2.button("⬇  CSV",      key="exp_csv",   use_container_width=True):
            st.toast("Exportação em CSV disponível em breve", icon="ℹ️")
        if _e3.button("📊  Gráfico", key="exp_chart", use_container_width=True):
            st.toast("Geração de gráfico disponível em breve", icon="ℹ️")

        if st.session_state.get("ai_resultado_erro"):
            st.warning(f"Erro na execução: {st.session_state['ai_resultado_erro']}")
