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
        # Tenta carregar o arquivo - ajuste o nome se necessário
        df = pd.read_excel('data_frame.xlsx')
        
        # Verifica se as colunas necessárias existem
        colunas_necessarias = ['Ticker', 'Ativo Total', 'Receita de Venda de Bens e/ou Serviços', 
                              'Lucro/Prejuízo Consolidado do Período', 'Patrimônio Líquido Consolidado']
        
        colunas_faltantes = [col for col in colunas_necessarias if col not in df.columns]
        if colunas_faltantes:
            st.warning(f"Colunas faltantes no arquivo: {colunas_faltantes}")
            st.info("Colunas disponíveis no arquivo:")
            st.write(df.columns.tolist())
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        st.info("Verifique se o arquivo 'data_frame.xlsx' está na pasta correta")
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
        # Tenta várias formas de obter a cotação
        try:
            hist = acao.history(period='1d', interval='1m')
            if not hist.empty:
                return hist['Close'].iloc[-1]
        except:
            pass
        
        try:
            hist = acao.history(period='2d')
            if not hist.empty:
                return hist['Close'].iloc[-1]
        except:
            pass
        
        # Última tentativa com info
        info = acao.info
        if 'currentPrice' in info and info['currentPrice']:
            return info['currentPrice']
        elif 'regularMarketPrice' in info and info['regularMarketPrice']:
            return info['regularMarketPrice']
        
        return None
        
    except Exception as e:
        st.warning(f"Erro ao buscar cotação de {ticker}: {e}")
        return None

def calcular_indicadores_fixos(dados_empresa):
    """Calcula indicadores com SELIC fixa de 15%"""
    try:
        # Extrair dados básicos com fallbacks
        ativo_total = dados_empresa.get('Ativo Total', dados_empresa.get('Ativo_Total', 0))
        receita = dados_empresa.get('Receita de Venda de Bens e/ou Serviços', 
                                  dados_empresa.get('Receita_Venda', 1))
        lucro = dados_empresa.get('Lucro/Prejuízo Consolidado do Períado', 
                                dados_empresa.get('Lucro_Periodo', 0))
        pl = dados_empresa.get('Patrimônio Líquido Consolidado', 
                             dados_empresa.get('Patrimonio_Liquido', 1))
        ativo_circulante = dados_empresa.get('Ativo Circulante', 
                                           dados_empresa.get('Ativo_Circulante', 0))
        passivo_circulante = dados_empresa.get('Passivo Circulante', 
                                             dados_empresa.get('Passivo_Circulante', 1))
        passivo_total = dados_empresa.get('Passivo Total', 
                                        dados_empresa.get('Passivo_Total', 1))
        
        # Garantir que valores são numéricos
        ativo_total = float(ativo_total) if pd.notna(ativo_total) else 0
        receita = float(receita) if pd.notna(receita) else 1
        lucro = float(lucro) if pd.notna(lucro) else 0
        pl = float(pl) if pd.notna(pl) else 1
        ativo_circulante = float(ativo_circulante) if pd.notna(ativo_circulante) else 0
        passivo_circulante = float(passivo_circulante) if pd.notna(passivo_circulante) else 1
        passivo_total = float(passivo_total) if pd.notna(passivo_total) else 1
        
        # Calcular indicadores
        margem_liquida = (lucro / receita) * 100 if receita > 0 else 0
        roe = (lucro / pl) * 100 if pl > 0 else 0
        roa = (lucro / ativo_total) * 100 if ativo_total > 0 else 0
        liquidez_corrente = ativo_circulante / passivo_circulante if passivo_circulante > 0 else 0
        endividamento = passivo_total / ativo_total if ativo_total > 0 else 0
        
        return {
            'Margem_Liquida': margem_liquida,
            'ROE': roe,
            'ROA': roa,
            'Liquidez_Corrente': liquidez_corrente,
            'Endividamento': endividamento,
            'SELIC_Utilizada': 0.15
        }
    except Exception as e:
        st.warning(f"Erro no cálculo de indicadores: {e}")
        return None

