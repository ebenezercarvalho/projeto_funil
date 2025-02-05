import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Print para debug (remova depois)
print("SUPABASE_KEY:", os.getenv("SUPABASE_KEY"))

SUPABASE_URL = os.getenv("SUPABASE_URL", "https://irxeceulcxzqirwtwjwh.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_KEY:
    raise ValueError("A chave da API Supabase não foi encontrada. Defina a variável SUPABASE_KEY no ambiente ou no arquivo .env.")