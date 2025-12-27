import streamlit as st
import pandas as pd
from io import StringIO
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema de Rotas & Expedição", layout="wide")

# Arquivo onde o histórico eterno será salvo (Local por enquanto)
ARQUIVO_HISTORICO = 'historico_geral.csv'

# --- 2. CARREGAR OS DADOS DE ROTAS (FIXO) ---
csv_data = """ROTA
CABO FRIO - ROTA 1 - CENTRO - PASSAGEM - VILA NOVA - PORTINHO - NOVO PORTINHO - JD EXCELSIOR - ALGODOAL - SÃO BENTO
CABO FRIO - ROTA 2 - BRAGA - SÃO CRISTÓVÃO - GUARANI - MANOEL CORREIA - RECANTO DAS DUNAS - VILA DO SOL- FOGUETE
CABO FRIO - ROTA 3 - JD CAIÇARA - JD OLINDA - PRAIA SIQUEIRA - PARQUE BURLE - JD FLAMBOYANT - PALMEIRAS
CABO FRIO - ROTA 4 - JD ESPERANÇA - PQ ELDORADO 1 - PORTO DO CARRO - MONTE ALEGRE - MINHA CASA MINHA VIDA
CABO FRIO - ROTA 5 - CAMINHO DE BÚZIOS - JD PERÓ - RESERVA DO PERÓ - TANGARÁ - GURIRI - PQ ELDORADO 3 - COLINAS DO PERÓ - SERRA PELADA
CABO FRIO - ROTA 6 - PERÓ - JACARÉ - GAMBOA - OGIVA - CAJUEIRO - CAMINHO VERDE
UNAMAR - ROTA 7 - VERÃO VERMELHO - SINAGOGA - ORLA 500 - SANTA MARGARIDA - LONG BEACH - TERRAMAR- FLORESTINHA
UNAMAR - ROTA 8 - NOVA CALIFORNIA - SAMBURÁ - CENTRO HÍPICO - AQUARIUS
UNAMAR - ROTA 9 - BOTAFOGO - CAMPOS NOVOS - SÃO JACINTO - ÁREA RURAL DE CABO FRIO - VILA COLONIAL
BÚZIOS - ROTA 10 - RASA - MARIA JOAQUINA - VILA VERDE - VILA CRUZEIRO - ARPOADOR
BÚZIOS - ROTA 11 - BAIA FORMOSA - JOSÉ GONÇALVES - CEM BRAÇAS - TUCUNS - CAPÃO
BÚZIOS - ROTA 12 - CENTRO - MANGUINHOS - CENTRO MANGUE - GERIBÁ - FERRADURA - JOÃO FERNANDES - TARTARUGA - BRAVA - PRAIA DOS OSSOS - ORLA BARDOT
ARRAIAL DO CABO - ROTA 13 - CENTRO - PRAIA DOS ANJOS - PRAINHA - MORRO DA COCA - PRAIA GRANDE - MACEDONIA - MORRO DA CABOCLA - CITY - VILA CANAA
ARRAIAL DO CABO - ROTA 14 - FIGUEIRA - MONTE ALTO - NOVO ARRAIAL - PARQUE DAS GARÇAS
ARRAIAL DO CABO - ROTA 15 - SABIA - CAIÇARA
IGUABA - ROTA 16 - CENTRO - SOPOTÓ - PEDREIRA - ESTAÇÃO- BOA VISTA
IGUABA - ROTA 17 - IGUABA PEQUENA - CANELAS CITY - LAGUNA AZUL - PARQUE TAMARIZ
IGUABA - ROTA 18 - CIDADE NOVA - SÃO MIGUEL - NOVA IGUABA - UNIÃO
IGUABA - ROTA 19 - CAPIVARA - COQUEIROS - UBAS
IGUABA - ROTA 20 - SAPIATIBA MIRIM
IGUABA - ROTA 21 - ARRASTÃO DAS PEDRAS - VILA NOVA 1 - IGARAPIAPUNHA
IGUABA - ROTA 22 - MORRO DA FAZENDA - VILA NOVA 2
IGUABA - ROTA 23 - JD SOLARES
ARARUAMA - ROTA 24 - IGUABINHA - CENTRO IGUABINHA
ARARUAMA - ROTA 25 - MORRO GRANDE
ARARUAMA - ROTA 26 - NOVO HORIZONTE - PARATI
ARARUAMA - ROTA 27 - FAZENDINHA - VILA CANAA - CLUBE DOS ENGENHEIROS
ARARUAMA - ROTA 28 - MULTIRÃO - BOA PERNA - PARQUE MATARUNA - JD SÃO PAULO - PQ DAS ACÁCIAS
ARARUAMA - ROTA 29 - TRÊS VENDAS - ITATIQUARA
ARARUAMA - ROTA 30 - CENTRO - PARQUE HOTEL - PRAÇA DA BANDEIRA -MATARUNA - FONTE LIMPA - NOSSA SENHORA DE NAZARÉ
ARARUAMA - ROTA 31 - XV DE NOVEMBRO - OUTEIRO - VIADUTO - AREAL - HOSPÍCIO - AMOR MORENO
ARARUAMA - ROTA 32 - LAKE VIEW
ARARUAMA - ROTA 33 - SÃO VICENTE
ARARUAMA - ROTA 34 - PONTINHA - COQUEIRAL - VILA CAPRI
ARARUAMA - ROTA 35 - PRAIA SECA"""