def calcular_selic_ajustada(dados_empresa, cotacao_atual):
    """Calcula SELIC ajustada para igualar cotação esperada à atual"""
    try:
        if cotacao_atual is None or cotacao_atual <= 0:
            return 0.15
            
        lucro = dados_empresa.get('Lucro/Prejuízo Consolidado do Período', 
                                dados_empresa.get('Lucro_Periodo', 0))
        pl = dados_empresa.get('Patrimônio Líquido Consolidado', 
                             dados_empresa.get('Patrimonio_Liquido', 1))
        
        lucro = float(lucro) if pd.notna(lucro) else 0
        pl = float(pl) if pd.notna(pl) else 1
        
        # Cálculo simplificado da SELIC ajustada
        roe = (lucro / pl) * 100 if pl > 0 else 0
        
        # Fator baseado no ROE e tamanho da empresa
        if roe > 25:
            selic_base = 0.08  # Empresas muito rentáveis - SELIC mais baixa
        elif roe > 15:
            selic_base = 0.12
        elif roe > 8:
            selic_base = 0.15
        elif roe > 0:
            selic_base = 0.18
        else:
            selic_base = 0.20  # Prejuízo - SELIC mais alta
            
        # Ajuste adicional baseado no tamanho (ativo total)
        ativo_total = dados_empresa.get('Ativo Total', dados_empresa.get('Ativo_Total', 0))
        ativo_total = float(ativo_total) if pd.notna(ativo_total) else 0
        
        if ativo_total > 1000000000:  # Mais de 1 bilhão
            selic_base *= 0.9  # Empresas grandes - desconto
        elif ativo_total < 100000000:  # Menos de 100 milhões
            selic_base *= 1.1  # Empresas pequenas - prêmio
            
        return max(0.05, min(0.25, selic_base))  # Limita entre 5% e 25%
        
    except Exception as e:
        st.warning(f"Erro no cálculo da SELIC ajustada: {e}")
        return 0.15

