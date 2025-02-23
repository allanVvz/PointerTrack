import psycopg2
from pynput import mouse
from datetime import datetime

# 🔹 Configuração do PostgreSQL
DB_NAME = "postgres"
DB_USER = "postgres"
DB_PASSWORD = "1234"
DB_HOST = "localhost"
DB_PORT = "5432"

# 🔹 Conectar ao banco de dados
try:
    conn = psycopg2.connect(
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT
    )
    cursor = conn.cursor()
    print("✅ Conectado ao PostgreSQL!")

    # 🔹 Criar tabela se não existir
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mouse_events (
        id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        event_type VARCHAR(10),
        x_position INT,
        y_position INT,
        button VARCHAR(10),
        action VARCHAR(10)
    );
    """)
    conn.commit()
    print("✅ Tabela 'mouse_events' pronta!")

except Exception as e:
    print(f"❌ Erro ao conectar ao PostgreSQL: {e}")
    exit()

# 🔹 Função para inserir eventos no banco
def insert_event(event_type, x, y, button=None, action=None):
    try:
        cursor.execute(
            "INSERT INTO mouse_events (event_type, x_position, y_position, button, action) VALUES (%s, %s, %s, %s, %s)",
            (event_type, x, y, button, action)
        )
        conn.commit()
        print(f"✔ {event_type} registrado: X={x}, Y={y}, Botão={button}, Ação={action}")
    except Exception as e:
        print(f"❌ Erro ao inserir evento: {e}")

# 🔹 Captura de eventos do mouse
def on_move(x, y):
    insert_event("move", x, y)

def on_click(x, y, button, pressed):
    action = "press" if pressed else "release"
    button_name = button.name  # "right", "left", "middle", etc.
    insert_event("click", x, y, button_name, action)


# 🔹 Inicia a captura de eventos do mouse
with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
    listener.join()

# 🔹 Fechar conexão ao finalizar
cursor.close()
conn.close()
