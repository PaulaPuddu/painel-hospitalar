# CLAUDE.md — Painel Inteligente de Acesso Hospitalar

> Arquivo de contexto para o Claude Code. Lê isto antes de mexer no `painel_hospitalar.py`.
> O projeto já tem um MVP funcionando; o trabalho agora é **lapidar o app** (visual + análises).

---

## 1. O que é o projeto

**Challenge Oracle + FIAP** (turma 1TSCO, Data Science). Construir um **Painel Inteligente de Acesso Hospitalar** usando dados públicos do SUS, com o diferencial de **perguntas em linguagem natural via Select AI da Oracle** (português → SQL automático).

**Tema/tese escolhida pelo grupo: VAZIO ASSISTENCIAL.**
Pergunta de negócio central:
> "Quais municípios não conseguem atender as necessidades de internação dos próprios moradores, obrigando-os a buscar hospitais em outras cidades — e para onde esses pacientes vão?"

É um problema social: cidades que "exportam" pacientes precisam de investimento; cidades que "importam" são polos sob pressão.

### Critérios que a FIAP/Oracle avalia (priorizar isto)
- Clareza na definição do problema
- **Uso correto dos 3 formatos de dados** (relacional, JSON, CSV) — cada um com propósito
- Valor para decisão (ajuda a priorizar ações/investimento)
- **Storytelling** (apresentação clara, fácil de seguir)
- **Perguntas com Select AI** úteis e conectadas ao negócio
- Usabilidade e interface intuitiva (peso na nota)

---

## 2. Arquitetura (100% Oracle)

```
Fontes públicas → Ingestão (Python/Colab) → OCI Object Storage
   → Autonomous AI Database (Lakehouse, Always Free) → Select AI → Painel (Streamlit)
```

- **Banco:** Autonomous AI Database, workload Lakehouse, Always Free, região `sa-saopaulo-1`
- **Namespace bucket:** `gruhherptm3e` / bucket `datalake-datascience` / prefixo `challenge/processed/`
- **Select AI profile:** usa OCI Generative AI, modelo `cohere.command-r-08-2024`, apiformat `COHERE`, via `OCI$RESOURCE_PRINCIPAL`

---

## 3. As 3 fontes (já carregadas no banco)

| Fonte | Formato | Tabela/objeto no banco | Volume |
|---|---|---|---|
| SIH/SUS (internações) | parquet → relacional | `SIH_INTERNACOES` | ~933 mil (SP: meses 2,6,8,12 de 2024) |
| CNES (estabelecimentos) | JSON via API → coleção | `CNES_ESTABELECIMENTOS` | 384 (filtrados hospitalares) |
| População IBGE | CSV → tabela | `POPULACAO_DADOS` | 5.570 municípios |

### Esquema do SIH_INTERNACOES (colunas)
`ano, mes, municipio_residencia, municipio_hospital, dias_permanencia, valor_total, cid_principal, cnes, obito, uf`
- `municipio_residencia` e `municipio_hospital` = códigos IBGE de **6 dígitos** (ex. '350570'), tipo VARCHAR
- Códigos de SP começam com '35', RJ com '33'

### POPULACAO_DADOS
`cod_municipio` (7 dígitos IBGE), `municipio`, `populacao`
- **ATENÇÃO ao JOIN:** o SIH tem 6 dígitos, a população 7. Casar com `SUBSTR(TO_CHAR(cod_municipio),1,6)`.

### CNES (coleção JSON)
Consultar com `JSON_VALUE(json_document, '$.campo')`. Campos úteis: `codigo_cnes`, `nome_fantasia`, `codigo_municipio`, `estabelecimento_possui_atendimento_hospitalar`. ATENÇÃO: a API ignorou o filtro de UF, então há hospitais de vários estados; filtrar por `codigo_municipio` começando com '35'/'33' se precisar só SP/RJ.

---

## 4. View principal (já criada)

`VW_VAZIO_ASSISTENCIAL` — por município de residência:
`cod_municipio, nome_municipio, populacao, total_internacoes, internou_na_cidade, internou_fora, taxa_evasao_pct`

Filtros recomendados nas análises: `total_internacoes >= 100`, `taxa_evasao_pct < 100` (tira ruído de borda), `cod_municipio LIKE '35%'` (só SP, que tem dados completos).

---

## 5. Achados já validados (usar no storytelling)

