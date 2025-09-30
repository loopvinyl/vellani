import streamlit as st
import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import warnings
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Análise de Empresas - Indicadores Financeiros",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Funções principais
@st.cache_data
def carregar_dados():
    """Carrega o dataframe principal"""
    try:
        df = pd.read_excel('/content/data_frame.xlsx')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

@st.cache_data(ttl=3600)  # Cache de 1 hora para cotações
def buscar_cotacao_atual(ticker):
    """Busca cotação atual no Yahoo Finance"""
    try:
        if not ticker.endswith('.SA'):
            ticker_yahoo = f"{ticker}.SA"
        else:
            ticker_yahoo = ticker
            
        acao = yf.Ticker(ticker_yahoo)
        hist = acao.history(period='1d')
        
        if not hist.empty:
            return hist['Close'].iloc[-1]
        else:
            return None
    except Exception:
        return None

def calcular_indicadores_fixos(dados_empresa):
    """Calcula indicadores com SELIC fixa de 15%"""
    try:
        # Extrair dados básicos
        ativo_total = dados_empresa.get('Ativo Total', 0)
        receita = dados_empresa.get('Receita de Venda de Bens e/ou Serviços', 1)
        lucro = dados_empresa.get('Lucro/Prejuízo Consolidado do Período', 0)
        pl = dados_empresa.get('Patrimônio Líquido Consolidado', 1)
        ativo_circulante = dados_empresa.get('Ativo Circulante', 0)
        passivo_circulante = dados_empresa.get('Passivo Circulante', 1)
        passivo_total = dados_empresa.get('Passivo Total', 1)
        
        # Calcular indicadores
        margem_liquida = (lucro / receita) * 100 if receita > 0 else 0
        roe = (lucro / pl) * 100 if pl > 0 else 0
        roa = (lucro / ativo_total) * 100 if ativo_total > 0 else 0
        liquidez_corrente = ativo_circulante / passivo_circulante if passivo_circulante > 0 else 0
        endividamento = passivo_total / ativo_total if ativo_total > 0 else 0
        
        return {
            'Margem Líquida': margem_liquida,
            'ROE': roe,
            'ROA': roa,
            'Liquidez Corrente': liquidez_corrente,
            'Endividamento': endividamento,
            'SELIC_Utilizada': 0.15
        }
    except Exception as e:
        st.error(f"Erro no cálculo de indicadores: {e}")
        return None

def calcular_selic_ajustada(dados_empresa, cotacao_atual):
    """Calcula SELIC ajustada para igualar cotação esperada à atual"""
    try:
        # Simulação simplificada do cálculo da SELIC ajustada
        # Na prática, isso replicaria a lógica da planilha "Indicadores"
        
        lucro = dados_empresa.get('Lucro/Prejuízo Consolidado do Período', 0)
        pl = dados_empresa.get('Patrimônio Líquido Consolidado', 1)
        
        # Fator de ajuste baseado no ROE e cotação
        roe = (lucro / pl) * 100 if pl > 0 else 0
        
        # SELIC base ajustada pelo ROE e diferença de valuation
        selic_base = 0.15
        fator_ajuste = max(0.05, min(0.25, selic_base * (roe / 15)))  # Limita entre 5% e 25%
        
        # Ajuste final baseado na "atratividade" (simplificado)
        if cotacao_atual > 0:
            # Se ROE alto e cotação baixa, SELIC mais baixa (mais atrativo)
            if roe > 20:
                selic_ajustada = max(0.08, fator_ajuste * 0.8)
            elif roe > 10:
                selic_ajustada = fator_ajuste
            else:
                selic_ajustada = min(0.25, fator_ajuste * 1.2)
        else:
            selic_ajustada = fator_ajuste
            
        return selic_ajustada
    except Exception:
        return 0.15

def criar_ranking_empresas(df):
    """Cria ranking das empresas baseado em múltiplos critérios"""
    try:
        ranking_data = []
        
        for _, empresa in df.iterrows():
            ticker = empresa.get('Ticker', '')
            if not ticker:
                continue
                
            # Buscar cotação atual
            cotacao_atual = buscar_cotacao_atual(ticker)
            
            # Calcular indicadores com SELIC fixa
            indicadores_fixos = calcular_indicadores_fixos(empresa)
            
            if indicadores_fixos:
                # Calcular SELIC ajustada
                selic_ajustada = calcular_selic_ajustada(empresa, cotacao_atual)
                
                # Score composto para ranking
                score = (
                    indicadores_fixos['ROE'] * 0.3 +
                    indicadores_fixos['ROA'] * 0.2 +
                    indicadores_fixos['Margem Líquida'] * 0.2 +
                    (1/indicadores_fixos['Endividamento'] if indicadores_fixos['Endividamento'] > 0 else 0) * 0.3
                )
                
                ranking_data.append({
                    'Ticker': ticker,
                    'Empresa': empresa.get('Nome_Empresa', ticker),
                    'Setor': empresa.get('Setor', 'N/A'),
                    'Cotacao_Atual': cotacao_atual or 0,
                    'ROE': indicadores_fixos['ROE'],
                    'ROA': indicadores_fixos['ROA'],
                    'Margem_Liquida': indicadores_fixos['Margem Líquida'],
                    'Liquidez_Corrente': indicadores_fixos['Liquidez Corrente'],
                    'Endividamento': indicadores_fixos['Endividamento'],
                    'SELIC_Fixa': 0.15,
                    'SELIC_Ajustada': selic_ajustada,
                    'Score_Ranking': score
                })
        
        ranking_df = pd.DataFrame(ranking_data)
        return ranking_df.sort_values('Score_Ranking', ascending=False)
        
    except Exception as e:
        st.error(f"Erro ao criar ranking: {e}")
        return pd.DataFrame()

