# analyze_service.py

import math
import time
from datetime import datetime
from database import get_connection
from insert_local import insert_analysis

def get_last_analysis_timestamp() -> datetime | None:
    """
    Retorna o timestamp do último registro inserido em mouse_analyse.
    Se não houver registro, retorna None.
    """
    conn = get_connection()
    if conn is None:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT timestamp FROM mouse_analyse ORDER BY movement_ts DESC LIMIT 1;"
            )
            row = cur.fetchone()
            return row[0] if row else None
    except Exception as e:
        print(f"❌ Erro ao obter último timestamp de análise: {e}")
        return None
    finally:
        conn.close()

def analyze_new_movements():
    """
    Serviço contínuo que:
      1. Lê só o MAX(timestamp) de mouse_movements para ver se há novidade.
      2. Enquanto não houver nada novo, dorme 1 s e volta.
      3. Quando surge um timestamp maior, busca esses novos registros,
         faz os cálculos e insere via insert_analysis().
    """
    print("🚀 Iniciando serviço de análise de movimentos (polling leve)…")
    last_processed_ts = None

    while True:
        # 1) Verifica só o máximo timestamp existente
        conn = get_connection()
        if conn is None:
            time.sleep(5)
            continue

        try:
            with conn.cursor() as cur:
                cur.execute("SELECT MAX(timestamp) FROM mouse_movements;")
                max_ts = cur.fetchone()[0]
        except Exception as e:
            print(f"❌ Falha ao buscar MAX(timestamp): {e}")
            conn.close()
            time.sleep(5)
            continue
        finally:
            conn.close()

        # 2) Se não mudou, dorme e repete (polling leve)
        if max_ts is None or (last_processed_ts and max_ts <= last_processed_ts):
            time.sleep(1)
            continue

        # 3) Encontrou algo novo: processa tudo entre last_processed_ts e max_ts
        print(f"🚀 Novos dados: de {last_processed_ts} até {max_ts}")

        conn = get_connection()
        if conn is None:
            time.sleep(5)
            continue

        try:
            with conn.cursor() as cur:
                if last_processed_ts:
                    cur.execute("""
                        SELECT
                          id,
                          timestamp,
                          dx,
                          dy,
                          (LEAD(timestamp) OVER (ORDER BY timestamp) - timestamp) AS tempo_delta
                        FROM mouse_movements
                        WHERE timestamp > %s
                        ORDER BY timestamp;
                    """, (last_processed_ts,))
                else:
                    cur.execute("""
                        SELECT
                          id,
                          timestamp,
                          dx,
                          dy,
                          (LEAD(timestamp) OVER (ORDER BY timestamp) - timestamp) AS tempo_delta
                        FROM mouse_movements
                        ORDER BY timestamp;
                    """)
                rows = cur.fetchall()
        except Exception as e:
            print(f"❌ Erro ao buscar movimentos novos: {e}")
            conn.close()
            time.sleep(5)
            continue
        finally:
            conn.close()

        # 4) Calcula e insere cada análise
        for mov_id, ts, dx, dy, delta in rows:
            t = delta.total_seconds() if delta and delta.total_seconds() >= 0.001 else 0.001

            vel_dir    = dx  / t if dx > 0 else 0
            vel_esq    = -dx / t if dx < 0 else 0
            vel_baixo  = dy  / t if dy > 0 else 0
            vel_cima   = -dy / t if dy < 0 else 0

            hip        = math.hypot(dx, dy)
            vel_euclid = hip / t

            acel_dir    = vel_dir    / t
            acel_esq    = vel_esq    / t
            acel_baixo  = vel_baixo  / t
            acel_cima   = vel_cima   / t
            acel_euclid = vel_euclid / t

            insert_analysis(
                movement_ts=ts,
                vel_dir=vel_dir,
                vel_esq=vel_esq,
                vel_cima=vel_cima,
                vel_baixo=vel_baixo,
                vel_euclid=vel_euclid,
                acel_dir=acel_dir,
                acel_esq=acel_esq,
                acel_cima=acel_cima,
                acel_baixo=acel_baixo,
                acel_euclid=acel_euclid
            )
            print(f"  ✔ ID {mov_id} @ {ts} analisado.")

        # 5) Atualiza o marcador e volta ao início
        last_processed_ts = max_ts
        print("✅ Lote concluído. Aguardando próximos dados…\n")

if __name__ == "__main__":
    analyze_new_movements()
