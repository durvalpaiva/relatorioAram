import streamlit as st

st.set_page_config(page_title="Relatório ARAM", page_icon="📬", layout="wide")

st.title("📬 Relatório ARAM - Automação de E-mails e PDFs")

st.markdown("""
Este sistema automatiza a leitura de e-mails do Hotmail de Durval, faz download de anexos PDF, extrai dados de faturamento, ocupação e datas, e apresenta relatórios interativos.

**Funcionalidades:**
- Leitura automática de e-mails e download de PDFs
- Extração de dados dos PDFs
- Relatórios de faturamento, ocupação e datas
- Visualização de dados e gráficos
- pode conter erros... são muitos dados... ainda em fase beta.

> **Importante:** Revise os dados antes de tomar decisões com base neles
            principalmente cálculo de "gatilho".
""")

st.info("Navegue pelo menu lateral para acessar os relatórios e consultas.")
