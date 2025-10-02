import streamlit as st
import pandas as pd
import numpy as np

st.title("📊 Teste de Carga - Análise Financeira")

# Tentativa básica de carregar dados
try:
    df = pd.read_excel('data_frame.xlsx')
    st.success("✅ Arquivo carregado com sucesso!")
    
    # Mostrar informações básicas
    st.write(f"**Total de linhas:** {len(df)}")
    st.write(f"**Total de colunas:** {len(df.columns)}")
    st.write(f"**Colunas:** {list(df.columns)}")
    
    # Filtrar apenas 2024
    df_2024 = df[df['Ano'] == 2024].copy()
    st.write(f"**Dados de 2024:** {len(df_2024)} linhas")
    
    # Mostrar primeiras linhas
    st.write("**Primeiras 5 linhas de 2024:**")
    st.dataframe(df_2024.head())
    
except Exception as e:
    st.error(f"❌ Erro: {e}")
    st.stop()
