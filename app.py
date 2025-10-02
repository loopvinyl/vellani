import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Análise Financeira 2024 - CVM",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("🏢 Dashboard de Análise Financeira - CVM 2024")
st.markdown("Indicadores financeiros das empresas brasileiras - Ano base 2024")

@st.cache_data
def load_data():
    """Carrega e processa os dados para 2024"""
    df = pd.read_excel('data_frame.xlsx')
    
    # Filtrar apenas 2024
    df_2024 = df[df['Ano'] == 2024].copy()
    
    return df_2024

def calcular_indicadores_2024(df):
    """Calcula indicadores para 2024 (sem saldos médios)"""
    
    # 1. INDICADORES DE RENTABILIDADE
    df['MARGEM_BRUTA'] = df['Resultado Bruto'] / df['Receita de Venda de Bens e/ou Serviços']
    df['MARGEM_EBIT'] = df['Resultado Antes do Resultado Financeiro e dos Tributos'] / df['Receita de Venda de Bens e/ou Serviços']
    df['MARGEM_LIQUIDA'] = df['Lucro/Prejuízo Consolidado do Período'] / df['Receita de Venda de Bens e/ou Serviços']
    
    # 2. INDICADORES DE LIQUIDEZ
    df['LIQUIDEZ_CORRENTE'] = df['Ativo Circulante'] / df['Passivo Circulante']
    df['LIQUIDEZ_SECA'] = (df['Ativo Circulante'] - df['Custo dos Bens e/ou Serviços Vendidos']) / df['Passivo Circulante']
    df['LIQUIDEZ_GERAL'] = df['Ativo Total'] / df['Passivo Total']
    
    # 3. INDICADORES DE ENDIVIDAMENTO
    df['ENDIVIDAMENTO_TOTAL'] = df['Passivo Total'] / df['Ativo Total']
    df['COMPOSICAO_ENDIVIDAMENTO'] = df['Passivo Circulante'] / df['Passivo Total']
    df['GARANTIA_CAPITAL_PROPRIO'] = df['Patrimônio Líquido Consolidado'] / df['Passivo Total']
    df['ALAVANCAGEM_FINANCEIRA'] = df['Passivo Total'] / df['Patrimônio Líquido Consolidado']
    
    # 4. INDICADORES DE EFICIÊNCIA
    df['GIRO_ATIVO'] = df['Receita de Venda de Bens e/ou Serviços'] / df['Ativo Total']
    
    # 5. INDICADORES DE FLUXO DE CAIXA
    df['FCO_RECEITA'] = df['Caixa Líquido Atividades Operacionais'] / df['Receita de Venda de Bens e/ou Serviços']
    df['FCO_LL'] = df['Caixa Líquido Atividades Operacionais'] / df['Lucro/Prejuízo Consolidado do Período']
    
    # 6. INDICADORES DE CUSTO
    df['CUSTO_DIVIDA'] = df['Despesas Financeiras'] / (df['Empréstimos e Financiamentos - Circulante'] + 
                                                     df['Empréstimos e Financiamentos - Não Circulante'])
    
    return df

# Carregar dados
df_2024 = load_data()
df_2024 = calcular_indicadores_2024(df_2024)

# Sidebar
st.sidebar.header("🔍 Filtros")
setores = st.sidebar.multiselect(
    "Setores Econômicos",
    options=df_2024['Setor Econômico'].unique(),
    default=df_2024['Setor Econômico'].unique()[:3]
)

empresas = st.sidebar.multiselect(
    "Empresas",
    options=df_2024['Nome Empresa'].unique()
)

# Aplicar filtros
if setores:
    df_2024 = df_2024[df_2024['Setor Econômico'].isin(setores)]
if empresas:
    df_2024 = df_2024[df_2024['Nome Empresa'].isin(empresas)]

# Layout principal
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📈 Visão Geral", 
    "💰 Rentabilidade", 
    "🏦 Liquidez & Endividamento", 
    "📊 Setores",
    "🔍 Detalhes"
])

