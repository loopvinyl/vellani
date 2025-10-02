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
        df = pd.read_csv('data_frame.xlsx - Sheet1.csv')
        
        # Filtrar apenas 2024
        df_2024 = df[df['Ano'] == 2024].copy()
        st.success(f"✅ Dados 2024 carregados: {len(df_2024)} linhas")
        
        return df_2024
    except Exception as e:
        st.error(f"❌ Erro ao carregar dados: {e}")
        return pd.DataFrame()

def calcular_indicadores_2024(df):
    """Calcula indicadores para 2024 usando os nomes corretos das colunas"""
    df_calc = df.copy()
    
    try:
        # 1. INDICADORES DE RENTABILIDADE
        df_calc['MARGEM_BRUTA'] = np.where(
            df_calc['Receita de Venda de Bens e/ou Serviços'] > 0,
            df_calc['Resultado Bruto'] / df_calc['Receita de Venda de Bens e/ou Serviços'],
            np.nan
        )
        
        df_calc['MARGEM_LIQUIDA'] = np.where(
            df_calc['Receita de Venda de Bens e/ou Serviços'] > 0,
            df_calc['Lucro/Prejuízo Consolidado do Período'] / df_calc['Receita de Venda de Bens e/ou Serviços'],
            np.nan
        )

        df_calc['ROE'] = np.where(
            df_calc['Patrimônio Líquido Consolidado'] > 0,
            df_calc['Lucro/Prejuízo Consolidado do Período'] / df_calc['Patrimônio Líquido Consolidado'],
            np.nan
        )
        
        df_calc['GIRO_ATIVO'] = np.where(
            df_calc['Ativo Total'] > 0,
            df_calc['Receita de Venda de Bens e/ou Serviços'] / df_calc['Ativo Total'],
            np.nan
        )
        
        # 2. INDICADORES DE ESTRUTURA
        df_calc['LIQUIDEZ_CORRENTE'] = np.where(
            df_calc['Passivo Circulante'] > 0,
            df_calc['Ativo Circulante'] / df_calc['Passivo Circulante'],
            np.nan
        )
        
        df_calc['ENDIVIDAMENTO_TOTAL'] = np.where(
            df_calc['Ativo Total'] > 0,
            df_calc['Passivo Total'] / df_calc['Ativo Total'],
            np.nan
        )
        
        df_calc['ALAVANCAGEM'] = np.where(
            df_calc['Patrimônio Líquido Consolidado'] > 0,
            df_calc['Ativo Total'] / df_calc['Patrimônio Líquido Consolidado'],
            np.nan
        )
        
        return df_calc
    
    except KeyError as e:
        st.error(f"❌ Erro: Coluna {e} não encontrada no DataFrame.")
        return pd.DataFrame()

# Carregar os dados
df_analise = load_data()

