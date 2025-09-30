import pandas as pd
import streamlit as st

# Configuração básica
st.set_page_config(page_title="Vellani - Valuation", layout="wide")
st.title("💰 Vellani - Análise de Valuation")
st.markdown("---")

# Carregar dados do Excel (igual ao script que funcionou)
try:
    df = pd.read_excel('data_frame.xlsx')  # Mesma sintaxe que funcionou
    
    st.success(f"✅ Dados carregados: {len(df)} empresas")
    
    # Mostrar informações básicas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Empresas", len(df))
    with col2:
        st.metric("Tickers Únicos", df['Ticker'].nunique())
    with col3:
        st.metric("Colunas", len(df.columns))
    
    # Mostrar primeiros dados
    st.markdown("---")
    st.subheader("📋 Primeiras Empresas no Dataset")
    st.dataframe(df[['Ticker', 'Ativo Total', 'Receita de Venda de Bens e/ou Serviços']].head(10))
    
    # Seleção de empresa
    st.markdown("---")
    st.subheader("🔍 Análise por Empresa")
    
    tickers = sorted(df['Ticker'].dropna().unique())
    selected_ticker = st.selectbox("Selecione uma empresa:", tickers)
    
    # Dados da empresa selecionada
    empresa_data = df[df['Ticker'] == selected_ticker].iloc[0]
    
    # Mostrar dados básicos
    st.write(f"**Dados da {selected_ticker}:**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Ativo Total", f"R$ {empresa_data['Ativo Total']:,.0f}")
        st.metric("Receita", f"R$ {empresa_data['Receita de Venda de Bens e/ou Serviços']:,.0f}")
    
    with col2:
        st.metric("Lucro", f"R$ {empresa_data['Lucro/Prejuízo Consolidado do Período']:,.0f}")
        st.metric("Patrimônio Líquido", f"R$ {empresa_data['Patrimônio Líquido Consolidado']:,.0f}")

except Exception as e:
    st.error(f"Erro: {str(e)}")
    st.info("Verifique se o arquivo 'data_frame.xlsx' está na raiz do repositório")
