import streamlit as st
import pandas as pd
import numpy as np

def main():
    st.set_page_config(
        page_title="Vellani - Valuation de Empresas",
        page_icon="💰",
        layout="wide"
    )
    
    st.title("💰 Vellani - Análise de Valuation")
    st.markdown("---")
    
    # Parâmetros fixos
    SELIC = 0.15
    WACC = 0.1613
    
    st.sidebar.title("⚙️ Configurações")
    st.sidebar.info(f"SELIC: {SELIC*100}% a.a.")
    st.sidebar.info(f"WACC: {WACC*100}%")
    
    # Carregar dados do CSV
    try:
        df = pd.read_csv('data_frame.csv', encoding='utf-8', sep=',')
        st.success(f"✅ Dados carregados: {len(df)} empresas encontradas")
        
        # Informações do dataset
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total de Empresas", df['Ticker'].nunique())
        with col2:
            st.metric("Período", "2023-2024")
        with col3:
            st.metric("Dados Contábeis", f"{len(df.columns)} colunas")
        
        # Seleção de empresa
        tickers = sorted(df['Ticker'].dropna().unique())
        selected_ticker = st.selectbox("Selecione a empresa para análise:", tickers)
        
        # Dados da empresa selecionada
        empresa_data = df[df['Ticker'] == selected_ticker].iloc[0]
        
        st.markdown("---")
        st.header(f"📊 Análise - {selected_ticker}")
        
        # Métricas básicas da empresa
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            ativo_total = empresa_data.get('Ativo Total', 0)
            ativo_total = float(ativo_total) if pd.notna(ativo_total) else 0
            st.metric("Ativo Total", f"R$ {ativo_total:,.0f}")
        
        with col2:
            receita = empresa_data.get('Receita de Venda de Bens e/ou Serviços', 0)
            receita = float(receita) if pd.notna(receita) else 0
            st.metric("Receita", f"R$ {receita:,.0f}")
        
        with col3:
            lucro = empresa_data.get('Lucro/Prejuízo Consolidado do Período', 0)
            lucro = float(lucro) if pd.notna(lucro) else 0
            st.metric("Lucro", f"R$ {lucro:,.0f}")
        
        with col4:
            pl = empresa_data.get('Patrimônio Líquido Consolidado', 0)
            pl = float(pl) if pd.notna(pl) else 0
            st.metric("Patrimônio Líquido", f"R$ {pl:,.0f}")
        
        st.markdown("---")
        st.header("🎯 Cálculo de Valuation")
        
        # Cálculos de valuation
        investimento_medio = ativo_total
        ebitda = empresa_data.get('Resultado Antes do Resultado Financeiro e dos Tributos', 0)
        ebitda = float(ebitda) if pd.notna(ebitda) else 0
        
        # ROI
        roi = (ebitda / investimento_medio) * 100 if investimento_medio > 0 else 0
        
        # Lucro Econômico
        lucro_economico_1 = (roi/100 - WACC) * investimento_medio
        lucro_economico_2 = ebitda - (WACC * investimento_medio)
        lucro_economico = (lucro_economico_1 + lucro_economico_2) / 2
        
        # Valor de Mercado
        valor_mercado = lucro_economico / SELIC if SELIC > 0 else 0
        
        # Quantidade de ações
        qtd_acoes = st.number_input(
            "Quantidade de Ações (em milhões):", 
            value=1152.25,
            format="%.2f"
        ) * 1000000
        
        # Cotação Esperada
        cotacao_esperada = valor_mercado / qtd_acoes if qtd_acoes > 0 else 0
        
        # Resultados
        st.subheader("📈 Resultados do Valuation")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("EBITDA", f"R$ {ebitda:,.0f}")
            st.metric("ROI", f"{roi:.2f}%")
            st.metric("Lucro Econômico", f"R$ {lucro_economico:,.0f}")
        
        with col2:
            st.metric("Investimento Médio", f"R$ {investimento_medio:,.0f}")
            st.metric("Valor de Mercado", f"R$ {valor_mercado:,.0f}")
            st.success(f"**Cotação Esperada:** R$ {cotacao_esperada:.2f}")
        
        # Explicação dos cálculos
        with st.expander("📝 Detalhes dos Cálculos"):
            st.markdown(f"""
            **Fórmulas Utilizadas:**
            
            - **EBITDA** = Resultado Antes do Resultado Financeiro e dos Tributos: R$ {ebitda:,.0f}
            - **Investimento Médio** = Ativo Total: R$ {investimento_medio:,.0f}
            - **ROI** = EBITDA / Investimento Médio = {roi:.2f}%
            - **Lucro Econômico 1** = (ROI - WACC) × Investimento = R$ {lucro_economico_1:,.0f}
            - **Lucro Econômico 2** = EBITDA - (WACC × Investimento) = R$ {lucro_economico_2:,.0f}
            - **Lucro Econômico Médio** = R$ {lucro_economico:,.0f}
            - **Valor de Mercado** = Lucro Econômico / SELIC = R$ {valor_mercado:,.0f}
            - **Cotação Esperada** = Valor de Mercado / Qtd. Ações = R$ {cotacao_esperada:.2f}
            """)
            
    except Exception as e:
        st.error(f"❌ Erro ao carregar os dados: {e}")
        st.info("""
        **Para resolver:**
        1. Verifique se o arquivo 'data_frame.csv' está na raiz do repositório
        2. Confirme que o arquivo foi salvo como CSV UTF-8
        3. O nome do arquivo deve ser exatamente 'data_frame.csv'
        """)

if __name__ == "__main__":
    main()
