import socket
from db import iniciar_banco, registrar_jogada, matriz_para_string, string_para_matriz, verificar_vitoria, verificar_empate

# Define o endereço e a porta do servidor
HOST = 'localhost'
PORT = 5000

# Inicializa o banco de dados
iniciar_banco()

# Cria o socket do cliente e conecta ao servidor
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

while True:
    print("Esperando jogada do jogador 1...")
    
    # Recebe o estado do jogo enviado pelo servidor (jogador 1)
    data = client.recv(1024)
    matriz = string_para_matriz(data.decode())
    
    # Exibe o estado atual do tabuleiro
    print("Estado atual:")
    for linha in matriz:
        print(linha)

    # Verifica se o jogador 1 venceu
    if verificar_vitoria(matriz, 'X'):
        print("Jogador 1 venceu!")
        break

    # Verifica se houve empate
    if verificar_empate(matriz):
        print("Empate!")
        break

    # Jogador 2 faz sua jogada
    print("Sua vez (jogador 2 - O)")
    while True:
        linha = int(input("Linha (0-2): "))
        coluna = int(input("Coluna (0-2): "))
        if matriz[linha][coluna] == ' ':
            break
        print("Posição ocupada. Escolha outra.")

    # Atualiza a matriz com a jogada do jogador 2
    matriz[linha][coluna] = 'O'

    # Converte a matriz para string e registra a jogada no banco de dados
    estado = matriz_para_string(matriz)
    registrar_jogada('Jogador 2', estado)

    # Envia o estado atualizado do jogo para o servidor
    client.sendall(estado.encode())

    # Verifica se o jogador 2 venceu
    if verificar_vitoria(matriz, 'O'):
        print("Jogador 2 venceu!")
        break

    # Verifica se houve empate
    if verificar_empate(matriz):
        print("Empate!")
        break
