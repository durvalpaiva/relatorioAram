"""
Conexão com banco de dados - Supabase ou SQLite
Projeto: relatorioAram
"""

import os
import sqlite3
import pandas as pd
from typing import Optional
from dotenv import load_dotenv
import streamlit as st

# Carregar variáveis de ambiente
load_dotenv()

def get_database_connection():
    """
    Conecta ao banco de dados - SQLite (local) para desenvolvimento
    Supabase será usado apenas em produção
    """
    # Para desenvolvimento, sempre usar SQLite local
    if os.path.exists('relatorios.db'):
        return {"type": "sqlite", "client": sqlite3.connect('relatorios.db')}
    
    # Se não existir o arquivo SQLite, tentar Supabase como fallback
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_ANON_KEY")
    
    if supabase_url and supabase_key:
        try:
            from supabase import create_client
            client = create_client(supabase_url, supabase_key)
            # Testar se as tabelas existem
            result = client.table('rds_vendas').select("*").limit(1).execute()
            return {"type": "supabase", "client": client}
        except ImportError:
            st.warning("⚠️ Supabase não instalado, criando SQLite local")
            return {"type": "sqlite", "client": sqlite3.connect('relatorios.db')}
        except Exception as e:
            st.info("ℹ️ Usando banco SQLite local (tabelas Supabase não criadas ainda)")
            return {"type": "sqlite", "client": sqlite3.connect('relatorios.db')}
    else:
        # Criar SQLite local se não existir
        return {"type": "sqlite", "client": sqlite3.connect('relatorios.db')}

def execute_query(query: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """
    Executa query SQL e retorna DataFrame
    Compatível com Supabase e SQLite
    """
    db_conn = get_database_connection()
    
    try:
        if db_conn["type"] == "supabase":
            # Para Supabase, converter SQL para PostgREST
            return execute_supabase_query(db_conn["client"], query, params)
        else:
            # SQLite tradicional
            if params:
                return pd.read_sql_query(query, db_conn["client"], params=params)
            else:
                return pd.read_sql_query(query, db_conn["client"])
    except Exception as e:
        st.error(f"❌ Erro na query: {str(e)}")
        return pd.DataFrame()
    finally:
        if db_conn["type"] == "sqlite":
            db_conn["client"].close()

def execute_supabase_query(client, query: str, params: Optional[tuple] = None) -> pd.DataFrame:
    """
    Converte queries SQL para Supabase PostgREST
    """
    # Determinar tabela principal da query
    query_lower = query.lower().strip()
    
    if "from rds_vendas" in query_lower:
        table = "rds_vendas"
    elif "from chart_compradores_duplo" in query_lower:
        table = "chart_compradores_duplo"
    elif "from chart_compradores" in query_lower:
        table = "chart_compradores"
    elif "from vendas_internas" in query_lower:
        table = "vendas_internas"
    elif "from eventos" in query_lower:
        table = "eventos"
    else:
        raise ValueError(f"Tabela não identificada na query: {query}")
    
    # Executar query básica (pode ser expandida conforme necessário)
    try:
        result = client.table(table).select("*").execute()
        df = pd.DataFrame(result.data)
        
        # Aplicar filtros se necessário
        if params and "WHERE data =" in query:
            # Exemplo de filtro por data
            df = df[df['data'] == params[0]]
        
        return df
    
    except Exception as e:
        st.error(f"❌ Erro na query Supabase: {str(e)}")
        return pd.DataFrame()

def insert_data(table: str, data: dict) -> bool:
    """
    Insere dados na tabela especificada
    """
    db_conn = get_database_connection()
    
    try:
        if db_conn["type"] == "supabase":
            result = db_conn["client"].table(table).insert(data).execute()
            return len(result.data) > 0
        else:
            # SQLite
            conn = db_conn["client"]
            columns = list(data.keys())
            values = list(data.values())
            placeholders = ','.join(['?' for _ in values])
            
            query = f"INSERT INTO {table} ({','.join(columns)}) VALUES ({placeholders})"
            cursor = conn.cursor()
            cursor.execute(query, values)
            conn.commit()
            return True
    
    except Exception as e:
        st.error(f"❌ Erro ao inserir dados: {str(e)}")
        return False
    finally:
        if db_conn["type"] == "sqlite":
            db_conn["client"].close()

def test_connection() -> bool:
    """
    Testa a conexão com o banco de dados
    """
    try:
        db_conn = get_database_connection()
        
        if db_conn["type"] == "supabase":
            # Testar com query simples
            result = db_conn["client"].table("rds_vendas").select("*").limit(1).execute()
            return True
        else:
            # SQLite
            conn = db_conn["client"]
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            conn.close()
            return True
    
    except Exception as e:
        st.error(f"❌ Erro na conexão: {str(e)}")
        return False
