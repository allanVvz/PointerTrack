from data.database import get_connection
from data.insert_local import insert_analysis
import math
import time

def get_last_processed_id():
    """
    Busca o último ID de movimento processado na tabela `mouse_analyse`.
    Se a tabela estiver vazia, retorna 0 para processar tudo desde o início.
    """
    conn = get_connection()
    if conn is None:
        return 0  # Se houver erro na conexão, começamos do início

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COALESCE(MAX(mov_id), 0) FROM mouse_analyse;")
        last_id = cursor.fetchone()[0]
        return last_id
    except Exception as e:
        print(f"❌ Erro ao buscar último ID processado: {e}")
        return 0
    finally:
        cursor.close()
        conn.close()

def analyze_new_movements():
    """
    Roda continuamente, analisando apenas novos registros de `mouse_movements`
    e inserindo os resultados na tabela `mouse_analyse`.
    """
    while True:
        conn = get_connection()
        if conn is None:
            time.sleep(5)  # Aguarda 5 segundos antes de tentar reconectar
            continue

        cursor = conn.cursor()
        try:
            last_processed_id = get_last_processed_id()

            # 🔹 Busca apenas movimentos que ainda não foram processados
            cursor.execute(f"""
                SELECT id, timestamp, dx_direita, dx_esquerda, dy_cima, dy_baixo,
                    (LEAD(timestamp) OVER (ORDER BY timestamp) - timestamp) AS tempo_total
                FROM mouse_movements
                WHERE id > {last_processed_id}
                ORDER BY timestamp ASC;
            """)
            rows = cursor.fetchall()
            if not rows:
                print("⏳ Nenhum novo movimento encontrado. Aguardando novos registros...")
                time.sleep(5)  # Aguarda 5 segundos antes de tentar novamente
                continue

            print(f"🚀 Processando {len(rows)} novos movimentos...\n")
            for row in rows:
                mov_id, ts, dx_direita, dx_esquerda, dy_cima, dy_baixo, tempo_total = row
                
                # ⚠ Evita divisão por zero e converte `tempo_total` para segundos
                if tempo_total is None or tempo_total.total_seconds() < 0.01:
                    tempo_total = 0.01
                else:
                    tempo_total = tempo_total.total_seconds()

                # Calcula deslocamentos líquidos
                net_dx = dx_direita - dx_esquerda
                net_dy = dy_baixo - dy_cima

                # Distância Euclidiana (hipotenusa)
                deslocamento_euclidiano = math.sqrt(net_dx**2 + net_dy**2)

                # Calculando velocidades médias (px/s)
                vel_direita = dx_direita / tempo_total
                vel_esquerda = dx_esquerda / tempo_total
                vel_cima = dy_cima / tempo_total
                vel_baixo = dy_baixo / tempo_total
                vel_euclidiana = deslocamento_euclidiano / tempo_total

                # Calculando acelerações médias (px/s²)
                acel_direita = vel_direita / tempo_total
                acel_esquerda = vel_esquerda / tempo_total
                acel_cima = vel_cima / tempo_total
                acel_baixo = vel_baixo / tempo_total
                acel_euclidiana = vel_euclidiana / tempo_total

                # Inserir análise no banco de dados
                insert_analysis(mov_id, vel_direita, vel_esquerda, vel_cima, vel_baixo, vel_euclidiana,
                                acel_direita, acel_esquerda, acel_cima, acel_baixo, acel_euclidiana)

                print(f"✔ Movimento {mov_id} analisado.")

            print("✅ Todos os novos movimentos foram processados!\n")

        except Exception as e:
            print(f"❌ Erro ao processar movimentos: {e}")

        finally:
            cursor.close()
            conn.close()

        time.sleep(2)  # Aguarda 2 segundos antes de verificar novos dados

if __name__ == "__main__":
    print("🚀 Serviço de análise de movimentos iniciado...\nPressione Ctrl+C para interromper.\n")
    analyze_new_movements()
