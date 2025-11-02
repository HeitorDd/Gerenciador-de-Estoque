import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import requests
import json

API_BASE_URL = "http://127.0.0.1:5000"

APP_TOKEN = None
AUTH_HEADER = {}
LISTA_PRODUTOS_MESTRE = []

def autenticar_usuario():
    global APP_TOKEN, AUTH_HEADER
    
    acao = messagebox.askquestion("Bem-vindo", "Você já tem um usuário para o App?\n\n'Sim' para Logar.\n'Não' para Registrar um novo.", type='yesno')
    
    if acao == 'no':
        username = simpledialog.askstring("Registrar", "Digite um novo NOME DE USUÁRIO:")
        password = simpledialog.askstring("Registrar", "Digite uma nova SENHA:", show='*')
        if not username or not password:
            messagebox.showerror("Erro", "Usuário e Senha são obrigatórios.")
            return False
        
        try:
            r = requests.post(f"{API_BASE_URL}/registrar_usuario_app", json={"username": username, "password": password})
            if r.status_code == 201:
                messagebox.showinfo("Sucesso", "Usuário registrado! Agora faça o login.")
            else:
                msg = r.json().get("mensagem", "Erro desconhecido")
                messagebox.showerror("Erro de Registro", f"{msg} (Status: {r.status_code})")
                return False
        except requests.RequestException as e:
            messagebox.showerror("Erro de Conexão", f"Não foi possível conectar à API.\n{e}")
            return False

    username = simpledialog.askstring("Login", "Usuário:")
    password = simpledialog.askstring("Login", "Senha:", show='*')
    if not username or not password:
        return False
        
    try:
        r = requests.post(f"{API_BASE_URL}/login", json={"username": username, "password": password})
        
        if r.status_code == 200:
            APP_TOKEN = r.json().get("token")
            AUTH_HEADER = {'Authorization': f'Bearer {APP_TOKEN}'}
            messagebox.showinfo("Sucesso", "Login realizado!")
            return True
        else:
            msg = r.json().get("mensagem", "Erro desconhecido")
            messagebox.showerror("Erro de Login", f"{msg} (Status: {r.status_code})")
            return False
            
    except requests.RequestException as e:
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar à API.\n{e}")
        return False

def atualizar_lista_produtos():
    global LISTA_PRODUTOS_MESTRE
    
    try:
        r = requests.get(f"{API_BASE_URL}/produtos", headers=AUTH_HEADER)
        if r.status_code != 200:
            messagebox.showerror("Erro", "Não foi possível carregar a lista de produtos.")
            return

        LISTA_PRODUTOS_MESTRE = r.json()
        
        nomes_produtos = [produto['nome'] for produto in LISTA_PRODUTOS_MESTRE]
        
        combobox_produto['values'] = nomes_produtos
        if nomes_produtos:
            combobox_produto.current(0)
        
        print("Lista de produtos atualizada.")

    except requests.RequestException as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao buscar produtos:\n{e}")

def cadastrar_novo_produto_master():
    nome_novo_produto = entry_novo_produto.get()
    if not nome_novo_produto:
        messagebox.showwarning("Erro", "Digite o nome do novo produto.")
        return

    try:
        r = requests.post(f"{API_BASE_URL}/produtos", 
                          json={"nome": nome_novo_produto}, 
                          headers=AUTH_HEADER)
        
        if r.status_code == 201:
            messagebox.showinfo("Sucesso", f"Produto '{nome_novo_produto}' cadastrado na lista mestre!")
            entry_novo_produto.delete(0, tk.END)
            atualizar_lista_produtos()
        else:
            msg = r.json().get("mensagem", "Erro desconhecido")
            messagebox.showerror("Erro", f"{msg} (Status: {r.status_code})")
            
    except requests.RequestException as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao cadastrar produto:\n{e}")

def registrar_entrada_inventario():
    try:
        quantidade = int(entry_quantidade.get())
        if quantidade <= 0:
            raise ValueError
    except ValueError:
        messagebox.showwarning("Erro", "Quantidade deve ser um número inteiro positivo.")
        return

    nome_produto_selecionado = combobox_produto.get()
    if not nome_produto_selecionado:
        messagebox.showwarning("Erro", "Selecione um produto.")
        return

    produto_id = None
    for produto in LISTA_PRODUTOS_MESTRE:
        if produto['nome'] == nome_produto_selecionado:
            produto_id = produto['id']
            break
    
    if produto_id is None:
        messagebox.showerror("Erro Grave", "Produto selecionado não encontrado na lista mestre.")
        return
        
    dados_inventario = {
        "produto_id": produto_id,
        "quantidade": quantidade
    }
    
    try:
        r = requests.post(f"{API_BASE_URL}/inventario", json=dados_inventario, headers=AUTH_HEADER)
        
        if r.status_code == 201:
            messagebox.showinfo("Sucesso", f"Registrada entrada de {quantidade}x {nome_produto_selecionado}.")
            entry_quantidade.delete(0, tk.END)
        else:
            msg = r.json().get("mensagem", "Erro desconhecido")
            messagebox.showerror("Erro", f"{msg} (Status: {r.status_code})")
            
    except requests.RequestException as e:
        messagebox.showerror("Erro de Conexão", f"Erro ao registrar entrada:\n{e}")

if __name__ == "__main__":
    
    if not autenticar_usuario():
        print("Login falhou. Encerrando.")
    else:
        janela = tk.Tk()
        janela.title(f"Controle de Inventário (Logado com Token: ...{APP_TOKEN[-6:]})")
        janela.geometry("500x300")

        frame_entrada = tk.LabelFrame(janela, text="Registrar Entrada no Inventário", padx=10, pady=10)
        frame_entrada.pack(fill="x", padx=10, pady=10)

        tk.Label(frame_entrada, text="Produto:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        combobox_produto = ttk.Combobox(frame_entrada, width=40, state="readonly")
        combobox_produto.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(frame_entrada, text="Quantidade:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        entry_quantidade = tk.Entry(frame_entrada, width=10)
        entry_quantidade.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        
        btn_registrar_entrada = tk.Button(frame_entrada, text="Registrar Entrada", command=registrar_entrada_inventario)
        btn_registrar_entrada.grid(row=2, column=1, padx=5, pady=10, sticky="w")
        
        frame_novo_produto = tk.LabelFrame(janela, text="Novo Produto cadastrado na Lista", padx=10, pady=10)
        frame_novo_produto.pack(fill="x", padx=10, pady=5)
        
        tk.Label(frame_novo_produto, text="Novo Produto:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        entry_novo_produto = tk.Entry(frame_novo_produto, width=42)
        entry_novo_produto.grid(row=0, column=1, padx=5, pady=5)
        
        btn_novo_produto = tk.Button(frame_novo_produto, text="Cadastrar Produto", command=cadastrar_novo_produto_master)
        btn_novo_produto.grid(row=1, column=1, padx=5, pady=10, sticky="w")

        atualizar_lista_produtos()

        janela.mainloop()