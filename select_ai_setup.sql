-- ============================================================
-- Oracle Select AI — Configuração e Exemplos de Uso
-- Challenge Oracle + FIAP · RadarSaúde · Turma 1TSCO 2026
-- ============================================================
--
-- Pré-requisito: Oracle Autonomous Database com OCI Gen AI ativado
-- Modelo usado:  Cohere Command-R (cohere.command-r-08-2024)
-- Região:        sa-saopaulo-1
-- Autenticação:  OCI Resource Principal (sem chave API manual)
-- ============================================================


-- ────────────────────────────────────────────────────────────
-- 1. CRIAR O PERFIL DE IA
--    Registra quais tabelas o modelo pode consultar
--    e qual provedor/modelo de linguagem será usado.
-- ────────────────────────────────────────────────────────────
BEGIN
    DBMS_CLOUD_AI.CREATE_PROFILE(
        profile_name => 'PAINEL_APP_GENAI',
        attributes   => '{
          "provider"         : "oci",
          "credential_name"  : "OCI$RESOURCE_PRINCIPAL",
          "region"           : "sa-saopaulo-1",
          "model"            : "cohere.command-r-08-2024",
          "oci_apiformat"    : "COHERE",
          "object_list"      : [
            {"owner":"ADMIN","name":"SIH_INTERNACOES"},
            {"owner":"ADMIN","name":"POPULACAO_DADOS"},
            {"owner":"ADMIN","name":"VW_VAZIO_ASSISTENCIAL"}
          ]
        }'
    );
END;
/


-- ────────────────────────────────────────────────────────────
-- 2. ATIVAR O PERFIL NA SESSÃO ATUAL
-- ────────────────────────────────────────────────────────────
BEGIN
    DBMS_CLOUD_AI.SET_PROFILE('PAINEL_APP_GENAI');
END;
/


-- ────────────────────────────────────────────────────────────
-- 3. VERIFICAR SE O PERFIL FOI CRIADO
-- ────────────────────────────────────────────────────────────
SELECT profile_name, status
FROM   user_cloud_ai_profiles;


-- ────────────────────────────────────────────────────────────
-- 4. EXEMPLOS DE USO — 3 ações disponíveis
-- ────────────────────────────────────────────────────────────

-- 4a. showsql — mostra o SQL gerado pela pergunta (sem executar)
SELECT DBMS_CLOUD_AI.GENERATE(
    prompt       => 'Quais municípios têm taxa de evasão acima de 60%?',
    profile_name => 'PAINEL_APP_GENAI',
    action       => 'showsql'
) FROM dual;

-- 4b. runsql — executa a query e retorna os dados como texto
SELECT DBMS_CLOUD_AI.GENERATE(
    prompt       => 'Quais são os 5 municípios que mais enviam pacientes para fora?',
    profile_name => 'PAINEL_APP_GENAI',
    action       => 'runsql'
) FROM dual;

-- 4c. narrate — resposta em linguagem natural (em português)
SELECT DBMS_CLOUD_AI.GENERATE(
    prompt       => 'INSTRUÇÕES: responda EXCLUSIVAMENTE em português do Brasil. '
                 || 'Em 3 frases, explique quais são os principais fluxos de evasão '
                 || 'hospitalar em São Paulo e o que isso significa para a saúde pública.',
    profile_name => 'PAINEL_APP_GENAI',
    action       => 'narrate'
) FROM dual;


-- ────────────────────────────────────────────────────────────
-- 5. EXEMPLOS USADOS NO PAINEL STREAMLIT
-- ────────────────────────────────────────────────────────────

-- "Quais municípios mais enviam pacientes para fora?"
SELECT DBMS_CLOUD_AI.GENERATE(
    prompt => 'Quais municípios mais enviam pacientes para fora?',
    profile_name => 'PAINEL_APP_GENAI', action => 'runsql'
) FROM dual;

-- "Quais municípios com mais de 50 mil habitantes têm maior evasão?"
SELECT DBMS_CLOUD_AI.GENERATE(
    prompt => 'Quais municípios com mais de 50 mil habitantes têm maior evasão?',
    profile_name => 'PAINEL_APP_GENAI', action => 'runsql'
) FROM dual;

-- "Qual a permanência média por município?"
SELECT DBMS_CLOUD_AI.GENERATE(
    prompt => 'Qual a permanência média por município?',
    profile_name => 'PAINEL_APP_GENAI', action => 'runsql'
) FROM dual;

-- "Quais são os principais destinos de Guarulhos?"
SELECT DBMS_CLOUD_AI.GENERATE(
    prompt => 'Quais são os principais destinos de Guarulhos?',
    profile_name => 'PAINEL_APP_GENAI', action => 'runsql'
) FROM dual;


-- ────────────────────────────────────────────────────────────
-- 6. REMOVER O PERFIL (se necessário recriar)
-- ────────────────────────────────────────────────────────────
-- BEGIN
--     DBMS_CLOUD_AI.DROP_PROFILE('PAINEL_APP_GENAI');
-- END;
-- /
