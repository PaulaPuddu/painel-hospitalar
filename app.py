import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import random


st.set_page_config(
    page_title="Painel Inteligente de Acesso Hospitalar",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)


st.markdown("""
<style>
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #0A3D55;
    }
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stRadio label {
        color: #A0C4D8 !important;
        font-size: 0.85rem;
    }

    /* Metric cards */
    [data-testid="stMetric"] {
        background-color: #F4FAFB;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        border: 1px solid #E2ECF0;
    }
    [data-testid="stMetric"] label {
        font-size: 0.8rem !important;
        color: #64748B !important;
    }
    [data-testid="stMetricValue"] {
        font-size: 1.6rem !important;
        color: #0A3D55 !important;
    }

    /* Cabeçalho principal */
    .main-header {
        background: linear-gradient(90deg, #0A3D55, #0D6E8A);
        color: white;
        padding: 1.2rem 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .main-header h1 { color: white; margin: 0; font-size: 1.4rem; }
    .main-header p  { color: #A0D4E8; margin: 0.2rem 0 0; font-size: 0.85rem; }

    /* Badge de status */
    .badge-critico  { background:#FAECE7; color:#993C1D; padding:3px 10px; border-radius:20px; font-size:0.78rem; }
    .badge-atencao  { background:#FAEEDA; color:#854F0B; padding:3px 10px; border-radius:20px; font-size:0.78rem; }
    .badge-adequado { background:#E1F5EE; color:#0F6E56; padding:3px 10px; border-radius:20px; font-size:0.78rem; }

    /* Chat Select AI */
    .chat-box {
        background:#0A3D55; color:#5DCAA5;
        font-family: monospace; font-size:0.82rem;
        padding:1rem; border-radius:8px;
        white-space: pre-wrap; line-height: 1.6;
    }
    .user-msg {
        background:#EEF4F8; border-radius:8px;
        padding:0.7rem 1rem; margin-bottom:0.5rem;
        font-size:0.9rem; color:#1E293B;
    }
    .ai-msg {
        background:#F4FAFB; border:1px solid #E2ECF0;
        border-radius:8px; padding:0.7rem 1rem;
        font-size:0.9rem; color:#1E293B;
    }
    div[data-testid="column"] { padding: 0 0.3rem; }
</style>
""", unsafe_allow_html=True)


random.seed(42)

municipios_sp = [
    "São Paulo","Campinas","Guarulhos","Santo André","Ribeirão Preto",
    "Sorocaba","São Bernardo do Campo","Santos","Mogi das Cruzes","Osasco",
    "São José dos Campos","Jundiaí","Piracicaba","Bauru","Carapicuíba"
]
municipios_rj = [
    "Rio de Janeiro","Niterói","Duque de Caxias","Nova Iguaçu","Belford Roxo",
    "São Gonçalo","Petrópolis","Campos dos Goytacazes","Volta Redonda","Macaé"
]

@st.cache_data
def gerar_dados():
    dados = []
    for m in municipios_sp:
        pop = random.randint(80_000, 12_000_000)
        intern = int(pop * random.uniform(0.028, 0.095))
        hosp   = max(1, int(pop / 200_000) + random.randint(0, 3))
        pc     = round(intern / pop * 1000, 2)
        zona   = "Crítico" if pc > 7 else ("Atenção" if pc > 5 else "Adequado")
        dados.append({"Município":m,"Estado":"SP","População":pop,
                       "Internações":intern,"Hospitais":hosp,
                       "Per capita (‰)":pc,"Zona":zona})
    for m in municipios_rj:
        pop = random.randint(60_000, 6_700_000)
        intern = int(pop * random.uniform(0.025, 0.088))
        hosp   = max(1, int(pop / 200_000) + random.randint(0, 2))
        pc     = round(intern / pop * 1000, 2)
        zona   = "Crítico" if pc > 7 else ("Atenção" if pc > 5 else "Adequado")
        dados.append({"Município":m,"Estado":"RJ","População":pop,
                       "Internações":intern,"Hospitais":hosp,
                       "Per capita (‰)":pc,"Zona":zona})
    return pd.DataFrame(dados).sort_values("Per capita (‰)", ascending=False)

