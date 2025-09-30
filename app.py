import streamlit as st
import pandas as pd
import os

# === Configuração da página ===
st.set_page_config(page_title="💰 Vellani - Valuation", layout="wide")
st.title("💰 Vellani - Análise de Valuation")
st.markdown("---")

# SELIC global
SELIC = 15.0  # % a.a.
st.info(f"⚙️ SELIC: {SELIC}% a.a.")

# === Caminho do arquivo Excel ===
arquivo_excel = "data_frame.xlsx"

# === Função para carregar Excel com validação ===
def carregar_excel(arquivo, sheet_name=None):
    if not os.path.exists(arquivo):
        raise FileNotFoundError(f"Arquivo '{arquivo}' não encontrado no diretório do script.")
    try:
        df = pd.read_excel(arquivo, sheet_name=sheet_name)
        df.rename(columns=lambda x: x.strip(), inplace=True)  # remove espaços extras
        if 'Ticker' not in df.columns:
            raise ValueError("Coluna 'Ticker' não encontrada no Excel.")
        return df
    except ImportError:
        st.error("openpyxl não está instalado. Instale com `pip install openpyxl`.")
        st.stop()
    except Exception as e:
        st.error(f"Erro ao carregar Excel: {e}")
        st.stop()

# Carrega os dados
df = carregar_excel(arquivo_excel)

# === Informações básicas do dataset ===
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total de Empresas", len(df))
with col2:
    st.metric("Tickers Únicos", df['Ticker'].nunique())
with col3:
    st.metric("Colunas", len(df.columns))

# === Seleção de empresa ===
st.markdown("---")
st.subheader("🔍 Seleção de Empresa")
tickers = sorted(df['Ticker'].dropna().unique())
selected_ticker = st.selectbox("Selecione uma empresa:", tickers)

# === Dados da empresa selecionada ===
empresa_data = df[df['Ticker'] == selected_ticker].iloc[0]
st.subheader(f"📊 Dados da {selected_ticker}")

col1, col2 = st.columns(2)
with col1:
    st.write("**Dados Principais:**")
    if 'Ativo Total' in df.columns:
        st.write(f"Ativo Total: R$ {empresa_data['Ativo Total']:,.0f}")
    if 'Receita de Venda de Bens e/ou Serviços' in df.columns:
        st.write(f"Receita: R$ {empresa_data['Receita de Venda de Bens e/ou Serviços']:,.0f}")
    if 'Lucro/Prejuízo Consolidado do Período' in df.columns:
        st.write(f"Lucro: R$ {empresa_data['Lucro/Prejuízo Consolidado do Período']:,.0f}")
with col2:
    st.write("**Outras Informações:**")
    if 'Patrimônio Líquido Consolidado' in df.columns:
        st.write(f"Patrimônio Líquido: R$ {empresa_data['Patrimônio Líquido Consolidado']:,.0f}")
    if 'Resultado Antes do Resultado Financeiro e dos Tributos' in df.columns:
        st.write(f"EBITDA: R$ {empresa_data['Resultado Antes do Resultado Financeiro e dos Tributos']:,.0f}")

# === Expander para ver todos os dados da empresa ===
with st.expander("📋 Ver todos os dados desta empresa"):
    st.write(empresa_data)

# === Expander para estrutura do dataset completo ===
with st.expander("🔧 Ver estrutura do dataset completo"):
    st.write("**Colunas disponíveis:**")
    st.write(df.columns.tolist())
    st.write("**Primeiras 5 linhas:**")
    st.dataframe(df.head())
