import streamlit as st
import pandas as pd

@st.cache_data
def load_data():
    try:
        # tenta abrir direto do repositório
        df = pd.read_excel("data_frame.xlsx", sheet_name="Sheet1", engine="openpyxl")
        return df
    except FileNotFoundError:
        st.warning("⚠️ O arquivo `data_frame.xlsx` não foi encontrado no repositório. Carregue manualmente abaixo:")
        uploaded_file = st.file_uploader("Carregue seu arquivo Excel", type=["xlsx"])
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file, sheet_name="Sheet1", engine="openpyxl")
            return df
        return None

df = load_data()

if df is not None:
    st.success("✅ Dados carregados com sucesso!")
    st.dataframe(df.head())
else:
    st.info("Aguardando arquivo Excel para continuar...")
