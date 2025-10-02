import streamlit as st
import pandas as pd
import os

st.write("📂 Arquivos disponíveis na pasta do app:", os.listdir("."))

try:
    df = pd.read_excel("data_frame.xlsx", sheet_name="Sheet1", engine="openpyxl")
    st.success("✅ Arquivo carregado com sucesso!")
    st.dataframe(df.head())
except Exception as e:
    st.error(f"❌ Erro ao abrir Excel: {e}")
    uploaded_file = st.file_uploader("Carregue manualmente o Excel", type=["xlsx"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file, sheet_name="Sheet1", engine="openpyxl")
        st.success("✅ Upload feito e Excel carregado!")
        st.dataframe(df.head())
