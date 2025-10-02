import streamlit as st
import pandas as pd

st.title("📊 Análise Financeira - Debug")
st.write("Carregando dados...")

try:
    df = pd.read_excel('data_frame.xlsx')
    st.success("Dados carregados!")
    st.write(f"Linhas: {len(df)}")
    st.write(f"Colunas: {list(df.columns)}")
    st.write("Primeiras linhas:")
    st.dataframe(df.head())
except Exception as e:
    st.error(f"Erro: {e}")
