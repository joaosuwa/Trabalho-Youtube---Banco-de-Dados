import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  # Usado para o Listbox/Treeview
import psycopg2
import consultas
import frames

# COISAS DO BANCO DE DADOS
DB_CONFIG = {
    "host": "localhost",
    "database": "Youtube",
    "user": "postgres",
    "password": "postgres",
    "port": 5432
}

def conectar_db():
    try:
        con = psycopg2.connect(**DB_CONFIG)
        return con
    except Exception as erro:
        messagebox.showerror("Erro de Conexão", f"Falha ao conectar ao banco de dados: {erro}")
        return None

 
# --- CLASSE PRINCIPAL ---

class YouTubeApp(tk.Tk):
    def __init__(self, usuario_autenticado, login_callback):
        super().__init__()
        self.title("YouTube DB Viewer")
        self.geometry("900x700")
        self.usuario_logado = usuario_autenticado

        container = tk.Frame(self) 
        container.pack(side="top", fill="both", expand=True)
        
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        
        #Instâncias de cada tela (Frame)

        frame_boas_vindas = frames.TelaBoasVindas(container, self)
        self.frames["BoasVindas"] = frame_boas_vindas
        frame_boas_vindas.grid(row=0, column=0, sticky="nsew")

        frame_consultas = frames.TelaConsultas(container, self) 
        self.frames["Consultas"] = frame_consultas
        frame_consultas.grid(row=0, column=0, sticky="nsew")

        self.frames["FrameCurtidasPorCanal"] = frames.FrameCurtidasPorCanal(container, self)
        self.frames["FrameCurtidasPorCanal"].grid(row=0, column=0, sticky="nsew") 

        self.frames["FrameSuperFas"] = frames.FrameSuperFas(container, self)
        self.frames["FrameSuperFas"].grid(row=0, column=0, sticky="nsew") 

        self.frames["FrameTopVideos"] = frames.FrameTopVideos(container, self)
        self.frames["FrameTopVideos"].grid(row=0, column=0, sticky="nsew")
        
        self.frames["FrameLivestreams"] = frames.FrameLivestreams(container, self)
        self.frames["FrameLivestreams"].grid(row=0, column=0, sticky="nsew")

        self.frames["FrameMaioresDoadores"] = frames.FrameMaioresDoadores(container, self)
        self.frames["FrameMaioresDoadores"].grid(row=0, column=0, sticky="nsew")

        self.frames["FrameLucroCanais"] = frames.FrameLucroCanais(container, self)
        self.frames["FrameLucroCanais"].grid(row=0, column=0, sticky="nsew")

        self.frames["FrameLucroPorTag"] = frames.FrameLucroPorTag(container, self)
        self.frames["FrameLucroPorTag"].grid(row=0, column=0, sticky="nsew")

        self.frames["FrameTop3Videos"] = frames.FrameTop3Videos(container, self)
        self.frames["FrameTop3Videos"].grid(row=0, column=0, sticky="nsew")

        self.frames["FrameAnunciantesFrequentes"] = frames.FrameAnunciantesFrequentes(container, self)
        self.frames["FrameAnunciantesFrequentes"].grid(row=0, column=0, sticky="nsew")

        self.frames["FrameMediaLikes"] = frames.FrameMediaLikes(container, self)
        self.frames["FrameMediaLikes"].grid(row=0, column=0, sticky="nsew")

        self.frames["FrameVideosPopulares"] = frames.FrameVideosPopulares(container, self)
        self.frames["FrameVideosPopulares"].grid(row=0, column=0, sticky="nsew")

        self.frames["FrameInsercaoNovaCurtida"] = frames.FrameInsercaoNovaCurtida(container, self)
        self.frames["FrameInsercaoNovaCurtida"].grid(row=0, column=0, sticky="nsew")

        self.login_callback = login_callback

        self.mostrar_frame("BoasVindas")

    # Método para trocar de frame
    def mostrar_frame(self, nome_pagina):
        """Traz o Frame desejado para a frente, escondendo os outros."""
        frame = self.frames[nome_pagina]
        frame.tkraise()

    # Deslogar da conta atual
    def logout(self):
        """Destrói a aplicação principal e volta para a tela de login."""
        self.destroy()
        self.login_callback()


def carregar_contas():

    global lista_contas_raw
    lista_contas.delete(0, tk.END)  
    
    con = conectar_db()
    if not con:
        return

    try:
        cur = con.cursor()
        
        # 1. Executa a consulta
        lista_contas_raw = consultas.listar_todas_contas(cur)
        
        if not lista_contas_raw:
            lista_contas.insert(tk.END, "Nenhuma conta encontrada.")
        else:
            # 2. Preenche o Listbox com os nomes das contas
            for id_conta, nome in lista_contas_raw:
                lista_contas.insert(tk.END, nome)
                
        status_label.config(text="Status: Contas carregadas. Selecione uma.", fg="blue")

    except Exception as erro:
        messagebox.showerror("Erro na Consulta", f"Falha ao carregar contas: {erro}")
        status_label.config(text="Status: Erro na consulta.", fg="red")
        
    finally:
        if con:
            con.close()

def autenticar_conta():
    selecao = lista_contas.curselection()
    
    if not selecao:
        messagebox.showwarning("Atenção", "Por favor, selecione uma conta na lista.")
        return

    indice_selecionado = selecao[0]
    
    id_conta_selecionada, nome_selecionado = lista_contas_raw[indice_selecionado]
    
    global usuario_autenticado
    usuario_autenticado = {
        "id": id_conta_selecionada,
        "nome": nome_selecionado
    }
    
    status_label.config(
        text=f"Status: Autenticado como: {usuario_autenticado['nome']} (ID: {usuario_autenticado['id']})", 
        fg="green"
    )
    
    janela.destroy() 
    
    iniciar_aplicacao_principal(usuario_autenticado, iniciar_tela_login)

def iniciar_aplicacao_principal(usuario_autenticado, login_callback):
    app = YouTubeApp(usuario_autenticado, login_callback)
    app.mainloop()


def iniciar_tela_login():
    global janela, status_label, lista_contas 
    
    janela = tk.Tk()
    janela.title("Autenticação e Listagem de Contas")
    janela.geometry("450x450")

    status_label = tk.Label(janela, text="Status: Carregando...", fg="gray")
    status_label.pack(pady=5)

    botao_carregar = tk.Button(janela, text="1. Carregar Contas do Banco", command=carregar_contas, bg="#ADD8E6")
    botao_carregar.pack(pady=10, padx=20, fill='x')
    
    tk.Label(janela, text="Contas Disponíveis:", font=("Arial", 10)).pack(pady=5)
    lista_contas = tk.Listbox(janela, height=10, width=40)
    lista_contas.pack(pady=10)

    botao_autenticar = tk.Button(janela, text="2. Autenticar Conta Selecionada", command=autenticar_conta, bg="#90EE90")
    botao_autenticar.pack(pady=20, padx=20, fill='x')

    janela.mainloop()


if __name__ == '__main__':
    iniciar_tela_login()