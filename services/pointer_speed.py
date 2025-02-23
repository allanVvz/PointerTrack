import psycopg2
import time
import numpy as np  # Para calcular variância

# 🔹 Configuração do PostgreSQL
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"

# 🔹 Definição do delta de tempo (ajustável)
DELTA_TIME = 0.5  # Meio segundo

# 🔹 Função para calcular velocidade
def calcular_variancia_velocidade():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # 🔹 Pegar eventos do mouse nos últimos DELTA_TIME segundos
        cursor.execute(f"""
            SELECT timestamp, x_position, y_position 
            FROM mouse_events
            WHERE timestamp >= NOW() - INTERVAL '{DELTA_TIME} seconds'
            ORDER BY timestamp ASC;
        """)
        rows = cursor.fetchall()

        if len(rows) < 2:
            print("⏳ Poucos dados para calcular velocidade. Aguardando mais eventos...")
            cursor.close()
            conn.close()
            return

        # 🔹 Calcular diferenças entre os pontos no tempo
        velocidades = []
        for i in range(1, len(rows)):
            t1, x1, y1 = rows[i - 1]
            t2, x2, y2 = rows[i]

            # Calcular deslocamento (distância euclidiana)
            deslocamento = np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

            # Calcular diferença de tempo em segundos
            delta_t = (t2 - t1).total_seconds()

            # Calcular velocidade (pixels por segundo)
            if delta_t > 0:
                velocidade = deslocamento / delta_t
                velocidades.append(velocidade)

        # 🔹 Calcular estatísticas de velocidade
        if velocidades:
            avg_speed = np.mean(velocidades)
            speed_variance = np.var(velocidades)
        else:
            avg_speed = 0
            speed_variance = 0

        print(f"✅ Média de Velocidade: {avg_speed:.2f} px/s | Variância: {speed_variance:.2f}")

        # 🔹 Inserir os dados calculados na tabela mouse_speed
        cursor.execute("""
            INSERT INTO mouse_speed (avg_speed, speed_variance, delta_time) 
            VALUES (%s, %s, %s);
        """, (float(avg_speed), float(speed_variance), DELTA_TIME))

        conn.commit()
        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Erro ao calcular variância da velocidade: {e}")

# 🔹 Serviço que roda continuamente
print("🚀 Iniciando serviço de monitoramento de velocidade...")
while True:
    calcular_variancia_velocidade()
    time.sleep(DELTA_TIME)  # Espera meio segundo antes da próxima leitura
