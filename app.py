import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuração da página
st.set_page_config(
    page_title="Dashboard CVM - Análise Contábil",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .section-header {
        color: #1f77b4;
        border-bottom: 2px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Header principal
st.markdown('<div class="main-header">📊 Dashboard de Análise Contábil - CVM</div>', unsafe_allow_html=True)

# Barra Lateral - Filtros
with st.sidebar:
    st.header("🔍 Filtros e Controles")
    
    st.subheader("Seleção de Empresa")
    empresa_selecionada = st.selectbox(
        "Empresa:",
        ["Todas as Empresas", "VALE S.A.", "PETROBRAS", "ITÚSA", "BBDC4", "WEGE3"]
    )
    
    st.subheader("Filtros por Setor")
    setor_selecionado = st.selectbox(
        "Setor Econômico:",
        ["Todos os Setores", "Energia Elétrica", "Bancos", "Comércio", "Construção Civil", "Metalurgia"]
    )
    
    st.subheader("Período")
    ano_selecionado = st.radio(
        "Ano de Referência:",
        [2023, 2024, "Todos"],
        horizontal=True
    )
    
    st.subheader("Tipo de Ação")
    tipo_acao = st.multiselect(
        "Selecione os tipos:",
        ["Ordinárias", "Preferenciais", "Units"],
        default=["Ordinárias", "Preferenciais"]
    )
    
    st.markdown("---")
    st.info("💡 **Status do App:**\n\n- ✅ Estrutura carregada\n- 🔄 Aguardando dados\n- 📊 Pronto para análise")

# Abas principais
tab1, tab2, tab3, tab4 = st.tabs(["🏠 Visão Geral", "🏢 Análise por Empresa", "📊 Benchmarking Setorial", "📈 Indicadores Financeiros"])

with tab1:
    st.markdown('<div class="section-header">Visão Geral do Mercado</div>', unsafe_allow_html=True)
    
    # Métricas gerais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total de Empresas",
            value="235",
            delta="+5 vs último ano"
        )
    
    with col2:
        st.metric(
            label="Taxa de Completude",
            value="84.9%",
            delta="2.1%"
        )
    
    with col3:
        st.metric(
            label="Setores Representados",
            value="25",
            delta="3"
        )
    
    with col4:
        st.metric(
            label="Dados Carregados",
            value="738 linhas",
            delta="100%"
        )
    
    # Gráficos de exemplo
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Distribuição por Setor")
        # Gráfico de exemplo
        setores = ['Comércio', 'Energia', 'Construção', 'Bancos', 'Metalurgia']
        empresas = [64, 64, 58, 48, 40]
        
        fig_setores = px.pie(
            values=empresas, 
            names=setores,
            title="Top 5 Setores com Mais Empresas"
        )
        st.plotly_chart(fig_setores, use_container_width=True)
    
    with col_right:
        st.subheader("Completude dos Dados")
        contas = ['Ativo Total', 'Receita', 'Lucro', 'Patrimônio', 'Dividendos']
        completude = [99.6, 99.6, 99.6, 99.6, 94.7]
        
        fig_completude = px.bar(
            x=completude,
            y=contas,
            orientation='h',
            title="Taxa de Preenchimento por Conta (%)",
            labels={'x': 'Percentual (%)', 'y': 'Contas Contábeis'}
        )
        st.plotly_chart(fig_completude, use_container_width=True)

with tab2:
    st.markdown('<div class="section-header">Análise Detalhada por Empresa</div>', unsafe_allow_html=True)
    
    if empresa_selecionada != "Todas as Empresas":
        st.success(f"📈 Analisando dados de: **{empresa_selecionada}**")
        
        # Métricas da empresa
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("💰 Receita")
            st.write("**2024:** R$ 150.2 Mi")
            st.write("**2023:** R$ 142.8 Mi")
            st.write("**Crescimento:** +5.2%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("📊 Lucro Líquido")
            st.write("**2024:** R$ 25.1 Mi")
            st.write("**2023:** R$ 22.3 Mi")
            st.write("**Margem:** 16.7%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="metric-card">', unsafe_allow_html=True)
            st.subheader("🏦 Patrimônio")
            st.write("**2024:** R$ 180.5 Mi")
            st.write("**2023:** R$ 165.2 Mi")
            st.write("**ROE:** 13.9%")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Gráfico de evolução
        st.subheader("Evolução Temporal - Últimos 2 Anos")
        anos = [2023, 2024]
        receitas = [142.8, 150.2]
        lucros = [22.3, 25.1]
        
        fig_evolucao = go.Figure()
        fig_evolucao.add_trace(go.Bar(name='Receita', x=anos, y=receitas, marker_color='blue'))
        fig_evolucao.add_trace(go.Bar(name='Lucro', x=anos, y=lucros, marker_color='green'))
        fig_evolucao.update_layout(title="Evolução de Receita e Lucro (R$ Mi)")
        st.plotly_chart(fig_evolucao, use_container_width=True)
    
    else:
        st.info("👆 Selecione uma empresa específica na barra lateral para ver a análise detalhada.")

with tab3:
    st.markdown('<div class="section-header">Benchmarking Setorial</div>', unsafe_allow_html=True)
    
    st.subheader("Comparativo de Rentabilidade por Setor")
    
    # Dados de exemplo para benchmarking
    setores_bench = ['Energia', 'Bancos', 'Comércio', 'Construção', 'Metalurgia']
    roe_medio = [12.5, 15.8, 8.2, 6.5, 10.1]
    margem_media = [18.2, 25.4, 12.1, 8.7, 14.3]
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        fig_roe = px.bar(
            x=setores_bench,
            y=roe_medio,
            title="ROE Médio por Setor (%)",
            labels={'x': 'Setor', 'y': 'ROE (%)'},
            color=roe_medio,
            color_continuous_scale='Viridis'
        )
        st.plotly_chart(fig_roe, use_container_width=True)
    
    with col_right:
        fig_margem = px.bar(
            x=setores_bench,
            y=margem_media,
            title="Margem Líquida Média por Setor (%)",
            labels={'x': 'Setor', 'y': 'Margem (%)'},
            color=margem_media,
            color_continuous_scale='Plasma'
        )
        st.plotly_chart(fig_margem, use_container_width=True)

with tab4:
    st.markdown('<div class="section-header">Indicadores e Múltiplos Financeiros</div>', unsafe_allow_html=True)
    
    st.info("🧮 Esta seção calculará automaticamente os principais indicadores financeiros a partir dos dados contábeis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Indicadores de Rentabilidade")
        st.write("- **ROE (Return on Equity):** Lucro Líquido / Patrimônio Líquido")
        st.write("- **ROA (Return on Assets):** Lucro Líquido / Ativo Total")
        st.write("- **Margem Bruta:** Resultado Bruto / Receita")
        st.write("- **Margem Líquida:** Lucro Líquido / Receita")
    
    with col2:
        st.subheader("Indicadores de Liquidez")
        st.write("- **Liquidez Corrente:** Ativo Circulante / Passivo Circulante")
        st.write("- **Liquidez Seca:** (Ativo Circulante - Estoques) / Passivo Circulante")
        st.write("- **Liquidez Geral:** (Ativo Circulante + Realizável LP) / (Passivo Circulante + Exigível LP)")
    
    st.subheader("Calculadora de Múltiplos")
    
    calc_col1, calc_col2, calc_col3 = st.columns(3)
    
    with calc_col1:
        preco_acao = st.number_input("Preço da Ação (R$)", value=50.0)
    
    with calc_col2:
        lucro_por_acao = st.number_input("LPA - Lucro por Ação (R$)", value=4.0)
    
    with calc_col3:
        valor_patrimonial_acao = st.number_input("VPA - Valor Patrimonial por Ação (R$)", value=35.0)
    
    if st.button("Calcular Múltiplos"):
        p_l = preco_acao / lucro_por_acao
        p_vp = preco_acao / valor_patrimonial_acao
        
        st.success(f"""
        **Resultados:**
        - **P/L (Preço/Lucro):** {p_l:.2f}
        - **P/VP (Preço/Valor Patrimonial):** {p_vp:.2f}
        """)

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        📊 <strong>Dashboard CVM</strong> - Desenvolvido para análise de dados contábeis | 
        Dados: Comissão de Valores Mobiliários | Última atualização: Outubro 2024
    </div>
    """, 
    unsafe_allow_html=True
)
