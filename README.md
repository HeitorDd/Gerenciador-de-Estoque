Um microssistema de controle de inventário construído 100% em Python. O projeto demonstra uma arquitetura cliente-servidor, composta por uma API RESTful (Backend) e dois clientes gráficos (Frontend) que se comunicam com ela.
🚀 Funcionalidades
Autenticação de Usuários: Sistema de registro e login para os usuários do aplicativo.
Proteção de Rotas: A API utiliza um sistema de autenticação baseado em Token (Bearer Token) para proteger as rotas de dados.
Cadastro de Produtos: O cliente de cadastro pode alimentar uma lista "mestre" de produtos.
Registro de Inventário: Usuários logados podem registrar entradas de estoque (Produto + Quantidade).
Monitoramento em Tempo Real: Um segundo cliente gráfico exibe um log ao vivo de todas as entradas de inventário registradas no sistema.
🏛️ Arquitetura
O sistema é dividido em três componentes principais que rodam de forma independente e simultânea:
api.py (Backend)
Um servidor Flask que atua como a API RESTful.
Gerencia toda a lógica de negócios e o estado do "banco de dados" (em memória).
Responsável por:
/registrar_usuario_app
/login (gera o token de acesso)
/produtos (GET, POST - protegido por token)
/inventario (GET, POST - protegido por token)
cadastro.py (Cliente Principal)
Uma interface gráfica (GUI) em Tkinter.
Permite ao usuário se registrar e logar no sistema.
Após o login, busca a lista de produtos na API para popular um dropdown.
Permite ao usuário cadastrar novos produtos na lista mestre e registrar novas entradas de inventário.
monitor_ui.py (Cliente de Monitoramento)
Uma segunda interface gráfica (GUI) em Tkinter.
Possui sua própria tela de login para se autenticar na API.
Após o login, entra em um loop (usando after()) que consulta a rota /inventario a cada 5 segundos.
Exibe em uma caixa de log qualquer novo registro de entrada detectado, mostrando quem registrou, o quê e a quantidade.
🛠️ Tecnologias Utilizadas
Python 3
Flask: Para a criação da API RESTful (Backend).
Tkinter: Para a construção das duas interfaces gráficas de usuário (Frontend).
Requests: Para a comunicação HTTP entre os clientes Tkinter e a API Flask.
🏃 Como Executar
1. Pré-requisitos
Certifique-se de ter o Python 3 instalado. Você precisará instalar as bibliotecas Flask e requests.
pip install Flask requests


2. Executando o Sistema
A forma mais fácil de iniciar todos os componentes é usando o lançador (start_sistema_completo.bat).
No Windows:
Simplesmente dê um clique duplo no arquivo start_sistema_completo.bat.
Isso irá:
Iniciar a API (api.py) em uma janela de terminal.
Iniciar o Monitor (monitor_ui.py) em uma segunda janela.
Iniciar o Cliente de Cadastro (cadastro.py) na janela principal.
Manualmente (em qualquer sistema operacional):
Abra três terminais separados na pasta do projeto e execute:
Terminal 1 (API):
python api.py


Terminal 2 (Monitor):
python monitor_ui.py


Terminal 3 (Cliente de Cadastro):
python cadastro.py


3. Primeiro Uso
Execute o sistema.
Na tela do cadastro.py, escolha "Não" para se registrar (ex: admin / 1234).
Feche e reabra o cadastro.py, agora logando com a conta criada.
Na tela do monitor_ui.py, logue com a mesma conta (ex: admin / 1234).
Use a tela de cadastro para adicionar um "Novo Produto" (ex: "Parafuso 10mm").
Use a tela de cadastro para "Registrar Entrada" (ex: "Parafuso 10mm", Qtd: "50").
Observe a tela do monitor. Ela deverá exibir o novo registro em tempo real.
