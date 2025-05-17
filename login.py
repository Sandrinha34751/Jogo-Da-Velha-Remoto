import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import subprocess
import os

# Caminho do banco de dados e senha (usados como variáveis globais)
DB_PATH = "jogo_da_velha.db"
DB_SENHA = "senha123"

# Cria a tabela 'usuarios' se ela não existir e insere um usuário admin padrão
def inicializar_banco():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE NOT NULL,
            senha TEXT NOT NULL
        )
    """)
    # Verifica se o usuário 'admin' já existe
    cursor.execute("SELECT * FROM usuarios WHERE usuario = 'admin'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO usuarios (usuario, senha) VALUES (?, ?)", ('admin', '1234'))
    conn.commit()
    conn.close()

# Verifica se usuário e senha existem no banco
def verificar_login(usuario, senha):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM usuarios WHERE usuario = ? AND senha = ?", (usuario, senha))
    resultado = cursor.fetchone()
    conn.close()
    return resultado is not None

# Exibe a janela de login com interface gráfica
def mostrar_login():
    def tentar_login():
        user = entrada_usuario.get()
        pwd = entrada_senha.get()
        if verificar_login(user, pwd):
            messagebox.showinfo("Login", f"🌱 Bem-vindo, {user}!")
            janela.destroy()

            # Passa variáveis de ambiente para o script cliente_gui.py
            os.environ["DB_PATH"] = DB_PATH
            os.environ["DB_SENHA"] = DB_SENHA

            # Inicia o cliente do jogo em uma nova janela/processo
            subprocess.Popen(["python", "cliente_gui.py"])
        else:
            messagebox.showerror("Erro", "Usuário ou senha inválidos.")

    # Criação da janela principal de login
    janela = tk.Tk()
    janela.title("Login Sustentável")
    janela.geometry("380x330")
    janela.configure(bg="#e6ffe6")  # Cor de fundo verde claro

    titulo = tk.Label(janela, text="🌍 Ecovelha: Natureza em Jogo 🌲🔥", font=("Arial", 14, "bold"), bg="#e6ffe6", fg="#2e8b57")
    titulo.pack(pady=20)

    # Frame central que contém os campos de entrada
    frame = ttk.Frame(janela, padding=20)
    frame.pack()

    # Estilo para os botões do ttk
    estilo = ttk.Style()
    estilo.theme_use('clam')  # Tema alternativo
    estilo.configure("TButton", background="#2e8b57", foreground="white", font=('Arial', 10, 'bold'))
    estilo.map("TButton", background=[("active", "#3cb371")])  # Efeito hover

    # Campo de entrada do usuário
    ttk.Label(frame, text="Usuário:").grid(row=0, column=0, sticky="w", pady=5)
    entrada_usuario = ttk.Entry(frame, width=30)
    entrada_usuario.grid(row=0, column=1, pady=5)

    # Campo de entrada da senha
    ttk.Label(frame, text="Senha:").grid(row=1, column=0, sticky="w", pady=5)
    entrada_senha = ttk.Entry(frame, show="*", width=30)
    entrada_senha.grid(row=1, column=1, pady=5)

    # Botão de login
    ttk.Button(frame, text="🌎 Entrar", command=tentar_login).grid(row=2, column=0, columnspan=2, pady=20)

    # Rodapé 
    rodape = tk.Label(janela, text="Transforme estratégia em ação ambiental 🌱", bg="#e6ffe6", fg="#2e8b57", font=("Arial", 10))
    rodape.pack(side="bottom", pady=10)

    # Inicia o loop da interface gráfica
    janela.mainloop()

# Execução principal: inicializa banco e exibe login
if __name__ == "__main__":
    inicializar_banco()
    mostrar_login()
