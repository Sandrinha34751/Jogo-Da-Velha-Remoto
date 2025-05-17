import socket
import threading
import tkinter as tk
from tkinter import messagebox
from db import iniciar_banco, registrar_jogada, matriz_para_string, string_para_matriz, verificar_vitoria, verificar_empate, verificar_senha

# Configurações do servidor 
HOST = 'localhost'
PORT = 5000

class ServidorGUI:
    def __init__(self, root):
        self.root = root
        self.simbolo = 'X'  # Símbolo do servidor (Jogador 1)
        self.outro_simbolo = 'O'  # Símbolo do cliente (Jogador 2)
        # Matriz do jogo 3x3 inicializada com espaços vazios
        self.matriz = [[' ' for _ in range(3)] for _ in range(3)]
        # Matriz para armazenar os botões da interface gráfica
        self.botoes = [[None for _ in range(3)] for _ in range(3)]
        self.sua_vez = True  # Controla se é o turno do servidor jogar
        self.conn = None  # Conexão socket com o cliente, iniciada após aceitar conexão

        self.criar_interface()  # Cria a interface gráfica do jogo
        # Inicia a thread para aguardar conexão do cliente sem travar a interface
        threading.Thread(target=self.aguardar_conexao, daemon=True).start()

    def criar_interface(self):
        self.root.title("Jogo da Velha - Jogador 1 (Servidor)")
        # Cria botões 3x3 na janela, cada um representando uma célula do tabuleiro
        for i in range(3):
            for j in range(3):
                btn = tk.Button(self.root, text=' ', font=('Arial', 24), width=5, height=2,
                                command=lambda i=i, j=j: self.fazer_jogada(i, j))
                btn.grid(row=i, column=j)
                self.botoes[i][j] = btn

    def aguardar_conexao(self):
        # Configura o socket TCP para aceitar conexões na porta definida
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen()
        print('Aguardando conexão...')
        # Aceita a conexão de um cliente (bloqueante)
        self.conn, _ = server.accept()
        print('Cliente conectado!')
        # Após conectar, inicia thread para receber dados sem travar interface
        threading.Thread(target=self.receber_dados, daemon=True).start()

    def fazer_jogada(self, i, j):
        # Ignora clique se não for a vez do jogador ou se a célula já estiver ocupada
        if not self.sua_vez or self.matriz[i][j] != ' ':
            return

        # Atualiza matriz com o símbolo do servidor (X)
        self.matriz[i][j] = self.simbolo
        # Atualiza botão para mostrar símbolo e desabilita para não ser clicado de novo
        self.botoes[i][j].config(text=self.simbolo, state='disabled')
        # Converte matriz para string para envio e registro
        estado = matriz_para_string(self.matriz)
        registrar_jogada('Jogador 1', estado)  # Salva jogada no banco
        self.conn.sendall(estado.encode())  # Envia novo estado para o cliente

        # Verifica se o servidor venceu após a jogada
        if verificar_vitoria(self.matriz, self.simbolo):
            messagebox.showinfo("Fim de jogo", "Jogador 1 venceu!")
            self.root.quit()  # Fecha a aplicação
        # Verifica se houve empate
        elif verificar_empate(self.matriz):
            messagebox.showinfo("Fim de jogo", "Empate!")
            self.root.quit()

        # Passa o turno para o cliente
        self.sua_vez = False

    def receber_dados(self):
        # Loop para receber dados enviados pelo cliente via socket
        while True:
            data = self.conn.recv(1024)  # Recebe até 1024 bytes
            if not data:  # Se conexão fechada, sai do loop
                break
            # Atualiza a matriz e interface com o estado recebido do cliente
            self.atualizar_estado(string_para_matriz(data.decode()))

    def atualizar_estado(self, nova_matriz):
        # Atualiza matriz local com a matriz recebida do cliente
        self.matriz = nova_matriz
        # Atualiza visualmente os botões para refletir o estado do tabuleiro
        for i in range(3):
            for j in range(3):
                self.botoes[i][j].config(text=self.matriz[i][j])
                if self.matriz[i][j] != ' ':
                    self.botoes[i][j].config(state='disabled')  # Desabilita células já jogadas
        # Verifica se o cliente venceu após a jogada
        if verificar_vitoria(self.matriz, self.outro_simbolo):
            messagebox.showinfo("Fim de jogo", "Jogador 2 venceu!")
            self.root.quit()
        # Verifica empate
        elif verificar_empate(self.matriz):
            messagebox.showinfo("Fim de jogo", "Empate!")
            self.root.quit()

        # Passa o turno para o servidor
        self.sua_vez = True

if __name__ == '__main__':
    verificar_senha()  # Verifica se o banco/sistema está com senha correta
    iniciar_banco()  # Inicializa banco de dados, criando tabelas se necessário
    root = tk.Tk()  # Cria janela principal do Tkinter
    app = ServidorGUI(root)  # Instancia a classe da interface servidor
    root.mainloop()  # Executa o loop principal do Tkinter (interface gráfica)