with tab1:
    st.header("Indicadores Principais - 2024")
    
    # Métricas rápidas
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Empresas Analisadas", len(df_2024))
    with col2:
        st.metric("Setores", df_2024['Setor Econômico'].nunique())
    with col3:
        margem_media = df_2024['MARGEM_LIQUIDA'].mean()
        st.metric("Margem Líquida Média", f"{margem_media:.1%}")
    with col4:
        roe_medio = (df_2024['Lucro/Prejuízo Consolidado do Período'] / df_2024['Patrimônio Líquido Consolidado']).mean()
        st.metric("ROE Médio", f"{roe_medio:.1%}")

    # Top empresas por lucro
    st.subheader("🏆 Top 10 Empresas - Maior Lucro Líquido")
    top_lucro = df_2024.nlargest(10, 'Lucro/Prejuízo Consolidado do Período')[['Nome Empresa', 'Lucro/Prejuízo Consolidado do Período', 'MARGEM_LIQUIDA']]
    st.dataframe(top_lucro.style.format({
        'Lucro/Prejuízo Consolidado do Período': 'R$ {:,.0f}',
        'MARGEM_LIQUIDA': '{:.1%}'
    }))

with tab2:
    st.header("📊 Análise de Rentabilidade")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição de Margem Líquida
        fig = px.histogram(df_2024, x='MARGEM_LIQUIDA', 
                          title='Distribuição da Margem Líquida',
                          labels={'MARGEM_LIQUIDA': 'Margem Líquida'})
        st.plotly_chart(fig)
    
    with col2:
        # Margem Bruta vs Margem Líquida
        fig = px.scatter(df_2024, x='MARGEM_BRUTA', y='MARGEM_LIQUIDA',
                        hover_data=['Nome Empresa'],
                        title='Margem Bruta vs Margem Líquida')
        st.plotly_chart(fig)

with tab3:
    st.header("🏦 Liquidez e Endividamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Liquidez Corrente
        fig = px.box(df_2024, y='LIQUIDEZ_CORRENTE', 
                    title='Distribuição da Liquidez Corrente')
        st.plotly_chart(fig)
    
    with col2:
        # Endividamento
        fig = px.histogram(df_2024, x='ENDIVIDAMENTO_TOTAL',
                          title='Distribuição do Endividamento Total')
        st.plotly_chart(fig)

with tab4:
    st.header("📈 Análise Setorial")
    
    # Métricas por setor
    setor_analysis = df_2024.groupby('Setor Econômico').agg({
        'MARGEM_LIQUIDA': 'mean',
        'LIQUIDEZ_CORRENTE': 'mean',
        'ENDIVIDAMENTO_TOTAL': 'mean',
        'Nome Empresa': 'count'
    }).round(4)
    
    setor_analysis = setor_analysis.rename(columns={'Nome Empresa': 'Nº Empresas'})
    st.dataframe(setor_analysis.style.format({
        'MARGEM_LIQUIDA': '{:.1%}',
        'LIQUIDEZ_CORRENTE': '{:.2f}',
        'ENDIVIDAMENTO_TOTAL': '{:.1%}'
    }))

with tab5:
    st.header("🔍 Dados Detalhados por Empresa")
    
    # Seletor de empresa para detalhes
    empresa_selecionada = st.selectbox(
        "Selecione uma empresa para detalhes:",
        options=df_2024['Nome Empresa'].unique()
    )
    
    if empresa_selecionada:
        empresa_data = df_2024[df_2024['Nome Empresa'] == empresa_selecionada].iloc[0]
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("💰 Dados Financeiros")
            st.metric("Receita", f"R$ {empresa_data['Receita de Venda de Bens e/ou Serviços']:,.0f}")
            st.metric("Lucro Líquido", f"R$ {empresa_data['Lucro/Prejuízo Consolidado do Período']:,.0f}")
            st.metric("Ativo Total", f"R$ {empresa_data['Ativo Total']:,.0f}")
            st.metric("Patrimônio Líquido", f"R$ {empresa_data['Patrimônio Líquido Consolidado']:,.0f}")
        
        with col2:
            st.subheader("📊 Indicadores")
            st.metric("Margem Líquida", f"{empresa_data['MARGEM_LIQUIDA']:.1%}")
            st.metric("Liquidez Corrente", f"{empresa_data['LIQUIDEZ_CORRENTE']:.2f}")
            st.metric("Endividamento", f"{empresa_data['ENDIVIDAMENTO_TOTAL']:.1%}")
            st.metric("Giro do Ativo", f"{empresa_data['GIRO_ATIVO']:.2f}")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.markdown("**Fonte:** Dados CVM - 2024")
st.sidebar.markdown("**Última atualização:** " + datetime.now().strftime("%d/%m/%Y"))