# Interface Streamlit
def main():
    st.title("📊 Análise de Empresas - Indicadores Financeiros")
    st.markdown("---")
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        df = carregar_dados()
    
    if df is None:
        st.error("Não foi possível carregar os dados. Verifique o arquivo.")
        return
    
    # Sidebar
    st.sidebar.title("🔧 Configurações")
    
    # Filtros
    st.sidebar.subheader("Filtros")
    
    # Seleção de tickers únicos
    tickers_unicos = df['Ticker'].unique() if 'Ticker' in df.columns else []
    ticker_selecionado = st.sidebar.selectbox(
        "Selecione um Ticker para análise detalhada:",
        options=tickers_unicos
    )
    
    # Navegação
    pagina = st.sidebar.radio(
        "Navegação:",
        ["🏆 Ranking Geral", "📈 Análise por Empresa", "📋 Todos os Indicadores"]
    )
    
    # Página 1: Ranking Geral
    if pagina == "🏆 Ranking Geral":
        st.header("🏆 Ranking das Melhores Empresas")
        
        with st.spinner("Calculando rankings..."):
            ranking_df = criar_ranking_empresas(df)
        
        if not ranking_df.empty:
            # Métricas gerais
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total de Empresas", len(ranking_df))
            with col2:
                st.metric("ROE Médio", f"{ranking_df['ROE'].mean():.1f}%")
            with col3:
                st.metric("ROA Médio", f"{ranking_df['ROA'].mean():.1f}%")
            with col4:
                st.metric("SELIC Ajustada Média", f"{ranking_df['SELIC_Ajustada'].mean()*100:.1f}%")
            
            # Tabela de ranking
            st.subheader("Top 20 Empresas")
            
            # Formatação da tabela
            display_cols = ['Ticker', 'Empresa', 'Setor', 'Cotacao_Atual', 'ROE', 'ROA', 
                          'Margem_Liquida', 'SELIC_Ajustada', 'Score_Ranking']
            
            formatted_df = ranking_df[display_cols].head(20).copy()
            formatted_df['Cotacao_Atual'] = formatted_df['Cotacao_Atual'].apply(
                lambda x: f"R$ {x:.2f}" if x > 0 else "N/A"
            )
            formatted_df['ROE'] = formatted_df['ROE'].apply(lambda x: f"{x:.1f}%")
            formatted_df['ROA'] = formatted_df['ROA'].apply(lambda x: f"{x:.1f}%")
            formatted_df['Margem_Liquida'] = formatted_df['Margem_Liquida'].apply(lambda x: f"{x:.1f}%")
            formatted_df['SELIC_Ajustada'] = formatted_df['SELIC_Ajustada'].apply(lambda x: f"{x*100:.1f}%")
            formatted_df['Score_Ranking'] = formatted_df['Score_Ranking'].apply(lambda x: f"{x:.1f}")
            
            st.dataframe(formatted_df, use_container_width=True)
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                # Top 10 por ROE
                fig_roe = px.bar(
                    ranking_df.head(10),
                    x='Ticker',
                    y='ROE',
                    title='Top 10 - Maior ROE',
                    color='ROE',
                    color_continuous_scale='viridis'
                )
                st.plotly_chart(fig_roe, use_container_width=True)
            
            with col2:
                # Distribuição da SELIC Ajustada
                fig_selic = px.histogram(
                    ranking_df,
                    x='SELIC_Ajustada',
                    title='Distribuição da SELIC Ajustada',
                    nbins=20
                )
                fig_selic.update_layout(xaxis_title="SELIC Ajustada", yaxis_title="Quantidade de Empresas")
                st.plotly_chart(fig_selic, use_container_width=True)
        
    # Página 2: Análise por Empresa
    elif pagina == "📈 Análise por Empresa":
        st.header(f"📈 Análise Detalhada - {ticker_selecionado}")
        
        # Buscar dados da empresa selecionada
        empresa_data = df[df['Ticker'] == ticker_selecionado].iloc[0]
        cotacao_atual = buscar_cotacao_atual(ticker_selecionado)
        
        if cotacao_atual:
            st.success(f"✅ Cotação atual: R$ {cotacao_atual:.2f}")
        else:
            st.warning("⚠️ Cotação não disponível")
        
        # Calcular indicadores
        indicadores_fixos = calcular_indicadores_fixos(empresa_data)
        selic_ajustada = calcular_selic_ajustada(empresa_data, cotacao_atual)
        
        if indicadores_fixos:
            # Métricas principais
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("ROE", f"{indicadores_fixos['ROE']:.1f}%")
            with col2:
                st.metric("ROA", f"{indicadores_fixos['ROA']:.1f}%")
            with col3:
                st.metric("Margem Líquida", f"{indicadores_fixos['Margem Líquida']:.1f}%")
            with col4:
                st.metric("Liquidez Corrente", f"{indicadores_fixos['Liquidez Corrente']:.2f}")
            
            # Comparação SELIC
            st.subheader("🔍 Comparação de Cenários de SELIC")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.info("**SELIC Oficial (15%)**")
                st.metric("Taxa SELIC", "15.0%")
                # Aqui viriam os cálculos com SELIC fixa
                # Simulação de valuation com SELIC fixa
                if cotacao_atual:
                    valuation_fixo = cotacao_atual * (0.15 / selic_ajustada) if selic_ajustada > 0 else cotacao_atual
                    st.metric("Valuation Estimado", f"R$ {valuation_fixo:.2f}")
            
            with col2:
                st.success("**SELIC Ajustada**")
                st.metric("Taxa SELIC", f"{selic_ajustada*100:.1f}%")
                # Valuation com SELIC ajustada
                if cotacao_atual:
                    valuation_ajustado = cotacao_atual
                    st.metric("Valuation Estimado", f"R$ {valuation_ajustado:.2f}")
            
            # Gráfico de indicadores
            st.subheader("📊 Indicadores Financeiros")
            
            indicadores_graf = {
                'ROE': indicadores_fixos['ROE'],
                'ROA': indicadores_fixos['ROA'],
                'Margem Líquida': indicadores_fixos['Margem Líquida'],
                'Liquidez Corrente': min(indicadores_fixos['Liquidez Corrente'], 10),  # Limitando para visualização
                'Endividamento': min(indicadores_fixos['Endividamento'] * 100, 100)  # Convertendo para %
            }
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                x=list(indicadores_graf.keys()),
                y=list(indicadores_graf.values()),
                marker_color='lightblue'
            ))
            fig.update_layout(title="Indicadores Financeiros da Empresa")
            st.plotly_chart(fig, use_container_width=True)
    
    # Página 3: Todos os Indicadores
    else:
        st.header("📋 Todos os Indicadores por Empresa")
        
        with st.spinner("Processando todas as empresas..."):
            resultados = []
            
            for _, empresa in df.iterrows():
                ticker = empresa.get('Ticker', '')
                if ticker:
                    cotacao_atual = buscar_cotacao_atual(ticker)
                    indicadores = calcular_indicadores_fixos(empresa)
                    selic_ajustada = calcular_selic_ajustada(empresa, cotacao_atual)
                    
                    if indicadores:
                        resultados.append({
                            'Ticker': ticker,
                            'Empresa': empresa.get('Nome_Empresa', ticker),
                            'Cotacao_Atual': cotacao_atual or 0,
                            'ROE': indicadores['ROE'],
                            'ROA': indicadores['ROA'],
                            'Margem_Liquida': indicadores['Margem Líquida'],
                            'Liquidez_Corrente': indicadores['Liquidez Corrente'],
                            'Endividamento': indicadores['Endividamento'],
                            'SELIC_Ajustada': selic_ajustada
                        })
            
            resultados_df = pd.DataFrame(resultados)
        
        if not resultados_df.empty:
            # Formatação
            display_df = resultados_df.copy()
            display_df['Cotacao_Atual'] = display_df['Cotacao_Atual'].apply(
                lambda x: f"R$ {x:.2f}" if x > 0 else "N/A"
            )
            display_df['ROE'] = display_df['ROE'].apply(lambda x: f"{x:.1f}%")
            display_df['ROA'] = display_df['ROA'].apply(lambda x: f"{x:.1f}%")
            display_df['Margem_Liquida'] = display_df['Margem_Liquida'].apply(lambda x: f"{x:.1f}%")
            display_df['Liquidez_Corrente'] = display_df['Liquidez_Corrente'].apply(lambda x: f"{x:.2f}")
            display_df['Endividamento'] = display_df['Endividamento'].apply(lambda x: f"{x:.2f}")
            display_df['SELIC_Ajustada'] = display_df['SELIC_Ajustada'].apply(lambda x: f"{x*100:.1f}%")
            
            st.dataframe(display_df, use_container_width=True)
            
            # Botão de download
            csv = resultados_df.to_csv(index=False)
            st.download_button(
                label="📥 Download CSV Completo",
                data=csv,
                file_name=f"indicadores_empresas_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )

    # Footer
    st.markdown("---")
    st.markdown(
        "**Desenvolvido com Streamlit** | "
        "📊 Indicadores calculados com base nos dados da CVM | "
        "💰 Cotações em tempo real do Yahoo Finance"
    )

if __name__ == "__main__":
    main()
