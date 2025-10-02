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
    try:
        df = pd.read_excel('data_frame.xlsx')
        st.success(f"✅ Dados carregados: {len(df)} linhas")
        
        # Verificar colunas disponíveis
        st.info(f"📋 Colunas disponíveis: {list(df.columns)}")
        
        # Verificar anos disponíveis
        if 'Ano' in df.columns:
            st.info(f"📅 Anos disponíveis: {sorted(df['Ano'].unique())}")
        
        # Filtrar apenas 2024
        df_2024 = df[df['Ano'] == 2024].copy()
        st.success(f"✅ Dados 2024: {len(df_2024)} linhas")
        
        return df_2024
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

def calcular_indicadores_seguro(df):
    """Calcula indicadores com tratamento de erros"""
    df_calc = df.copy()
    
    try:
        # 1. INDICADORES DE RENTABILIDADE
        df_calc['MARGEM_BRUTA'] = np.where(
            df_calc['Receita de Venda de Bens e/ou Serviços'] != 0,
            df_calc['Resultado Bruto'] / df_calc['Receita de Venda de Bens e/ou Serviços'],
            np.nan
        )
        
        df_calc['MARGEM_EBIT'] = np.where(
            df_calc['Receita de Venda de Bens e/ou Serviços'] != 0,
            df_calc['Resultado Antes do Resultado Financeiro e dos Tributos'] / df_calc['Receita de Venda de Bens e/ou Serviços'],
            np.nan
        )
        
        df_calc['MARGEM_LIQUIDA'] = np.where(
            df_calc['Receita de Venda de Bens e/ou Serviços'] != 0,
            df_calc['Lucro/Prejuízo Consolidado do Período'] / df_calc['Receita de Venda de Bens e/ou Serviços'],
            np.nan
        )
        
        # 2. INDICADORES DE LIQUIDEZ
        df_calc['LIQUIDEZ_CORRENTE'] = np.where(
            df_calc['Passivo Circulante'] != 0,
            df_calc['Ativo Circulante'] / df_calc['Passivo Circulante'],
            np.nan
        )
        
        df_calc['LIQUIDEZ_GERAL'] = np.where(
            df_calc['Passivo Total'] != 0,
            df_calc['Ativo Total'] / df_calc['Passivo Total'],
            np.nan
        )
        
        # 3. INDICADORES DE ENDIVIDAMENTO
        df_calc['ENDIVIDAMENTO_TOTAL'] = np.where(
            df_calc['Ativo Total'] != 0,
            df_calc['Passivo Total'] / df_calc['Ativo Total'],
            np.nan
        )
        
        df_calc['COMPOSICAO_ENDIVIDAMENTO'] = np.where(
            df_calc['Passivo Total'] != 0,
            df_calc['Passivo Circulante'] / df_calc['Passivo Total'],
            np.nan
        )
        
        # 4. INDICADORES DE EFICIÊNCIA
        df_calc['GIRO_ATIVO'] = np.where(
            df_calc['Ativo Total'] != 0,
            df_calc['Receita de Venda de Bens e/ou Serviços'] / df_calc['Ativo Total'],
            np.nan
        )
        
        st.success("✅ Indicadores calculados com sucesso!")
        
    except Exception as e:
        st.error(f"❌ Erro ao calcular indicadores: {e}")
    
    return df_calc

# Carregar dados
df_2024 = load_data()

if df_2024.empty:
    st.stop()

# Calcular indicadores
df_2024 = calcular_indicadores_seguro(df_2024)

# Debug: mostrar estrutura dos dados
with st.expander("🔍 Debug - Ver estrutura dos dados"):
    st.write("**Primeiras linhas:**")
    st.dataframe(df_2024.head())
    st.write("**Colunas disponíveis:**")
    st.write(list(df_2024.columns))
    st.write("**Estatísticas básicas:**")
    st.write(df_2024.describe())

# Sidebar simplificada
st.sidebar.header("🔍 Filtros")

# Verificar se as colunas existem antes de criar filtros
if 'Setor Econômico' in df_2024.columns:
    setores = st.sidebar.multiselect(
        "Setores Econômicos",
        options=df_2024['Setor Econômico'].unique(),
        default=df_2024['Setor Econômico'].unique()[:3] if len(df_2024) > 0 else []
    )
else:
    setores = []
    st.sidebar.warning("Coluna 'Setor Econômico' não encontrada")

if 'Nome Empresa' in df_2024.columns:
    empresas = st.sidebar.multiselect(
        "Empresas",
        options=df_2024['Nome Empresa'].unique()
    )