df = gerar_dados()

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🏥 Painel Hospitalar")
    st.markdown("---")
    pagina = st.radio(
        "Navegação",
        ["📊 Dashboard", "🔍 Análise por Região", "🤖 Select AI", "🏨 Estabelecimentos"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("**Filtros globais**")
    estado_filtro = st.multiselect(
        "Estado", ["SP", "RJ"], default=["SP", "RJ"],
        key="estado_global"
    )
    st.markdown("---")
    st.markdown(
        "<small style='color:#A0C4D8'>Challenge Oracle + FIAP · 1TSCO<br>"
        "Fontes: SIH/SUS · CNES · IBGE</small>",
        unsafe_allow_html=True
    )

df_f = df[df["Estado"].isin(estado_filtro)] if estado_filtro else df


if pagina == "📊 Dashboard":

    st.markdown("""
    <div class="main-header">
        <h1>📊 Dashboard Principal</h1>
        <p>Visão geral do acesso hospitalar — SP + RJ · 1º semestre de 2024</p>
    </div>
    """, unsafe_allow_html=True)

    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total de internações", f"{df_f['Internações'].sum():,.0f}".replace(",", "."))
    with col2:
        criticos = len(df_f[df_f["Zona"] == "Crítico"])
        st.metric("Municípios críticos", criticos, delta=f"de {len(df_f)} analisados", delta_color="inverse")
    with col3:
        st.metric("Hospitais mapeados", f"{df_f['Hospitais'].sum()}", help="Fonte: CNES")
    with col4:
        st.metric("Municípios analisados", len(df_f), help="Fonte: IBGE")

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([2, 1])

    with col_a:
        st.markdown("#### Internações por município (top 15)")
        top15 = df_f.nlargest(15, "Internações")
        cores = {"Crítico": "#D85A30", "Atenção": "#EF9F27", "Adequado": "#1D9E75"}
        fig = px.bar(
            top15, x="Internações", y="Município",
            orientation="h", color="Zona",
            color_discrete_map=cores,
            template="plotly_white", height=400
        )
        fig.update_layout(
            legend_title="Zona",
            plot_bgcolor="white",
            yaxis=dict(autorange="reversed"),
            margin=dict(l=0, r=0, t=10, b=0)
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_b:
        st.markdown("#### Distribuição por zona")
        zona_count = df_f["Zona"].value_counts().reset_index()
        zona_count.columns = ["Zona", "Qtd"]
        fig2 = px.pie(
            zona_count, values="Qtd", names="Zona",
            color="Zona", color_discrete_map=cores,
            template="plotly_white", height=220, hole=0.45
        )
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title="")
        st.plotly_chart(fig2, use_container_width=True)

        st.markdown("#### Top 5 — pressão hospitalar")
        top5 = df_f.nlargest(5, "Per capita (‰)")[["Município", "Per capita (‰)", "Zona"]]
        for _, row in top5.iterrows():
            badge_class = "badge-critico" if row["Zona"] == "Crítico" else \
                          "badge-atencao" if row["Zona"] == "Atenção" else "badge-adequado"
            st.markdown(
                f"<div style='display:flex;justify-content:space-between;align-items:center;"
                f"padding:6px 0;border-bottom:1px solid #eee;'>"
                f"<span style='font-size:0.88rem;color:#1E293B'>{row['Município']}</span>"
                f"<span class='{badge_class}'>{row['Per capita (‰)']}‰</span></div>",
                unsafe_allow_html=True
            )

elif pagina == "🔍 Análise por Região":

    st.markdown("""
    <div class="main-header">
        <h1>🔍 Análise por Região</h1>
        <p>Explore os indicadores por estado e município</p>
    </div>
    """, unsafe_allow_html=True)

    col_f1, col_f2, col_f3 = st.columns(3)
    with col_f1:
        estado_sel = st.selectbox("Estado", ["Todos", "SP", "RJ"])
    with col_f2:
        zona_sel = st.selectbox("Zona", ["Todas", "Crítico", "Atenção", "Adequado"])
    with col_f3:
        top_n = st.slider("Exibir top N municípios", 5, 25, 10)

    df_reg = df_f.copy()
    if estado_sel != "Todos":
        df_reg = df_reg[df_reg["Estado"] == estado_sel]
    if zona_sel != "Todas":
        df_reg = df_reg[df_reg["Zona"] == zona_sel]

    df_reg = df_reg.nlargest(top_n, "Per capita (‰)")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"#### Per capita por município (top {top_n})")
        cores = {"Crítico": "#D85A30", "Atenção": "#EF9F27", "Adequado": "#1D9E75"}
        fig = px.bar(
            df_reg.sort_values("Per capita (‰)"),
            x="Per capita (‰)", y="Município",
            orientation="h", color="Zona",
            color_discrete_map=cores,
            template="plotly_white", height=420
        )
        fig.update_layout(
            margin=dict(l=0, r=0, t=10, b=0),
            legend_title="Zona", yaxis_title=""
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown("#### Relação população × internações")
        fig2 = px.scatter(
            df_reg, x="População", y="Internações",
            color="Zona", color_discrete_map=cores,
            size="Hospitais", hover_name="Município",
            template="plotly_white", height=420
        )
        fig2.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title="Zona")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Tabela detalhada")
    df_show = df_reg.copy()
    df_show["População"] = df_show["População"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    df_show["Internações"] = df_show["Internações"].apply(lambda x: f"{x:,.0f}".replace(",", "."))
    st.dataframe(
        df_show[["Município", "Estado", "População", "Internações", "Hospitais", "Per capita (‰)", "Zona"]],
        use_container_width=True, hide_index=True
    )

elif pagina == "🤖 Select AI":

    st.markdown("""
    <div class="main-header">
        <h1>🤖 Oracle Select AI</h1>
        <p>Faça perguntas em português — o sistema gera o SQL automaticamente</p>
    </div>
    """, unsafe_allow_html=True)

    respostas = {
        "Quais municípios de SP têm maior pressão hospitalar?": {
            "sql": """SELECT m.nome_municipio,
       COUNT(*) AS internacoes,
       ROUND(COUNT(*) / p.populacao * 1000, 2) AS per_capita
FROM   internacoes i
JOIN   municipios  m ON i.id_municipio = m.id
JOIN   populacao   p ON m.id = p.id_municipio
WHERE  m.estado = 'SP'
ORDER  BY per_capita DESC
FETCH  FIRST 10 ROWS ONLY""",
            "dados": df[df["Estado"] == "SP"].nlargest(5, "Per capita (‰)")[
                ["Município", "Internações", "Per capita (‰)", "Zona"]
            ]
        },
        "Quais regiões têm menos hospitais por habitante?": {
            "sql": """SELECT m.nome_municipio,
       COUNT(e.id) AS hospitais,
       ROUND(p.populacao / NULLIF(COUNT(e.id), 0)) AS hab_por_hospital
FROM   municipios      m
JOIN   estabelecimentos e ON e.id_municipio = m.id
JOIN   populacao        p ON p.id_municipio = m.id
WHERE  e.tipo = 'HOSPITAL'
GROUP  BY m.nome_municipio, p.populacao
ORDER  BY hab_por_hospital DESC
FETCH  FIRST 10 ROWS ONLY""",
            "dados": df.nsmallest(5, "Hospitais")[["Município", "Estado", "Hospitais", "População"]]
        },
        "Quantas internações aconteceram em SP no 1º semestre de 2024?": {
            "sql": """SELECT estado,
       SUM(total_internacoes)  AS total,
       ROUND(AVG(per_capita), 2) AS media_per_capita
FROM   vw_indicadores_regionais
WHERE  estado   = 'SP'
  AND  periodo  = '2024-S1'
GROUP  BY estado""",
            "dados": df[df["Estado"] == "SP"][["Município", "Internações"]].head(5)
        },
    }

    st.markdown("**Sugestões de perguntas:**")
    cols = st.columns(3)
    perguntas = list(respostas.keys())
    pergunta_selecionada = None
    for i, p in enumerate(perguntas):
        with cols[i]:
            if st.button(p, use_container_width=True, key=f"btn_{i}"):
                st.session_state["pergunta_ai"] = p

    st.markdown("---")
    pergunta_input = st.text_input(
        "Digite sua pergunta:",
        value=st.session_state.get("pergunta_ai", ""),
        placeholder="Ex: Quais municípios de SP têm maior pressão hospitalar?"
    )

    if pergunta_input:
        match = None
        for chave in respostas:
            if any(w in pergunta_input.lower() for w in chave.lower().split()[:3]):
                match = chave
                break

        if match:
            resp = respostas[match]
            col_sql, col_res = st.columns(2)
            with col_sql:
                st.markdown("**SQL gerado automaticamente:**")
                st.markdown(
                    f"<div class='chat-box'>{resp['sql']}</div>",
                    unsafe_allow_html=True
                )
            with col_res:
                st.markdown("**Resultado:**")
                st.dataframe(resp["dados"], use_container_width=True, hide_index=True)

            st.success("✅ Consulta executada via Oracle Select AI — Oracle Autonomous DB Lakehouse")
        else:
            st.info("💡 No protótipo, use uma das sugestões acima. Na versão final, qualquer pergunta será respondida via Oracle Select AI conectado ao banco real.")


elif pagina == "🏨 Estabelecimentos":

    st.markdown("""
    <div class="main-header">
        <h1>🏨 Estabelecimentos de Saúde</h1>
        <p>Dados do CNES — 10.000+ estabelecimentos mapeados</p>
    </div>
    """, unsafe_allow_html=True)

    hospitais = [
        {"Nome": "Hospital das Clínicas de SP", "Município": "São Paulo", "Estado": "SP",
         "Tipo": "Hospital Geral", "Leitos SUS": 2200, "Internações": 18420,
         "CNES": "2077485", "Zona": "Crítico"},
        {"Nome": "UNICAMP Hospital de Clínicas", "Município": "Campinas", "Estado": "SP",
         "Tipo": "Hospital Universitário", "Leitos SUS": 390, "Internações": 6840,
         "CNES": "2077220", "Zona": "Crítico"},
        {"Nome": "Hospital Estadual Mario Covas", "Município": "Santo André", "Estado": "SP",
         "Tipo": "Hospital Geral", "Leitos SUS": 270, "Internações": 4120,
         "CNES": "2078100", "Zona": "Atenção"},
        {"Nome": "Hospital Geral de Bonsucesso", "Município": "Rio de Janeiro", "Estado": "RJ",
         "Tipo": "Hospital Geral", "Leitos SUS": 523, "Internações": 9810,
         "CNES": "2269456", "Zona": "Crítico"},
        {"Nome": "Hospital Universitário Pedro Ernesto", "Município": "Rio de Janeiro", "Estado": "RJ",
         "Tipo": "Hospital Universitário", "Leitos SUS": 305, "Internações": 5430,
         "CNES": "2270762", "Zona": "Atenção"},
    ]

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        busca = st.text_input("🔎 Buscar hospital", placeholder="Nome ou município...")
    with col_s2:
        tipo_sel = st.selectbox("Tipo", ["Todos", "Hospital Geral", "Hospital Universitário"])

    lista_filtrada = [
        h for h in hospitais
        if (busca.lower() in h["Nome"].lower() or busca.lower() in h["Município"].lower() or busca == "")
        and (tipo_sel == "Todos" or h["Tipo"] == tipo_sel)
    ]

    for h in lista_filtrada:
        badge_class = "badge-critico" if h["Zona"] == "Crítico" else \
                      "badge-atencao" if h["Zona"] == "Atenção" else "badge-adequado"
        with st.container():
            st.markdown(
                f"""<div style='background:#F4FAFB;border:1px solid #E2ECF0;
                border-radius:10px;padding:1rem 1.2rem;margin-bottom:0.8rem;'>
                <div style='display:flex;justify-content:space-between;align-items:center;'>
                    <div>
                        <span style='font-weight:600;font-size:1rem;color:#0A3D55'>{h['Nome']}</span>
                        <span style='color:#64748B;font-size:0.85rem;margin-left:10px'>
                            {h['Município']} – {h['Estado']}
                        </span>
                    </div>
                    <span class='{badge_class}'>{h['Zona']}</span>
                </div>
                <div style='display:flex;gap:2rem;margin-top:0.7rem;flex-wrap:wrap;'>
                    <span style='font-size:0.82rem;color:#64748B'>
                        🏷️ {h['Tipo']}
                    </span>
                    <span style='font-size:0.82rem;color:#64748B'>
                        🛏️ <b>{h['Leitos SUS']:,}</b> leitos SUS
                    </span>
                    <span style='font-size:0.82rem;color:#64748B'>
                        📋 <b>{h['Internações']:,}</b> internações
                    </span>
                    <span style='font-size:0.82rem;color:#64748B'>
                        🔑 CNES: {h['CNES']}
                    </span>
                </div>
                </div>""",
                unsafe_allow_html=True
            )

    st.markdown("---")
    st.caption("Fonte: CNES — Cadastro Nacional de Estabelecimentos de Saúde · Dados ilustrativos para prototipagem")
