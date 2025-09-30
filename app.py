import streamlit as st
import pandas as pd

# Configuração mais simples possível
st.set_page_config(page_title="Teste App", layout="wide")

st.title("📊 Teste - Análise de Empresas")
st.markdown("Versão mínima para teste")

try:
    # Tentar carregar dados
    df = pd.read_excel('data_frame.xlsx')
    st.success("✅ Arquivo carregado com sucesso!")
    
    # Informações básicas
    st.write(f"**Dimensões do dataset:** {df.shape[0]} linhas × {df.shape[1]} colunas")
    
    # Mostrar colunas disponíveis
    st.write("**Colunas disponíveis:**")
    st.write(df.columns.tolist())
    
    # Mostrar primeiras linhas
    st.write("**Primeiras 5 linhas:**")
    st.dataframe(df.head())
    
    # Verificar se existe coluna Ticker
    if 'Ticker' in df.columns:
        tickers = df['Ticker'].dropna().unique()
        st.write(f"**Tickers encontrados:** {len(tickers)}")
        st.write(tickers[:10])  # Mostrar apenas os 10 primeiros
        
        # Selecionar um ticker para ver dados
        ticker_selecionado = st.selectbox("Selecione um ticker para ver detalhes:", tickers)
        
        # Mostrar dados do ticker selecionado
        dados_ticker = df[df['Ticker'] == ticker_selecionado].iloc[0]
        st.write(f"**Dados do {ticker_selecionado}:**")
        st.json(dados_ticker.to_dict())
    
except Exception as e:
    st.error(f"❌ Erro: {e}")
    st.info("Verifique se o arquivo 'data_frame.xlsx' está na pasta raiz do projeto")
