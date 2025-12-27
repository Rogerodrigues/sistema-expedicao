import streamlit as st
import pandas as pd
from io import StringIO
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Sistema de Rotas & Expedição", layout="wide")

# Arquivo onde o histórico eterno será salvo
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

# --- 3. FUNÇÕES AUXILIARES ---

def processar_bipe():
    """Lê o código bipado, busca no Romaneio (se existir) e adiciona na tabela."""
    codigo_bipe = st.session_state.scanner_input.strip() # Remove espaços extras
    
    if codigo_bipe:
        # Valores padrão (vazios) caso não encontre no romaneio
        at_found = ''
        gaiola_origem_found = ''
        bairro_found = ''
        
        # Lógica de Busca no Romaneio (Cruzamento de Dados)
        if 'df_romaneio' in st.session_state and st.session_state.df_romaneio is not None:
            # Converte para string para garantir a comparação
            df_search = st.session_state.df_romaneio
            
            # Tenta encontrar a linha onde a coluna 'BR' é igual ao código bipado
            # (Assumindo que o CSV do romaneio tem uma coluna chamada 'BR')
            match = df_search[df_search['BR'].astype(str).str.strip() == codigo_bipe]
            
            if not match.empty:
                # Se achou, pega os dados. 
                # OBS: Ajuste os nomes abaixo ('AT', 'GAIOLA', etc) se o seu CSV tiver nomes diferentes
                try:
                    at_found = match.iloc[0]['AT'] if 'AT' in match.columns else ''
                    gaiola_origem_found = match.iloc[0]['GAIOLA ORIGEM'] if 'GAIOLA ORIGEM' in match.columns else ''
                    bairro_found = match.iloc[0]['BAIRRO CABEÇA'] if 'BAIRRO CABEÇA' in match.columns else ''
                    # Feedback visual rápido
                    st.toast(f"BR Encontrado! Bairro: {bairro_found}", icon="✅")
                except Exception as e:
                    st.toast(f"Erro ao ler colunas do romaneio: {e}", icon="⚠️")
            else:
                st.toast("BR não encontrado no Romaneio atual.", icon="⚠️")

        # Cria o registro novo
        novo_registro = {
            'DATA_HORA': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            'BR': codigo_bipe,
            'AT': at_found,
            'GAIOLA ORIGEM': gaiola_origem_found,
            'BAIRRO CABEÇA': bairro_found,
            'GAIOLA DESTINO': '', # Geralmente preenchido na hora
            'AT DESTINO': ''      # Geralmente preenchido na hora
        }
        
        # Adiciona no topo do DataFrame
        st.session_state.df_input = pd.concat([pd.DataFrame([novo_registro]), st.session_state.df_input], ignore_index=True)
        
        # Limpa o campo
        st.session_state.scanner_input = ""

def salvar_historico():
    if not st.session_state.df_input.empty:
        header_mode = not os.path.exists(ARQUIVO_HISTORICO)
        st.session_state.df_input.to_csv(ARQUIVO_HISTORICO, mode='a', header=header_mode, index=False, encoding='utf-8')
        st.success(f"{len(st.session_state.df_input)} registros salvos no Histórico Geral!")
        st.session_state.df_input = pd.DataFrame(columns=['DATA_HORA', 'BR', 'AT', 'GAIOLA ORIGEM', 'BAIRRO CABEÇA', 'GAIOLA DESTINO', 'AT DESTINO'])
    else:
        st.warning("A tabela está vazia.")

# --- 4. BARRA LATERAL (UPLOADS E BUSCA) ---
with st.sidebar:
    st.title("⚙️ Configurações")
    
    # --- UPLOAD DO ROMANEIO ---
    st.header("📂 Upload do Romaneio")
    st.info("Suba o CSV com colunas: BR, AT, GAIOLA ORIGEM, BAIRRO CABEÇA")
    uploaded_file = st.file_uploader("Escolha o arquivo CSV", type="csv")
    
    if uploaded_file is not None:
        try:
            # Lê o arquivo. Sep=";" é padrão BR, mas se der erro mude para ","
            df_romaneio = pd.read_csv(uploaded_file, sep=";", dtype=str)
            st.session_state.df_romaneio = df_romaneio
            st.success(f"Romaneio carregado: {len(df_romaneio)} linhas.")
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
    else:
        st.session_state.df_romaneio = None

    st.divider()

    # --- BUSCADOR DE ROTAS ---
    st.header("🔍 Buscador de Rotas")
    termo_busca = st.text_input("Filtrar Bairro/Cidade:", "")
    if termo_busca:
        resultado = df_rotas[df_rotas['ROTA'].str.contains(termo_busca, case=False, na=False)]
    else:
        resultado = df_rotas
    st.dataframe(resultado, hide_index=True, use_container_width=True)

# --- 5. TELA PRINCIPAL ---
st.title("🚛 Controle de Expedição Inteligente")

# Status do Romaneio
if 'df_romaneio' in st.session_state and st.session_state.df_romaneio is not None:
    st.success("🟢 Sistema conectado ao Romaneio. Bipagem automática ativa.")
else:
    st.warning("🔴 Nenhum Romaneio carregado. O preenchimento será manual.")

aba_operacao, aba_historico = st.tabs(["📋 Operação (Scan)", "🗄️ Histórico Completo"])

with aba_operacao:
    st.markdown("### Área de Bipagem")
    
    # Campo de Scan com auto-submit
    st.text_input(
        "Bipe o código aqui (ENTER automático):", 
        key="scanner_input", 
        on_change=processar_bipe
    )

    st.divider()
    
    if 'df_input' not in st.session_state:
        st.session_state.df_input = pd.DataFrame(columns=['DATA_HORA', 'BR', 'AT', 'GAIOLA ORIGEM', 'BAIRRO CABEÇA', 'GAIOLA DESTINO', 'AT DESTINO'])

    st.markdown("### Conferência")
    # Tabela editável
    df_editado = st.data_editor(
        st.session_state.df_input,
        num_rows="dynamic",
        use_container_width=True,
        key="editor_dados"
    )

    col1, col2 = st.columns([1, 4])
    with col1:
        st.button("✅ Salvar no Histórico", on_click=salvar_historico, type="primary")

with aba_historico:
    st.markdown("### Histórico Geral")
    if os.path.exists(ARQUIVO_HISTORICO):
        df_hist = pd.read_csv(ARQUIVO_HISTORICO)
        st.dataframe(df_hist, use_container_width=True)
        st.download_button("📥 Baixar Histórico (CSV)", df_hist.to_csv(index=False).encode('utf-8'), 'historico.csv', 'text/csv')
    else:
        st.write("Histórico vazio.")