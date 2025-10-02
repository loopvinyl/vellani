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
        
        # ROE (usando Patrimônio Líquido do final do período para 2024)
        df_calc['ROE'] = np.where(
            df_calc['Patrimônio Líquido Consolidado'] != 0,
            df_calc['Lucro/Prejuízo Consolidado do Período'] / df_calc['Patrimônio Líquido Consolidado'],
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
        
        df_calc['ALAVANCAGEM_FINANCEIRA'] = np.where(
            df_calc['Patrimônio Líquido Consolidado'] != 0,
            df_calc['Passivo Total'] / df_calc['Patrimônio Líquido Consolidado'],
            np.nan
        )
        
        # 4. INDICADORES DE EFICIÊNCIA
        df_calc['GIRO_ATIVO'] = np.where(
            df_calc['Ativo Total'] != 0,
            df_calc['Receita de Venda de Bens e/ou Serviços'] / df_calc['Ativo Total'],
            np.nan
        )
        
        # 5. INDICADORES DE FLUXO DE CAIXA
        df_calc['FCO_RECEITA'] = np.where(
            df_calc['Receita de Venda de Bens e/ou Serviços'] != 0,
            df_calc['Caixa Líquido Atividades Operacionais'] / df_calc['Receita de Venda de Bens e/ou Serviços'],
            np.nan
        )
        
        # 6. INDICADORES DE CUSTO
        emprestimos_total = df_calc['Empréstimos e Financiamentos - Circulante'].fillna(0) + df_calc['Empréstimos e Financiamentos - Não Circulante'].fillna(0)
        df_calc['CUSTO_DIVIDA'] = np.where(
            emprestimos_total != 0,
            df_calc['Despesas Financeiras'] / emprestimos_total,
            np.nan
        )
        
        st.success("✅ Indicadores calculados com sucesso!")
        
    except Exception as e:
        st.error(f"❌ Erro ao calcular indicadores: {e}")
    
    return df_calc

# Carregar dados
df_2024 = load_data()

if df_2024.empty:
    st.error("Não foi possível carregar os dados de 2024.")
    st.stop()

# Calcular indicadores
df_2024 = calcular_indicadores_2024(df_2024)

# Sidebar
st.sidebar.header("🔍 Filtros")

# Filtro por setor
setores = st.sidebar.multiselect(
    "Setores Econômicos",
    options=df_2024['SETOR_ATIV'].unique(),
    default=df_2024['SETOR_ATIV'].unique()[:3]
)

# Filtro por tipo de ação
tipos_acao = st.sidebar.multiselect(
    "Tipo de Ação",
    options=df_2024['Tipo_Acao'].unique(),
    default=df_2024['Tipo_Acao'].unique()
)

# Filtro por empresa
empresas = st.sidebar.multiselect(
    "Empresas",
    options=df_2024['DENOM_CIA'].unique()
)

# Aplicar filtros
if setores:
    df_2024 = df_2024[df_2024['SETOR_ATIV'].isin(setores)]
if tipos_acao:
    df_2024 = df_2024[df_2024['Tipo_Acao'].isin(tipos_acao)]
if empresas:
    df_2024 = df_2024[df_2024['DENOM_CIA'].isin(empresas)]

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
        st.metric("Setores", df_2024['SETOR_ATIV'].nunique())
    with col3:
        margem_media = df_2024['MARGEM_LIQUIDA'].mean()
        st.metric("Margem Líquida Média", f"{margem_media:.1%}" if not pd.isna(margem_media) else "N/A")
    with col4:
        roe_medio = df_2024['ROE'].mean()
        st.metric("ROE Médio", f"{roe_medio:.1%}" if not pd.isna(roe_medio) else "N/A")

    # Top empresas por lucro
    st.subheader("🏆 Top 10 Empresas - Maior Lucro Líquido")
    top_lucro = df_2024.nlargest(10, 'Lucro/Prejuízo Consolidado do Período')[['DENOM_CIA', 'Ticker', 'Lucro/Prejuízo Consolidado do Período', 'MARGEM_LIQUIDA', 'ROE']]
    st.dataframe(top_lucro.style.format({
        'Lucro/Prejuízo Consolidado do Período': 'R$ {:,.0f}',
        'MARGEM_LIQUIDA': '{:.1%}',
        'ROE': '{:.1%}'
    }))

with tab2:
    st.header("📊 Análise de Rentabilidade")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Distribuição de Margem Líquida
        fig = px.histogram(df_2024, x='MARGEM_LIQUIDA', 
                          title='Distribuição da Margem Líquida',
                          labels={'MARGEM_LIQUIDA': 'Margem Líquida'},
                          nbins=30)
        fig.update_layout(xaxis_tickformat='.0%')
        st.plotly_chart(fig)
    
    with col2:
        # Margem Bruta vs Margem Líquida
        fig = px.scatter(df_2024, x='MARGEM_BRUTA', y='MARGEM_LIQUIDA',
                        hover_data=['DENOM_CIA', 'Ticker'],
                        title='Margem Bruta vs Margem Líquida',
                        labels={'MARGEM_BRUTA': 'Margem Bruta', 'MARGEM_LIQUIDA': 'Margem Líquida'})
        fig.update_layout(xaxis_tickformat='.0%', yaxis_tickformat='.0%')
        st.plotly_chart(fig)
    
    # ROE por setor
    st.subheader("📈 ROE por Setor Econômico")
    roe_setor = df_2024.groupby('SETOR_ATIV')['ROE'].mean().sort_values(ascending=False)
    fig = px.bar(roe_setor, 
                 title='ROE Médio por Setor',
                 labels={'value': 'ROE', 'SETOR_ATIV': 'Setor Econômico'})
    fig.update_layout(yaxis_tickformat='.0%')
    st.plotly_chart(fig)

with tab3:
    st.header("🏦 Liquidez e Endividamento")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Liquidez Corrente
        fig = px.box(df_2024, y='LIQUIDEZ_CORRENTE', 
                    title='Distribuição da Liquidez Corrente',
                    labels={'LIQUIDEZ_CORRENTE': 'Liquidez Corrente'})
        st.plotly_chart(fig)
        
        # Composição do Endividamento
        fig = px.histogram(df_2024, x='COMPOSICAO_ENDIVIDAMENTO',
                          title='Composição do Endividamento',
                          labels={'COMPOSICAO_ENDIVIDAMENTO': '% Passivo Circulante / Total'})
        fig.update_layout(xaxis_tickformat='.0%')
        st.plotly_chart(fig)
    
    with col2:
        # Endividamento Total
        fig = px.histogram(df_2024, x='ENDIVIDAMENTO_TOTAL',
                          title='Distribuição do Endividamento Total',
                          labels={'ENDIVIDAMENTO_TOTAL': 'Passivo / Ativo'})
        fig.update_layout(xaxis_tickformat='.0%')
        st.plotly_chart(fig)
        
        # Alavancagem Financeira
        fig = px.box(df_2024, y='ALAVANCAGEM_FINANCEIRA',
                    title='Alavancagem Financeira',
                    labels={'ALAVANCAGEM_FINANCEIRA': 'Passivo / PL'})
        st.plotly_chart(fig)

with tab4:
    st.header("📈 Análise Setorial")
    
    # Métricas por setor
    setor_analysis = df_2024.groupby('SETOR_ATIV').agg({
        'MARGEM_LIQUIDA': 'mean',
        'ROE': 'mean',
        'LIQUIDEZ_CORRENTE': 'mean',
        'ENDIVIDAMENTO_TOTAL': 'mean',
        'GIRO_ATIVO': 'mean',
        'DENOM_CIA': 'count'
    }).round(4).sort_values('MARGEM_LIQUIDA', ascending=False)
    
    setor_analysis = setor_analysis.rename(columns={'DENOM_CIA': 'Nº Empresas'})
    
    st.dataframe(setor_analysis.style.format({
        'MARGEM_LIQUIDA': '{:.1%}',
        'ROE': '{:.1%}',
        'LIQUIDEZ_CORRENTE': '{:.2f}',
        'ENDIVIDAMENTO_TOTAL': '{:.1%}',
        'GIRO_ATIVO': '{:.2f}'
    }))

with tab5:
    st.header("🔍 Dados Detalhados por Empresa")
    
    # Seletor de empresa para detalhes
    empresa_selecionada = st.selectbox(
        "Selecione uma empresa para detalhes:",
        options=df_2024['DENOM_CIA'].unique()
    )
    
    if empresa_selecionada:
        empresa_data = df_2024[df_2024['DENOM_CIA'] == empresa_selecionada].iloc[0]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("💰 Dados Financeiros")
            st.metric("Receita", f"R$ {empresa_data['Receita de Venda de Bens e/ou Serviços']:,.0f}")
            st.metric("Lucro Líquido", f"R$ {empresa_data['Lucro/Prejuízo Consolidado do Período']:,.0f}")
            st.metric("Ativo Total", f"R$ {empresa_data['Ativo Total']:,.0f}")
            st.metric("Patrimônio Líquido", f"R$ {empresa_data['Patrimônio Líquido Consolidado']:,.0f}")
        
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
            st.metric("Alavancagem", f"{empresa_data['ALAVANCAGEM_FINANCEIRA']:.2f}" if not pd.isna(empresa_data['ALAVANCAGEM_FINANCEIRA']) else "N/A")
            st.metric("Composição Endivid.", f"{empresa_data['COMPOSICAO_ENDIVIDAMENTO']:.1%}" if not pd.isna(empresa_data['COMPOSICAO_ENDIVIDAMENTO']) else "N/A")

# Rodapé
st.sidebar.markdown("---")
st.sidebar.markdown("**Fonte:** Dados CVM - 2024")
st.sidebar.markdown(f"**Última atualização:** {datetime.now().strftime('%d/%m/%Y %H:%M')}")