- **Padrão metropolitano:** Guarulhos→São Paulo (2.317), Osasco→SP (1.656), Carapicuíba→SP (813) — cidades da Grande SP dependem da capital.
- **Polos regionais:** Santo André (2.491 pacientes de 58 cidades), Santos (2.400 de 29), Mogi das Cruzes (2.205 de 71), Catanduva (de ~90 cidades — alcance largo).
- **Eixo litorâneo:** São Vicente→Santos.
- **Dois tipos de polo:** alcance largo (Catanduva, muitas cidades pequenas) vs. volume concentrado (Santos, região densa).

---

## 6. Estado atual do app (`painel_hospitalar.py`)

App Streamlit funcionando, com 3 abas:
1. **Visão geral** — ranking de municípios por taxa de evasão + gráfico de barras
2. **Pergunte em português** — Select AI (showsql / runsql / narrate)
3. **Fluxo de pacientes** — polos que mais recebem

### Conexão
- Usa `oracledb` (Thin mode) + wallet, credenciais em `st.secrets` (nunca hardcode)
- Usuário do banco: `painel_app` (só leitura), DSN `painelsus_low`
- Secrets locais em `.streamlit/secrets.toml`; pasta `wallet/` com o wallet extraído
- O app cria o profile do Select AI sozinho na 1ª conexão (`garantir_profile`)

### Segredos esperados (st.secrets)
`DB_USER, DB_PASSWORD, DB_DSN, WALLET_DIR, WALLET_PASSWORD`

---

## 6.5. TAREFA PRINCIPAL: FUNDIR os dois apps

Existem DOIS arquivos:
- `painel_hospitalar.py` — **dados REAIS** (conecta no Autonomous, Select AI funciona), mas visual simples.
- `app.py` (do colega) — **visual EXCELENTE** (CSS, paleta saúde, sidebar, cards, badges, 4 páginas), mas **dados 100% FALSOS**.

**O objetivo é casar os dois: manter o design do `app.py` e plugar os dados reais do `painel_hospitalar.py`.** Resultado = painel bonito E verdadeiro.

### O que no `app.py` é FALSO e precisa virar REAL
- `gerar_dados()` (linha ~97): usa `random`. SUBSTITUIR por queries reais à `VW_VAZIO_ASSISTENCIAL` / `SIH_INTERNACOES` / `POPULACAO_DADOS`.
- Página "Select AI" (linha ~285): respostas **hardcoded** num dict. SUBSTITUIR pela chamada real `DBMS_CLOUD_AI.GENERATE` (ver `painel_hospitalar.py`, função `perguntar_ai`).
- Página "Estabelecimentos" (linha ~375): lista fixa de hospitais inventados. SUBSTITUIR por consulta real à coleção `CNES_ESTABELECIMENTOS` (`JSON_VALUE`).
- O texto "10.000+ estabelecimentos" está errado: são **384** (filtrados hospitalares).

### O que MANTER do `app.py`
- Todo o bloco de CSS (`st.markdown` com `<style>`) — a identidade visual está ótima.
- A estrutura de sidebar + navegação por páginas.
- Os cards `st.metric` estilizados e os badges de zona (Crítico/Atenção/Adequado).
- A paleta: azul-petróleo `#0A3D55`/`#0D6E8A`, e cores de zona laranja/âmbar/verde.

### Como plugar a conexão real
Copiar do `painel_hospitalar.py`: `get_connection()`, `garantir_profile()`, `perguntar_ai()`, e o uso de `st.secrets`. As queries reais (com os JOINs corretos 6-vs-7 dígitos) estão neste documento e no `painel_hospitalar.py`.

---

## 6.6. ESTRUTURA DETALHADA DAS 4 PÁGINAS (roteiro de construção)

Manter a sidebar de navegação e o CSS do `app.py`. As 4 páginas, em ordem (a ordem conta a história no pitch):

### Página 1 — Dashboard executivo — layout fechado
**Papel:** abrir o pitch, panorama num olhar. Resumo executivo (não aprofunda).
- **Topo: 4 cards `st.metric`** — total de internações (933 mil), taxa de evasão média (%), municípios críticos, hospitais mapeados (384).
- **Esquerda (proporção ~1.5fr): MAPA de SP** — `plotly.express.scatter_mapbox`:
  - Uma bolha por município. Tamanho = volume de internações; cor = taxa de evasão (escala vermelho→âmbar→verde, ou contínua).
  - `mapbox_style="carto-positron"` (estilo claro, sem precisar de token).
  - **Coordenadas: usar um CSV de CENTRÓIDES dos municípios de SP** (lat/long por código IBGE), NÃO as coordenadas do CNES.
    - Motivo: o CNES só tem coordenada de quem tem hospital; os municípios "exportadores críticos" (o coração da tese) muitas vezes NÃO têm hospital, então sumiriam do mapa. O centróide do município garante que todos aparecem.
    - O CSV é pequeno (~645 municípios SP, ~30KB), fonte IBGE/dados abertos. Adicionar ao projeto como `municipios_sp_coords.csv` (colunas: cod_municipio 6 dígitos, lat, lng). Fazer JOIN com a `vw_vazio_assistencial` pelo código.
