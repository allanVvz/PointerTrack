import psycopg2

# Função para obter a conexão com o banco de dados PostgreSQL
def get_connection():
    try:
        conn = psycopg2.connect(
            dbname="postgres",
            user="postgres",
            password="1234",
            host="localhost",
            port="5432"
        )
        return conn
    except Exception as e:
        print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
        return None
