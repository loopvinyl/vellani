import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Dashboard CVM", layout="wide")
st.title("📊 Dashboard CVM - Teste")
st.success("✅ App carregado com sucesso!")

# Teste básico
try:
    df = pd.DataFrame({
        'Setor': ['Comércio', 'Energia', 'Bancos', 'Construção'],
        'Empresas': [64, 64, 48, 58]
    })
    
    fig = px.bar(df, x='Setor', y='Empresas', title="Distribuição por Setor")
    st.plotly_chart(fig)
    
    st.dataframe(df)
    st.balloons()
    
except Exception as e:
    st.error(f"Erro: {e}")
