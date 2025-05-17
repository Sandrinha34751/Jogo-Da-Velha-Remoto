import sqlite3
import os

# Caminho do banco de dados, com valor padrão 'jogo_da_velha.db'
DB_PATH = os.getenv('DB_PATH', 'jogo_da_velha.db')

# Senha do banco, usada apenas para simular verificação simples
DB_SENHA = os.getenv('DB_SENHA', 'senha123') 

# Verifica se a senha do ambiente é a correta 
def verificar_senha():
    if DB_SENHA != 'senha123':
        print("Senha incorreta. Encerrando aplicação.")
        exit()

# Inicializa o banco de dados e cria a tabela de jogadas, se não existir
def iniciar_banco():
    verificar_senha()
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS jogadas (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  jogador TEXT,
                  estado TEXT
              )''')
    conn.commit()
    conn.close()

# Registra uma jogada no banco de dados, associando o jogador ao estado do tabuleiro
def registrar_jogada(jogador, estado):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('INSERT INTO jogadas (jogador, estado) VALUES (?, ?)', (jogador, estado))
    conn.commit()
    conn.close()

# Converte a matriz 3x3 do jogo para uma string linear (para armazenamento ou envio via rede)
def matriz_para_string(matriz):
    return ''.join([celula for linha in matriz for celula in linha])

# Converte a string de volta para uma matriz 3x3 (para reconstruir o tabuleiro)
def string_para_matriz(s):
    return [[s[i * 3 + j] for j in range(3)] for i in range(3)]

# Verifica se o jogador com o símbolo fornecido venceu o jogo
def verificar_vitoria(matriz, simbolo):
    for i in range(3):
        # Verifica linhas e colunas
        if all(matriz[i][j] == simbolo for j in range(3)) or all(matriz[j][i] == simbolo for j in range(3)):
            return True
    # Verifica diagonais
    if matriz[0][0] == matriz[1][1] == matriz[2][2] == simbolo or matriz[0][2] == matriz[1][1] == matriz[2][0] == simbolo:
        return True
    return False

# Verifica se o tabuleiro está cheio e ninguém venceu (empate)
def verificar_empate(matriz):
    return all(matriz[i][j] != ' ' for i in range(3) for j in range(3))
