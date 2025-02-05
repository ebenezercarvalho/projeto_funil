import streamlit as st
from supabase import create_client, Client
import pandas as pd
from dotenv import load_dotenv
import os

st.set_page_config(page_title="Database", layout="wide")
st.title("📋 Banco de Dados")

# Carregar variáveis de ambiente
load_dotenv()

# Configuração da Supabase
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")

if not url or not key:
    st.error("Erro: Supabase URL ou Key não encontradas nas variáveis de ambiente.")
    st.stop()

supabase: Client = create_client(url, key)

# Autenticação
SUPABASE_EMAIL = os.getenv("SUPABASE_EMAIL")
SUPABASE_PASSWORD = os.getenv("SUPABASE_PASSWORD")

if not SUPABASE_EMAIL or not SUPABASE_PASSWORD:
    st.error("Erro: Credenciais do usuário da Supabase não encontradas.")
    st.stop()

try:
    user = supabase.auth.sign_up({"email": SUPABASE_EMAIL, "password": SUPABASE_PASSWORD})
except Exception:
    user = supabase.auth.sign_in_with_password({"email": SUPABASE_EMAIL, "password": SUPABASE_PASSWORD})

# Carregar dados
response = supabase.table("qualidade").select("*").execute()
if response.data:
    df = pd.DataFrame(response.data)
    st.dataframe(df, use_container_width=True)
else:
    st.warning("Nenhum dado encontrado na tabela.")