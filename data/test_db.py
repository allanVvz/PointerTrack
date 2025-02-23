import psycopg2

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user="postgres",  # Mude se seu usuário for diferente
        password="1234",
        host="localhost",
        port="5432"
    )
    cursor = conn.cursor()
    print("✅ Conectado ao PostgreSQL!")
    
    # Testando um SELECT
    cursor.execute("SELECT * FROM mouse_events;")
    print(cursor.fetchall())  # Deve estar vazio no começo

    cursor.close()
    conn.close()
except Exception as e:
    print(f"❌ Erro ao conectar: {e}")
