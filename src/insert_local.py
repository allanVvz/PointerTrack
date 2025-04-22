# insert_local.py

import json
from datetime import datetime
import psycopg2

# ─── Variáveis de módulo ────────────────────────────────────────────────────

_conn = None
_cur  = None
_BUFFER = []
_BUFFER_SIZE = 10

# ─── Conecta e prepara (chamado automáticamente) ──────────────────────────

def _auto_init():
    """
    Se não houver conexão, abre uma e chama ensure_tables().
    """
    global _conn, _cur
    if _conn is None:
        # Ajuste user/password/database conforme seu ambiente
        dsn = (
            "dbname=postgres "
            "user=postgres "
            "password=1234 "
            "host=localhost "
            "port=5432 "
            "options='-c client_encoding=UTF8'"
        )
        try:
            _conn = psycopg2.connect(dsn)
            _cur  = _conn.cursor()
            _ensure_tables()
            print("✅ Conexão aberta e tabelas garantidas.")
        except Exception as e:
            print(f"❌ Falha ao inicializar inserter: {e}")
            _conn = None
            _cur  = None

# ─── Criação de tabelas (CREATE IF NOT EXISTS) ─────────────────────────────

def _ensure_tables():
    ddl = [
        """
        CREATE TABLE IF NOT EXISTS mouse_movements (
            id        SERIAL PRIMARY KEY,
            timestamp TIMESTAMP NOT NULL,
            dx        INTEGER   NOT NULL,
            dy        INTEGER   NOT NULL,
            L         INTEGER   NOT NULL,
            U         INTEGER   NOT NULL,
            R         INTEGER   NOT NULL,
            D         INTEGER   NOT NULL,
            X         INTEGER   NOT NULL
        );
        """,
        """
        CREATE TABLE IF NOT EXISTS mouse_clicks (
            id        SERIAL      PRIMARY KEY,
            timestamp TIMESTAMP   NOT NULL,
            dx        INTEGER     NOT NULL,
            dy        INTEGER     NOT NULL,
            action    VARCHAR(10) NOT NULL
        );
        """
    ]
    for stmt in ddl:
        _cur.execute(stmt)
    _conn.commit()

# ─── Inserção com buffer e batch de 10 ─────────────────────────────────────

def insert_local_from_json(json_payload: str):
    """
    Recebe JSON {"dx", "dy", "L","U","R","D","X"},
    e faz batch insert a cada 10 itens.
    """
    global _BUFFER

    # inicializa conexão+cursor se necessário
    _auto_init()
    if _conn is None or _cur is None:
        return

    # parse JSON
    try:
        data = json.loads(json_payload)
    except json.JSONDecodeError:
        print(f"❌ JSON inválido: {json_payload}")
        return

    print("➜ Parsed dict:", data)
    #print("   types: dx->", type(data.get("dx")), "dy->", type(data.get("dy")))
    # ───────────────────────────────────────────────────────────────────────────

    ts = datetime.now()

    # extração sem erro de chave
    dx = data.get("dx", 0)
    dy = data.get("dy", 0)
    L  = data.get("L",  0)
    U  = data.get("U",  0)
    R  = data.get("R",  0)
    D  = data.get("D",  0)
    X  = data.get("X",  0)

    # se vierem strings, converta depois do debug
    try:
        dx = int(dx)
        dy = int(dy)
        L  = int(L)
        U  = int(U)
        R  = int(R)
        D  = int(D)
        X  = int(X)
    except Exception as e:
        print(f"❌ Falha ao converter tipos: {e}")
        return

    # adiciona ao buffer
    _BUFFER.append((ts, dx, dy, L, U, R, D, X))
    print(f"📥 Buffer: {len(_BUFFER)}/{_BUFFER_SIZE}")

    # batch insert de movimentos
    if len(_BUFFER) >= _BUFFER_SIZE:
        _flush_buffer()

    # insere clique imediatamente
    #if X == 1:
    #    try:
    #        _cur.execute(
    #            "INSERT INTO mouse_clicks (timestamp, dx, dy, action) VALUES (%s,%s,%s,%s)",
    #            (ts, dx, dy, "press")
    #        )
    #        _conn.commit()
    #    except Exception as e:
    #        print(f"❌ Erro no insert_click: {e}")

def _flush_buffer():
    global _BUFFER
    if not _BUFFER:
        return
    sql = """
        INSERT INTO mouse_movements (timestamp, dx, dy, L, U, R, D, X)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    try:
        _cur.executemany(sql, _BUFFER)
        _conn.commit()
        print(f"✅ Batch insert de {len(_BUFFER)} movimentos")
    except Exception as e:
        print(f"❌ Erro no batch insert: {e}")
    finally:
        _BUFFER = []

# ─── Limpa tudo ao finalizar ────────────────────────────────────────────────

def close_inserter():
    """
    Garante que o buffer restante seja enviado e fecha conexão.
    """
    if _conn is None or _cur is None:
        return
    try:
        _flush_buffer()
    finally:
        try: _cur.close()
        except: pass
        try: _conn.close()
        except: pass
        print("🔒 Inserter encerrado.")

# ─── Se executado diretamente, apenas garante tabelas ───────────────────────

if __name__ == "__main__":
    _auto_init()
    close_inserter()
