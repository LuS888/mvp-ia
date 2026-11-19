import streamlit as st
import pandas as pd

# Configuração da página
st.set_page_config(page_title="IAV - Inteligência Artificial em Valor", layout="wide")

# Injeção de CSS para a Identidade Visual (Paleta IAV)
st.markdown("""
    <style>
    /* Fundo principal e cor do texto */
    .stApp {
        background-color: #311951; /* Roxo Escuro */
        color: #E4F4F4; /* Cinza Claro */
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #451477; /* Roxo Médio */
    }
    
    /* Títulos e Cabeçalhos */
    h1, h2, h3, h4, h5, h6 {
        color: #E4F4F4 !important;
    }
    
    /* Botões */
    .stButton>button {
        background-color: #626496; /* Roxo Claro */
        color: #E4F4F4;
        border: none;
        border-radius: 5px;
    }
    .stButton>button:hover {
        background-color: #451477;
        color: #E4F4F4;
    }
    
    /* Tabelas do DataFrame */
    [data-testid="stDataFrame"] {
        background-color: #E4F4F4;
    }
    
    /* Métricas (Cards) */
    [data-testid="stMetricValue"] {
        color: #E4F4F4;
    }
    [data-testid="stMetricLabel"] {
        color: #626496;
    }
    
    /* Caixa de informação (Info) */
    .stAlert {
        background-color: #451477;
        color: #E4F4F4;
        border: 1px solid #626496;
    }
    </style>
""", unsafe_allow_html=True)

st.title("IAV: Gestão de Modelos de IA como Ativo de Valor")
st.caption("Protótipo acadêmico — TCC MBA ICMC/USP. Dados fictícios para demonstração.")

TAXA_ANUAL = 0.10
MESES_VIDA_UTIL = 24
TAXA_MENSAL = (1 + TAXA_ANUAL) ** (1/12) - 1

def calcular(custo_treino, custo_dado, custo_inferencia, custo_manutencao, beneficio_mensal):
    ctm = (custo_treino / MESES_VIDA_UTIL) + (custo_dado / MESES_VIDA_UTIL) + custo_inferencia + custo_manutencao
    blm = beneficio_mensal - ctm
    if blm > 0:
        fator = (1 - (1 + TAXA_MENSAL) ** -MESES_VIDA_UTIL) / TAXA_MENSAL
        vpl = blm * fator - custo_treino - custo_dado
    else:
        vpl = blm * MESES_VIDA_UTIL - custo_treino - custo_dado
    custo_total = custo_treino + custo_dado + (ctm * MESES_VIDA_UTIL)
    beneficio_total = beneficio_mensal * MESES_VIDA_UTIL
    roi = ((beneficio_total - custo_total) / custo_total * 100) if custo_total > 0 else 0
    payback = (custo_treino + custo_dado) / blm if blm > 0 else None
    if roi > 30 and payback and payback < 12:
        rec = "ESCALAR"
    elif roi >= 0:
        rec = "MANTER"
    elif roi >= -10:
        rec = "REVISAR"
    else:
        rec = "APOSENTAR"
    return {"CTM": ctm, "BLM": blm, "VPL": vpl, "ROI": roi, "Payback": payback, "Recomendação": rec}

# Dados fictícios
modelos_demo = [
    {"Modelo": "Churn Preditivo", "Área": "Vendas", "Custo Treino": 80000, "Custo Dado": 20000,
     "Custo Inferência": 3000, "Custo Manutenção": 2000, "Benefício Mensal": 25000},
    {"Modelo": "Triagem de CV", "Área": "RH", "Custo Treino": 30000, "Custo Dado": 10000,
     "Custo Inferência": 1500, "Custo Manutenção": 1000, "Benefício Mensal": 5000},
    {"Modelo": "Previsão de Demanda", "Área": "Operações", "Custo Treino": 60000, "Custo Dado": 15000,
     "Custo Inferência": 4000, "Custo Manutenção": 3000, "Benefício Mensal": 6000},
]

st.sidebar.header("Cadastrar novo modelo")
with st.sidebar.form("form_modelo"):
    nome = st.text_input("Nome do modelo", "Novo Modelo")
    area = st.selectbox("Área", ["Vendas", "RH", "Operações", "Financeiro"])
    ct = st.number_input("Custo de treinamento (R$)", 0.0, value=50000.0, step=1000.0)
    cd = st.number_input("Custo do dado (R$)", 0.0, value=10000.0, step=1000.0)
    ci = st.number_input("Custo mensal de inferência (R$)", 0.0, value=2000.0, step=500.0)
    cm = st.number_input("Custo mensal de manutenção (R$)", 0.0, value=1000.0, step=500.0)
    bm = st.number_input("Benefício mensal estimado (R$)", 0.0, value=10000.0, step=1000.0)
    submitted = st.form_submit_button("Calcular valuation")
    if submitted:
        modelos_demo.append({"Modelo": nome, "Área": area, "Custo Treino": ct, "Custo Dado": cd,
                             "Custo Inferência": ci, "Custo Manutenção": cm, "Benefício Mensal": bm})

linhas = []
for m in modelos_demo:
    r = calcular(m["Custo Treino"], m["Custo Dado"], m["Custo Inferência"], m["Custo Manutenção"], m["Benefício Mensal"])
    linhas.append({"Modelo": m["Modelo"], "Área": m["Área"], "VPL (R$)": round(r["VPL"], 2),
                   "ROI (%)": round(r["ROI"], 1),
                   "Payback (meses)": round(r["Payback"], 1) if r["Payback"] else "Não recupera",
                   "Recomendação": r["Recomendação"]})
df = pd.DataFrame(linhas)

st.subheader("Portfólio de Modelos")
st.dataframe(df, use_container_width=True)

st.subheader("Detalhe do modelo selecionado")
sel = st.selectbox("Escolha um modelo", df["Modelo"])
m_sel = next(m for m in modelos_demo if m["Modelo"] == sel)
r = calcular(m_sel["Custo Treino"], m_sel["Custo Dado"], m_sel["Custo Inferência"], m_sel["Custo Manutenção"], m_sel["Benefício Mensal"])

col1, col2, col3, col4 = st.columns(4)
col1.metric("VPL (24 meses)", f"R$ {r['VPL']:,.0f}")
col2.metric("ROI", f"{r['ROI']:.1f}%")
col3.metric("Payback", f"{r['Payback']:.1f} meses" if r['Payback'] else "Não recupera")
col4.metric("Recomendação", r["Recomendação"])

st.info("Este é um protótipo acadêmico com dados fictícios. O objetivo é demonstrar o conceito de valuation de modelos de IA como ativos de negócio.")