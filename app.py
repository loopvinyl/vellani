import streamlit as st
import pandas as pd

# Configuração básica
st.set_page_config(page_title="Vellani - Valuation", layout="wide")
st.title("💰 Vellani - Análise de Valuation")
st.markdown("---")

# SELIC global
SELIC = 15.0  # % a.a.
st.info(f"⚙️ SELIC: {SELIC}% a.a.")

# Carregar dados
try:
    df = pd.read_csv('data_frame.csv', encoding='utf-8', on_bad_lines='skip')
    
    # Checar se a coluna 'Ticker' existe
    if 'Ticker' not in df.columns:
        raise ValueError("Coluna 'Ticker' não encontrada no arquivo CSV.")
    
    st.success(f"✅ Dados carregados com sucesso! ({len(df)} empresas)")

    # Informações básicas do dataset
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de Empresas", len(df))
    with col2:
        st.metric("Tickers Únicos", df['Ticker'].nunique())
    with col3:
        st.metric("Colunas", len(df.columns))
    
    # Seleção de empresa
    st.markdown("---")
    st.subheader("🔍 Seleção de Empresa")
    
    tickers = sorted(df['Ticker'].dropna().unique())
    selected_ticker = st.selectbox("Selecione uma empresa:", tickers)
    
    # Dados da empresa selecionada
    empresa_data = df[df['Ticker'] == selected_ticker].iloc[0]
    
    st.subheader(f"📊 Dados da {selected_ticker}")
    
    # Mostrar algumas colunas importantes
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
    
    # Expander para ver todos os dados
    with st.expander("📋 Ver todos os dados desta empresa"):
        st.write(empresa_data)
    
    # Expander para estrutura do dataset
    with st.expander("🔧 Ver estrutura do dataset completo"):
        st.write("**Colunas disponíveis:**")
        st.write(df.columns.tolist())
        st.write("**Primeiras 5 linhas:**")
        st.dataframe(df.head())

except Exception as e:
    st.error(f"Erro ao carregar dados: {str(e)}")
    
    # Modo de emergência
    st.info("""
    **Se continuar com erro:**
    1. Verifique se o arquivo CSV está correto
    2. Confirme que a coluna 'Ticker' existe
    3. Tente usar dados de exemplo abaixo
    """)
    
    # Dados de exemplo
    st.subheader("🧪 Dados de Exemplo")
    exemplo_ticker = st.selectbox("Empresa exemplo:", ["PETR4", "VALE3", "ITUB4"])
    
    st.write(f"**Dados de exemplo para {exemplo_ticker}:**")
    st.write("- Ativo Total: R$ 100.000.000")
    st.write("- Receita: R$ 50.000.000") 
    st.write("- Lucro: R$ 10.000.000")
    st.write("- Patrimônio Líquido: R$ 60.000.000")