df_rotas = pd.read_csv(StringIO(csv_data), sep=";")

# --- 3. INICIALIZAÇÃO DE VARIÁVEIS DE ESTADO ---
if 'df_input' not in st.session_state:
    st.session_state.df_input = pd.DataFrame(columns=['DATA_HORA', 'BR', 'AT', 'GAIOLA ORIGEM', 'BAIRRO CABEÇA', 'GAIOLA DESTINO', 'AT DESTINO'])
if 'df_romaneio' not in st.session_state:
    st.session_state.df_romaneio = None

# --- 4. FUNÇÕES AUXILIARES ---

def processar_bipe():
    """Lê o código bipado, busca no Romaneio e adiciona na tabela."""
    codigo_bipe = st.session_state.scanner_input.strip()
    
    if codigo_bipe:
        at_found = ''
        gaiola_origem_found = ''
        bairro_found = ''
        
        # Busca no Romaneio
        if st.session_state.df_romaneio is not None:
            df_search = st.session_state.df_romaneio
            # Garante que ambos sejam string para comparar
            match = df_search[df_search['BR'].astype(str).str.strip() == codigo_bipe]
            
            if not match.empty:
                try:
                    at_found = match.iloc[0]['AT'] if 'AT' in match.columns else ''
                    gaiola_origem_found = match.iloc[0]['GAIOLA ORIGEM'] if 'GAIOLA ORIGEM' in match.columns else ''
                    bairro_found = match.iloc[0]['BAIRRO CABEÇA'] if 'BAIRRO CABEÇA' in match.columns else ''
                    st.toast(f"✅ BR Encontrado: {bairro_found}")
                except:
                    pass
            else:
                st.toast("⚠️ BR não consta no Romaneio carregado.")

        novo_registro = {
            'DATA_HORA': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'BR': codigo_bipe,
            'AT': at_found,
            'GAIOLA ORIGEM': gaiola_origem_found,
            'BAIRRO CABEÇA': bairro_found,
            'GAIOLA DESTINO': '',
            'AT DESTINO': ''
        }
        
        st.session_state.df_input = pd.concat([pd.DataFrame([novo_registro]), st.session_state.df_input], ignore_index=True)
        st.session_state.scanner_input = ""

def salvar_historico():
    if not st.session_state.df_input.empty:
        header_mode = not os.path.exists(ARQUIVO_HISTORICO)
        st.session_state.df_input.to_csv(ARQUIVO_HISTORICO, mode='a', header=header_mode, index=False, encoding='utf-8')
        st.success(f"{len(st.session_state.df_input)} registros salvos no Histórico!")
        st.session_state.df_input = pd.DataFrame(columns=['DATA_HORA', 'BR', 'AT', 'GAIOLA ORIGEM', 'BAIRRO CABEÇA', 'GAIOLA DESTINO', 'AT DESTINO'])
    else:
        st.warning("Tabela vazia.")

