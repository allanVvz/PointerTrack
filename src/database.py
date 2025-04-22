# data/database.py

import pg8000

def get_connection():
    try:
        return pg8000.connect(
            user="postgres",
            password="1234",
            database="postgres",
            host="localhost",
            port=5432
        )
    except Exception as e:
        print(f"❌ Falha na conexão com pg8000: {e}")
        return None
def ensure_tables():
    """
    Dropa e recria as 3 tabelas sem duplicar colunas.
    WARNING: isto apaga TODOS os dados existentes!
    """
    conn = get_connection()
    if not conn:
        return
    cur = conn.cursor()
    try:
        cur.execute("DROP TABLE IF EXISTS mouse_analyse CASCADE;")
        cur.execute("DROP TABLE IF EXISTS mouse_clicks CASCADE;")
        cur.execute("DROP TABLE IF EXISTS mouse_movements CASCADE;")

        cur.execute("""
            CREATE TABLE mouse_movements (
                id        SERIAL PRIMARY KEY,
                timestamp TIMESTAMP NOT NULL,
                x         INTEGER NOT NULL,
                y         INTEGER NOT NULL,
                L         INTEGER NOT NULL,
                U         INTEGER NOT NULL,
                R         INTEGER NOT NULL,
                D         INTEGER NOT NULL,
                X         INTEGER NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE mouse_clicks (
                id         SERIAL PRIMARY KEY,
                timestamp  TIMESTAMP NOT NULL,
                x          INTEGER NOT NULL,
                y          INTEGER NOT NULL,
                action     VARCHAR(10) NOT NULL
            );
        """)

        cur.execute("""
            CREATE TABLE mouse_analyse (
                id               SERIAL PRIMARY KEY,
                mov_id           INTEGER REFERENCES mouse_movements(id),
                vel_direita      DOUBLE PRECISION,
                vel_esquerda     DOUBLE PRECISION,
                vel_cima         DOUBLE PRECISION,
                vel_baixo        DOUBLE PRECISION,
                vel_euclidiana   DOUBLE PRECISION,
                acel_direita     DOUBLE PRECISION,
                acel_esquerda    DOUBLE PRECISION,
                acel_cima        DOUBLE PRECISION,
                acel_baixo       DOUBLE PRECISION,
                acel_euclidiana  DOUBLE PRECISION,
                timestamp        TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        print("✅ Tabelas recriadas com sucesso.")
    except Exception as e:
        print(f"❌ Erro ao recriar tabelas: {e}")
    finally:
        try: cur.close()
        except: pass
        try: conn.close()
        except: pass