- **Direita (proporção ~1fr): dois painéis empilhados:**
  - "Contexto e Insights" em texto (pode ser fixo aqui, ou Select AI narrate).
  - "Legenda — zonas": Crítico (vermelho, evasão alta) / Atenção (âmbar) / Adequado (verde, atende os seus).
- Responde: "qual o panorama do acesso hospitalar?"
- **Distinção da página 2:** aqui é PANORAMA (mapa geral, números grandes); a página 2 é MERGULHO (fluxo detalhado). Não repetir.

### Página 2 — Vazio assistencial (A ESTRELA) — layout fechado
**Papel:** o coração da tese. Mergulho analítico no fluxo de pacientes.
- **Topo: 4 cards de métrica** — (1) pacientes que viajaram [total de internou_fora], (2) municípios exportadores, (3) polos receptores, (4) maior rota de evasão (texto, ex. "Guarulhos → São Paulo").
- **Esquerda (proporção ~1.6fr): Sankey** (`plotly go.Sankey`) do fluxo origem→destino.
  - Limitar aos **top 10-12 fluxos** mais fortes (senão vira emaranhado).
  - Espessura da fita = volume de pacientes. Usar a query do par origem→destino (seção 7.1).
- **Direita (proporção ~1fr): dois painéis empilhados:**
  - Painel "Classificação dos municípios" com badges: `Exportador crítico` (coral/vermelho), `Polo receptor` (âmbar), `Autossuficiente` (verde). Reusar os badges do CSS do colega.
  - Painel "Contexto e Insights" em texto.
- **Decisões fechadas:**
  - Sankey limitado a top 10-12 fluxos.
  - Classificação de municípios: **incluir** (query nova abaixo).
  - Bloco de insights: **dinâmico via Select AI `narrate`** (mais impressionante). Fallback: texto fixo se a chamada falhar.
- Responde: "quem exporta pacientes e para onde?"

### Página 3 — Perfil de atendimento — layout fechado
**Papel:** mostrar que o painel responde mais que a tese. Ataca "valor para decisão". Aprofunda a análise antes do grande final.
- **Topo: 3 cards** — capítulo que mais interna, maior permanência média (dias), maior custo total (R$).
- **Esquerda (~1.3fr): barras horizontais** — internações por **capítulo do CID** (não por código cru). ~15-20 capítulos, legível.
- **Direita (~1fr): tabela** permanência média + custo por capítulo, + micro-insight: "volume alto ≠ custo alto" (parto interna muito mas é barato/rápido; neoplasia interna menos mas custa/permanece mais).
- **Ponte com a tese:** cruzar com o vazio assistencial — as cidades que exportam, exportam para qual tipo de atendimento? Se alta complexidade (câncer/cardíaco) → falta estrutura especializada.
- Responde: "quais perfis de atendimento pressionam o sistema?"

**Mapeamento CID → capítulo (cuidado: nem todo capítulo é uma letra inteira).**
A maioria é por letra (I=circulatório, J=respiratório, K=digestivo, N=geniturinário, O=gravidez/parto, F=mental, G=nervoso, E=endócrino/metabólico, M=osteomuscular, L=pele). MAS algumas letras dividem por faixa numérica:
- A00-B99 → Infecciosas e parasitárias (letras A e B juntas)
- C00-D48 → Neoplasias (tumores) | D50-D89 → Doenças do sangue (a letra D é dividida!)
- H00-H59 → Olho | H60-H95 → Ouvido (a letra H é dividida!)
- S00-T98 → Lesões e causas externas (S e T juntas)
- Demais por letra única conforme acima.
Implementar com função que olha letra + 2 primeiros dígitos para os casos D, H, e agrupa A/B e S/T. Mapa fixo no código, sem tabela externa.

Query base (seção 7.1, "Perfil de atendimento") + agrupar o resultado por capítulo no Python.

