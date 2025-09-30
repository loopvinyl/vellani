import streamlit as st

# Apenas Streamlit - sem outras dependências
st.set_page_config(
    page_title="Teste Básico",
    page_icon="✅",
    layout="centered"
)

st.title("🧪 Teste Básico do Streamlit")
st.markdown("---")

st.success("✅ Se você está vendo esta mensagem, o Streamlit está funcionando!")

# Teste de funcionalidades básicas
st.header("Teste de Componentes Básicos")

# 1. Texto
st.write("Este é um texto simples.")

# 2. Botão
if st.button("Clique aqui"):
    st.balloons()
    st.write("🎉 Botão funcionando!")

# 3. Input
nome = st.text_input("Digite seu nome:", "João")
st.write(f"Olá, {nome}!")

# 4. Slider
idade = st.slider("Selecione sua idade:", 0, 100, 25)
st.write(f"Idade selecionada: {idade}")

# 5. Selectbox
opcoes = ["Opção 1", "Opção 2", "Opção 3"]
opcao = st.selectbox("Selecione uma opção:", opcoes)
st.write(f"Opção selecionada: {opcao}")

# 6. DataFrame simples (sem pandas)
st.header("DataFrame Simulado")
dados = [
    {"Ticker": "PETR4", "Preço": 35.50, "Variação": "+2%"},
    {"Ticker": "VALE3", "Preço": 68.90, "Variação": "+1.5%"},
    {"Ticker": "ITUB4", "Preço": 32.15, "Variação": "-0.5%"}
]
st.table(dados)

st.markdown("---")
st.info("""
**Próximos passos:**
1. Se esta página funciona → Adicionar pandas
2. Se pandas funciona → Adicionar leitura de Excel
3. Se Excel funciona → Adicionar cálculos
""")

st.error("Se esta página NÃO aparece, o problema é no Streamlit Cloud")
