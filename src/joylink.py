import psycopg2
import serial

# Conectar ao PostgreSQL
conn = psycopg2.connect(
    dbname="joylink_db",
    user="pi",
    password="raspberry",
    host="localhost"
)
cursor = conn.cursor()

# Criar a tabela
cursor.execute("""
CREATE TABLE IF NOT EXISTS joystick_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP DEFAULT NOW(),
    analog_x INT,
    analog_y INT,
    button_states JSONB
)
""")
conn.commit()

# Configuração da UART
ser = serial.Serial("/dev/serial0", 115200, timeout=1)

while True:
    try:
        line = ser.readline().decode("utf-8").strip()
        if line:
            data = dict(item.split("=") for item in line.split(","))
            analog_x = int(data["A0"])
            analog_y = int(data["A1"])
            button_states = {key: int(value) for key, value in data.items() if key.startswith("B")}

            cursor.execute(
                "INSERT INTO joystick_data (analog_x, analog_y, button_states) VALUES (%s, %s, %s)",
                (analog_x, analog_y, str(button_states))
            )
            conn.commit()
            print(f"Salvo: {analog_x}, {analog_y}, {button_states}")

    except Exception as e:
        print(f"Erro: {e}")
