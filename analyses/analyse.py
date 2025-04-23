import time
import math
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from insert_local import *


def analyze_and_plot():
    """
    Executa continuamente:
    1. Processa apenas novos registros da tabela `mouse_movements`.
    2. Insere os cálculos na tabela `mouse_analyse`.
    3. Plota gráficos de evolução da velocidade.
    """
    while True:
        conn = get_connection()
        if conn is None:
            time.sleep(5)
            continue

        cursor = conn.cursor()
        try:
            # 🔹 Busca apenas movimentos que ainda não foram processados
            cursor.execute(f"""
                SELECT id, timestamp, dx_direita, dx_esquerda, dy_cima, dy_baixo,
                    (LEAD(timestamp) OVER (ORDER BY timestamp) - timestamp) AS tempo_total
                FROM mouse_movements
                ORDER BY timestamp ASC;
            """)
            rows = cursor.fetchall()

            velocities = []
            timestamps = []

            mov_id, ts, dx_direita, dx_esquerda, dy_cima, dy_baixo, tempo_total = rows

            # ⚠ Evita divisão por zero
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

            # Salvando os dados para visualização
            velocities.append([vel_direita, vel_esquerda, vel_cima, vel_baixo, vel_euclidiana])
            timestamps.append(ts)


            print("✅ Todos os novos movimentos foram processados!\n")

            # 📊 Gera gráficos a cada iteração
            df = pd.DataFrame(velocities, columns=["Velocidade Direita", "Velocidade Esquerda", "Velocidade Cima", "Velocidade Baixo", "Velocidade Euclidiana"])

            # 📈 1. Gráfico de Linha - Evolução da Velocidade ao Longo do Tempo
            plt.figure(figsize=(10, 5))
            plt.plot(df.index, df["Velocidade Direita"], label="Direita", linestyle='-', marker='o')
            plt.plot(df.index, df["Velocidade Esquerda"], label="Esquerda", linestyle='--', marker='s')
            plt.plot(df.index, df["Velocidade Cima"], label="Cima", linestyle='-.', marker='^')
            plt.plot(df.index, df["Velocidade Baixo"], label="Baixo", linestyle=':', marker='d')
            plt.xlabel("Movimentos")
            plt.ylabel("Velocidade (px/s)")
            plt.title("Evolução da Velocidade nas Direções")
            plt.legend()
            plt.grid(True)
            plt.show()

            # 📊 2. Histograma - Distribuição das Velocidades
            plt.figure(figsize=(10, 5))
            plt.hist(df["Velocidade Direita"], bins=10, alpha=0.5, label="Direita")
            plt.hist(df["Velocidade Esquerda"], bins=10, alpha=0.5, label="Esquerda")
            plt.hist(df["Velocidade Cima"], bins=10, alpha=0.5, label="Cima")
            plt.hist(df["Velocidade Baixo"], bins=10, alpha=0.5, label="Baixo")
            plt.xlabel("Velocidade (px/s)")
            plt.ylabel("Frequência")
            plt.title("Distribuição das Velocidades")
            plt.legend()
            plt.grid(True)
            plt.show()

            # 📊 3. Boxplot - Comparação das Velocidades por Direção
            plt.figure(figsize=(8, 6))
            df.boxplot(column=["Velocidade Direita", "Velocidade Esquerda", "Velocidade Cima", "Velocidade Baixo"])
            plt.ylabel("Velocidade (px/s)")
            plt.title("Boxplot das Velocidades nas Direções")
            plt.grid(True)
            plt.show()

        except Exception as e:
            print(f"❌ Erro ao processar movimentos: {e}")

        finally:
            cursor.close()
            conn.close()

        time.sleep(2)  # Aguarda 2 segundos antes de verificar novos dados

if __name__ == "__main__":
    print("🚀 Serviço de análise de movimentos iniciado...\nPressione Ctrl+C para interromper.\n")
    analyze_and_plot()
