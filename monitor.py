import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, scrolledtext
import requests
import json
import time

API_BASE_URL = "http://127.0.0.1:5000"
API_URL_INVENTARIO = f"{API_BASE_URL}/inventario"
API_URL_LOGIN = f"{API_BASE_URL}/login"

AUTH_HEADER = {}
total_registros_conhecidos = 0
janela_monitor = None
txt_log = None
frame_login = None
frame_monitor = None
entry_user = None
entry_pass = None

def log_message(message, tag=None):
    if txt_log:
        txt_log.config(state=tk.NORMAL)
        if tag:
            txt_log.insert(tk.END, f"{message}\n", tag)
        else:
            txt_log.insert(tk.END, f"{message}\n")
        txt_log.config(state=tk.DISABLED)
        txt_log.see(tk.END)

def obter_token_acesso():
    global AUTH_HEADER
    
    username = entry_user.get()
    password = entry_pass.get()
    
    if not username or not password:
        messagebox.showerror("Erro", "Usuário e Senha são obrigatórios.")
        return

    log_message(f"Monitor tentando fazer login como '{username}'...")
    try:
        r = requests.post(API_URL_LOGIN, json={"username": username, "password": password})
        
        if r.status_code == 200:
            token = r.json().get("token")
            AUTH_HEADER = {'Authorization': f'Bearer {token}'}
            log_message("Monitor logado com sucesso!", "sucesso")
            
            frame_login.pack_forget()
            criar_tela_monitor()
            
            janela_monitor.after(1000, check_api)
        else:
            msg = r.json().get("mensagem", "Erro desconhecido")
            log_message(f"Erro de Login: {msg}", "erro")
            messagebox.showerror("Erro de Login", msg)
            
    except requests.RequestException as e:
        log_message(f"Erro de Conexão: {e}", "erro")
        messagebox.showerror("Erro de Conexão", f"Não foi possível conectar à API.\n{e}")

def processar_novo_registro(item):
    global txt_log
    
    nome = item.get('nome_produto', f"ID: {item['produto_id']}")
    qtd = item.get('quantidade', 0)
    user = item.get('registrado_por', 'desconhecido')
    
    log_message(f"  [NOVO] Produto: {nome}", "novo_item")
    log_message(f"         Qtd: {qtd} | Por: {user}", "novo_item")

    try:
        with open("inventario.log", "a", encoding="utf-8") as f:
            f.write(f"Novo registro: {nome}, Qtd: {qtd}, por: {user}\n")
    except Exception as e:
        log_message(f"  -> Erro ao salvar log em arquivo: {e}", "erro")

def check_api():
    global total_registros_conhecidos, AUTH_HEADER, frame_monitor
    
    try:
        response = requests.get(API_URL_INVENTARIO, headers=AUTH_HEADER, timeout=3)
        
        if response.status_code == 200:
            lista_inventario_atual = response.json()
            total_registros_atual = len(lista_inventario_atual)
            
            if total_registros_atual > total_registros_conhecidos:
                num_novos = total_registros_atual - total_registros_conhecidos
                log_message(f"\nDetectado(s) {num_novos} novo(s) registro(s)!", "info")
                
                novos_registros = lista_inventario_atual[-num_novos:]
                for item in novos_registros:
                    processar_novo_registro(item)
                
                total_registros_conhecidos = total_registros_atual
            
        elif response.status_code == 401:
            log_message("Erro 401: Token inválido ou expirado. Faça o login novamente.", "erro")
            AUTH_HEADER = {}
            frame_monitor.pack_forget()
            criar_tela_login()
            return

        else:
            log_message(f"Erro ao acessar API (Status: {response.status_code})", "erro")

    except requests.exceptions.RequestException:
        log_message("Não foi possível conectar à API. (Verificando...)", "erro")
    
    janela_monitor.after(5000, check_api)

def criar_tela_login():
    global frame_login, entry_user, entry_pass
    
    janela_monitor.geometry("400x200")
    frame_login = tk.Frame(janela_monitor, padx=10, pady=10)
    frame_login.pack(expand=True)
    
    tk.Label(frame_login, text="Login do Monitor", font=("Segoe UI", 14, "bold")).pack(pady=5)
    
    tk.Label(frame_login, text="Usuário:").pack(pady=(5,0))
    entry_user = tk.Entry(frame_login, width=30)
    entry_user.pack()
    
    tk.Label(frame_login, text="Senha:").pack(pady=(5,0))
    entry_pass = tk.Entry(frame_login, width=30, show="*")
    entry_pass.pack()
    
    btn_login = tk.Button(frame_login, text="Logar e Iniciar Monitor", command=obter_token_acesso)
    btn_login.pack(pady=15)
    
def criar_tela_monitor():
    global frame_monitor, txt_log, total_registros_conhecidos
    
    janela_monitor.geometry("600x400")
    frame_monitor = tk.Frame(janela_monitor)
    frame_monitor.pack(fill="both", expand=True, padx=5, pady=5)
    
    total_registros_conhecidos = 0 
    
    tk.Label(frame_monitor, text="Monitor de Inventário (Verificando a cada 5s)", font=("Segoe UI", 12)).pack()
    
    txt_log = scrolledtext.ScrolledText(frame_monitor, state=tk.DISABLED, height=20, font=("Consolas", 9))
    txt_log.pack(fill="both", expand=True, padx=5, pady=5)
    
    txt_log.tag_config('erro', foreground='red')
    txt_log.tag_config('sucesso', foreground='green', font=('Segoe UI', 9, 'bold'))
    txt_log.tag_config('info', foreground='blue')
    txt_log.tag_config('novo_item', foreground='#006400', font=('Segoe UI', 9, 'bold'))

if __name__ == "__main__":
    janela_monitor = tk.Tk()
    janela_monitor.title("Monitor de Inventário")
    
    criar_tela_login() 
    
    janela_monitor.mainloop()