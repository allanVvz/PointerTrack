# data/database.py
import os
from typing import Optional
import psycopg2

def get_connection():
    """
    Abre e retorna uma conexão psycopg2 com o banco de dados.
    - PG_DB: nome do banco (default: 'postgres')
    - PG_USER: usuário (default: 'postgres')
    - PG_PASS: senha (default: '1234')
    - PG_HOST: host (default: 'localhost')
    - PG_PORT: porta (default: '5432')

    Retorna None caso falhe na conexão.
    """
    try:
        conn = psycopg2.connect(
            dbname=os.getenv("PG_DB", "postgres"),
            user=os.getenv("PG_USER", "postgres"),
            password=os.getenv("PG_PASS", "1234"),
            host=os.getenv("PG_HOST", "localhost"),
            port=os.getenv("PG_PORT", "5432"),
            options="-c client_encoding=UTF8"
        )
        return conn
    except Exception as e:
        print(f"❌ Falha ao conectar no PostgreSQL: {e}")
        return None
    