### Página 4 — Pergunte em português (GRANDE FINAL — diferencial Oracle)
**Papel:** o clímax do pitch. Mostrar que tudo que foi analisado pode ser perguntado em português. Última impressão = diferencial Oracle.
- Caixa de pergunta + botões de sugestões clicáveis (perguntas ligadas à tese).
- Mostra: SQL gerado (showsql) de um lado, resultado (runsql) e/ou narração (narrate) do outro.
- Usar a função `perguntar_ai` do `painel_hospitalar.py` (já funciona).
- Sugestões: "quais municípios mais enviam pacientes para fora?", "qual a permanência média por município?", "quais municípios com mais de 50 mil habitantes têm maior evasão?".
- Responde: qualquer pergunta em linguagem natural.

**NOTA DE ORDEM:** a ordem final é 1-Dashboard, 2-Vazio assistencial, 3-Perfil de atendimento, 4-Select AI. As análises (1-2-3) ficam agrupadas; o Select AI fecha como clímax. Ajustar a sidebar nessa ordem.

### Query nova — classificação de municípios (para a página 2)
```sql
SELECT cod_municipio, nome_municipio, total_internacoes, taxa_evasao_pct,
  CASE
    WHEN taxa_evasao_pct >= 60 AND total_internacoes >= 100 THEN 'Exportador crítico'
    WHEN taxa_evasao_pct < 30 THEN 'Autossuficiente'
    ELSE 'Intermediário'
  END AS classificacao
FROM vw_vazio_assistencial
WHERE cod_municipio LIKE '35%' AND total_internacoes >= 100;
-- Polo receptor: cruzar com a query de polos (quem mais recebe de fora).
-- Um município pode ser exportador E polo ao mesmo tempo (manda alguns, recebe outros).
```

---

## 7. PLANO DE MELHORIAS (detalhe técnico)

### Frente A — Visual / UX (inspirado nos exemplos da FIAP)
Os exemplos da FIAP mostram o padrão esperado: cards de métrica grandes, gauge/velocímetro, mapa colorido, e bloco de "CONTEXTO E INSIGHTS" em texto. Replicar esse padrão:
- [ ] Manter o CSS/identidade do `app.py` do colega
- [ ] Cards de métrica no topo de cada página (`st.metric` estilizado)
- [ ] **MAPA** (alto impacto, a FIAP valoriza): usar `plotly scatter_mapbox` com os municípios de SP — lat/long vêm do CNES (`latitude_estabelecimento_decimo_grau`, `longitude_estabelecimento_decimo_grau`). Tamanho da bolha = volume de internações; cor = taxa de evasão. (Choropleth de municípios é pesado; o scatter_mapbox é mais viável e bonito.)
- [ ] **Diagrama de Sankey** (plotly) para o fluxo origem→destino — é a "cara" do vazio assistencial
- [ ] Bloco "Contexto e Insights" em texto ao lado dos gráficos (como o exemplo verde da FIAP), explicando o achado
- [ ] Gauge/velocímetro para a taxa de evasão média (estilo o exemplo TOTVS)

### Frente B — Análises / Indicadores (cobrir mais do enunciado da FIAP)
A tese (vazio assistencial) é a estrela, mas os dados respondem mais perguntas do desafio. Adicionar:
- [ ] **Fluxo origem→destino** (query validada na seção 7.1) — o par principal de cada município
- [ ] **Classificação de municípios** em 3 perfis (cobre a frente "Padrões e Agrupamentos" da FIAP):
      exportador crítico (evasão alta) / polo receptor (recebe muitos de fora) / autossuficiente
- [ ] **Perfil de atendimento** (cobre a pergunta "quais perfis pressionam o sistema"): ranking de `cid_principal` por volume, permanência média e custo. Dado pronto no SIH.
- [ ] **Pressão hospitalar**: internações per capita (SIH + população) por município
- [ ] **Polos de atração**: ranking de quem recebe mais pacientes de fora + de quantas cidades
- [ ] Filtros: faixa de população, taxa de evasão, busca por município
- [ ] Select AI com perguntas sugeridas conectadas à tese (não genéricas)

### 7.1. Queries reais validadas (usar no lugar dos dados falsos)

**Ranking de evasão (dashboard principal):**
```sql
SELECT nome_municipio, populacao, total_internacoes, internou_fora, taxa_evasao_pct
FROM vw_vazio_assistencial
WHERE total_internacoes >= 100 AND taxa_evasao_pct < 100 AND cod_municipio LIKE '35%'
ORDER BY taxa_evasao_pct DESC FETCH FIRST 15 ROWS ONLY;
```

