from flask import Flask, request, jsonify, g
import os
import uuid
from functools import wraps

app = Flask(__name__)

usuarios_app_db = []
produtos_master_db = []
inventario_db = []
tokens_ativos = {}

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"mensagem": "Formato de token inválido. Use 'Bearer <token>'"}), 401

        if not token:
            return jsonify({"mensagem": "Token de autorização não encontrado"}), 401

        if token not in tokens_ativos:
            return jsonify({"mensagem": "Token inválido ou expirado"}), 401
        
        g.current_user = tokens_ativos[token]
        
        return f(*args, **kwargs)
    return decorated

@app.route('/registrar_usuario_app', methods=['POST'])
def registrar_usuario_app():
    dados = request.get_json()
    try:
        username = dados['username']
        password = dados['password']
    except KeyError:
        return jsonify({"mensagem": "Campos 'username' e 'password' são obrigatórios"}), 400

    for user in usuarios_app_db:
        if user['username'] == username:
            return jsonify({"mensagem": "Este nome de usuário já existe"}), 409

    novo_usuario = {"id": str(uuid.uuid4()), "username": username, "password": password}
    usuarios_app_db.append(novo_usuario)
    print(f"Novo usuário do app registrado: {username}")
    
    return jsonify({"mensagem": f"Usuário {username} registrado com sucesso"}), 201

@app.route('/login', methods=['POST'])
def login():
    dados = request.get_json()
    try:
        username = dados['username']
        password = dados['password']
    except KeyError:
        return jsonify({"mensagem": "Campos 'username' e 'password' são obrigatórios"}), 400

    for user in usuarios_app_db:
        if user['username'] == username and user['password'] == password:
            token = str(uuid.uuid4())
            tokens_ativos[token] = user['username']
            print(f"Usuário {username} logado com token: {token}")
            
            return jsonify({"mensagem": "Login bem-sucedido", "token": token}), 200
            
    return jsonify({"mensagem": "Usuário ou senha incorretos"}), 401

@app.route('/produtos', methods=['POST'])
@token_required
def adicionar_produto_master():
    print(f"Usuário '{g.current_user}' está adicionando um produto.")
    
    dados = request.get_json()
    if 'nome' not in dados:
        return jsonify({"mensagem": "Campo 'nome' do produto é obrigatório"}), 400
    
    nome_produto = dados['nome']

    for prod in produtos_master_db:
        if prod['nome'].lower() == nome_produto.lower():
            return jsonify({"mensagem": f"Produto '{nome_produto}' já existe na lista"}), 409

    novo_produto = {
        "id": f"p{len(produtos_master_db) + 1}",
        "nome": nome_produto
    }
    produtos_master_db.append(novo_produto)
    
    return jsonify(novo_produto), 201

@app.route('/produtos', methods=['GET'])
@token_required
def get_produtos_master():
    return jsonify(produtos_master_db), 200

@app.route('/inventario', methods=['POST'])
@token_required
def registrar_inventario():
    dados = request.get_json()
    try:
        produto_id = dados['produto_id']
        quantidade = int(dados['quantidade'])
    except (KeyError, ValueError):
        return jsonify({"mensagem": "Campos 'produto_id' (string) e 'quantidade' (int) são obrigatórios"}), 400
    
    produto_valido = False
    for prod in produtos_master_db:
        if prod['id'] == produto_id:
            produto_valido = True
            break
            
    if not produto_valido:
        return jsonify({"mensagem": f"Erro: produto_id '{produto_id}' não encontrado na lista mestre."}), 404

    novo_registro = {
        "id": str(uuid.uuid4()),
        "produto_id": produto_id,
        "quantidade": quantidade,
        "registrado_por": g.current_user,
        "timestamp": str(os.times())
    }
    inventario_db.append(novo_registro)
    
    return jsonify(novo_registro), 201

@app.route('/inventario', methods=['GET'])
@token_required
def get_inventario():
    inventario_completo = []
    for item in inventario_db:
        nome_prod = "Produto Desconhecido"
        for prod in produtos_master_db:
            if prod['id'] == item['produto_id']:
                nome_prod = prod['nome']
                break
        
        item_com_nome = item.copy()
        item_com_nome['nome_produto'] = nome_prod
        inventario_completo.append(item_com_nome)
        
    return jsonify(inventario_completo), 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)