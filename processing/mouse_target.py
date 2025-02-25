import psycopg2
import matplotlib.pyplot as plt
import numpy as np

# 🔹 Configuração do Banco de Dados PostgreSQL
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"


# 🔹 Conectar ao banco e buscar dados de velocidade
def get_speed_data():
    try:
        conn = psycopg2.connect(
            dbname=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            host=DB_HOST,
            port=DB_PORT
        )
        cursor = conn.cursor()

        # 🔹 Buscar os últimos 100 registros para análise
        cursor.execute("""
            SELECT avg_speed, x_position, y_position 
            FROM mouse_speed 
            JOIN mouse_events ON mouse_speed.timestamp = mouse_events.timestamp
            ORDER BY mouse_speed.timestamp DESC 
            LIMIT 100;
        """)
        rows = cursor.fetchall()
        
        cursor.close()
        conn.close()
        return rows
    except Exception as e:
        print(f"❌ Erro ao conectar ao banco: {e}")
        return []

# 🔹 Processar os dados e calcular a força de cada direção
def process_data(rows):
    direita, esquerda, cima, baixo = 0, 0, 0, 0

    for avg_speed, x, y in rows:
        if x > 0:   # Movimento para a direita
            direita += avg_speed
        elif x < 0:  # Movimento para a esquerda
            esquerda += avg_speed
        if y > 0:   # Movimento para cima
            cima += avg_speed
        elif y < 0:  # Movimento para baixo
            baixo += avg_speed

    return direita, esquerda, cima, baixo

# 🔹 Criar o gráfico do alvo
def plot_target(direita, esquerda, cima, baixo):
    angles = ["Direita", "Esquerda", "Cima", "Baixo"]
    values = [direita, esquerda, cima, baixo]

    # 🔹 Criar gráfico de radar (alvo)
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-max(values)-10, max(values)+10)
    ax.set_ylim(-max(values)-10, max(values)+10)

    # 🔹 Desenhar os círculos do alvo
    for i in range(10, max(values)+10, 10):
        circle = plt.Circle((0, 0), i, color="gray", fill=False, linestyle="dotted")
        ax.add_patch(circle)

    # 🔹 Plotar direções
    ax.quiver(0, 0, direita, 0, angles="xy", scale_units="xy", scale=1, color="red", label="Direita")
    ax.quiver(0, 0, -esquerda, 0, angles="xy", scale_units="xy", scale=1, color="blue", label="Esquerda")
    ax.quiver(0, 0, 0, cima, angles="xy", scale_units="xy", scale=1, color="green", label="Cima")
    ax.quiver(0, 0, 0, -baixo, angles="xy", scale_units="xy", scale=1, color="yellow", label="Baixo")

    # 🔹 Configurações do gráfico
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title("🔥 Alvo de Movimento do Mouse 🔥")
    ax.legend()
    
    # 🔹 Mostrar gráfico
    plt.show()

# 🔹 Rodar o programa
data = get_speed_data()
if data:
    direita, esquerda, cima, baixo = process_data(data)
    plot_target(direita, esquerda, cima, baixo)
else:
    print("⚠️ Nenhum dado encontrado!")
