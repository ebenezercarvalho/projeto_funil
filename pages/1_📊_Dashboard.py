import streamlit as st
from supabase import create_client, Client
import pandas as pd
from dotenv import load_dotenv
import os
import plotly.express as px

def init_connection():
    load_dotenv()
    url: str = os.getenv("SUPABASE_URL")
    key: str = os.getenv("SUPABASE_KEY")
    
    if not url or not key:
        st.error("Erro: Supabase URL ou Key não encontradas nas variáveis de ambiente.")
        st.stop()
    
    return create_client(url, key)

def authenticate_user(supabase: Client):
    email = os.getenv("SUPABASE_EMAIL")
    password = os.getenv("SUPABASE_PASSWORD")
    
    if not email or not password:
        st.error("Erro: Credenciais do usuário da Supabase não encontradas.")
        st.stop()
    
    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
    except Exception:
        user = supabase.auth.sign_in_with_password({"email": email, "password": password})
    
    return user

def load_data(supabase: Client):
    try:
        response = supabase.table("qualidade").select("*").execute()
        if not response.data:
            return pd.DataFrame()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Erro ao acessar Supabase: {str(e)}")
        return pd.DataFrame()

def process_data(df: pd.DataFrame):
    if df.empty:
        return None
    
    df["Data Coleta"] = pd.to_datetime(df["Data Coleta"], errors='coerce')
    df_parametros = df[df["Análise"].isin(["DBO", "DQO"])]
    df_parametros["Valor"] = pd.to_numeric(df_parametros["Valor"], errors='coerce')
    df_parametros["Mês/Ano"] = df_parametros["Data Coleta"].dt.strftime("%Y-%m")
    df_parametros = df_parametros.dropna(subset=['Valor'])
    
    df_mensal = df_parametros.groupby(["Mês/Ano", "Análise"]).agg({
        "Valor": "mean",
        "Data Coleta": "first"
    }).reset_index()
    
    return df_mensal.sort_values("Data Coleta")

def create_chart(df_mensal: pd.DataFrame):
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
    return fig

def main():
    st.set_page_config(page_title="Dashboard de Qualidade", layout="wide")
    st.title("📊 Dashboard de Qualidade da Água")
    
    supabase = init_connection()
    user = authenticate_user(supabase)
    df = load_data(supabase)
    
    if not df.empty:
        df_mensal = process_data(df)
        if df_mensal is not None:
            fig = create_chart(df_mensal)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Nenhum dado encontrado na tabela.")

if __name__ == "__main__":
    main()