import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

def calcular_saldos_medios(df):
    """Calcula saldos médios para indicadores financeiros"""
    df = df.sort_values(['CNPJ_CIA', 'ANO'])
    
    # Calcular saldos do ano anterior
    df['ATIVO_TOTAL_ANTERIOR'] = df.groupby('CNPJ_CIA')['Ativo Total'].shift(1)
    df['PL_ANTERIOR'] = df.groupby('CNPJ_CIA')['Patrimônio Líquido Consolidado'].shift(1)
    df['PASSIVO_TOTAL_ANTERIOR'] = df.groupby('CNPJ_CIA')['Passivo Total'].shift(1)
    
    # Calcular saldos médios
    df['ATIVO_TOTAL_MEDIO'] = (df['Ativo Total'] + df['ATIVO_TOTAL_ANTERIOR']) / 2
    df['PL_MEDIO'] = (df['Patrimônio Líquido Consolidado'] + df['PL_ANTERIOR']) / 2
    df['PASSIVO_TOTAL_MEDIO'] = (df['Passivo Total'] + df['PASSIVO_TOTAL_ANTERIOR']) / 2
    
    return df

def calcular_indicadores_financeiros(df):
    """Calcula todos os indicadores financeiros com saldos médios"""
    
    # Rentabilidade com saldos médios
    df['ROE'] = df['Lucro/Prejuízo Consolidado do Período'] / df['PL_MEDIO']
    df['ROA'] = df['Resultado Antes do Resultado Financeiro e dos Tributos'] / df['ATIVO_TOTAL_MEDIO']
    df['ROI'] = df['Resultado Antes dos Tributos sobre o Lucro'] / df['ATIVO_TOTAL_MEDIO']
    df['ROIC'] = df['Resultado Antes do Resultado Financeiro e dos Tributos'] / (df['PL_MEDIO'] + df['PASSIVO_TOTAL_MEDIO'])
    
    # Eficiência com saldos médios
    df['GIRO_ATIVO'] = df['Receita de Venda de Bens e/ou Serviços'] / df['ATIVO_TOTAL_MEDIO']
    df['GIRO_PL'] = df['Receita de Venda de Bens e/ou Serviços'] / df['PL_MEDIO']
    
    # Margens
    df['MARGEM_BRUTA'] = df['Resultado Bruto'] / df['Receita de Venda de Bens e/ou Serviços']
    df['MARGEM_EBIT'] = df['Resultado Antes do Resultado Financeiro e dos Tributos'] / df['Receita de Venda de Bens e/ou Serviços']
    df['MARGEM_LIQUIDA'] = df['Lucro/Prejuízo Consolidado do Período'] / df['Receita de Venda de Bens e/ou Serviços']
    
    # Liquidez
    df['LIQUIDEZ_CORRENTE'] = df['Ativo Circulante'] / df['Passivo Circulante']
    df['LIQUIDEZ_SECA'] = (df['Ativo Circulante'] - df['Custo dos Bens e/ou Serviços Vendidos']) / df['Passivo Circulante']
    df['LIQUIDEZ_GERAL'] = df['Ativo Total'] / df['Passivo Total']
    
    # Endividamento
    df['ENDIVIDAMENTO_TOTAL'] = df['Passivo Total'] / df['Ativo Total']
    df['COMPOSICAO_ENDIVIDAMENTO'] = df['Passivo Circulante'] / df['Passivo Total']
    df['GARANTIA_CAPITAL_PROPRIO'] = df['Patrimônio Líquido Consolidado'] / df['Passivo Total']
    
    # Fluxo de Caixa
    df['FCO_RECEITA'] = df['Caixa Líquido Atividades Operacionais'] / df['Receita de Venda de Bens e/ou Serviços']
    df['FCO_LL'] = df['Caixa Líquido Atividades Operacionais'] / df['Lucro/Prejuízo Consolidado do Período']
    
    return df

# No carregamento dos dados:
@st.cache_data
def load_and_process_data():
    df = pd.read_excel('data_frame.xlsx')
    df = calcular_saldos_medios(df)
    df = calcular_indicadores_financeiros(df)
    return df
