import socket
from db import iniciar_banco, registrar_jogada, matriz_para_string, string_para_matriz, verificar_vitoria, verificar_empate

# Definição do endereço e porta para o servidor TCP
HOST = 'localhost'
PORT = 5000

# Inicializa o banco de dados 
iniciar_banco()

# Cria o socket do servidor usando IPv4 e TCP
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))  # Liga o socket ao endereço e porta especificados
server.listen()  # Começa a escutar conexões

print('Aguardando conexão...')
conn, addr = server.accept()  # Aceita uma conexão de cliente (bloqueante)
print(f'Conectado por {addr}')  # Exibe endereço do cliente conectado

# Inicializa a matriz do jogo (tabuleiro 3x3 vazio)
matriz = [[' ']*3 for _ in range(3)]

while True:
    # Turno do servidor (Jogador 1) para fazer a jogada
    print("Sua vez (jogador 1 - X)")
    while True:
        # Solicita que o usuário informe linha e coluna para a jogada
        linha = int(input("Linha (0-2): "))
        coluna = int(input("Coluna (0-2): "))
        # Verifica se a posição está vazia para jogar
        if matriz[linha][coluna] == ' ':
            break
        print("Posição ocupada. Escolha outra.")  # Se ocupada, pede outra posição

    matriz[linha][coluna] = 'X'  # Marca o tabuleiro com o símbolo 'X'

    # Converte a matriz para string para registro e envio via rede
    estado = matriz_para_string(matriz)
    registrar_jogada('Jogador 1', estado)  # Registra a jogada no banco de dados
    conn.sendall(estado.encode())  # Envia o estado atualizado para o cliente

    # Verifica se o jogador 1 venceu após a jogada
    if verificar_vitoria(matriz, 'X'):
        print("Jogador 1 venceu!")
        break
    # Verifica se houve empate
    if verificar_empate(matriz):
        print("Empate!")
        break

    # Agora aguarda a jogada do jogador 2 (cliente)
    print("Esperando jogada do jogador 2...")
    data = conn.recv(1024)  # Recebe dados do cliente
    matriz = string_para_matriz(data.decode())  # Converte string recebida para matriz

    # Exibe estado atual do jogo no console
    print("Estado atual do jogo:")
    for linha in matriz:
        print(linha)

    # Verifica se jogador 2 venceu após sua jogada
    if verificar_vitoria(matriz, 'O'):
        print("Jogador 2 venceu!")
        break
    # Verifica empate
    if verificar_empate(matriz):
        print("Empate!")
        break
