from pynput import mouse
from datetime import datetime
import time

# Importa as funções de inserção do módulo insert_local
from data.insert_local import insert_movement_event, insert_click_event

# Variável para indicar se há um movimento ativo
movimento_ativo = False

# Buffer para acumular os dados de movimento (cada item: (x, y, timestamp))
buffer_movimento = []

# Acumuladores para deslocamentos relativos
dx_direita = 0.0   # Deslocamento para a direita (x positivo)
dx_esquerda = 0.0  # Deslocamento para a esquerda (x negativo, armazenado como valor positivo)
dy_cima = 0.0      # Deslocamento para cima (y negativo, armazenado como valor positivo)
dy_baixo = 0.0     # Deslocamento para baixo (y positivo)

# Parâmetro para considerar o mouse parado (sem movimento por 1 segundo)
TEMPO_INATIVIDADE = 1.0

# Variáveis auxiliares para o último evento
ultimo_x, ultimo_y, ultimo_t = None, None, None

def reset_movimento():
    global buffer_movimento, dx_direita, dx_esquerda, dy_cima, dy_baixo, ultimo_x, ultimo_y, ultimo_t
    buffer_movimento = []
    dx_direita = 0.0
    dx_esquerda = 0.0
    dy_cima = 0.0
    dy_baixo = 0.0
    ultimo_x, ultimo_y, ultimo_t = None, None, None

def on_move(x, y):
    global movimento_ativo, buffer_movimento, dx_direita, dx_esquerda, dy_cima, dy_baixo, ultimo_x, ultimo_y, ultimo_t

    agora = datetime.now()
    # Se não há movimento ativo, inicia a sessão de movimento
    if not movimento_ativo:
        movimento_ativo = True
        reset_movimento()
        ultimo_x, ultimo_y, ultimo_t = x, y, agora
        buffer_movimento.append((x, y, agora))
    else:
        # Calcula as diferenças relativas
        dx = x - ultimo_x
        dy = y - ultimo_y

        # Acumula os deslocamentos por direção
        if dx > 0:
            dx_direita += dx
        elif dx < 0:
            dx_esquerda += abs(dx)
        if dy < 0:
            dy_cima += abs(dy)
        elif dy > 0:
            dy_baixo += dy

        buffer_movimento.append((x, y, agora))
        ultimo_x, ultimo_y, ultimo_t = x, y, agora

def on_click(x, y, button, pressed):
    timestamp = datetime.now()
    action = "press" if pressed else "release"
    button_name = button.name  # 'left' ou 'right'
    # Insere o evento de clique na tabela 'mouse_clicks'
    insert_click_event(timestamp, button_name, action, x, y)
    # Se houver um clique e um movimento ativo, finaliza o movimento
    global movimento_ativo
    if movimento_ativo:
        finalizar_movimento()

def finalizar_movimento():
    global movimento_ativo, buffer_movimento, dx_direita, dx_esquerda, dy_cima, dy_baixo
    if not buffer_movimento:
        return
    # Usa o timestamp do último evento como o fim do movimento
    timestamp_final = buffer_movimento[-1][2]
    # Insere os dados de movimento na tabela 'mouse_movements'
    insert_movement_event(timestamp_final, dx_direita, dx_esquerda, dy_cima, dy_baixo)
    reset_movimento()
    movimento_ativo = False

def check_inatividade():
    """
    Verifica periodicamente se não houve movimento por TEMPO_INATIVIDADE segundos;
    se sim, finaliza o movimento.
    """
    while True:
        time.sleep(0.5)
        if movimento_ativo and buffer_movimento:
            ultimo_evento = buffer_movimento[-1]
            if (datetime.now() - ultimo_evento[2]).total_seconds() >= TEMPO_INATIVIDADE:
                finalizar_movimento()

def iniciar_captura():
    """
    Função principal para iniciar a captura dos dados do mouse.
    """
    # Inicia uma thread para monitorar inatividade
    import threading
    threading.Thread(target=check_inatividade, daemon=True).start()
    # Inicia o listener do mouse
    with mouse.Listener(on_move=on_move, on_click=on_click) as listener:
        listener.join()

if __name__ == "__main__":
    iniciar_captura()