# --- 5. BARRA LATERAL ---
with st.sidebar:
    st.title("🚛 Expedição")
    st.markdown("---")
    
    # Upload do Romaneio
    st.header("📂 1. Carregar Romaneio")
    uploaded_file = st.file_uploader("Arquivo CSV (BR, AT, GAIOLA...)", type="csv")
    if uploaded_file is not None:
        try:
            st.session_state.df_romaneio = pd.read_csv(uploaded_file, sep=";", dtype=str)
            st.success(f"Romaneio: {len(st.session_state.df_romaneio)} volumes.")
        except:
            st.error("Erro no arquivo. Verifique se é CSV separado por ponto e vírgula.")

    st.markdown("---")
    
    # Buscador
    st.header("🔍 2. Consultar Rota")
    termo_busca = st.text_input("Bairro ou Cidade:", "")
    if termo_busca:
        resultado = df_rotas[df_rotas['ROTA'].str.contains(termo_busca, case=False, na=False)]
    else:
        resultado = df_rotas
    st.dataframe(resultado, hide_index=True, use_container_width=True)

# --- 6. TELA PRINCIPAL & DASHBOARD ---

# --- DASHBOARD SUPERIOR (Novidade!) ---
st.markdown("### 📊 Painel de Controle em Tempo Real")
col1, col2, col3, col4 = st.columns(4)

total_bipados = len(st.session_state.df_input)
total_meta = len(st.session_state.df_romaneio) if st.session_state.df_romaneio is not None else 0
pendentes = total_meta - total_bipados if total_meta > 0 else 0

# Calcula % apenas se tiver meta
if total_meta > 0:
    progresso = min(total_bipados / total_meta, 1.0)
else:
    progresso = 0.0

col1.metric("📦 Volumes Bipados", total_bipados)
col2.metric("🎯 Meta (Romaneio)", total_meta)
col3.metric("⚠️ Pendentes", max(pendentes, 0))
col4.metric("🚀 Progresso", f"{progresso*100:.1f}%")

st.progress(progresso)
st.divider()

# --- ABAS DE OPERAÇÃO ---
aba_scan, aba_pendencia, aba_historico = st.tabs(["🔫 Operação (Scan)", "⚠️ Relatório de Faltas", "🗄️ Histórico Geral"])

# ABA 1: SCAN
with aba_scan:
    st.markdown("#### Bipagem")
    st.text_input("Bipe aqui:", key="scanner_input", on_change=processar_bipe)
    
    st.markdown("#### Conferência Atual")
    df_editado = st.data_editor(st.session_state.df_input, num_rows="dynamic", use_container_width=True, key="editor")
    
    st.button("✅ Consolidar Lote no Histórico", on_click=salvar_historico, type="primary")

# ABA 2: RELATÓRIO DE FALTAS (Novidade!)
with aba_pendencia:
    st.markdown("### 🕵️ O que falta bipar?")
    
    if st.session_state.df_romaneio is not None:
        # Lógica de Conjuntos para achar a diferença
        # Converte tudo para string e remove espaços para garantir match
        todos_brs = set(st.session_state.df_romaneio['BR'].astype(str).str.strip())
        bipados_brs = set(st.session_state.df_input['BR'].astype(str).str.strip())
        
        # Quem está no Romaneio MAS NÃO está nos Bipados
        faltantes = todos_brs - bipados_brs
        
        if len(faltantes) > 0:
            st.error(f"Faltam {len(faltantes)} volumes do Romaneio!")
            # Filtra o dataframe original para mostrar os detalhes dos faltantes
            df_faltantes = st.session_state.df_romaneio[st.session_state.df_romaneio['BR'].astype(str).str.strip().isin(faltantes)]
            st.dataframe(df_faltantes, use_container_width=True)
        else:
            st.success("Parabéns! Tudo o que estava no Romaneio foi bipado.")
    else:
        st.info("Carregue um Romaneio na barra lateral para ver as pendências.")

# ABA 3: HISTÓRICO
with aba_historico:
    st.markdown("### 🗄️ Banco de Dados Local")
    if os.path.exists(ARQUIVO_HISTORICO):
        df_hist = pd.read_csv(ARQUIVO_HISTORICO)
        st.dataframe(df_hist, use_container_width=True)
        st.download_button("📥 Baixar CSV Completo", df_hist.to_csv(index=False).encode('utf-8'), 'historico_completo.csv', 'text/csv')
    else:
        st.write("Ainda não há histórico salvo.")