else:
    empresas = []
    st.sidebar.warning("Coluna 'Nome Empresa' não encontrada")

# Aplicar filtros
if setores and 'Setor Econômico' in df_2024.columns:
    df_2024 = df_2024[df_2024['Setor Econômico'].isin(setores)]
if empresas and 'Nome Empresa' in df_2024.columns:
    df_2024 = df_2024[df_2024['Nome Empresa'].isin(empresas)]

# Layout principal simplificado
tab1, tab2, tab3 = st.tabs([
    "📈 Visão Geral", 
    "💰 Análise Financeira", 
    "🔍 Dados Detalhados"
])

with tab1:
    st.header("Visão Geral - 2024")
    
    if len(df_2024) > 0:
        # Métricas rápidas
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Empresas Analisadas", len(df_2024))
        with col2:
            if 'Setor Econômico' in df_2024.columns:
                st.metric("Setores", df_2024['Setor Econômico'].nunique())
            else:
                st.metric("Empresas Únicas", df_2024['Nome Empresa'].nunique() if 'Nome Empresa' in df_2024.columns else "N/A")
        with col3:
            if 'MARGEM_LIQUIDA' in df_2024.columns:
                margem_media = df_2024['MARGEM_LIQUIDA'].mean()
                st.metric("Margem Líquida Média", f"{margem_media:.1%}" if not pd.isna(margem_media) else "N/A")
            else:
                st.metric("Margem Líquida", "N/A")
        with col4:
            if 'LIQUIDEZ_CORRENTE' in df_2024.columns:
                liquidez_media = df_2024['LIQUIDEZ_CORRENTE'].mean()
                st.metric("Liquidez Corrente Média", f"{liquidez_media:.2f}" if not pd.isna(liquidez_media) else "N/A")
            else:
                st.metric("Liquidez", "N/A")

        # Top empresas
        st.subheader("Principais Empresas")
        if 'Nome Empresa' in df_2024.columns and 'Receita de Venda de Bens e/ou Serviços' in df_2024.columns:
            colunas_show = ['Nome Empresa', 'Receita de Venda de Bens e/ou Serviços']
            if 'Lucro/Prejuízo Consolidado do Período' in df_2024.columns:
                colunas_show.append('Lucro/Prejuízo Consolidado do Período')
            if 'MARGEM_LIQUIDA' in df_2024.columns:
                colunas_show.append('MARGEM_LIQUIDA')
            
            top_empresas = df_2024[colunas_show].head(10)
            st.dataframe(top_empresas)
        else:
            st.dataframe(df_2024.head(10))

with tab2:
    st.header("Análise Financeira")
    
    if len(df_2024) > 0:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'MARGEM_LIQUIDA' in df_2024.columns:
                fig = px.histogram(df_2024, x='MARGEM_LIQUIDA', 
                                  title='Distribuição da Margem Líquida',
                                  labels={'MARGEM_LIQUIDA': 'Margem Líquida'})
                st.plotly_chart(fig)
            else:
                st.warning("Indicador MARGEM_LIQUIDA não disponível")
        
        with col2:
            if 'LIQUIDEZ_CORRENTE' in df_2024.columns:
                fig = px.box(df_2024, y='LIQUIDEZ_CORRENTE', 
                            title='Distribuição da Liquidez Corrente')
                st.plotly_chart(fig)
            else:
                st.warning("Indicador LIQUIDEZ_CORRENTE não disponível")

with tab3:
    st.header("Dados Detalhados")
    
    if len(df_2024) > 0:
        # Mostrar todas as colunas disponíveis
        st.subheader("Dados Completos")
        
        # Selecionar colunas para mostrar
        colunas_numericas = df_2024.select_dtypes(include=[np.number]).columns.tolist()
        colunas_texto = df_2024.select_dtypes(include=['object']).columns.tolist()
        
        colunas_para_mostrar = st.multiselect(
            "Selecionar colunas para mostrar:",
            options=df_2024.columns.tolist(),
            default=colunas_texto + colunas_numericas[:5]  # Primeiras 5 numéricas
        )
        
        if colunas_para_mostrar:
            st.dataframe(df_2024[colunas_para_mostrar])
        else:
            st.dataframe(df_2024)

# Rodapé
st.sidebar.markdown("---")
st.sidebar.markdown("**Desenvolvido para Análise Financeira**")
st.sidebar.markdown(f"**Dados carregados:** {len(df_2024)} registros")