def criar_ranking_empresas(df):
    """Cria ranking das empresas baseado em múltiplos critérios"""
    try:
        ranking_data = []
        tickers_processados = 0
        
        for idx, empresa in df.iterrows():
            ticker = empresa.get('Ticker')
            if not ticker or pd.isna(ticker):
                continue
                
            # Buscar cotação atual
            cotacao_atual = buscar_cotacao_atual(str(ticker).strip())
            
            # Calcular indicadores com SELIC fixa
            indicadores_fixos = calcular_indicadores_fixos(empresa)
            
            if indicadores_fixos:
                # Calcular SELIC ajustada
                selic_ajustada = calcular_selic_ajustada(empresa, cotacao_atual)
                
                # Score composto para ranking (evitando divisão por zero)
                endividamento = indicadores_fixos['Endividamento']
                score_endividamento = (1/endividamento if endividamento > 0.1 else 10) * 0.3
                
                score = (
                    indicadores_fixos['ROE'] * 0.3 +
                    indicadores_fixos['ROA'] * 0.2 +
                    indicadores_fixos['Margem_Liquida'] * 0.2 +
                    score_endividamento
                )
                
                # Obter nome da empresa (usando diferentes colunas possíveis)
                nome_empresa = empresa.get('Nome_Empresa', 
                                         empresa.get('Empresa',
                                                   empresa.get('Razão Social', ticker)))
                
                setor = empresa.get('Setor', 
                                  empresa.get('Setor_Economico', 
                                            empresa.get('Setor Econômico', 'N/A')))
                
                ranking_data.append({
                    'Ticker': str(ticker).strip(),
                    'Empresa': nome_empresa if pd.notna(nome_empresa) else str(ticker).strip(),
                    'Setor': setor if pd.notna(setor) else 'N/A',
                    'Cotacao_Atual': cotacao_atual or 0,
                    'ROE': indicadores_fixos['ROE'],
                    'ROA': indicadores_fixos['ROA'],
                    'Margem_Liquida': indicadores_fixos['Margem_Liquida'],
                    'Liquidez_Corrente': indicadores_fixos['Liquidez_Corrente'],
                    'Endividamento': indicadores_fixos['Endividamento'],
                    'SELIC_Fixa': 0.15,
                    'SELIC_Ajustada': selic_ajustada,
                    'Score_Ranking': score
                })
                
                tickers_processados += 1
                
                # Limitar para demonstração (remover em produção)
                if tickers_processados >= 50:  # Processa apenas 50 para teste
                    break
        
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
    st.markdown("---")
    
    # Carregar dados
    with st.spinner("Carregando dados..."):
        df = carregar_dados()
    
    if df is None:
        st.error("""
        ❌ Não foi possível carregar os dados. Verifique:
        - Se o arquivo 'data_frame.xlsx' está na pasta raiz
        - Se o nome do arquivo está correto
        - Se o arquivo não está corrompido
        """)
        
        # Tentar listar arquivos disponíveis
        import os
        st.info("Arquivos na pasta atual:")
        try:
            files = [f for f in os.listdir('.') if os.path.isfile(f)]
            st.write(files)
        except:
            st.write("Não foi possível listar os arquivos")
            
        return
    
    # Mostrar informações básicas do dataset
    st.sidebar.success(f"✅ Dados carregados: {len(df)} linhas, {len(df.columns)} colunas")
    
    # Sidebar
    st.sidebar.title("🔧 Configurações")
    
    # Filtros
    st.sidebar.subheader("Filtros")
    
    # Seleção de tickers únicos
    tickers_unicos = []
    if 'Ticker' in df.columns:
        tickers_unicos = [t for t in df['Ticker'].unique() if pd.notna(t)]
        tickers_unicos = sorted(tickers_unicos)
    
    if not tickers_unicos:
        st.error("Não foi encontrada a coluna 'Ticker' no arquivo.")
        st.info("Colunas disponíveis:")
        st.write(df.columns.tolist())
        return
    
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
            
            # Verificar quais colunas existem
            display_cols = [col for col in display_cols if col in ranking_df.columns]
            
            formatted_df = ranking_df[display_cols].head(20).copy()
            
            # Formatação condicional
            if 'Cotacao_Atual' in formatted_df.columns:
                formatted_df['Cotacao_Atual'] = formatted_df['Cotacao_Atual'].apply(
                    lambda x: f"R$ {x:.2f}" if x > 0 else "N/A"
                )
            if 'ROE' in formatted_df.columns:
                formatted_df['ROE'] = formatted_df['ROE'].apply(lambda x: f"{x:.1f}%")
            if 'ROA' in formatted_df.columns:
                formatted_df['ROA'] = formatted_df['ROA'].apply(lambda x: f"{x:.1f}%")
            if 'Margem_Liquida' in formatted_df.columns:
                formatted_df['Margem_Liquida'] = formatted_df['Margem_Liquida'].apply(lambda x: f"{x:.1f}%")
            if 'SELIC_Ajustada' in formatted_df.columns:
                formatted_df['SELIC_Ajustada'] = formatted_df['SELIC_Ajustada'].apply(lambda x: f"{x*100:.1f}%")
            if 'Score_Ranking' in formatted_df.columns:
                formatted_df['Score_Ranking'] = formatted_df['Score_Ranking'].apply(lambda x: f"{x:.1f}")
            
            st.dataframe(formatted_df, use_container_width=True)
            
            # Gráficos
            if len(ranking_df) >= 5:  # Só mostra gráficos se tiver dados suficientes
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
            else:
                st.warning("Dados insuficientes para gerar gráficos")
        
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
                        valuation_fixo = cotacao_atual * (0.15 / selic_ajustada) if selic_ajustada > 0 else cotacao_atual
                        st.metric("Valuation Estimado", f"R$ {valuation_fixo:.2f}")
                
                with col2:
                    st.success("**SELIC Ajustada**")
                    st.metric("Taxa SELIC", f"{selic_ajustada*100:.1f}%")
                    if cotacao_atual:
                        valuation_ajustado = cotacao_atual
                        st.metric("Valuation Estimado", f"R$ {valuation_ajustado:.2f}")
                
                # Gráfico de indicadores
                st.subheader("📊 Indicadores Financeiros")
                
                indicadores_graf = {
                    'ROE': indicadores_fixos['ROE'],
                    'ROA': indicadores_fixos['ROA'],
                    'Margem Líquida': indicadores_fixos['Margem_Liquida'],
                    'Liquidez Corrente': min(indicadores_fixos['Liquidez_Corrente'], 10),
                    'Endividamento': min(indicadores_fixos['Endividamento'] * 100, 100)
                }
                
                fig = go.Figure()
                fig.add_trace(go.Bar(
                    x=list(indicadores_graf.keys()),
                    y=list(indicadores_graf.values()),
                    marker_color='lightblue'
                ))
                fig.update_layout(title="Indicadores Financeiros da Empresa")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.error("Não foi possível calcular os indicadores para esta empresa")
                
        except Exception as e:
            st.error(f"Erro ao processar empresa {ticker_selecionado}: {e}")
    
    # Página 3: Todos os Indicadores
    else:
        st.header("📋 Todos os Indicadores por Empresa")
        
        with st.spinner("Processando todas as empresas..."):
            resultados = []
            
            for idx, empresa in df.iterrows():
                ticker = empresa.get('Ticker')
                if not ticker or pd.isna(ticker):
                    continue
                    
                cotacao_atual = buscar_cotacao_atual(str(ticker).strip())
                indicadores = calcular_indicadores_fixos(empresa)
                selic_ajustada = calcular_selic_ajustada(empresa, cotacao_atual)
                
                if indicadores:
                    nome_empresa = empresa.get('Nome_Empresa', 
                                             empresa.get('Empresa',
                                                       empresa.get('Razão Social', ticker)))
                    
                    resultados.append({
                        'Ticker': str(ticker).strip(),
                        'Empresa': nome_empresa if pd.notna(nome_empresa) else str(ticker).strip(),
                        'Cotacao_Atual': cotacao_atual or 0,
                        'ROE': indicadores['ROE'],
                        'ROA': indicadores['ROA'],
                        'Margem_Liquida': indicadores['Margem_Liquida'],
                        'Liquidez_Corrente': indicadores['Liquidez_Corrente'],
                        'Endividamento': indicadores['Endividamento'],
                        'SELIC_Ajustada': selic_ajustada
                    })
            
            resultados_df = pd.DataFrame(resultados)
        
        if not resultados_df.empty:
            # Formatação
            display_df = resultados_df.copy()
            
            # Formatação condicional
            if 'Cotacao_Atual' in display_df.columns:
                display_df['Cotacao_Atual'] = display_df['Cotacao_Atual'].apply(
                    lambda x: f"R$ {x:.2f}" if x > 0 else "N/A"
                )
            if 'ROE' in display_df.columns:
                display_df['ROE'] = display_df['ROE'].apply(lambda x: f"{x:.1f}%")
            if 'ROA' in display_df.columns:
                display_df['ROA'] = display_df['ROA'].apply(lambda x: f"{x:.1f}%")
            if 'Margem_Liquida' in display_df.columns:
                display_df['Margem_Liquida'] = display_df['Margem_Liquida'].apply(lambda x: f"{x:.1f}%")
            if 'Liquidez_Corrente' in display_df.columns:
                display_df['Liquidez_Corrente'] = display_df['Liquidez_Corrente'].apply(lambda x: f"{x:.2f}")
            if 'Endividamento' in display_df.columns:
                display_df['Endividamento'] = display_df['Endividamento'].apply(lambda x: f"{x:.2f}")
            if 'SELIC_Ajustada' in display_df.columns:
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
        else:
            st.error("Não foi possível processar os indicadores")

    # Footer
    st.markdown("---")
    st.markdown(
        "**Desenvolvido com Streamlit** | "
        "📊 Indicadores calculados com base nos dados da CVM | "
        "💰 Cotações em tempo real do Yahoo Finance"
    )

if __name__ == "__main__":
    main()
