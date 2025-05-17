 Jogo da Velha Remoto

Este projeto implementa um jogo da velha multiplayer com comunicação em rede via sockets TCP/IP, utilizando a linguagem Python e a biblioteca Pygame para a interface gráfica. O jogo também se conecta a um banco de dados SQLite, onde são registradas as informações de login e as jogadas de cada partida.

O sistema permite que dois jogadores se conectem de forma remota, trocando mensagens via chat integrado e disputando partidas consecutivas. A cada nova partida, o servidor pode ser iniciado com uma porta diferente, garantindo a criação de sessões independentes.

---

 Funcionalidades

- Interface gráfica interativa com Pygame  
- Conexão cliente-servidor usando sockets TCP/IP  
- Cadastro e login de usuários  
- Registro de jogadas no banco de dados  
- Chat entre os jogadores durante a partida  
- Opção de "Nova Partida" ou "Sair" ao final do jogo  

---

Como Executar o Projeto

Pré-requisitos

- Python 3 instalado (recomendado: versão 3.10 ou superior)  
- Sistema operacional: Windows  
- Instalar a biblioteca `pygame`:

```bash
pip install pygame

▶️ Executando o Servidor
Abra o terminal (cmd, PowerShell ou Git Bash)

Navegue até a pasta onde o projeto está salvo. Por exemplo:

cd "C:\Users\sandr\Documents\Projetos\Projeto_APS_2025\APS\APS"

Primeiro, execute o script de login/cadastro:

python login.py

Em seguida, execute a interface do jogo:

python cliente_gui.py

🔐 Banco de Dados
O sistema utiliza SQLite para gerenciar:

Credenciais de login dos usuários
Histórico das jogadas realizadas em cada partida
As informações são armazenadas localmente no arquivo banco.db.
