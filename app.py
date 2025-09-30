import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

# Configuração da página
st.set_page_config(
    page_title="Análise de Empresas - Indicadores Financeiros",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Tenta importar yfinance com fallback
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    st.warning("yfinance não disponível - usando dados estáticos")

# Funções principais
@st.cache_data
def carregar_dados():
    """Carrega o dataframe principal"""
    try:
        df = pd.read_excel('data_frame.xlsx')
        st.sidebar.success(f"✅ Dados carregados: {len(df)} linhas")
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

def buscar_cotacao_atual(ticker):
    """Busca cotação atual no Yahoo Finance com fallback"""
    if not YFINANCE_AVAILABLE:
        return None
        
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
        resultado_bruto = dados_empresa.get('Resultado Bruto', 0)
        
        # Converter para float e tratar valores missing
        ativo_total = float(ativo_total) if pd.notna(ativo_total) else 0
        receita = float(receita) if pd.notna(receita) and float(receita) != 0 else 1
        lucro = float(lucro) if pd.notna(lucro) else 0
        pl = float(pl) if pd.notna(pl) and float(pl) != 0 else 1
        ativo_circulante = float(ativo_circulante) if pd.notna(ativo_circulante) else 0
        passivo_circulante = float(passivo_circulante) if pd.notna(passivo_circulante) and float(passivo_circulante) != 0 else 1
        passivo_total = float(passivo_total) if pd.notna(passivo_total) else 1
        resultado_bruto = float(resultado_bruto) if pd.notna(resultado_bruto) else 0
        
        # Calcular indicadores com proteção contra divisão por zero
        margem_bruta = (resultado_bruto / receita) * 100 if receita > 0 else 0
        margem_liquida = (lucro / receita) * 100 if receita > 0 else 0
        roe = (lucro / pl) * 100 if pl > 0 else 0
        roa = (lucro / ativo_total) * 100 if ativo_total > 0 else 0
        liquidez_corrente = ativo_circulante / passivo_circulante if passivo_circulante > 0 else 0
        endividamento = passivo_total / ativo_total if ativo_total > 0 else 0
        giro_ativo = receita / ativo_total if ativo_total > 0 else 0
        
        return {
            'Margem_Bruta': margem_bruta,
            'Margem_Liquida': margem_liquida,
            'ROE': roe,
            'ROA': roa,
            'Liquidez_Corrente': liquidez_corrente,
            'Endividamento': endividamento,
            'Giro_Ativo': giro_ativo,
            'SELIC_Utilizada': 0.15
        }
    except Exception as e:
        st.warning(f"Erro no cálculo de indicadores: {e}")
        return None

def calcular_selic_ajustada(dados_empresa, cotacao_atual):
    """Calcula SELIC ajustada baseada nos indicadores"""
    try:
        if cotacao_atual is None or cotacao_atual <= 0:
            return 0.15
            
        # Dados da empresa
        lucro = dados_empresa.get('Lucro/Prejuízo Consolidado do Período', 0)
        pl = dados_empresa.get('Patrimônio Líquido Consolidado', 1)
        ativo_total = dados_empresa.get('Ativo Total', 0)
        receita = dados_empresa.get('Receita de Venda de Bens e/ou Serviços', 1)
        
        lucro = float(lucro) if pd.notna(lucro) else 0
        pl = float(pl) if pd.notna(pl) and float(pl) != 0 else 1
        ativo_total = float(ativo_total) if pd.notna(ativo_total) else 0
        receita = float(receita) if pd.notna(receita) and float(receita) != 0 else 1
        
        # Cálculo do ROE
        roe = (lucro / pl) * 100 if pl > 0 else 0
        
        # SELIC base ajustada pela qualidade dos indicadores
        if roe > 20:
            selic_ajuste = 0.08
        elif roe > 15:
            selic_ajuste = 0.10
        elif roe > 10:
            selic_ajuste = 0.12
        elif roe > 5:
            selic_ajuste = 0.15
        elif roe > 0:
            selic_ajuste = 0.18
        else:
            selic_ajuste = 0.22
            
        return max(0.05, min(0.25, selic_ajuste))
        
    except Exception:
        return 0.15

def criar_ranking_empresas(df):
    """Cria ranking das empresas"""
    try:
        ranking_data = []
        tickers_processados = 0
        
        # Obter tickers únicos
        tickers_unicos = df['Ticker'].dropna().unique()
        
        for ticker in tickers_unicos[:50]:  # Limite para performance
            try:
                # Buscar dados da empresa
                empresa_data = df[df['Ticker'] == ticker].iloc[0]
                
                # Buscar cotação atual
                cotacao_atual = buscar_cotacao_atual(str(ticker).strip())
                
                # Calcular indicadores
                indicadores_fixos = calcular_indicadores_fixos(empresa_data)
                
                if indicadores_fixos:
                    # Calcular SELIC ajustada
                    selic_ajustada = calcular_selic_ajustada(empresa_data, cotacao_atual)
                    
                    # Score composto para ranking
                    score = (
                        indicadores_fixos['ROE'] * 0.25 +
                        indicadores_fixos['ROA'] * 0.20 +
                        indicadores_fixos['Margem_Liquida'] * 0.20 +
                        indicadores_fixos['Liquidez_Corrente'] * 0.15 +
                        (1 - min(indicadores_fixos['Endividamento'], 1)) * 0.20
                    )
                    
                    ranking_data.append({
                        'Ticker': str(ticker).strip(),
                        'Cotacao_Atual': cotacao_atual or 0,
                        'ROE': indicadores_fixos['ROE'],
                        'ROA': indicadores_fixos['ROA'],
                        'Margem_Bruta': indicadores_fixos['Margem_Bruta'],
                        'Margem_Liquida': indicadores_fixos['Margem_Liquida'],
                        'Liquidez_Corrente': indicadores_fixos['Liquidez_Corrente'],
                        'Endividamento': indicadores_fixos['Endividamento'],
                        'Giro_Ativo': indicadores_fixos['Giro_Ativo'],
                        'SELIC_Fixa': 0.15,
                        'SELIC_Ajustada': selic_ajustada,
                        'Score_Ranking': score
                    })
                    
                    tickers_processados += 1
            except Exception:
                continue
        
        if not ranking_data:
            return pd.DataFrame()
            
        ranking_df = pd.DataFrame(ranking_data)
        return ranking_df.sort_values('Score_Ranking', ascending=False)
        
    except Exception as e:
        st.error(f"Erro ao criar ranking: {e}")
        return pd.DataFrame()

# Interface Streamlit
def main():
    st.title("📊 Análise de Empresas - Indicadores Financeiros")
    st.markdown("Analisando dados contábeis da CVM - 2023/2024")
    st.markdown("---")
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        df = carregar_dados()
    
    if df is None:
        st.error("Não foi possível carregar os dados. Verifique o arquivo 'data_frame.xlsx'")
        return
    
    # Informações do dataset
    st.sidebar.title("🔧 Configurações")
    st.sidebar.info(f"📊 {len(df)} linhas carregadas")
    st.sidebar.info(f"🎯 {df['Ticker'].nunique()} tickers únicos")
    
    if not YFINANCE_AVAILABLE:
        st.sidebar.warning("⚠️ yfinance não disponível")
    
    # Seleção de tickers
    tickers_unicos = df['Ticker'].dropna().unique()
    tickers_unicos = sorted([str(t) for t in tickers_unicos])
    
    ticker_selecionado = st.sidebar.selectbox(
        "Selecione um Ticker:",
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
                st.metric("Empresas Analisadas", len(ranking_df))
            with col2:
                st.metric("ROE Médio", f"{ranking_df['ROE'].mean():.1f}%")
            with col3:
                st.metric("ROA Médio", f"{ranking_df['ROA'].mean():.1f}%")
            with col4:
                st.metric("SELIC Ajustada Média", f"{ranking_df['SELIC_Ajustada'].mean()*100:.1f}%")
            
            # Tabela de ranking
            st.subheader("Top 20 Empresas")
            
            # Formatação
            display_df = ranking_df.head(20).copy()
            display_df['Cotacao_Atual'] = display_df['Cotacao_Atual'].apply(
                lambda x: f"R$ {x:.2f}" if x > 0 else "N/A"
            )
            for col in ['ROE', 'ROA', 'Margem_Bruta', 'Margem_Liquida']:
                display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}%")
            display_df['SELIC_Ajustada'] = display_df['SELIC_Ajustada'].apply(lambda x: f"{x*100:.1f}%")
            display_df['Score_Ranking'] = display_df['Score_Ranking'].apply(lambda x: f"{x:.1f}")
            
            st.dataframe(display_df[['Ticker', 'Cotacao_Atual', 'ROE', 'ROA', 'Margem_Liquida', 'SELIC_Ajustada', 'Score_Ranking']], 
                        use_container_width=True)
            
            # Gráficos
            col1, col2 = st.columns(2)
            
            with col1:
                fig_roe = px.bar(
                    ranking_df.head(10),
                    x='Ticker',
                    y='ROE',
                    title='Top 10 - Maior ROE'
                )
                st.plotly_chart(fig_roe, use_container_width=True)
            
            with col2:
                fig_selic = px.histogram(
                    ranking_df,
                    x='SELIC_Ajustada',
                    title='Distribuição da SELIC Ajustada'
                )
                st.plotly_chart(fig_selic, use_container_width=True)
        
        else:
            st.error("Não foi possível gerar o ranking.")
    
    # Página 2: Análise por Empresa
    elif pagina == "📈 Análise por Empresa":
        st.header(f"📈 Análise Detalhada - {ticker_selecionado}")
        
        try:
            empresa_data = df[df['Ticker'] == ticker_selecionado].iloc[0]
            cotacao_atual = buscar_cotacao_atual(ticker_selecionado)
            indicadores = calcular_indicadores_fixos(empresa_data)
            selic_ajustada = calcular_selic_ajustada(empresa_data, cotacao_atual)
            
            if indicadores:
                # Informações básicas
                col1, col2 = st.columns(2)
                with col1:
                    if cotacao_atual:
                        st.success(f"💰 Cotação: R$ {cotacao_atual:.2f}")
                    else:
                        st.warning("💰 Cotação: Não disponível")
                with col2:
                    st.info(f"🔧 SELIC Ajustada: {selic_ajustada*100:.1f}%")
                
                # Métricas
                st.subheader("📊 Indicadores Principais")
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("ROE", f"{indicadores['ROE']:.1f}%")
                with col2:
                    st.metric("ROA", f"{indicadores['ROA']:.1f}%")
                with col3:
                    st.metric("Margem Líquida", f"{indicadores['Margem_Liquida']:.1f}%")
                with col4:
                    st.metric("Liquidez", f"{indicadores['Liquidez_Corrente']:.2f}")
                
                # Comparação SELIC
                st.subheader("🔍 Comparação de Cenários")
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info("**SELIC Oficial (15%)**")
                    st.metric("Taxa", "15.0%")
                
                with col2:
                    st.success("**SELIC Ajustada**")
                    st.metric("Taxa", f"{selic_ajustada*100:.1f}%")
                
                # Gráfico
                st.subheader("📈 Perfil de Indicadores")
                indicadores_graf = {
                    'ROE': indicadores['ROE'],
                    'ROA': indicadores['ROA'],
                    'Margem Líquida': indicadores['Margem_Liquida'],
                    'Liquidez': min(indicadores['Liquidez_Corrente'], 5)
                }
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=list(indicadores_graf.keys()),
                    y=list(indicadores_graf.values())
                ))
                st.plotly_chart(fig, use_container_width=True)
            
            else:
                st.error("Indicadores não disponíveis")
                
        except Exception as e:
            st.error(f"Erro ao processar: {e}")
    
    # Página 3: Todos os Indicadores
    else:
        st.header("📋 Todos os Indicadores")
        
        with st.spinner("Processando..."):
            resultados = []
            for ticker in tickers_unicos[:30]:  # Limite para performance
                try:
                    empresa_data = df[df['Ticker'] == ticker].iloc[0]
                    indicadores = calcular_indicadores_fixos(empresa_data)
                    if indicadores:
                        resultados.append({
                            'Ticker': ticker,
                            'ROE': indicadores['ROE'],
                            'ROA': indicadores['ROA'],
                            'Margem_Liquida': indicadores['Margem_Liquida'],
                            'Liquidez_Corrente': indicadores['Liquidez_Corrente'],
                            'SELIC_Ajustada': calcular_selic_ajustada(empresa_data, None)
                        })
                except:
                    continue
            
            if resultados:
                resultados_df = pd.DataFrame(resultados)
                
                # Formatação
                display_df = resultados_df.copy()
                for col in ['ROE', 'ROA', 'Margem_Liquida']:
                    display_df[col] = display_df[col].apply(lambda x: f"{x:.1f}%")
                display_df['SELIC_Ajustada'] = display_df['SELIC_Ajustada'].apply(lambda x: f"{x*100:.1f}%")
                display_df['Liquidez_Corrente'] = display_df['Liquidez_Corrente'].apply(lambda x: f"{x:.2f}")
                
                st.dataframe(display_df, use_container_width=True)
            else:
                st.error("Nenhum indicador calculado")

    # Footer
    st.markdown("---")
    st.markdown("**Desenvolvido com Streamlit** | Dados CVM 2023-2024")

if __name__ == "__main__":
    main()
