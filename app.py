import streamlit as st
import pandas as pd
import yfinance as yf
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

# Funções principais
@st.cache_data
def carregar_dados():
    """Carrega o dataframe principal"""
    try:
        df = pd.read_excel('data_frame.xlsx')
        
        # Log das colunas disponíveis para debug
        st.sidebar.info(f"Colunas carregadas: {len(df.columns)}")
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

@st.cache_data(ttl=3600)
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
            # Tentar método alternativo
            info = acao.info
            return info.get('currentPrice', info.get('regularMarketPrice', None))
            
    except Exception as e:
        st.warning(f"Erro ao buscar cotação de {ticker}: {e}")
        return None

def calcular_indicadores_fixos(dados_empresa):
    """Calcula indicadores com SELIC fixa de 15% usando as colunas reais do arquivo"""
    try:
        # Extrair dados básicos - USANDO AS COLUNAS EXATAS DO SEU ARQUIVO
        ativo_total = dados_empresa.get('Ativo Total', 0)
        receita = dados_empresa.get('Receita de Venda de Bens e/ou Serviços', 1)
        lucro = dados_empresa.get('Lucro/Prejuízo Consolidado do Período', 0)
        pl = dados_empresa.get('Patrimônio Líquido Consolidado', 1)
        ativo_circulante = dados_empresa.get('Ativo Circulante', 0)
        passivo_circulante = dados_empresa.get('Passivo Circulante', 1)
        passivo_total = dados_empresa.get('Passivo Total', 1)
        custo_venda = dados_empresa.get('Custo dos Bens e/ou Serviços Vendidos', 0)
        resultado_bruto = dados_empresa.get('Resultado Bruto', 0)
        
        # Garantir que valores são numéricos
        ativo_total = float(ativo_total) if pd.notna(ativo_total) else 0
        receita = float(receita) if pd.notna(receita) else 1
        lucro = float(lucro) if pd.notna(lucro) else 0
        pl = float(pl) if pd.notna(pl) else 1
        ativo_circulante = float(ativo_circulante) if pd.notna(ativo_circulante) else 0
        passivo_circulante = float(passivo_circulante) if pd.notna(passivo_circulante) else 1
        passivo_total = float(passivo_total) if pd.notna(passivo_total) else 1
        custo_venda = float(custo_venda) if pd.notna(custo_venda) else 0
        resultado_bruto = float(resultado_bruto) if pd.notna(resultado_bruto) else 0
        
        # Calcular indicadores
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
    """Calcula SELIC ajustada baseada nos indicadores reais"""
    try:
        if cotacao_atual is None or cotacao_atual <= 0:
            return 0.15
            
        # Dados da empresa para cálculo
        lucro = dados_empresa.get('Lucro/Prejuízo Consolidado do Período', 0)
        pl = dados_empresa.get('Patrimônio Líquido Consolidado', 1)
        ativo_total = dados_empresa.get('Ativo Total', 0)
        receita = dados_empresa.get('Receita de Venda de Bens e/ou Serviços', 1)
        
        lucro = float(lucro) if pd.notna(lucro) else 0
        pl = float(pl) if pd.notna(pl) else 1
        ativo_total = float(ativo_total) if pd.notna(ativo_total) else 0
        receita = float(receita) if pd.notna(receita) else 1
        
        # Cálculo do ROE e ROA
        roe = (lucro / pl) * 100 if pl > 0 else 0
        roa = (lucro / ativo_total) * 100 if ativo_total > 0 else 0
        margem_liquida = (lucro / receita) * 100 if receita > 0 else 0
        
        # SELIC base ajustada pela qualidade dos indicadores
        selic_base = 0.15
        
        # Ajuste por ROE (Quanto maior o ROE, menor a SELIC requerida)
        if roe > 20:
            selic_ajuste = 0.08  # Empresas excelentes
        elif roe > 15:
            selic_ajuste = 0.10
        elif roe > 10:
            selic_ajuste = 0.12
        elif roe > 5:
            selic_ajuste = 0.15
        elif roe > 0:
            selic_ajuste = 0.18
        else:
            selic_ajuste = 0.22  # Empresas com prejuízo
        
        # Ajuste adicional por margem líquida
        if margem_liquida > 20:
            selic_ajuste *= 0.9
        elif margem_liquida < 5:
            selic_ajuste *= 1.1
            
        # Ajuste por tamanho da empresa (Ativo Total)
        if ativo_total > 1000000000:  # Mais de 1 bilhão
            selic_ajuste *= 0.95  # Empresas grandes - menor risco
        elif ativo_total < 100000000:  # Menos de 100 milhões
            selic_ajuste *= 1.05  # Empresas pequenas - maior risco
            
        return max(0.05, min(0.25, selic_ajuste))  # Limita entre 5% e 25%
        
    except Exception as e:
        st.warning(f"Erro no cálculo da SELIC ajustada: {e}")
        return 0.15

