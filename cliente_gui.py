import socket
import threading
import tkinter as tk
import time
import random
from tkinter import messagebox
from db import iniciar_banco, registrar_jogada, matriz_para_string, string_para_matriz, verificar_vitoria, verificar_empate, verificar_senha

HOST = 'localhost'
PORT = 5000
# Socket global que pode ser fechado quando necessário
servidor_socket = None

SIMBOLO_ARVORE = "🌲"
SIMBOLO_FOGO = "🔥"

# Cores para o tema ambiental
COR_FUNDO = "#EFFAD3"  # Verde claro para fundo
COR_BOTAO = "#8BC34A"  # Verde para botões
COR_TEXTO = "#1B5E20"  # Verde escuro para texto
COR_CHAT = "#E8F5E9"   # Verde muito claro para o chat
COR_AVISO = "#BF360C"  # Laranja avermelhado para avisos (fogo)

class JogoDaVelhaGUI:
    def __init__(self, root, simbolo, outro_simbolo, conexao, jogador):
        self.root = root
        self.simbolo = simbolo  # 'X' (árvore) ou 'O' (fogo)
        self.outro_simbolo = outro_simbolo
        self.matriz = [[' ' for _ in range(3)] for _ in range(3)]
        self.botoes = [[None for _ in range(3)] for _ in range(3)]
        self.sua_vez = jogador == 'Servidor'
        self.conexao = conexao
        self.jogador = jogador
        
        # Configurar a janela
        self.root.title(f"Jogo da Velha Ambiental - {self.jogador}")
        self.root.configure(bg=COR_FUNDO)
        self.root.resizable(False, False)
        
        # Criar ícones para árvore e fogo
        self.icone_arvore = self.criar_emoji_imagem(SIMBOLO_ARVORE, 36)
        self.icone_fogo = self.criar_emoji_imagem(SIMBOLO_FOGO, 36)
        
        threading.Thread(target=self.receber_dados, daemon=True).start()
        self.criar_interface()

    def criar_emoji_imagem(self, emoji, tamanho):
        """Cria uma imagem a partir de um emoji para usar como ícone"""
        fonte = ('Arial', tamanho)
        label = tk.Label(text=emoji, font=fonte, bg=COR_FUNDO)
        label.update()
        
        # Captura o rótulo como imagem
        x = label.winfo_width()
        y = label.winfo_height()
        
        # Retorna o próprio emoji como string (será usado diretamente)
        return emoji

    def criar_interface(self):
        # Frame principal com fundo personalizado
        frame_principal = tk.Frame(self.root, bg=COR_FUNDO, padx=20, pady=20)
        frame_principal.pack(padx=20, pady=20)
        
        # Título
        titulo_text = "Preservação Ambiental: Árvores 🌲 vs Fogo 🔥"
        titulo = tk.Label(frame_principal, text=titulo_text, font=('Arial', 16, 'bold'), 
                          bg=COR_FUNDO, fg=COR_TEXTO)
        titulo.pack(pady=(0, 15))
        
        # Subtítulo com instrução
        subtitulo = "Plante árvores para vencer o fogo!"
        instrucao = tk.Label(frame_principal, text=subtitulo, font=('Arial', 12), 
                           bg=COR_FUNDO, fg=COR_TEXTO)
        instrucao.pack(pady=(0, 15))

        # Frame para o tabuleiro
        frame_jogo = tk.Frame(frame_principal, bg="#A5D6A7", bd=3, relief=tk.RIDGE)
        frame_jogo.pack(pady=10)

        # Criar o tabuleiro 
        for i in range(3):
            for j in range(3):
                btn = tk.Button(frame_jogo, text=' ', font=('Arial', 24), width=3, height=1,
                                bg="#A5D6A7", activebackground="#81C784", 
                                command=lambda i=i, j=j: self.fazer_jogada(i, j))
                btn.grid(row=i, column=j, padx=5, pady=5, sticky="nsew")
                self.botoes[i][j] = btn

        # Indicador de vez com ícones
        frame_vez = tk.Frame(frame_principal, bg=COR_FUNDO)
        frame_vez.pack(pady=10)
        
        self.label_vez_texto = tk.Label(frame_vez, text="Vez de: ", 
                                       font=('Arial', 12, 'bold'), 
                                       bg=COR_FUNDO, fg=COR_TEXTO)
        self.label_vez_texto.pack(side=tk.LEFT)
        
        self.label_vez_jogador = tk.Label(frame_vez, 
                                         text="Você" if self.sua_vez else "Oponente",
                                         font=('Arial', 12, 'bold'), 
                                         bg=COR_FUNDO, 
                                         fg="#1B5E20" if self.sua_vez else "#BF360C")
        self.label_vez_jogador.pack(side=tk.LEFT)

        frame_info = tk.Frame(frame_principal, bg=COR_FUNDO)
        frame_info.pack(pady=5)
        
        tk.Label(frame_info, text="Você é: ", font=('Arial', 11), 
                bg=COR_FUNDO, fg=COR_TEXTO).pack(side=tk.LEFT)
        
        simbolo_display = SIMBOLO_ARVORE if self.simbolo == 'X' else SIMBOLO_FOGO
        tk.Label(frame_info, text=simbolo_display, font=('Arial', 16), 
                bg=COR_FUNDO).pack(side=tk.LEFT)

        # Chat 
        frame_chat = tk.LabelFrame(frame_principal, text="Chat da Floresta", 
                                  font=('Arial', 11, 'bold'),
                                  bg=COR_FUNDO, fg=COR_TEXTO)
        frame_chat.pack(pady=10, fill=tk.BOTH, expand=True)
        
        self.chat_box = tk.Text(frame_chat, height=6, width=30, 
                               bg=COR_CHAT, fg=COR_TEXTO,
                               font=('Arial', 10), relief=tk.SUNKEN,
                               wrap=tk.WORD, state='disabled')
        self.chat_box.pack(pady=5, padx=5, fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(self.chat_box)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.chat_box.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.chat_box.yview)
        
        frame_msg = tk.Frame(frame_chat, bg=COR_FUNDO)
        frame_msg.pack(fill=tk.X, padx=5, pady=5)
        
        self.msg_entry = tk.Entry(frame_msg, bg="white", fg=COR_TEXTO, 
                                 font=('Arial', 10))
        self.msg_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.msg_entry.bind("<Return>", self.enviar_mensagem)
        
        btn_enviar = tk.Button(frame_msg, text="Enviar", bg=COR_BOTAO, fg="white",
                              command=self.enviar_mensagem)
        btn_enviar.pack(side=tk.RIGHT, padx=5)
        
        # Status do jogo
        self.status_label = tk.Label(frame_principal, text="Jogo em andamento...", 
                                    font=('Arial', 10), bg=COR_FUNDO, fg=COR_TEXTO)
        self.status_label.pack(pady=5)

    def fazer_jogada(self, i, j):
        if not self.sua_vez or self.matriz[i][j] != ' ':
            return

        # Atualizar matriz interna
        self.matriz[i][j] = self.simbolo
        
        # Atualizar botão com símbolo apropriado (árvore ou fogo)
        simbolo_visual = self.icone_arvore if self.simbolo == 'X' else self.icone_fogo
        self.botoes[i][j].config(text=simbolo_visual, fg="green" if self.simbolo == 'X' else "#BF360C")
        self.botoes[i][j].config(state='disabled')
        
        estado = matriz_para_string(self.matriz)
        registrar_jogada(self.jogador, estado)
        self.conexao.sendall(f"JOGADA:{estado}".encode())

        if verificar_vitoria(self.matriz, self.simbolo):
            mensagem = "As árvores venceram! A floresta foi salva! 🌿" if self.simbolo == 'X' else "O fogo se espalhou! A floresta foi consumida! 🔥"
            self.status_label.config(text=mensagem, fg="green" if self.simbolo == 'X' else "#BF360C", font=('Arial', 10, 'bold'))
            self.mostrar_tela_finalizacao(mensagem, True)
        elif verificar_empate(self.matriz):
            mensagem = "Empate! A natureza está em equilíbrio! 🌍"
            self.status_label.config(text=mensagem, fg=COR_TEXTO, font=('Arial', 10, 'bold'))
            self.mostrar_tela_finalizacao(mensagem, False)

        self.sua_vez = False
        self.label_vez_jogador.config(text="Oponente", fg="#BF360C")

    def enviar_mensagem(self, event=None):
        msg = self.msg_entry.get()
        if msg:
            prefixo = "🌲: " if self.simbolo == 'X' else "🔥: "
            self.adicionar_chat(f"{prefixo}{msg}")
            self.conexao.sendall(f"MSG:{msg}".encode())
            self.msg_entry.delete(0, tk.END)

    def adicionar_chat(self, mensagem):
        self.chat_box.config(state='normal')
        self.chat_box.insert(tk.END, mensagem + '\n')
        self.chat_box.config(state='disabled')
        self.chat_box.see(tk.END)

    def receber_dados(self):
        while True:
            try:
                data = self.conexao.recv(1024)
                if not data:
                    break
                msg = data.decode()
                if msg.startswith("JOGADA:"):
                    nova_matriz = string_para_matriz(msg[7:])
                    self.atualizar_estado(nova_matriz)
                elif msg.startswith("MSG:"):
                    prefixo = "🔥: " if self.simbolo == 'X' else "🌲: "  # Invertido em relação ao local
                    self.adicionar_chat(f"{prefixo}{msg[4:]}")
            except:
                break

    def atualizar_estado(self, nova_matriz):
        self.matriz = nova_matriz
        for i in range(3):
            for j in range(3):
                if self.matriz[i][j] != ' ' and self.botoes[i][j]['text'] == ' ':
                    # Atualizar com árvore ou fogo
                    if self.matriz[i][j] == 'X':
                        self.botoes[i][j].config(text=SIMBOLO_ARVORE, fg="green")
                    else:
                        self.botoes[i][j].config(text=SIMBOLO_FOGO, fg="#BF360C")
                    self.botoes[i][j].config(state='disabled')
                    
        if verificar_vitoria(self.matriz, self.outro_simbolo):
            mensagem = "As árvores venceram! A floresta foi salva! 🌿" if self.outro_simbolo == 'X' else "O fogo se espalhou! A floresta foi consumida! 🔥"
            self.status_label.config(text=mensagem, fg="green" if self.outro_simbolo == 'X' else "#BF360C", font=('Arial', 10, 'bold'))
            self.mostrar_tela_finalizacao(mensagem, True)
        elif verificar_empate(self.matriz):
            mensagem = "Empate! A natureza está em equilíbrio! 🌍"
            self.status_label.config(text=mensagem, fg=COR_TEXTO, font=('Arial', 10, 'bold'))
            self.mostrar_tela_finalizacao(mensagem, False)

        self.sua_vez = True
        self.label_vez_jogador.config(text="Você", fg="#1B5E20")

    def mostrar_tela_finalizacao(self, mensagem, vitoria):
        """Mostra uma tela de finalização para o jogo"""
        # Criar uma nova janela para a tela de finalização
        janela_fim = tk.Toplevel(self.root)
        janela_fim.title("Fim de Jogo")
        janela_fim.configure(bg=COR_FUNDO)
        janela_fim.geometry("400x450")
        janela_fim.resizable(False, False)
        
        # Garante que a janela de finalização fique em foco
        janela_fim.transient(self.root)
        janela_fim.grab_set()
        
        # Título
        titulo_fim = tk.Label(janela_fim, text="Fim de Jogo", font=('Arial', 22, 'bold'), 
                             bg=COR_FUNDO, fg=COR_TEXTO)
        titulo_fim.pack(pady=(30, 20))
        
        # Resultadoadicional
        cor_resultado = "green" if "árvores venceram" in mensagem else "#BF360C" if "fogo" in mensagem else COR_TEXTO
        resultado = tk.Label(janela_fim, text=mensagem, font=('Arial', 14), 
                            bg=COR_FUNDO, fg=cor_resultado)
        resultado.pack(pady=(10, 30))
        
        # Adicionar um ícone baseado no resultado
        if vitoria:
            if "árvores venceram" in mensagem:
                emoji = "🌲🌳🌲\n🌿🍃🌿"
            else:
                emoji = "🔥🔥🔥\n🔥🔥🔥"
        else:
            emoji = "🌲🔥🌲\n🔥🌲🔥"
            
        icone_label = tk.Label(janela_fim, text=emoji, font=('Arial', 40), 
                              bg=COR_FUNDO)
        icone_label.pack(pady=20)
        
        # Mensagem 
        if "árvores venceram" in mensagem:
            msg_adicional = "Parabéns por proteger a floresta!"
        elif "fogo" in mensagem:
            msg_adicional = "A natureza precisará de tempo para se recuperar."
        else:
            msg_adicional = "O equilíbrio da natureza é delicado."
            
        adicional_label = tk.Label(janela_fim, text=msg_adicional, font=('Arial', 12, 'italic'), 
                                  bg=COR_FUNDO, fg=COR_TEXTO)
        adicional_label.pack(pady=10)
        
        # Botões para nova partida ou sair
        frame_botoes = tk.Frame(janela_fim, bg=COR_FUNDO)
        frame_botoes.pack(pady=30)
        
        btn_nova_partida = tk.Button(frame_botoes, text="Nova Partida", 
                                   font=('Arial', 12), 
                                   width=15, height=1,
                                   bg=COR_BOTAO, fg="white",
                                   command=lambda: self.reiniciar_jogo(janela_fim))
        btn_nova_partida.pack(side=tk.LEFT, padx=10)
        
        btn_sair = tk.Button(frame_botoes, text="Sair", 
                           font=('Arial', 12), 
                           width=15, height=1,
                           bg="#F44336", fg="white",
                           command=lambda: self.sair_jogo(janela_fim))
        btn_sair.pack(side=tk.LEFT, padx=10)
        
        # Impedir que a janela principal seja fechada diretamente
        self.root.protocol("WM_DELETE_WINDOW", lambda: self.sair_jogo(janela_fim))

    def reiniciar_jogo(self, janela_fim):
        """Reiniciar o jogo para uma nova partida"""
        # Fechar a janela de finalização
        janela_fim.destroy()
        
        # Notificar o outro jogador sobre a reinicialização
        try:
            self.conexao.sendall("MSG:Solicitou uma nova partida!".encode())
        except:
            pass
        
        # Fechar a conexão atual
        try:
            self.conexao.close()
        except:
            pass
            
        # Fechar a janela atual
        self.root.destroy()
        
        # Delay para garantir que os sockets sejam liberados
        time.sleep(1)
        
        # Iniciar nova interface
        iniciar_interface()

    def sair_jogo(self, janela_fim=None):
        """Sair do jogo"""
        if janela_fim:
            janela_fim.destroy()
        
        # Notificar o outro jogador sobre a saída (opcional)
        try:
            self.conexao.sendall("MSG:Saiu do jogo.".encode())
            self.conexao.close()
        except:
            pass
            
        # Fechar a janela e encerrar o programa
        self.root.destroy()
        exit()

