import tkinter as tk
from tkinter import messagebox
from tkinter import ttk  
import psycopg2
import consultas
import YoutubeApp


class FrameConsultaPadrao(tk.Frame):
    def __init__(self, parent, controller, titulo, nome_consulta_db, colunas_tabela, requer_input=False):
        super().__init__(parent)
        self.controller = controller
        self.nome_consulta_db = nome_consulta_db 
        self.colunas_tabela = colunas_tabela
        self.requer_input = requer_input
        

        self.criar_header_com_usuario() 
        
        tk.Label(
            self, 
            text=titulo, 
            font=("Arial", 16, "bold")
        ).pack(pady=10)

        self.input_var = None
        if self.requer_input:
            tk.Label(self, text="Nome do Canal/Usuário:", font=("Arial", 11)).pack(pady=5)
            self.input_entry = tk.Entry(self, width=50)
            self.input_entry.pack(pady=5)
            self.input_var = self.input_entry.get
            
        # --- Botão de Execução ---
        tk.Button(
            self, 
            text="EXECUTAR CONSULTA", 
            command=self.executar_consulta,
            bg="#008080", fg="white",
        ).pack(pady=10)

        # --- Treeview (Tabela de Resultados) ---
        self.tabela = ttk.Treeview(self, columns=colunas_tabela, show='headings')
        
        for col in colunas_tabela:
            self.tabela.heading(col, text=col)
        
        self.tabela.pack(pady=10, padx=10, fill='both', expand=True)

        # --- Botão Voltar para o Menu ---
        tk.Button(
            self, 
            text="<< Voltar ao Menu Principal", 
            command=lambda: controller.mostrar_frame("Consultas")
        ).pack(pady=15)
        
    def executar_consulta(self):
        """Método que se conecta ao DB e executa a consulta."""
        
        for item in self.tabela.get_children():
            self.tabela.delete(item)
            
        con = YoutubeApp.conectar_db() 
        if not con: return

        try:
            cur = con.cursor()
            
            # Prepara o input
            args = ()
            if self.requer_input:
                input_valor = self.input_entry.get().strip()
                if not input_valor:
                    messagebox.showwarning("Atenção", "O campo de entrada está vazio.")
                    return
                args = (input_valor,)

            # Chama a função de consulta usando o nome_consulta_db
            funcao_consulta = getattr(consultas, self.nome_consulta_db)
            resultados = funcao_consulta(cur, *args)
            
            # Preenche a tabela
            if resultados:
                for linha in resultados:
                    # Formata a reação LIKE/DISLIKE para a primeira consulta específica
                    if self.nome_consulta_db == "tabela_curtidas_feitas_por_canal" and len(linha) == 4:
                        linha = list(linha)
                        linha[3] = "DISLIKE" if linha[3] else "LIKE"
                        linha = tuple(linha)

                    self.tabela.insert('', tk.END, values=linha)
            else:
                messagebox.showinfo("Resultado", "A consulta não retornou resultados.")
                
        except Exception as erro:
            messagebox.showerror("Erro de Consulta", f"Erro: {erro}")
            
        finally:
            if con: con.close()

    def criar_header_com_usuario(self):
        header_frame = tk.Frame(self, bg="#E0E0E0", padx=10, pady=5)
        header_frame.pack(fill='x')
        
        # Usuário Logado
        user_name = self.controller.usuario_logado['nome']
        user_text = f"👤 Usuário Logado: {user_name}"
        tk.Label(
            header_frame, 
            text=user_text, 
            bg="#E0E0E0", 
            font=("Arial", 10, "bold"), 
            fg="#444444"
        ).pack(side=tk.LEFT, padx=10)
        
        # Botão Mudar Conta
        tk.Button(
            header_frame,
            text="Mudar Conta / Logout",
            # Chama o método logout da classe YouTubeApp (controller)
            command=self.controller.logout, 
            bg="#FFB3B3", 
            fg="black",
            font=("Arial", 9)
        ).pack(side=tk.RIGHT)



