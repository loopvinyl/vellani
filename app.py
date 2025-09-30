import streamlit as st
import pandas as pd
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Análise de Empresas - Valuation",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def carregar_dados():
    """Carrega o dataframe principal"""
    try:
        df = pd.read_excel('data_frame.xlsx')
        return df
    except Exception as e:
        st.error(f"Erro ao carregar dados: {e}")
        return None

def calcular_ebitda(dados_empresa):
    """Calcula EBITDA aproximado"""
    try:
        # EBIT (Resultado Antes do Resultado Financeiro e dos Tributos)
        ebit = dados_empresa.get('Resultado Antes do Resultado Financeiro e dos Tributos', 0)
        ebit = float(ebit) if pd.notna(ebit) else 0
        
        # Como não temos depreciação/amortização, usamos EBIT como aproximação do EBITDA
        # Em uma análise real, precisaríamos das depreciações
        return ebit
    except:
        return 0

def calcular_indicadores_valuation(dados_empresa):
    """Calcula indicadores de valuation baseados na planilha modelo"""
    try:
        # Dados básicos
        ativo_total = dados_empresa.get('Ativo Total', 0)
        ativo_total = float(ativo_total) if pd.notna(ativo_total) else 0
        
        # Supondo que temos dados de dois períodos para calcular a média
        # Para simplificar, vamos usar o ativo_total atual como investimento médio
        investimento_medio = ativo_total
        
        # EBITDA
        ebitda = calcular_ebitda(dados_empresa)
        
        # ROI (Return on Investment)
        roi = (ebitda / investimento_medio) * 100 if investimento_medio > 0 else 0
        
        # WACC (Weighted Average Cost of Capital) - fixo em 16.13% conforme planilha
        wacc = 0.1613
        
        # SELIC fixa em 15%
        selic = 0.15
        
        # Lucro Econômico
        lucro_economico_1 = (roi/100 - wacc) * investimento_medio
        lucro_economico_2 = ebitda - (wacc * investimento_medio)
        
        # Usar a média dos dois cálculos de lucro econômico
        lucro_economico = (lucro_economico_1 + lucro_economico_2) / 2
        
        # Valor de Mercado (em R$ mil)
        valor_mercado_mil = lucro_economico / selic
        
        # Converter para R$ (multiplicar por 1000)
        valor_mercado = valor_mercado_mil * 1000
        
        # Quantidade de ações fictícia - em uma aplicação real, isso viria de base de dados
        # Usando valor similar ao da planilha modelo como exemplo
        qtd_acoes = 1152254440  # Exemplo: mesma quantidade da CPFE3
        
        # Cotação esperada
        cotacao_esperada = valor_mercado / qtd_acoes if qtd_acoes > 0 else 0
        
        return {
            'Investimento_Medio': investimento_medio,
            'EBITDA': ebitda,
            'ROI': roi,
            'WACC': wacc * 100,  # Em percentual
            'Lucro_Economico_1': lucro_economico_1,
            'Lucro_Economico_2': lucro_economico_2,
            'Lucro_Economico_EBITDA': lucro_economico * 1000,  # Em R$
            'SELIC': selic * 100,  # Em percentual
            'Valor_Mercado': valor_mercado,
            'Qtd_Acoes': qtd_acoes,
            'Cotacao_Esperada': cotacao_esperada
        }
    except Exception as e:
        st.error(f"Erro no cálculo: {e}")
        return None

def main():
    st.title("📊 Valuation de Empresas - Modelo Simplificado")
    st.markdown("Cálculo de cotação esperada usando SELIC de 15%")
    st.markdown("---")
    
    # Carregar dados
    df = carregar_dados()
    
    if df is None:
        st.error("Não foi possível carregar o arquivo 'data_frame.xlsx'")
        return
    
    # Sidebar
    st.sidebar.title("Configurações")
    
    # Seleção de ticker
    tickers = df['Ticker'].dropna().unique()
    tickers = sorted([str(t) for t in tickers])
    
    ticker_selecionado = st.sidebar.selectbox("Selecione o Ticker:", tickers)
    
    st.sidebar.markdown("---")
    st.sidebar.info("**Parâmetros Fixos:**")
    st.sidebar.info("- SELIC: 15% a.a.")
    st.sidebar.info("- WACC: 16.13%")
    
    # Análise da empresa selecionada
    st.header(f"Análise - {ticker_selecionado}")
    
    try:
        empresa_data = df[df['Ticker'] == ticker_selecionado].iloc[0]
        indicadores = calcular_indicadores_valuation(empresa_data)
        
        if indicadores:
            # Mostrar dados básicos da empresa
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
            
            st.markdown("---")
            
            # Indicadores de Valuation
            st.subheader("📈 Indicadores de Valuation")
            
            # Primeira linha de métricas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Investimento Médio", f"R$ {indicadores['Investimento_Medio']:,.0f}")
            
            with col2:
                st.metric("EBITDA", f"R$ {indicadores['EBITDA']:,.0f}")
            
            with col3:
                st.metric("ROI", f"{indicadores['ROI']:.2f}%")
            
            with col4:
                st.metric("WACC", f"{indicadores['WACC']:.2f}%")
            
            # Segunda linha de métricas
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Lucro Econômico 1", f"R$ {indicadores['Lucro_Economico_1']:,.0f}")
            
            with col2:
                st.metric("Lucro Econômico 2", f"R$ {indicadores['Lucro_Economico_2']:,.0f}")
            
            with col3:
                st.metric("SELIC", f"{indicadores['SELIC']:.2f}%")
            
            with col4:
                st.metric("Qtd de Ações", f"{indicadores['Qtd_Acoes']:,.0f}")
            
            st.markdown("---")
            
            # Resultado Final - Cotação Esperada
            st.subheader("🎯 Resultado Final")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Valor de Mercado", 
                    f"R$ {indicadores['Valor_Mercado']:,.0f}",
                    delta="Valuation Calculado"
                )
            
            with col2:
                st.metric(
                    "Lucro Econômico (EBITDA)", 
                    f"R$ {indicadores['Lucro_Economico_EBITDA']:,.0f}",
                    delta="Base do Cálculo"
                )
            
            with col3:
                st.success(f"**Cotação Esperada:** R$ {indicadores['Cotacao_Esperada']:.2f}")
            
            # Explicação do cálculo
            with st.expander("📝 Entenda o Cálculo"):
                st.markdown("""
                **Fórmulas Utilizadas:**
                
                1. **EBITDA** ≈ Resultado Antes do Resultado Financeiro e dos Tributos
                2. **ROI** = EBITDA / Investimento Médio
                3. **Lucro Econômico 1** = (ROI - WACC) × Investimento Médio
                4. **Lucro Econômico 2** = EBITDA - (WACC × Investimento Médio)
                5. **Valor de Mercado** = Lucro Econômico / SELIC
                6. **Cotação Esperada** = Valor de Mercado / Quantidade de Ações
                
                *Nota: Esta é uma simplificação para demonstração.*
                """)
        
        else:
            st.error("Não foi possível calcular os indicadores para esta empresa")
            
    except Exception as e:
        st.error(f"Erro ao processar {ticker_selecionado}: {e}")

if __name__ == "__main__":
    main()