def iniciar_interface():
    def encontrar_porta_disponivel():
        """Encontra uma porta disponível para usar"""
        global PORT
        # Tenta usar a porta padrão primeiro
        porta_teste = PORT
        for _ in range(10):  # Tenta até 10 portas diferentes
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.bind((HOST, porta_teste))
                sock.close()
                # Se conseguir fazer bind, a porta está disponível
                PORT = porta_teste
                return porta_teste
            except OSError:
                # Porta em uso, tenta a próxima
                porta_teste = random.randint(5001, 5999)
        # Se todas as tentativas falharem, retorna a porta original
        return PORT

    def iniciar_como_servidor():
        janela_inicial.destroy()
        global servidor_socket
        
        try:
            # Encontrar uma porta disponível
            porta = encontrar_porta_disponivel()
            
            # Criar e configurar o socket do servidor
            servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # Configurar o socket para reutilizar o endereço
            servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            servidor_socket.bind((HOST, porta))
            servidor_socket.listen()
            
            # Janela de espera
            janela_espera = tk.Tk()
            janela_espera.title("Aguardando conexão")
            janela_espera.configure(bg=COR_FUNDO)
            info_texto = f"Aguardando o outro jogador conectar...\nUsando porta: {porta}"
            tk.Label(janela_espera, text=info_texto,
                   font=('Arial', 12), bg=COR_FUNDO, fg=COR_TEXTO).pack(padx=30, pady=20)
            janela_espera.update()
            
            # Configurar timeout para não bloquear indefinidamente
            servidor_socket.settimeout(300)  # 5 minutos de timeout
            
            # Aguardar conexão do cliente
            conexao, _ = servidor_socket.accept()
            janela_espera.destroy()
            
            # Iniciar o jogo
            root_jogo = tk.Tk()
            JogoDaVelhaGUI(root_jogo, 'X', 'O', conexao, 'Servidor').root.mainloop()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao iniciar servidor: {e}")
            try:
                if servidor_socket:
                    servidor_socket.close()
            except:
                pass

    def iniciar_como_cliente():
        janela_inicial.destroy()
        
        # Pedir porta de conexão
        porta_dialogo = tk.Toplevel()
        porta_dialogo.title("Conectar ao Servidor")
        porta_dialogo.configure(bg=COR_FUNDO)
        porta_dialogo.geometry("300x150")
        porta_dialogo.resizable(False, False)
        
        tk.Label(porta_dialogo, text="Digite a porta do servidor:", 
               font=('Arial', 12), bg=COR_FUNDO, fg=COR_TEXTO).pack(pady=(15, 5))
        
        entrada_porta = tk.Entry(porta_dialogo, width=10, font=('Arial', 12))
        entrada_porta.insert(0, str(PORT))  # Preenche com a porta padrão
        entrada_porta.pack(pady=5)
        
        def confirmar_porta():
            porta = int(entrada_porta.get())
            porta_dialogo.destroy()
            conectar_ao_servidor(porta)
        
        tk.Button(porta_dialogo, text="Conectar", 
                font=('Arial', 12), bg=COR_BOTAO, fg="white",
                command=confirmar_porta).pack(pady=15)
        
    def conectar_ao_servidor(porta):
        try:
            cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cliente.connect((HOST, porta))
            JogoDaVelhaGUI(tk.Tk(), 'O', 'X', cliente, 'Cliente').root.mainloop()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao servidor: {e}")

    # Janela de escolha de modo
    janela_inicial = tk.Tk()
    janela_inicial.title("Jogo da Velha Ambiental")
    janela_inicial.configure(bg=COR_FUNDO)
    janela_inicial.resizable(False, False)

    # Frame principal
    frame_principal = tk.Frame(janela_inicial, bg=COR_FUNDO, padx=30, pady=30)
    frame_principal.pack()

    tk.Label(frame_principal, 
           text="Jogo da Velha Ambiental", 
           font=('Arial', 18, 'bold'),
           bg=COR_FUNDO, fg=COR_TEXTO).pack(pady=(0, 10))

    # Subtítulo explicando o tema
    tk.Label(frame_principal, 
           text="Árvores 🌲 vs Fogo 🔥", 
           font=('Arial', 14),
           bg=COR_FUNDO, fg=COR_TEXTO).pack(pady=(0, 20))

    # Escolha de modo
    tk.Label(frame_principal, 
           text="Escolha como deseja jogar:", 
           font=('Arial', 12),
           bg=COR_FUNDO, fg=COR_TEXTO).pack(pady=(0, 10))

    # Botão servidor (Árvores)
    btn_servidor = tk.Button(frame_principal, 
                           text="Servidor (Árvores 🌲)", 
                           font=('Arial', 12),
                           width=25, height=2,
                           bg="#4CAF50", fg="white",
                           command=iniciar_como_servidor)
    btn_servidor.pack(pady=5)

    # Botão cliente (Fogo)
    btn_cliente = tk.Button(frame_principal, 
                          text="Cliente (Fogo 🔥)", 
                          font=('Arial', 12),
                          width=25, height=2,
                          bg="#FF5722", fg="white",
                          command=iniciar_como_cliente)
    btn_cliente.pack(pady=5)

    # Mensagem ambiental na parte inferior
    mensagem = "Proteja a floresta, cada árvore importa!"
    tk.Label(frame_principal, text=mensagem, 
           font=('Arial', 10, 'italic'),
           bg=COR_FUNDO, fg=COR_TEXTO).pack(pady=(20, 0))

    janela_inicial.mainloop()

if __name__ == '__main__':
    verificar_senha()
    iniciar_banco()
    
    # Tenta liberar a porta ao iniciar
    try:
        temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        temp_socket.bind((HOST, PORT))
        temp_socket.close()
    except:

        pass
        
    iniciar_interface()