def criar_ranking_empresas(df):
    """Cria ranking das empresas baseado nos dados reais"""
    try:
        ranking_data = []
        tickers_processados = 0
        
        # Obter tickers únicos
        tickers_unicos = df['Ticker'].dropna().unique()
        
        for ticker in tickers_unicos:
            if tickers_processados >= 100:  # Limite para performance
                break
                
            # Buscar dados da empresa
            empresa_data = df[df['Ticker'] == ticker].iloc[0]
            
            # Buscar cotação atual
            cotacao_atual = buscar_cotacao_atual(str(ticker).strip())
            
            # Calcular indicadores com SELIC fixa
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
                
                # Identificar nome da empresa (usando diferentes possibilidades)
                nome_empresa = "Empresa"
                for col in df.columns:
                    if 'nome' in col.lower() or 'empresa' in col.lower() or 'razão' in col.lower():
                        if pd.notna(empresa_data.get(col)):
                            nome_empresa = empresa_data[col]
                            break
                
                # Identificar setor
                setor = "Setor Não Identificado"
                for col in df.columns:
                    if 'setor' in col.lower():
                        if pd.notna(empresa_data.get(col)):
                            setor = empresa_data[col]
                            break
                
                ranking_data.append({
                    'Ticker': str(ticker).strip(),
                    'Empresa': nome_empresa,
                    'Setor': setor,
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
        
        if not ranking_data:
            st.error("Nenhum dado pôde ser processado para o ranking.")
            return pd.DataFrame()
            
        ranking_df = pd.DataFrame(ranking_data)
        return ranking_df.sort_values('Score_Ranking', ascending=False)
        
    except Exception as e:
        st.error(f"Erro ao criar ranking: {e}")
        return pd.DataFrame()

# Interface Streamlit
def main():
    st.title("📊 Análise de Empresas - Indicadores Financeiros")
    st.markdown("Analisando 297 tickers com dados contábeis da CVM")
    st.markdown("---")
    
    # Carregar dados
    with st.spinner("Carregando dados do arquivo data_frame.xlsx..."):
        df = carregar_dados()
    
    if df is None:
        st.error("""
        ❌ Não foi possível carregar os dados. Verifique:
        - Se o arquivo 'data_frame.xlsx' está na pasta raiz
        - Se o arquivo não está corrompido
        """)
        return
    
    # Informações do dataset
    st.sidebar.success(f"✅ Dataset carregado: {len(df)} linhas")
    st.sidebar.info(f"📊 Tickers únicos: {df['Ticker'].nunique()}")
    st.sidebar.info(f"🏢 Empresas únicas: {df['Ticker'].nunique()}")
    
    # Sidebar
    st.sidebar.title("🔧 Configurações")
    
    # Filtros
    st.sidebar.subheader("Filtros")
    
    # Seleção de tickers únicos
    tickers_unicos = df['Ticker'].dropna().unique()
    tickers_unicos = sorted([str(t) for t in tickers_unicos])
    
    ticker_selecionado = st.sidebar.selectbox(
        "Selecione um Ticker para análise detalhada:",
        options=tickers_unicos
    )
    
    # Navegação
    pagina = st.sidebar.radio(
        "Navegação:",
        ["🏆 Ranking Geral", "📈 Análise por Empresa", "📋 Todos os Indicadores", "🔍 Sobre os Dados"]
    )
    
    # Página 1: Ranking Geral
    if pagina == "🏆 Ranking Geral":
        st.header("🏆 Ranking das Melhores Empresas")
        
        with st.spinner("Calculando rankings e indicadores..."):
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
            st.subheader("Top 20 Empresas - Ranking por Score")
            
            # Formatação da tabela
            display_cols = ['Ticker', 'Empresa', 'Setor', 'Cotacao_Atual', 'ROE', 'ROA', 
                          'Margem_Liquida', 'SELIC_Ajustada', 'Score_Ranking']
            
            formatted_df = ranking_df[display_cols].head(20).copy()
            
            # Formatação dos valores
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
            st.subheader("📈 Visualizações")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # Top 10 por ROE
                fig_roe = px.bar(
                    ranking_df.head(10),
                    x='Ticker',
                    y='ROE',
                    title='Top 10 - Maior ROE (%)',
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
                    nbins=20,
                    color_discrete_sequence=['#00CC96']
                )
                fig_selic.update_layout(
                    xaxis_title="SELIC Ajustada (%)", 
                    yaxis_title="Quantidade de Empresas"
                )
                st.plotly_chart(fig_selic, use_container_width=True)
            
            # Gráfico de dispersão ROE vs SELIC Ajustada
            st.subheader("📊 Relação ROE vs SELIC Ajustada")
            fig_disp = px.scatter(
                ranking_df.head(30),
                x='ROE',
                y='SELIC_Ajustada',
                size='Margem_Liquida',
                color='Setor',
                hover_data=['Ticker', 'Empresa'],
                title='ROE vs SELIC Ajustada (Tamanho: Margem Líquida)'
            )
            st.plotly_chart(fig_disp, use_container_width=True)
        
        else:
            st.error("Não foi possível gerar o ranking. Verifique os dados.")
    
    # Página 2: Análise por Empresa
    elif pagina == "📈 Análise por Empresa":
        st.header(f"📈 Análise Detalhada - {ticker_selecionado}")
        
        try:
            # Buscar dados da empresa selecionada
            empresa_data = df[df['Ticker'] == ticker_selecionado]
            if len(empresa_data) == 0:
                st.error(f"Dados não encontrados para o ticker {ticker_selecionado}")
                return
                
            empresa_data = empresa_data.iloc[0]
            cotacao_atual = buscar_cotacao_atual(ticker_selecionado)
            
            # Calcular indicadores
            indicadores_fixos = calcular_indicadores_fixos(empresa_data)
            selic_ajustada = calcular_selic_ajustada(empresa_data, cotacao_atual)
            
            if indicadores_fixos:
                # Informações básicas
                col1, col2 = st.columns(2)
                
                with col1:
                    if cotacao_atual:
                        st.success(f"✅ Cotação atual: R$ {cotacao_atual:.2f}")
                    else:
                        st.warning("⚠️ Cotação não disponível")
                
                with col2:
                    st.info(f"🔧 SELIC Ajustada: {selic_ajustada*100:.1f}%")
                
                # Métricas principais
                st.subheader("📊 Indicadores Principais")
                
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("ROE", f"{indicadores_fixos['ROE']:.1f}%")
                with col2:
                    st.metric("ROA", f"{indicadores_fixos['ROA']:.1f}%")
                with col3:
                    st.metric("Margem Líquida", f"{indicadores_fixos['Margem_Liquida']:.1f}%")
                with col4:
                    st.metric("Liquidez Corrente", f"{indicadores_fixos['Liquidez_Corrente']:.2f}")
                
                # Comparação SELIC
                st.subheader("🔍 Comparação de Cenários de SELIC")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info("**SELIC Oficial (15%)**")
                    st.metric("Taxa SELIC", "15.0%")
                    if cotacao_atual:
                        # Cálculo simplificado de valuation
                        valuation_fixo = cotacao_atual * (0.15 / selic_ajustada) if selic_ajustada > 0 else cotacao_atual
                        st.metric("Valuation Relativo", f"R$ {valuation_fixo:.2f}")
                
                with col2:
                    st.success("**SELIC Ajustada**")
                    st.metric("Taxa SELIC", f"{selic_ajustada*100:.1f}%")
                    if cotacao_atual:
                        valuation_ajustado = cotacao_atual
                        st.metric("Valuation Relativo", f"R$ {valuation_ajustado:.2f}")
                
                # Gráfico de indicadores
                st.subheader("📈 Perfil de Indicadores")
                
                indicadores_graf = {
                    'ROE': indicadores_fixos['ROE'],
                    'ROA': indicadores_fixos['ROA'],
                    'Margem Bruta': indicadores_fixos['Margem_Bruta'],
                    'Margem Líquida': indicadores_fixos['Margem_Liquida'],
                    'Liquidez Corrente': min(indicadores_fixos['Liquidez_Corrente'], 5),
                    'Giro Ativo': min(indicadores_fixos['Giro_Ativo'] * 10, 10)  # Escalado para visualização
                }
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=list(indicadores_graf.keys()),
                    y=list(indicadores_graf.values()),
                    marker_color='#1f77b4'
                ))
                fig.update_layout(
                    title="Indicadores Financeiros da Empresa",
                    yaxis_title="Valor (%) ou Razão"
                )
                st.plotly_chart(fig, use_container_width=True)
                
                # Dados contábeis básicos
                st.subheader("💼 Dados Contábeis (R$)")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    ativo_total = empresa_data.get('Ativo Total', 0)
                    st.metric("Ativo Total", f"R$ {ativo_total:,.0f}")
                
                with col2:
                    receita = empresa_data.get('Receita de Venda de Bens e/ou Serviços', 0)
                    st.metric("Receita", f"R$ {receita:,.0f}")
                
                with col3:
                    lucro = empresa_data.get('Lucro/Prejuízo Consolidado do Período', 0)
                    st.metric("Lucro", f"R$ {lucro:,.0f}")
                    
            else:
                st.error("Não foi possível calcular os indicadores para esta empresa")
                
        except Exception as e:
            st.error(f"Erro ao processar empresa {ticker_selecionado}: {e}")
    
    # Página 3: Todos os Indicadores
    elif pagina == "📋 Todos os Indicadores":
        st.header("📋 Todos os Indicadores por Empresa")
        
        with st.spinner("Processando todas as empresas..."):
            resultados = []
            
            for ticker in df['Ticker'].dropna().unique()[:100]:  # Limite para performance
                empresa_data = df[df['Ticker'] == ticker].iloc[0]
                cotacao_atual = buscar_cotacao_atual(str(ticker).strip())
                indicadores = calcular_indicadores_fixos(empresa_data)
                selic_ajustada = calcular_selic_ajustada(empresa_data, cotacao_atual)
                
                if indicadores:
                    resultados.append({
                        'Ticker': str(ticker).strip(),
                        'Cotacao_Atual': cotacao_atual or 0,
                        'ROE': indicadores['ROE'],
                        'ROA': indicadores['ROA'],
                        'Margem_Bruta': indicadores['Margem_Bruta'],
                        'Margem_Liquida': indicadores['Margem_Liquida'],
                        'Liquidez_Corrente': indicadores['Liquidez_Corrente'],
                        'Endividamento': indicadores['Endividamento'],
                        'Giro_Ativo': indicadores['Giro_Ativo'],
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
            display_df['Margem_Bruta'] = display_df['Margem_Bruta'].apply(lambda x: f"{x:.1f}%")
            display_df['Margem_Liquida'] = display_df['Margem_Liquida'].apply(lambda x: f"{x:.1f}%")
            display_df['Liquidez_Corrente'] = display_df['Liquidez_Corrente'].apply(lambda x: f"{x:.2f}")
            display_df['Endividamento'] = display_df['Endividamento'].apply(lambda x: f"{x:.2f}")
            display_df['Giro_Ativo'] = display_df['Giro_Ativo'].apply(lambda x: f"{x:.2f}")
            display_df['SELIC_Ajustada'] = display_df['SELIC_Ajustada'].apply(lambda x: f"{x*100:.1f}%")
            
            st.dataframe(display_df, use_container_width=True)
            
            # Botão de download
            csv = resultados_df.to_csv(index=False, sep=';', decimal=',')
            st.download_button(
                label="📥 Download CSV Completo",
                data=csv,
                file_name=f"indicadores_empresas_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
        else:
            st.error("Não foi possível processar os indicadores")
    
    # Página 4: Sobre os Dados
    else:
        st.header("🔍 Sobre os Dados")
        
        st.info("""
        ### 📊 Fonte dos Dados
        - **Dados Contábeis**: Comissão de Valores Mobiliários (CVM)
        - **Período**: 2023-2024
        - **Empresas**: 235 empresas únicas
        - **Tickers**: 297 tickers únicos
        """)
        
        st.success("""
        ### ✅ Qualidade dos Dados
        - **Taxa de completude**: 84.9%
        - **Empresas com dados**: 100%
        - **Contas com >50% preenchidas**: 19/22
        """)
        
        # Estatísticas básicas
        st.subheader("📈 Estatísticas do Dataset")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total de Linhas", len(df))
        with col2:
            st.metric("Tickers Únicos", df['Ticker'].nunique())
        with col3:
            st.metric("Colunas", len(df.columns))
        
        # Principais setores
        st.subheader("🏭 Principais Setores")
        
        # Tentar identificar coluna de setor
        setor_col = None
        for col in df.columns:
            if 'setor' in col.lower():
                setor_col = col
                break
        
        if setor_col:
            setores = df[setor_col].value_counts().head(10)
            fig_setores = px.bar(
                x=setores.index,
                y=setores.values,
                title="Top 10 Setores",
                labels={'x': 'Setor', 'y': 'Quantidade de Empresas'}
            )
            st.plotly_chart(fig_setores, use_container_width=True)
        else:
            st.info("Coluna de setor não identificada no dataset")

    # Footer
    st.markdown("---")
    st.markdown(
        "**Desenvolvido com Streamlit** | "
        "📊 Dados CVM 2023-2024 | "
        "💰 Cotações em tempo real do Yahoo Finance | "
        "🔧 SELIC Oficial: 15% vs SELIC Ajustada por Empresa"
    )

if __name__ == "__main__":
    main()
