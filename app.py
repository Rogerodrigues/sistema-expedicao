import streamlit as st
import pandas as pd
import os
from datetime import datetime

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Controle de Rota Mista", layout="wide")

# Mensagem de verificação no log
print("App Iniciado V4.1...")

try:
    # --- 2. CONFIGURAÇÕES GERAIS ---
    ARQUIVO_HISTORICO = 'historico_geral.csv'

    # --- 3. FUNÇÕES ---
    def carregar_dados(arquivo_ou_url):
        """Lê CSV/Excel com tratamento de erro e separador automático"""
        if arquivo_ou_url is None: return None
        
        try:
            # Se for link do Google Sheets
            if isinstance(arquivo_ou_url, str) and "docs.google.com" in arquivo_ou_url:
                url = arquivo_ou_url.replace('/edit#gid=', '/export?format=csv&gid=')
                url = url.replace('/edit?usp=sharing', '/export?format=csv')
                if '/edit' in url: url = url.split('/edit')[0] + '/export?format=csv'
                return pd.read_csv(url, sep=None, engine='python')
            
            # Se for arquivo local
            return pd.read_csv(arquivo_ou_url, sep=None, engine='python')
        except Exception as e:
            st.error(f"Erro ao ler arquivo: {e}")
            return None

    def normalizar_colunas(df):
        """Padroniza os nomes das colunas (Inglês/Português)"""
        if df is None: return None
        
        # Mapa de tradução baseado nos seus arquivos
        mapa = {
            'SPX TN': 'BR',
            'SPX tracking num': 'BR',
            'Planned AT': 'AT',
            'AT / TO': 'AT',
            'Neighborhood': 'BAIRRO',
            'Bairro': 'BAIRRO',
            'Rota': 'ROTA',
            'City': 'CIDADE',
            'Cidade': 'CIDADE',
            'Corridor/Cage': 'GAIOLA ORIGEM'
        }
        
        df_renomeado = df.rename(columns=mapa)
        
        # Cria colunas faltantes para evitar erro
        cols_obrigatorias = ['BR', 'AT', 'GAIOLA ORIGEM', 'BAIRRO', 'ROTA', 'CIDADE']
        for col in cols_obrigatorias:
            if col not in df_renomeado.columns:
                df_renomeado[col] = ''
        
        return df_renomeado

    def processar_bipe():
        if 'scanner_input' in st.session_state and st.session_state.scanner_input:
            codigo = st.session_state.scanner_input.strip()
            
            dados = {'AT': '', 'GAIOLA ORIGEM': '', 'BAIRRO CABEÇA': '', 'ROTA': ''}
            
            # Busca na base se existir
            if st.session_state.get('df_base_dados') is not None:
                df = st.session_state.df_base_dados
                match = df[df['BR'].astype(str).str.strip() == codigo]
                if not match.empty:
                    linha = match.iloc[0]
                    dados['AT'] = linha.get('AT', '')
                    dados['GAIOLA ORIGEM'] = linha.get('GAIOLA ORIGEM', '')
                    dados['BAIRRO CABEÇA'] = linha.get('BAIRRO', '')
                    dados['ROTA'] = linha.get('ROTA', '')
                    st.toast(f"✅ Encontrado: {dados['BAIRRO CABEÇA']}", icon="📦")
                else:
                    st.toast("⚠️ BR não consta na base carregada", icon="⚠️")

            novo = {
                'DATA_HORA': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                'BR': codigo,
                'AT': dados['AT'],
                'GAIOLA ORIGEM': dados['GAIOLA ORIGEM'],
                'BAIRRO CABEÇA': dados['BAIRRO CABEÇA'],
                'ROTA': dados['ROTA'],
                'GAIOLA DESTINO': '',
                'AT DESTINO': ''
            }
            
            # Adiciona no topo
            st.session_state.df_input = pd.concat([pd.DataFrame([novo]), st.session_state.df_input], ignore_index=True)
            st.session_state.scanner_input = "" 

    def salvar():
        if not st.session_state.df_input.empty:
            hdr = not os.path.exists(ARQUIVO_HISTORICO)
            st.session_state.df_input.to_csv(ARQUIVO_HISTORICO, mode='a', header=hdr, index=False)
            st.success("Lote salvo no Histórico Geral!")
            # Limpa a tela atual
            st.session_state.df_input = st.session_state.df_input.iloc[0:0]
        else:
            st.warning("A tela está vazia, nada para salvar.")

    # --- 4. INICIALIZAÇÃO DE ESTADO ---
    if 'df_input' not in st.session_state:
        st.session_state.df_input = pd.DataFrame(columns=['DATA_HORA', 'BR', 'AT', 'GAIOLA ORIGEM', 'BAIRRO CABEÇA', 'ROTA', 'GAIOLA DESTINO', 'AT DESTINO'])
    if 'df_base_dados' not in st.session_state:
        st.session_state.df_base_dados = None
    if 'df_plano_rotas' not in st.session_state:
        st.session_state.df_plano_rotas = None

    # --- 5. INTERFACE ---
    
    # Barra Lateral
    with st.sidebar:
        st.title("⚙️ Arquivos")
        
        st.markdown("**1. Base do Scanner** (Calculation Tasks)")
        opcao = st.radio("Fonte:", ["Arquivo CSV", "Link Google Sheets"], horizontal=True)
        
        df_temp = None
        if opcao == "Arquivo CSV":
            up = st.file_uploader("Upload Tasks", type=["csv", "txt"])
            if up: df_temp = carregar_dados(up)
        else:
            link = st.text_input("Link Planilha Pública")
            if link: df_temp = carregar_dados(link)
            
        if df_temp is not None:
            st.session_state.df_base_dados = normalizar_colunas(df_temp)
            st.success(f"Carregado: {len(df_temp)} linhas")

        st.markdown("---")
        
        st.markdown("**2. Consultar Rotas** (Plano Expedição)")
        up_rotas = st.file_uploader("Upload Plano", type=["csv", "txt"])
        if up_rotas:
            df_rotas = carregar_dados(up_rotas)
            st.session_state.df_plano_rotas = normalizar_colunas(df_rotas)
            st.success("Rotas Dinâmicas Ativas!")
            
        st.markdown("---")
        st.header("🔍 Buscar Bairro")
        if st.session_state.df_plano_rotas is not None:
            tb = st.session_state.df_plano_rotas
            q = st.text_input("Nome do Bairro/Cidade")
            if q:
                # Filtra Bairro OU Cidade
                filtro = tb[tb['BAIRRO'].astype(str).str.contains(q, case=False, na=False) | 
                            tb['CIDADE'].astype(str).str.contains(q, case=False, na=False)]
                # Mostra colunas limpas
                st.dataframe(filtro[['ROTA', 'BAIRRO', 'CIDADE']].drop_duplicates(), hide_index=True)
        else:
            st.info("Carregue o Plano de Expedição.")

    # Tela Principal
    st.title("🚛 Controle de Rota Mista")
    
    # KPIs
    c1, c2, c3 = st.columns(3)
    qtd = len(st.session_state.df_input)
    total = len(st.session_state.df_base_dados) if st.session_state.df_base_dados is not None else 0
    c1.metric("Bipados Agora", qtd)
    c2.metric("Total Base", total)
    c3.metric("Faltam", max(0, total - qtd))
    
    if total > 0: st.progress(qtd/total)

    # Abas
    t1, t2, t3 = st.tabs(["🔫 Operação", "⚠️ Pendências", "🗄️ Histórico"])
    
    with t1:
        st.text_input("Bipe aqui (ENTER automático):", key="scanner_input", on_change=processar_bipe)
        
        st.markdown("### 📋 Conferência em Tempo Real")
        # AQUI ESTÁ A MUDANÇA: height=600
        st.data_editor(
            st.session_state.df_input,
            use_container_width=True,
            num_rows="dynamic",
            height=600,  # Aumentei a altura da caixa
            key="editor_principal"
        )
        
        st.button("💾 Salvar Lote e Limpar Tela", on_click=salvar, type="primary")
        
    with t2:
        if st.session_state.df_base_dados is not None and not st.session_state.df_input.empty:
            todos = set(st.session_state.df_base_dados['BR'].astype(str).str.strip())
            feitos = set(st.session_state.df_input['BR'].astype(str).str.strip())
            falta = todos - feitos
            if falta:
                st.error(f"Atenção: Faltam {len(falta)} volumes!")
                ver = st.session_state.df_base_dados
                st.dataframe(ver[ver['BR'].astype(str).str.strip().isin(falta)])
            else:
                st.success("Parabéns! Tudo bipado.")
        else:
            st.info("Carregue a base e comece a bipar.")
            
    with t3:
        if os.path.exists(ARQUIVO_HISTORICO):
            h = pd.read_csv(ARQUIVO_HISTORICO)
            st.dataframe(h)
            st.download_button("📥 Baixar Histórico Completo", h.to_csv(index=False).encode('utf-8'), 'historico_completo.csv')
        else:
            st.write("Nenhum histórico salvo ainda.")

except Exception as e:
    st.error("❌ Erro Fatal no App:")
    st.error(e)