# Processamento e visualização somente se o DataFrame não estiver vazio
if not df_analise.empty:

    # Cálculo dos indicadores
    df_indicadores = calcular_indicadores_2024(df_analise)
    
    # Adicionar uma coluna de 'Tipo de Atividade' para o filtro
    df_indicadores['Tipo de Atividade'] = df_indicadores['SETOR_ATIV'].apply(lambda x: 'Serviços' if 'Serviços' in x else 'Outros')

    # Exibição do DataFrame processado
    st.subheader("📋 Dados Processados com Indicadores")
    with st.expander("Ver DataFrame"):
        st.dataframe(df_indicadores, use_container_width=True)
    
    # Criação do Filtro
    st.sidebar.header("⚙️ Opções de Filtro")
    setores_unicos = ['Todos'] + sorted(df_indicadores['SETOR_ATIV'].unique())
    setor_selecionado = st.sidebar.selectbox("Selecione o Setor de Atividade", setores_unicos)
    
    if setor_selecionado != 'Todos':
        df_filtrado = df_indicadores[df_indicadores['SETOR_ATIV'] == setor_selecionado]
    else:
        df_filtrado = df_indicadores

    # Título para o gráfico
    st.subheader("📉 Análise Gráfica dos Indicadores")

    # Gráfico de Dispersão
    fig_scatter = px.scatter(
        df_filtrado,
        x='Receita de Venda de Bens e/ou Serviços',
        y='Lucro/Prejuízo Consolidado do Período',
        color='SETOR_ATIV',
        hover_data=['DENOM_CIA', 'Ticker', 'MARGEM_LIQUIDA'],
        title='Receita vs. Lucro por Empresa (2024)',
        labels={
            'Receita de Venda de Bens e/ou Serviços': 'Receita de Vendas (R$)',
            'Lucro/Prejuízo Consolidado do Período': 'Lucro/Prejuízo (R$)'
        }
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Adicionando um espaço entre os gráficos
    st.markdown("---")

    # Gráfico de Barras para os 5 principais
    top_5_receita = df_filtrado.nlargest(5, 'Receita de Venda de Bens e/ou Serviços')
    fig_bar = px.bar(
        top_5_receita,
        x='DENOM_CIA',
        y='Receita de Venda de Bens e/ou Serviços',
        color='SETOR_ATIV',
        title='Top 5 Empresas por Receita de Venda (2024)',
        labels={
            'DENOM_CIA': 'Empresa',
            'Receita de Venda de Bens e/ou Serviços': 'Receita de Vendas (R$)'
        }
    )
    st.plotly_chart(fig_bar, use_container_width=True)
    
    st.markdown("---")

    # Detalhes de uma empresa selecionada
    st.subheader("🔍 Detalhes de uma Empresa Específica")
    empresas_unicas = sorted(df_filtrado['DENOM_CIA'].unique())
    empresa_selecionada = st.selectbox("Selecione a Empresa para Análise Detalhada", empresas_unicas)
    
    if empresa_selecionada:
        empresa_data = df_filtrado[df_filtrado['DENOM_CIA'] == empresa_selecionada].iloc[0]
        st.success(f"📈 Dados de {empresa_selecionada} (2024)")
        
        # Layout em 3 colunas para exibir os indicadores
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("💰 Indicadores de Balanço")
            st.metric("Ativo Total", f"R${empresa_data['Ativo Total']:,.0f}")
            st.metric("Passivo Total", f"R${empresa_data['Passivo Total']:,.0f}")
            st.metric("Patrimônio Líquido", f"R${empresa_data['Patrimônio Líquido Consolidado']:,.0f}")
        
        with col2:
            st.subheader("📊 Indicadores de Rentabilidade")
            st.metric("Margem Bruta", f"{empresa_data['MARGEM_BRUTA']:.1%}" if not pd.isna(empresa_data['MARGEM_BRUTA']) else "N/A")
            st.metric("Margem Líquida", f"{empresa_data['MARGEM_LIQUIDA']:.1%}" if not pd.isna(empresa_data['MARGEM_LIQUIDA']) else "N/A")
            st.metric("ROE", f"{empresa_data['ROE']:.1%}" if not pd.isna(empresa_data['ROE']) else "N/A")
            st.metric("Giro do Ativo", f"{empresa_data['GIRO_ATIVO']:.2f}" if not pd.isna(empresa_data['GIRO_ATIVO']) else "N/A")
        
        with col3:
            st.subheader("🏦 Indicadores de Estrutura")
            st.metric("Liquidez Corrente", f"{empresa_data['LIQUIDEZ_CORRENTE']:.2f}" if not pd.isna(empresa_data['LIQUIDEZ_CORRENTE']) else "N/A")
            st.metric("Endividamento", f"{empresa_data['ENDIVIDAMENTO_TOTAL']:.1%}" if not pd.isna(empresa_data['ENDIVIDAMENTO_TOTAL']) else "N/A")
            st.metric("Alavancagem", f"{empresa_data['ALAVANCAGEM']:.2f}" if not pd.isna(empresa_data['ALAVANCAGEM']) else "N/A")