class TelaConsultas(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.criar_header_com_usuario() 
        
        tk.Label(
            self, 
            text="Menu Principal: Selecione a Consulta (12 Opções)", 
            font=("Arial", 18, "bold")
        ).pack(pady=10)

        # Container Principal para os Botões
        botoes_frame = tk.Frame(self)
        botoes_frame.pack(pady=10, padx=20, fill='both', expand=True)

        # Lista de botões a serem criados: (Nome do botão, Nome do Frame de Destino)
        botoes_config = [
            ("1. Curtidas Feitas por Canal (Input)", "FrameCurtidasPorCanal"), 
            ("2. Usuários Super Fãs (Input)", "FrameSuperFas"),
            ("3. Top Vídeos Normais (Visualizações)", "FrameTopVideos"),
            ("4. Todas as Livestreams", "FrameLivestreams"),
            ("5. Maiores Doadores por Live", "FrameMaioresDoadores"),
            ("6. Lucro Total dos Canais", "FrameLucroCanais"),
            ("7. Lucro por TAG (Anúncios)", "FrameLucroPorTag"),
            ("8. Top 3 Vídeos Mais Curtidos por Canal", "FrameTop3Videos"),
            ("9. Vídeos c/ Anunciantes Frequentes", "FrameAnunciantesFrequentes"),
            ("10. Ranking: Média de Likes por Vídeo", "FrameMediaLikes"),
            ("11. Ranking: Vídeos Populares (>5000 Likes)", "FrameVideosPopulares"),
            ("12. Curtir: Insira aqui sua nova curtida (Input)", "FrameInsercaoNovaCurtida"), 
        ]

        # Criação dos Botões usando o Loop (2 colunas, 6 linhas)
        for i, (texto, destino) in enumerate(botoes_config):
            row = i // 2
            col = i % 2
            
            botao = tk.Button(
                botoes_frame, 
                text=texto, 
                font=("Arial", 11),
                bg="#3498DB" if "Input" in texto else "#2ECC71", 
                fg="white", 
                width=45,
                height=2,
                command=lambda d=destino: controller.mostrar_frame(d)
            )

            # Garante que as colunas e linhas se expandam
            botao.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")
            botoes_frame.grid_columnconfigure(col, weight=1)
            botoes_frame.grid_rowconfigure(row, weight=1)


        # Botão para voltar ao Menu Inicial de Boas-Vindas
        botao_voltar = tk.Button(
            self, 
            text="<< Voltar ao Início", 
            command=lambda: controller.mostrar_frame("BoasVindas")
        )
        botao_voltar.pack(pady=20)

    def criar_header_com_usuario(self):
        header_frame = tk.Frame(self, bg="#E0E0E0", padx=10, pady=5)
        header_frame.pack(fill='x')
        
        # Usuário Logado
        user_name = self.controller.usuario_logado['nome']
        user_text = f"👤 Usuário Logado: {user_name}"
        tk.Label(
            header_frame, 
            text=user_text, 
            bg="#E0E0E0", 
            font=("Arial", 10, "bold"), 
            fg="#444444"
        ).pack(side=tk.LEFT, padx=10)
        
        # Botão Mudar Conta
        tk.Button(
            header_frame,
            text="Mudar Conta / Logout",
            # Chama o método logout da classe YouTubeApp (controller)
            command=self.controller.logout, 
            bg="#FFB3B3", 
            fg="black",
            font=("Arial", 9)
        ).pack(side=tk.RIGHT)


class FrameCurtidasPorCanal(FrameConsultaPadrao):
    def __init__(self, parent, controller):
        super().__init__(
            parent, controller, 
            titulo="1. Curtidas Feitas por Canal", 
            nome_consulta_db="tabela_curtidas_feitas_por_canal", 
            colunas_tabela=("USUÁRIO", "ID PUBLICAÇÃO", "CANAL DO VÍDEO", "REAÇÃO"), 
            requer_input=True
        )

class FrameSuperFas(FrameConsultaPadrao):
    def __init__(self, parent, controller):
        super().__init__(
            parent, controller, 
            titulo="2. Usuários Super Fãs", 
            nome_consulta_db="tabela_usuarios_super_fas", 
            colunas_tabela=("ID CONTA", "NOME DO SUPER FÃ"), 
            requer_input=True
        )

class FrameTopVideos(FrameConsultaPadrao):
    def __init__(self, parent, controller):
        super().__init__(
            parent, controller, 
            titulo="3. Top Vídeos Normais (Visualizações)", 
            nome_consulta_db="tabela_top_videos", 
            colunas_tabela=("TÍTULO", "ID PUBLICAÇÃO", "CANAL", "VISUALIZAÇÕES"),
        )

class FrameLivestreams(FrameConsultaPadrao):
    def __init__(self, parent, controller):
        super().__init__(
            parent, controller, 
            titulo="4. Todas as Livestreams", 
            nome_consulta_db="tabela_livestreams", 
            colunas_tabela=("ID PUBLICAÇÃO", "NÚMERO DE VIEWERS" ,"TÍTULO LIVE", "CANAL", "TERMINADA?"),
        )

class FrameMaioresDoadores(FrameConsultaPadrao):
    def __init__(self, parent, controller):
        super().__init__(
            parent, controller, 
            titulo="5. Maiores Doadores por Live", 
            nome_consulta_db="tabela_maiores_doadores", 
            colunas_tabela=("DOADOR", "LIVESTREAM" ,"TÍTULO", "TOTAL DOADO"),
        )

class FrameLucroCanais(FrameConsultaPadrao):
    def __init__(self, parent, controller):
        super().__init__(
            parent, controller, 
            titulo="6. Lucro Total dos Canais (Anúncios + Doações)", 
            nome_consulta_db="tabela_lucro_canais", 
            colunas_tabela=("ID CANAL", "NOME DO CANAL", "TOTAL ANÚNCIOS", "TOTAL DOAÇÕES", "LUCRO TOTAL"),
            requer_input=False # Não requer input do usuário
        )

class FrameLucroPorTag(FrameConsultaPadrao):
    def __init__(self, parent, controller):
        super().__init__(
            parent, controller, 
            titulo="7. Lucro por TAG (Proveniente de Anúncios)", 
            nome_consulta_db="tabela_lucro_por_tag", 
            colunas_tabela=("TAG", "LUCRO TOTAL"), 
            requer_input=False
        )

class FrameTop3Videos(FrameConsultaPadrao):
    def __init__(self, parent, controller):
        super().__init__(
            parent, controller, 
            titulo="8. Top 3 Vídeos Mais Curtidos por Canal", 
            nome_consulta_db="tabela_top3_videos_por_canal", 
            colunas_tabela=("ID PUBLICAÇÃO", "CANAL", "TÍTULO", "LIKES"), 
            requer_input=False
        )

class FrameAnunciantesFrequentes(FrameConsultaPadrao):
    def __init__(self, parent, controller):
        super().__init__(
            parent, controller, 
            titulo="9. Vídeos c/ Anunciantes Frequentes (> 3 Anúncios)", 
            nome_consulta_db="relatorio_videos_anunciantes_frequentes", 
            colunas_tabela=("ID PUBLICAÇÃO", "TÍTULO", "CANAL"), 
            requer_input=False
        )

class FrameMediaLikes(FrameConsultaPadrao):
    def __init__(self, parent, controller):
        super().__init__(
        parent, controller, 
        titulo="10. Ranking: Média de Likes por Vídeo (Canais)", 
        nome_consulta_db="tabela_view_ordenada_por_likes", 
        colunas_tabela=("ID CANAL", "NOME DO CANAL", "MÉDIA LIKES POR VÍDEO"), 
        requer_input=False
    )
        
class FrameVideosPopulares(FrameConsultaPadrao):
    def __init__(self, parent, controller):
        super().__init__(
            parent, controller, 
            titulo="11. Ranking: Canais c/ Mais Vídeos Populares (>5k Likes)", 
            nome_consulta_db="tabela_videos_populares", 
            colunas_tabela=("ID CANAL", "NOME DO CANAL", "VÍDEOS POPULARES"), 
            requer_input=False
        )

    
class FrameInsercaoNovaCurtida(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        
        self.criar_header_com_usuario()

        tk.Label(
            self, 
            text="Cadastro de Nova Curtida (Inserção)", 
            font=("Arial", 16, "bold")
        ).pack(pady=15)
        
        campos_frame = tk.Frame(self)
        campos_frame.pack(pady=10)
        
        # ID da Conta (Quem curtiu)
        tk.Label(campos_frame, text="ID da Conta:", width=20, anchor='w').grid(row=0, column=0, padx=5, pady=5)
        self.entry_id_conta = tk.Entry(campos_frame, width=30)
        self.entry_id_conta.grid(row=0, column=1, padx=5, pady=5)
        
        # (Lógica para inserir o ID da conta logada e torná-lo readonly)
        id_conta_logada = str(self.controller.usuario_logado['id'])
        self.entry_id_conta.insert(0, id_conta_logada)
        self.entry_id_conta.config(state='readonly')
        
        # ID da Publicação (O que foi curtido)
        tk.Label(campos_frame, text="ID da Publicação:", width=20, anchor='w').grid(row=1, column=0, padx=5, pady=5)
        self.entry_id_publicacao = tk.Entry(campos_frame, width=30)
        self.entry_id_publicacao.grid(row=1, column=1, padx=5, pady=5)

        # ID do Canal a Consultar (para a consulta de curtidas recebidas)
        tk.Label(campos_frame, text="ID da Publicação a consultar:", width=20, anchor='w').grid(row=2, column=0, padx=5, pady=5)
        self.entry_id_publicacao_consulta = tk.Entry(campos_frame, width=30) 
        self.entry_id_publicacao_consulta.grid(row=2, column=1, padx=5, pady=5)

        # Checkbox de Dislike 
        self.dislike_var = tk.BooleanVar() 
        tk.Label(campos_frame, text="Dislike (Descurtir):", width=20, anchor='w').grid(row=3, column=0, padx=5, pady=5)
        self.check_dislike = tk.Checkbutton(
            campos_frame, 
            text="Marque para DISLIKE", 
            variable=self.dislike_var
        )
        self.check_dislike.grid(row=3, column=1, padx=5, pady=5, sticky='w')


        botoes_acao_frame = tk.Frame(self)
        botoes_acao_frame.pack(pady=20)
        
        # Botão INSERIR
        tk.Button(
            botoes_acao_frame, 
            text="INSERIR NOVA CURTIDA", 
            command=self.inserir_dados,
            bg="#008080", fg="white", width=25
        ).grid(row=0, column=0, padx=10)
        
        # Botão LISTAR PUBLICAÇÕES 
        tk.Button(
            botoes_acao_frame, 
            text="LISTAR PUBLICAÇÕES", 
            command=self.listar_dados_necessarios,
            bg="#F39C12", width=25
        ).grid(row=0, column=1, padx=10)

        # Botão LISTAR CURTIDAS FEITAS
        tk.Button(
            botoes_acao_frame, 
            text="LISTAR CURTIDAS FEITAS", 
            # NOVO COMMAND: Chama o método atualizado
            command=self.listar_curtidas_por_publicacao,
            bg="#95A5A6", width=25
        ).grid(row=0, column=2, padx=10)

        # --- ÁREA DE SAÍDA / LISTAGEM ---
        tk.Label(self, text="Resultados da Listagem:").pack(pady=5)
        self.saida_texto = tk.Text(self, height=10, width=80)
        self.saida_texto.pack(pady=10)

        tk.Button(
            self, 
            text="<< Voltar ao Menu Principal", 
            command=lambda: controller.mostrar_frame("Consultas")
        ).pack(pady=15)


    def criar_header_com_usuario(self):
        header_frame = tk.Frame(self, bg="#E0E0E0", padx=10, pady=5)
        header_frame.pack(fill='x')
        
        # Usuário Logado
        user_name = self.controller.usuario_logado['nome']
        user_text = f"👤 Usuário Logado: {user_name}"
        tk.Label(
            header_frame, 
            text=user_text, 
            bg="#E0E0E0", 
            font=("Arial", 10, "bold"), 
            fg="#444444"
        ).pack(side=tk.LEFT, padx=10)
        
        # Botão Mudar Conta
        tk.Button(
            header_frame,
            text="Mudar Conta / Logout",
            # Chama o método logout da classe YouTubeApp (controller)
            command=self.controller.logout, 
            bg="#FFB3B3", 
            fg="black",
            font=("Arial", 9)
        ).pack(side=tk.RIGHT)

    
    def inserir_dados(self):
        """Método chamado pelo botão INSERIR."""
        id_conta = self.entry_id_conta.get().strip()
        id_pub = self.entry_id_publicacao.get().strip()
        is_dislike_bool = self.dislike_var.get()
        
        if not all([id_pub]):
            messagebox.showwarning("Atenção", "Preencha todos os campos.")
            return

        try:
            con = YoutubeApp.conectar_db()
            cur = con.cursor()
            
            comando = """
            INSERT INTO Curtida (id_conta, id_publicacao, dislike)
            VALUES (%s, %s, %s);
            """
            
            cur.execute(comando, (id_conta, id_pub, is_dislike_bool))
            con.commit()
            messagebox.showinfo("Sucesso", "Nova curtida inserida com sucesso! (Trigger ativado)")
            
            # Limpar campos
            self.entry_id_conta.delete(0, tk.END)
            self.entry_id_publicacao.delete(0, tk.END)
            self.dislike_var.set(False)
            self.saida_texto.delete(1.0, tk.END)
            
        except Exception as erro:
            if con: con.rollback()
            messagebox.showerror("Erro de Inserção", f"Falha ao inserir curtida: {erro}")
        finally:
            if con: con.close()


    def listar_dados_necessarios(self):
        """Método chamado pelo botão LISTAR: Lista vídeos que a conta logada AINDA NÃO curtiu."""
        self.saida_texto.delete(1.0, tk.END) # Limpa a área
        
        id_conta_logada = self.controller.usuario_logado['id']
        
        con = YoutubeApp.conectar_db()
        if not con: return

        try:
            cur = con.cursor()
            
            videos_disponiveis = consultas.listar_videos_nao_curtidos_por_conta(cur, id_conta_logada)
            
            if not videos_disponiveis:
                self.saida_texto.insert(tk.END, "🎉 Parabéns! Você já curtiu/descurtiu todos os vídeos disponíveis!")
            else:
                self.saida_texto.insert(tk.END, f"{'ID PUB':<10} | {'TÍTULO':<30} | {'CANAL'}\n")
                self.saida_texto.insert(tk.END, "-" * 50 + "\n")
                
                for id_pub, titulo, canal in videos_disponiveis:
                    self.saida_texto.insert(tk.END, f"{id_pub:<10} | {titulo:<30.30} | {canal}\n")
            
        except Exception as erro:
            messagebox.showerror("Erro de Listagem", f"Falha ao listar vídeos: {erro}")
        finally:
            if con: con.close()


    def listar_curtidas_por_publicacao(self):
        """Lista todas as curtidas (likes/dislikes) recebidas em uma Publicação específica."""
        
        id_publicacao_para_consultar = self.entry_id_publicacao_consulta.get().strip()
        
        if not id_publicacao_para_consultar:
            messagebox.showwarning("Atenção", "Por favor, digite o ID da Publicação no campo de consulta.")
            return

        self.saida_texto.delete(1.0, tk.END)
        con = YoutubeApp.conectar_db() 
        if not con: return

        try:
            cur = con.cursor()
            
            resultados = consultas.listar_curtidas_por_publicacao(cur, id_publicacao_para_consultar)
            resultados2 = consultas.conta_likes_dislikes_publicacao(cur, id_publicacao_para_consultar)

            self.saida_texto.insert(tk.END, f"--- CURTIDAS RECEBIDAS PELA PUBLICAÇÃO ID: {id_publicacao_para_consultar} ---\n")
            for likes, dislikes in resultados2:
                self.saida_texto.insert(tk.END, f"Total de Likes: {likes} | Total de Dislikes: {dislikes}\n\n")

            if not resultados:
                self.saida_texto.insert(tk.END, "Nenhuma curtida encontrada para esta publicação.")
            else:
                self.saida_texto.insert(tk.END, f"{'REACÃO':<10} | {'USUÁRIO QUE CURTIU':<30} | {'ID DO USUÁRIO'}\n")
                self.saida_texto.insert(tk.END, "-" * 80 + "\n")
                
                for nome_curtidor, id_curtidor, reacao in resultados:
                    self.saida_texto.insert(tk.END, f"{reacao:<10} | {nome_curtidor:<30.30} | {id_curtidor:<30.30}\n")
                
        except Exception as erro:
            messagebox.showerror("Erro de Listagem", f"Falha ao listar curtidas: {erro}")
        finally:
            if con: con.close()

class TelaBoasVindas(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller 
        
        self.criar_header_com_usuario()

        tk.Label(
            self, 
            text="👋 Olá!", 
            font=("Arial", 20, "bold")
        ).pack(pady=40)
        
        tk.Label(
            self, 
            text=f"Bem-vindo(a), {controller.usuario_logado['nome']}!", 
            font=("Arial", 14)
        ).pack(pady=10)
        
        # Botão Iniciar
        botao_iniciar = tk.Button(
            self, 
            text="Iniciar Aplicação (Consultas)", 
            font=("Arial", 16, "bold"),
            bg="#4CAF50",
            fg="white",
            command=lambda: controller.mostrar_frame("Consultas")
        )
        botao_iniciar.pack(pady=30, padx=50, fill='x')


    def criar_header_com_usuario(self):
        header_frame = tk.Frame(self, bg="#E0E0E0", padx=10, pady=5)
        header_frame.pack(fill='x')
        
        # Usuário Logado
        user_name = self.controller.usuario_logado['nome']
        user_text = f"👤 Usuário Logado: {user_name}"
        tk.Label(
            header_frame, 
            text=user_text, 
            bg="#E0E0E0", 
            font=("Arial", 10, "bold"), 
            fg="#444444"
        ).pack(side=tk.LEFT, padx=10)
        
        # Botão Mudar Conta
        tk.Button(
            header_frame,
            text="Mudar Conta / Logout",
            # Chama o método logout da classe YouTubeApp (controller)
            command=self.controller.logout, 
            bg="#FFB3B3", 
            fg="black",
            font=("Arial", 9)
        ).pack(side=tk.RIGHT)