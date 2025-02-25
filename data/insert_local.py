from data.database import get_connection

def insert_movement_event(timestamp, dx_direita, dx_esquerda, dy_cima, dy_baixo):
    """
    Insere um evento de movimento na tabela 'mouse_movements'.
    - timestamp: data/hora do evento.
    - dx_direita: deslocamento acumulado para a direita (valores positivos).
    - dx_esquerda: deslocamento acumulado para a esquerda (valores positivos).
    - dy_cima: deslocamento acumulado para cima (valores positivos).
    - dy_baixo: deslocamento acumulado para baixo (valores positivos).
    """
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO mouse_movements (timestamp, dx_direita, dx_esquerda, dy_cima, dy_baixo)
        VALUES (%s, %s, %s, %s, %s);
        """
        cursor.execute(query, (timestamp, dx_direita, dx_esquerda, dy_cima, dy_baixo))
        conn.commit()
        print(f"✔ Evento de movimento inserido: {timestamp}, dx_direita={dx_direita}, dx_esquerda={dx_esquerda}, dy_cima={dy_cima}, dy_baixo={dy_baixo}")
    except Exception as e:
        print(f"❌ Erro ao inserir evento de movimento: {e}")
    finally:
        cursor.close()
        conn.close()

def insert_click_event(timestamp, button, action, x_position, y_position):
    """
    Insere um evento de clique na tabela 'mouse_clicks'.
    - timestamp: data/hora do evento.
    - button: nome do botão ('left' ou 'right').
    - action: 'press' ou 'release'.
    - x_position, y_position: posição do mouse no momento do clique.
    
    Os dados serão inseridos nas colunas correspondentes:
      - Se button for 'left', será populada a coluna button1.
      - Se button for 'right', será populada a coluna button2.
      - As demais colunas (button3 a button14) permanecerão nulas.
    """
    conn = get_connection()
    if conn is None:
        return
    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO mouse_clicks (timestamp, button1, button2, button3, button4, button5,
                                  button6, button7, button8, button9, button10, button11,
                                  button12, button13, button14, x_position, y_position)
        VALUES (%s, %s, %s, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, %s, %s);
        """
        # Se o clique for esquerdo, preenche a coluna button1; se for direito, preenche a coluna button2.
        if button == "left":
            b1, b2 = action, None
        elif button == "right":
            b1, b2 = None, action
        else:
            b1, b2 = None, None

        cursor.execute(query, (timestamp, b1, b2, x_position, y_position))
        conn.commit()
        print(f"✔ Evento de clique inserido: {timestamp}, button1={b1}, button2={b2}, x={x_position}, y={y_position}")
    except Exception as e:
        print(f"❌ Erro ao inserir evento de clique: {e}")
    finally:
        cursor.close()
        conn.close()


def insert_analysis(mov_id, vel_direita, vel_esquerda, vel_cima, vel_baixo, vel_euclidiana,
                    acel_direita, acel_esquerda, acel_cima, acel_baixo, acel_euclidiana):
    """
    Insere os resultados da análise de movimento na tabela `mouse_analyse`.

    - `mov_id`: ID do movimento analisado.
    - `vel_direita`, `vel_esquerda`, `vel_cima`, `vel_baixo`: Velocidade média em cada direção.
    - `vel_euclidiana`: Velocidade considerando deslocamento euclidiano.
    - `acel_direita`, `acel_esquerda`, `acel_cima`, `acel_baixo`: Aceleração média em cada direção.
    - `acel_euclidiana`: Aceleração média considerando deslocamento euclidiano.
    """
    conn = get_connection()
    if conn is None:
        return

    cursor = conn.cursor()
    try:
        query = """
        INSERT INTO mouse_analyse (mov_id, vel_direita, vel_esquerda, vel_cima, vel_baixo, vel_euclidiana,
                                   acel_direita, acel_esquerda, acel_cima, acel_baixo, acel_euclidiana)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """
        cursor.execute(query, (mov_id, vel_direita, vel_esquerda, vel_cima, vel_baixo, vel_euclidiana,
                               acel_direita, acel_esquerda, acel_cima, acel_baixo, acel_euclidiana))
        conn.commit()
        print(f"✔ Análise inserida para Movimento ID {mov_id}")
    except Exception as e:
        print(f"❌ Erro ao inserir análise: {e}")
    finally:
        cursor.close()
        conn.close()