import json
from datetime import datetime
from database import *

class MouseMovementInserter:
    def __init__(self, buffer_size: int = 10):
        """
        Inicializa o inserter: abre conexão e garante tabelas.
        :param buffer_size: número de eventos antes de batch insert
        """
        self._conn = get_connection()
        self._cur = self._conn.cursor() if self._conn else None
        self._buffer = []
        self._buffer_size = buffer_size
        if self._cur:
            self._ensure_tables()

    def _ensure_tables(self):
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
            self._cur.execute(stmt)
        self._conn.commit()

    def insert_from_json(self, json_payload: str):
        """
        Parseia JSON com chaves dx,dy,L,U,R,D,X,
        adiciona ao buffer e faz batch de movimentos;
        insere clique imediatamente.
        """
        if not self._cur:
            return

        try:
            data = json.loads(json_payload)
        except json.JSONDecodeError:
            print(f"❌ JSON inválido: {json_payload}")
            return

        ts = datetime.now()
        try:
            dx = int(data.get("dx", 0))
            dy = int(data.get("dy", 0))
            L  = int(data.get("L",  0))
            U  = int(data.get("U",  0))
            R  = int(data.get("R",  0))
            D  = int(data.get("D",  0))
            X  = int(data.get("X",  0))
        except (ValueError, TypeError) as e:
            print(f"❌ Falha ao converter tipos: {e}")
            return

        # Buffer de movimentos
        self._buffer.append((ts, dx, dy, L, U, R, D, X))
        print(f"📥 Buffer: {len(self._buffer)}/{self._buffer_size}")

        if len(self._buffer) >= self._buffer_size:
            self._flush_buffer()

        # Clique X imediato
        if X == 1:
            try:
                self._cur.execute(
                    "INSERT INTO mouse_clicks (timestamp, dx, dy, action) VALUES (%s, %s, %s, %s)",
                    (ts, dx, dy, 'press')
                )
                self._conn.commit()
            except Exception as e:
                print(f"❌ Erro no insert_click: {e}")

    def _flush_buffer(self):
        if not self._buffer:
            return
        sql = ("INSERT INTO mouse_movements "
               "(timestamp, dx, dy, L, U, R, D, X) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)")
        try:
            self._cur.executemany(sql, self._buffer)
            self._conn.commit()
            print(f"✅ Batch insert de {len(self._buffer)} movimentos")
        except Exception as e:
            print(f"❌ Erro no batch insert: {e}")
        finally:
            self._buffer.clear()

    def close(self):
        if self._cur:
            self._flush_buffer()
            try:
                self._cur.close()
                self._conn.close()
            except:
                pass

# Instância padrão e atalhos
inserter = MouseMovementInserter()
insert_local_from_json = inserter.insert_from_json
close_inserter = inserter.close

def insert_analysis(movement_ts: datetime,
                    vel_dir: float, vel_esq: float,
                    vel_cima: float, vel_baixo: float,
                    vel_euclid: float,
                    acel_dir: float, acel_esq: float,
                    acel_cima: float, acel_baixo: float,
                    acel_euclid: float):
    """
    Insere um registro na tabela mouse_analyse com os resultados de análise,
    usando o timestamp do movimento como chave.
    Só insere se movement_ts for maior que o último timestamp inserido.
    Ignora registros sem deslocamento.
    """
    # filtra movimentos sem deslocamento
    if vel_dir == 0 and vel_esq == 0 and vel_cima == 0 and vel_baixo == 0 and vel_euclid == 0:
        print(f"⏭ Análise ignorada para movimento em {movement_ts}: sem deslocamento.")
        return

    conn = get_connection()
    if conn is None:
        return
    cur = conn.cursor()
    try:
        query = (
            "INSERT INTO mouse_analyse (movement_ts, vel_direita, vel_esquerda, vel_cima, vel_baixo, "
            "vel_euclidiana, acel_direita, acel_esquerda, acel_cima, acel_baixo, acel_euclidiana) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        cur.execute(query, (
            movement_ts,
            vel_dir, vel_esq, vel_cima, vel_baixo, vel_euclid,
            acel_dir, acel_esq, acel_cima, acel_baixo, acel_euclid
        ))
        conn.commit()
        print(f"✔ Análise inserida para movimento em {movement_ts}")
    except Exception as e:
        print(f"❌ Erro ao inserir análise: {e}")
    finally:
        cur.close()
        conn.close()
