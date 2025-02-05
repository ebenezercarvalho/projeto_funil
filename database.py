from supabase import create_client
import pandas as pd
from config import SUPABASE_URL, SUPABASE_KEY

# Criar cliente Supabase
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def carregar_dados():
    """Obtém dados da tabela 'qualidade' da Supabase."""
    response = supabase.table("qualidade").select("*").execute()
    return pd.DataFrame(response.data) if response.data else pd.DataFrame()

if __name__ == "__main__":
    df = carregar_dados()
    if df.empty:
        print("Nenhum dado encontrado.")
    else:
        print(df.head())