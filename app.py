import streamlit as st
from supabase import create_client, Client
import pandas as pd
from dotenv import load_dotenv
import os
import plotly.express as px

# Configuração inicial do Streamlit
st.set_page_config(page_title="Dashboard de Qualidade", layout="wide")
st.title("📊 Dashboard de Qualidade da Água")

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da Supabase
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

if not url or not key:
    st.error("Erro: Supabase URL ou Key não encontradas nas variáveis de ambiente.")
    st.stop()

supabase: Client = create_client(url, key)

# Credenciais do usuário na Supabase
SUPABASE_EMAIL = os.getenv("SUPABASE_EMAIL")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")

if not SUPABASE_EMAIL or not SUPABASE_PASSWORD:
    st.error("Erro: Credenciais do usuário da Supabase não encontradas.")
    st.stop()

# Autenticação do usuário na Supabase
try:
    user = supabase.auth.sign_up({"email": SUPABASE_EMAIL, "password": SUPABASE_PASSWORD})
except Exception:
    user = supabase.auth.sign_in_with_password({"email": SUPABASE_EMAIL, "password": SUPABASE_PASSWORD})

# Função para carregar dados da tabela 'qualidade'
def carregar_dados():
    try:
        response = supabase.table("qualidade").select("*").execute()
        if not response.data:
            return pd.DataFrame()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erro ao acessar Supabase: {str(e)}")
        return pd.DataFrame()

# Verificação da conexão
projeto_correto = url.startswith("https://") and "ebenezercarvalho" in url
# st.sidebar.markdown(f"🔗 Conexão com projeto: **{'Válida' if projeto_correto else 'Inválida'}**")

# Carregar os dados
df = carregar_dados()

# Converter 'Data Coleta' para datetime
if not df.empty:
    df["Data Coleta"] = pd.to_datetime(df["Data Coleta"], errors='coerce')
    
    # Filtrar e preparar dados para DBO e DQO
    parametros = ["DBO", "DQO"]
    df_parametros = df[df["Análise"].isin(parametros)]
    
    # Converter valores para numérico
    df_parametros["Valor"] = pd.to_numeric(df_parametros["Valor"], errors='coerce')
    
    # Criar coluna de mês/ano
    df_parametros["Mês/Ano"] = df_parametros["Data Coleta"].dt.strftime("%Y-%m")
    
    # Remover valores nulos
    df_parametros = df_parametros.dropna(subset=['Valor'])
    
    # Agrupar por mês e análise
    df_mensal = df_parametros.groupby(["Mês/Ano", "Análise"]).agg({
        "Valor": "mean",
        "Data Coleta": "first"
    }).reset_index()
    
    # Ordenar por data
    df_mensal = df_mensal.sort_values("Data Coleta")
    
    # Criar gráfico de barras agrupadas
    fig = px.bar(
        df_mensal, 
        x="Mês/Ano", 
        y="Valor",
        color="Análise",
        barmode="group",
        title="Média Mensal de DBO e DQO",
        labels={
            "Mês/Ano": "Período",
            "Valor": "Concentração Média (mg/L)",
            "Análise": "Parâmetro"
        }
    )
    
    fig.update_layout(
        xaxis_tickangle=-45,
        bargap=0.2,
        plot_bgcolor="white"
    )
    
    fig.update_yaxes(gridcolor='lightgrey')
    
    # Exibir gráfico
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado na tabela.")