**Polos receptores (fluxo de pacientes):**
```sql
SELECT MAX(d.municipio) AS destino, COUNT(*) AS pacientes_de_fora,
       COUNT(DISTINCT s.municipio_residencia) AS cidades_origem
FROM sih_internacoes s
LEFT JOIN populacao_dados d ON TO_CHAR(s.municipio_hospital)=SUBSTR(TO_CHAR(d.cod_municipio),1,6)
WHERE s.municipio_residencia <> s.municipio_hospital AND s.municipio_hospital LIKE '35%'
GROUP BY s.municipio_hospital ORDER BY pacientes_de_fora DESC FETCH FIRST 15 ROWS ONLY;
```

**Par origem→destino principal (Sankey):**
```sql
SELECT * FROM (
  SELECT s.municipio_residencia AS cod_origem, MAX(o.municipio) AS nome_origem,
         s.municipio_hospital AS cod_destino, MAX(d.municipio) AS nome_destino,
         COUNT(*) AS qtd_pacientes,
         ROW_NUMBER() OVER (PARTITION BY s.municipio_residencia ORDER BY COUNT(*) DESC) AS rank_destino
  FROM sih_internacoes s
  LEFT JOIN populacao_dados o ON TO_CHAR(s.municipio_residencia)=SUBSTR(TO_CHAR(o.cod_municipio),1,6)
  LEFT JOIN populacao_dados d ON TO_CHAR(s.municipio_hospital)=SUBSTR(TO_CHAR(d.cod_municipio),1,6)
  WHERE s.municipio_residencia <> s.municipio_hospital AND s.municipio_residencia LIKE '35%'
  GROUP BY s.municipio_residencia, s.municipio_hospital
) WHERE rank_destino = 1 AND qtd_pacientes >= 50 ORDER BY qtd_pacientes DESC;
```

**Perfil de atendimento (CID que mais pressiona):**
```sql
SELECT cid_principal, COUNT(*) AS internacoes,
       ROUND(AVG(dias_permanencia),1) AS permanencia_media,
       ROUND(SUM(valor_total)) AS custo_total
FROM sih_internacoes WHERE uf='SP' AND cid_principal IS NOT NULL
GROUP BY cid_principal ORDER BY internacoes DESC FETCH FIRST 20 ROWS ONLY;
```

**Estabelecimentos CNES (substituir lista falsa) — com lat/long para o mapa:**
```sql
SELECT JSON_VALUE(json_document,'$.nome_fantasia') AS nome,
       JSON_VALUE(json_document,'$.codigo_municipio') AS cod_mun,
       JSON_VALUE(json_document,'$.codigo_cnes') AS cnes,
       JSON_VALUE(json_document,'$.latitude_estabelecimento_decimo_grau') AS lat,
       JSON_VALUE(json_document,'$.longitude_estabelecimento_decimo_grau') AS lng
FROM cnes_estabelecimentos
WHERE JSON_VALUE(json_document,'$.codigo_municipio') LIKE '35%';
```

### Cobertura do enunciado da FIAP (para o pitch)
Os dados respondem (total ou parcialmente) 5 das 7 demandas da FIAP:
- Perfis de atendimento que pressionam → SIM (cid_principal)
- Onde a capacidade é ultrapassada → SIM (per capita + CNES)
- Rankings e comparações → SIM
- Indicadores de capacidade → SIM (permanência + estrutura)
- Padrões/agrupamentos → SIM (classificação de municípios)
- Explicabilidade → SIM (Select AI narrate)
- Crescimento/sazonalidade temporal → PARCIAL (só 4 meses não-consecutivos: 2,6,8,12)
Estratégia: vazio assistencial como protagonista; as outras como "o painel também responde".

---

## 8. Regras importantes
- **Escopo do MVP:** SP, 4 meses de 2024. Apresentar como recorte consciente, não limitação. Arquitetura escala para mais estados/períodos.
- **Não hardcode senhas** — sempre `st.secrets`.
- **Não usar localStorage/browser storage** — usar estado do Streamlit.
- O app é **público** (Streamlit Cloud) → usuário `painel_app` é só-leitura por segurança.
- Performance: o DSN `_low` permite mais conexões simultâneas; usar `@st.cache_data` para queries que não mudam, com TTL.
- Cuidado com nomes de coluna em MAIÚSCULAS nos DataFrames (o Oracle retorna assim): `df["TAXA_EVASAO_PCT"]`, etc.

---

## 9. Próximos passos depois do app
1. Publicar no Streamlit Cloud (link público para o pitch)
2. Enriquecer CNES (cruzar estrutura hospitalar com evasão)
3. Vídeo pitch (5 min) + README no GitHub
