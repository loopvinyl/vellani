import streamlit as st
import pandas as pd
import numpy as np

# Configuração básica
st.set_page_config(page_title="Vellani - Valuation", layout="wide")
st.title("💰 Vellani - Análise de Valuation")
st.markdown("---")

# Parâmetros
SELIC = 0.15
WACC = 0.1613  # Fixo por enquanto

st.sidebar.title("⚙️ Configurações")
st.sidebar.info(f"SELIC: {SELIC*100}% a.a.")
st.sidebar.info(f"WACC: {WACC*100}%")

# Carregar dados
try:
    # Tentar diferentes formas de ler o CSV
    try:
        df = pd.read_csv('data_frame.csv', encoding='utf-8', on_bad_lines='skip')
    except:
        df = pd.read_csv('data_frame.csv', encoding='latin-1', on_bad_lines='skip')
    
    st.success(f"✅ Dados carregados: {len(df)} empresas")
    
    # Seleção simples
    ticker = st.selectbox("Selecione a empresa:", sorted(df['Ticker'].dropna().unique()))
    
    # Dados da empresa
    dados = df[df['Ticker'] == ticker].iloc[0]
    
    # Valores básicos
    ativo = float(dados.get('Ativo Total', 0) or 0)
    ebitda = float(dados.get('Resultado Antes do Resultado Financeiro e dos Tributos', 0) or 0)
    
    # Cálculos diretos
    roi = (ebitda / ativo) * 100 if ativo > 0 else 0
    lucro_economico = ebitda - (WACC * ativo)
    valor_mercado = lucro_economico / SELIC if SELIC > 0 else 0
    
    # Quantidade de ações (valor padrão editável)
    qtd_acoes = st.number_input("Qtd. Ações (milhões):", value=1152.25, format="%.2f") * 1000000
    
    # Cotação esperada
    cotacao_esperada = valor_mercado / qtd_acoes if qtd_acoes > 0 else 0
    
    # Resultados em colunas simples
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Ativo Total", f"R$ {ativo:,.0f}")
        st.metric("EBITDA", f"R$ {ebitda:,.0f}")
        st.metric("ROI", f"{roi:.1f}%")
    
    with col2:
        st.metric("WACC", f"{WACC*100:.1f}%")
        st.metric("Lucro Econômico", f"R$ {lucro_economico:,.0f}")
        st.metric("Valor de Mercado", f"R$ {valor_mercado:,.0f}")
    
    with col3:
        st.metric("SELIC", f"{SELIC*100}%")
        st.metric("Qtd. Ações", f"{qtd_acoes:,.0f}")
        st.success(f"**Cotação Esperada:** R$ {cotacao_esperada:.2f}")

except Exception as e:
    st.error(f"Erro: {e}")
    st.info("Verifique se o arquivo 'data_frame.csv' está no repositório")
