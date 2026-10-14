"""Interface gráfica (Tkinter + ttk) do RoboRace.

Aqui não há regras do jogo: a interface só chama a classe Partida e mostra o estado.
Desafios implementados: 05 (tamanho do texto), 07 (TXT), 08 (CSV),
09 (estatísticas de várias partidas) e 12 (semente reproduzível).
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

import regras
from partida import Estatisticas, Partida, exportar_csv, exportar_txt

TAMANHOS_TEXTO = {"Pequeno": 9, "Médio": 11, "Grande": 14}
COR_ROBO = {"Azul": "#2b6cb0", "Vermelho": "#c53030", "Verde": "#2f855a"}
COR_PADRAO = "#4a5568"


class AreaRolavel(ttk.Frame):
    """Contêiner que acompanha o redimensionamento e oferece rolagem em telas pequenas."""

    def __init__(self, mestre):
        super().__init__(mestre)
        self.canvas = tk.Canvas(self, highlightthickness=0)
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        hsb = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
        self.conteudo = ttk.Frame(self.canvas)
        self._janela = self.canvas.create_window((0, 0), window=self.conteudo, anchor="nw")
        self.canvas.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.canvas.bind("<Configure>", self._reajustar)
        self.conteudo.bind("<Configure>", self._reajustar)

    def _reajustar(self, _evento=None):
        # O conteúdo ocupa pelo menos a janela, mas nunca menos que o tamanho necessário.
        largura = max(self.canvas.winfo_width(), self.conteudo.winfo_reqwidth())
        altura = max(self.canvas.winfo_height(), self.conteudo.winfo_reqheight())
        self.canvas.itemconfigure(self._janela, width=largura, height=altura)
        self.canvas.configure(scrollregion=(0, 0, largura, altura))


class App:
    def __init__(self, root: tk.Tk):
        self.root = root
        root.title("RoboRace — corrida e desafios de programação")
        root.geometry("1180x780")
        root.minsize(560, 420)

        self.estat = Estatisticas()        # preservada entre partidas (desafio 09)
        self.partida: Partida | None = None
        self.estat_registrada = False
        self.dialogo_aberto = False
        self.rotulos_longos: list[ttk.Label] = []

        self._criar_fontes()
        area = AreaRolavel(root)
        area.pack(fill="both", expand=True)
        self.raiz = area.conteudo
        self.raiz.columnconfigure(0, weight=1)
        self.raiz.rowconfigure(2, weight=1)
        self.raiz.rowconfigure(3, weight=2)

        self._montar_cabecalho()
        self._montar_largada()
        self._montar_pista()
        self._montar_inferior()
        self.mensagem_var = tk.StringVar(value="Escolha seu robô e clique em “Iniciar corrida”.")
        msg = ttk.Label(self.raiz, textvariable=self.mensagem_var, anchor="w", wraplength=900)
        msg.grid(row=4, column=0, sticky="ew", padx=10, pady=(4, 8))
        self.rotulos_longos.append(msg)

        root.bind("<Return>", self._ao_enter)
        self.aplicar_tamanho()
        self.atualizar()

    # ------------------------------------------------------------------ fontes
    def _criar_fontes(self):
        familia = tkfont.nametofont("TkDefaultFont").actual("family")
        self.fonte_titulo = tkfont.Font(family=familia, weight="bold")
        self.fonte_destaque = tkfont.Font(family=familia, weight="bold")
        self.fonte_pista = tkfont.Font(family=familia)
        self.fonte_pista_neg = tkfont.Font(family=familia, weight="bold")
        self.tamanho_var = tk.StringVar(value="Médio")
        self.estilo = ttk.Style()
        self.estilo.configure("Principal.TButton", font=self.fonte_destaque, padding=8)

    def aplicar_tamanho(self, _evento=None):
        """Desafio 05: muda o tamanho do texto em pista, painéis e relatórios."""
        t = TAMANHOS_TEXTO[self.tamanho_var.get()]
        for nome in ("TkDefaultFont", "TkTextFont", "TkMenuFont", "TkHeadingFont",
                     "TkCaptionFont", "TkSmallCaptionFont", "TkIconFont",
                     "TkTooltipFont", "TkFixedFont"):
            try:
                tkfont.nametofont(nome).configure(size=t)
            except tk.TclError:
                pass
        self.fonte_titulo.configure(size=t + 8)
        self.fonte_destaque.configure(size=t + 1)
        self.fonte_pista.configure(size=t)
        self.fonte_pista_neg.configure(size=t)
        for rotulo in self.rotulos_longos:
            rotulo.configure(wraplength=t * 28 if rotulo.master is not self.raiz else t * 80)
        self.desenhar_pista()

    # ---------------------------------------------------------------- widgets
    def _montar_cabecalho(self):
        f = ttk.Frame(self.raiz)
        f.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 4))
        f.columnconfigure(0, weight=1)
        ttk.Label(f, text="RoboRace", font=self.fonte_titulo).grid(row=0, column=0, sticky="w")
        ttk.Label(f, text="Texto:").grid(row=0, column=1, padx=(8, 4))
        caixa = ttk.Combobox(f, textvariable=self.tamanho_var, values=list(TAMANHOS_TEXTO),
                             state="readonly", width=9)
        caixa.grid(row=0, column=2)
        caixa.bind("<<ComboboxSelected>>", self.aplicar_tamanho)

    def _montar_largada(self):
        f = ttk.LabelFrame(self.raiz, text="Largada")
        f.grid(row=1, column=0, sticky="ew", padx=10, pady=4)
        f.columnconfigure(5, weight=1)
        ttk.Label(f, text="Seu robô:").grid(row=0, column=0, padx=6, pady=6)
        self.jogador_var = tk.StringVar(value="")        # vazio = ainda não escolheu
        self.radios = []
        for i, nome in enumerate(regras.ROBOS_PADRAO, start=1):
            rb = ttk.Radiobutton(f, text=nome, value=nome, variable=self.jogador_var,
                                 command=self.desenhar_pista)
            rb.grid(row=0, column=i, padx=4)
            self.radios.append(rb)
        base = len(regras.ROBOS_PADRAO) + 1
        ttk.Label(f, text="Semente (opcional):").grid(row=0, column=base, padx=(14, 4))
        self.semente_var = tk.StringVar()
        self.ent_semente = ttk.Entry(f, textvariable=self.semente_var, width=10)
        self.ent_semente.grid(row=0, column=base + 1)
        self.semente_usada_var = tk.StringVar(value="")
        ttk.Label(f, textvariable=self.semente_usada_var).grid(row=0, column=base + 2, padx=8)
        self.btn_principal = ttk.Button(f, style="Principal.TButton", command=self.acao_principal)
        self.btn_principal.grid(row=1, column=0, columnspan=4, sticky="w", padx=6, pady=(0, 6))
        self.btn_nova = ttk.Button(f, text="Nova partida", command=self.nova_partida)
        self.btn_nova.grid(row=1, column=base, columnspan=2, sticky="w", padx=6, pady=(0, 6))

    def _montar_pista(self):
        self.pista = tk.Canvas(self.raiz, width=720, height=220, bg="white",
                               highlightthickness=1, highlightbackground="#a0aec0")
        self.pista.grid(row=2, column=0, sticky="nsew", padx=10, pady=4)
        self.pista.bind("<Configure>", self.desenhar_pista)

    def _rotulo(self, pai, variavel, **extra):
        r = ttk.Label(pai, textvariable=variavel, justify="left", anchor="w", **extra)
        self.rotulos_longos.append(r)
        return r

    def _montar_inferior(self):
        baixo = ttk.Frame(self.raiz)
        baixo.grid(row=3, column=0, sticky="nsew", padx=10, pady=4)
        baixo.columnconfigure(2, weight=1)
        baixo.rowconfigure(0, weight=1)

        # --- coluna 0: corrida e progresso do jogador
        col0 = ttk.Frame(baixo)
        col0.grid(row=0, column=0, sticky="ns", padx=(0, 8))
        lf1 = ttk.LabelFrame(col0, text="Corrida")
        lf1.pack(fill="x", pady=(0, 6))
        self.rodada_var, self.lider_var = tk.StringVar(), tk.StringVar()
        self.seu_robo_var, self.resultado_var = tk.StringVar(), tk.StringVar()
        for var in (self.rodada_var, self.lider_var, self.seu_robo_var):
            self._rotulo(lf1, var).pack(fill="x", padx=6, pady=2)
        self._rotulo(lf1, self.resultado_var, font=self.fonte_destaque).pack(fill="x", padx=6, pady=4)

        lf2 = ttk.LabelFrame(col0, text="Seu progresso")
        lf2.pack(fill="x")
        self.acertos_var, self.creditos_var = tk.StringVar(), tk.StringVar()
        self.equipado_var, self.aplicacao_var = tk.StringVar(), tk.StringVar()
        for var in (self.acertos_var, self.creditos_var, self.equipado_var, self.aplicacao_var):
            self._rotulo(lf2, var).pack(fill="x", padx=6, pady=2)

        # --- coluna 1: desafio e benefícios
        lf3 = ttk.LabelFrame(baixo, text="Desafio e benefícios")
        lf3.grid(row=0, column=1, sticky="ns", padx=(0, 8))
        self.desafio_var = tk.StringVar()
        self._rotulo(lf3, self.desafio_var).pack(fill="x", padx=6, pady=4)
        self.btn_responder = ttk.Button(lf3, text="Responder desafio", command=self.abrir_desafio)
        self.btn_responder.pack(fill="x", padx=6, pady=2)
        ttk.Separator(lf3).pack(fill="x", padx=6, pady=6)
        self.botoes_compra = {}
        for nome in regras.BENEFICIOS:
            b = ttk.Button(lf3, command=lambda n=nome: self.comprar(n))
            b.pack(fill="x", padx=6, pady=2)
            self.botoes_compra[nome] = b
        explicacao = tk.StringVar(value=(
            f"Turbo: +{regras.BONUS_TURBO_COMPRADO} posições depois dos efeitos do evento "
            "(vale até em pane).\nEscudo: converte pane, óleo ou buraco em movimento normal."))
        self._rotulo(lf3, explicacao).pack(fill="x", padx=6, pady=4)

        # --- coluna 2: relatórios, histórico e estatísticas
        self.abas = ttk.Notebook(baixo)
        self.abas.grid(row=0, column=2, sticky="nsew")
        aba_rel, self.txt_rel = self._criar_texto(self.abas)
        self.abas.add(aba_rel, text="Relatório da rodada")

        aba_hist = ttk.Frame(self.abas)
        quadro, self.txt_hist = self._criar_texto(aba_hist)
        quadro.pack(fill="both", expand=True)
        barra = ttk.Frame(aba_hist)
        barra.pack(fill="x", pady=4)
        ttk.Button(barra, text="Exportar TXT", command=lambda: self.exportar("txt")).pack(side="left", padx=4)
        ttk.Button(barra, text="Exportar CSV", command=lambda: self.exportar("csv")).pack(side="left", padx=4)
        self.abas.add(aba_hist, text="Histórico")

        aba_est = ttk.Frame(self.abas)
        self.est_var = tk.StringVar()
        ttk.Label(aba_est, textvariable=self.est_var, justify="left").pack(anchor="w", padx=10, pady=10)
        ttk.Button(aba_est, text="Zerar estatísticas", command=self.zerar_estatisticas).pack(anchor="w", padx=10)
        self.abas.add(aba_est, text="Estatísticas")

    def _criar_texto(self, pai):
        quadro = ttk.Frame(pai)
        txt = tk.Text(quadro, height=10, width=44, wrap="word", state="disabled", font="TkFixedFont")
        sb = ttk.Scrollbar(quadro, orient="vertical", command=txt.yview)
        txt.configure(yscrollcommand=sb.set)
        txt.grid(row=0, column=0, sticky="nsew")
        sb.grid(row=0, column=1, sticky="ns")
        quadro.rowconfigure(0, weight=1)
        quadro.columnconfigure(0, weight=1)
        return quadro, txt

    @staticmethod
    def _escrever(txt: tk.Text, conteudo: str, anexar=False):
        txt.configure(state="normal")
        if not anexar:
            txt.delete("1.0", "end")
        txt.insert("end", conteudo)
        txt.see("end" if anexar else "1.0")
        txt.configure(state="disabled")

    def _mensagem(self, texto: str):
        self.mensagem_var.set(texto)

    # ------------------------------------------------------------------ pista
    def desenhar_pista(self, _evento=None):
        c = self.pista
        c.delete("all")
        p = self.partida
        robos = p.corrida.robos if p else regras.ROBOS_PADRAO
        posicoes = p.corrida.posicoes if p else {r: 0 for r in robos}
        jogador = p.jogador if p else self.jogador_var.get()
        finalizada = bool(p and p.finalizada)

        altura_faixa, topo = 62, 34
        c.configure(height=topo + altura_faixa * len(robos) + 8)
        rotulos = [f"★ {r} (VOCÊ)" for r in robos]
        margem_esq = max(150, max(self.fonte_pista_neg.measure(t) for t in rotulos) + 30)
        x0 = margem_esq
        x1 = max(c.winfo_width(), 720) - 70

        c.create_text(x0, 16, text="INÍCIO (0)", anchor="w", font=self.fonte_pista_neg)
        c.create_text(x1, 16, text=f"CHEGADA ({regras.META})", anchor="e", font=self.fonte_pista_neg)
        for i, robo in enumerate(robos):
            y = topo + altura_faixa * i + altura_faixa // 2
            c.create_rectangle(x0, y - 22, x1, y + 22, fill="#edf2f7", outline="#a0aec0")
            ehvoce = robo == jogador
            nome = f"★ {robo} (VOCÊ)" if ehvoce else robo
            pos = posicoes[robo]
            situacao = f"posição {pos}" + (" — CHEGOU" if finalizada and robo in p.corrida.vencedores else "")
            c.create_text(8, y - 10, text=nome, anchor="w",
                          font=self.fonte_pista_neg if ehvoce else self.fonte_pista)
            c.create_text(8, y + 10, text=situacao, anchor="w", font=self.fonte_pista)
            # Progresso visual limitado à chegada; o número mostra a posição real.
            x = x0 + min(pos, regras.META) / regras.META * (x1 - x0)
            cor, r = COR_ROBO.get(robo, COR_PADRAO), 15
            if ehvoce:   # jogador: quadrado com borda grossa (não depende só da cor)
                c.create_rectangle(x - r, y - r, x + r, y + r, fill=cor, outline="black", width=4)
            else:        # computador: círculo com borda fina
                c.create_oval(x - r, y - r, x + r, y + r, fill=cor, outline="#1a202c", width=1)
            c.create_text(x, y, text=robo[0], fill="white", font=self.fonte_pista_neg)
        c.create_line(x0, topo - 6, x0, topo + altura_faixa * len(robos), width=3)
        c.create_line(x1, topo - 6, x1, topo + altura_faixa * len(robos), width=4, dash=(6, 4))

    # -------------------------------------------------------------- atualizar
    def atualizar(self):
        p = self.partida
        em_andamento = p is not None and not p.finalizada
        finalizada = p is not None and p.finalizada

        sel = "normal" if p is None else "disabled"      # não troca de robô durante a corrida
        for rb in self.radios:
            rb.configure(state=sel)
        self.ent_semente.configure(state=sel)

        if p is None:
            self.btn_principal.configure(text="Iniciar corrida (Enter)", state="normal")
        elif em_andamento:
            self.btn_principal.configure(text="Avançar rodada (Enter)", state="normal")
        else:
            self.btn_principal.configure(text="Corrida encerrada", state="disabled")

        if p is None:
            self.rodada_var.set("Rodada: 0")
            self.lider_var.set("Líder: —")
            escolhido = self.jogador_var.get()
            self.seu_robo_var.set(f"Seu robô: {escolhido} ★" if escolhido else "Seu robô: (escolha um)")
            self.resultado_var.set("")
            self.acertos_var.set("Acertos: 0")
            self.creditos_var.set("Créditos: 0")
            self.equipado_var.set("Benefício equipado: nenhum")
            self.aplicacao_var.set("Os bônus comprados valem só para o seu robô.")
            self.desafio_var.set("Inicie a corrida para receber o desafio.")
        else:
            d, c = p.desafios, p.corrida
            self.rodada_var.set(f"Rodada: {c.rodada}" + (f" (próxima: {c.rodada + 1})" if em_andamento else ""))
            lideres = c.lideres()
            pos_lider = c.posicoes[lideres[0]]
            self.lider_var.set(("Líder: " if len(lideres) == 1 else "Líderes (empatados): ")
                               + ", ".join(lideres) + f" — posição {pos_lider}")
            self.seu_robo_var.set(f"Seu robô: {p.jogador} ★")
            self.resultado_var.set(p.resumo_final() if finalizada else "")
            self.acertos_var.set(f"Acertos: {d.acertos}")
            self.creditos_var.set(f"Créditos: {d.creditos}")
            if d.beneficio:
                self.equipado_var.set(f"Benefício equipado: {d.beneficio}")
                self.aplicacao_var.set(f"O {d.beneficio} será aplicado ao robô {p.jogador} (você) "
                                       "na próxima rodada e depois será consumido.")
            else:
                self.equipado_var.set("Benefício equipado: nenhum")
                self.aplicacao_var.set(f"Bônus comprados valem só para o robô {p.jogador} (você), "
                                       "na próxima rodada.")
            if finalizada:
                self.desafio_var.set("Corrida encerrada: desafios e compras bloqueados.")
            elif d.respondida:
                self.desafio_var.set(f"Desafio da rodada: {d.resultado}. Só é permitida uma resposta por rodada.")
            else:
                self.desafio_var.set("Desafio da rodada: disponível (responder é opcional).")

        pode_responder = em_andamento and not p.desafios.respondida
        self.btn_responder.configure(state="normal" if pode_responder else "disabled")
        for nome, custo in regras.BENEFICIOS.items():
            botao = self.botoes_compra[nome]
            texto = f"Comprar {nome} — {custo} crédito(s)"
            ativo = False
            if em_andamento:
                if p.desafios.beneficio is not None:
                    texto += " (já há benefício equipado)"
                elif p.desafios.creditos < custo:
                    texto += f" (faltam {custo - p.desafios.creditos})"
                else:
                    ativo = True
            botao.configure(text=texto, state="normal" if ativo else "disabled")

        if finalizada and not self.estat_registrada:
            self.estat.registrar(p)
            self.estat_registrada = True
        self._atualizar_estatisticas()
        self.desenhar_pista()

    def _atualizar_estatisticas(self):
        e = self.estat
        self.est_var.set(f"Partidas concluídas: {e.concluidas}\nVitórias: {e.vitorias}\n"
                         f"Derrotas: {e.derrotas}\nEmpates: {e.empates}\n"
                         f"Média de rodadas: {e.media_rodadas:.1f}")

    # ------------------------------------------------------------------ ações
    def _ao_enter(self, _evento):
        if self.dialogo_aberto:
            return
        if str(self.btn_principal.cget("state")) != "disabled":
            self.acao_principal()

    def acao_principal(self):
        if self.partida is None:
            self.iniciar()
        else:
            self.avancar()

    def iniciar(self):
        texto = self.semente_var.get().strip()
        semente = None
        if texto:
            try:
                semente = int(texto)
            except ValueError:
                messagebox.showerror("Semente inválida", "Digite apenas um número inteiro ou deixe em branco.")
                return
        try:
            partida = Partida(self.jogador_var.get(), semente)
        except ValueError:
            messagebox.showwarning("Escolha seu robô", "Escolha Azul, Vermelho ou Verde antes da largada.")
            return
        self.partida = partida
        partida.iniciar()
        self.estat_registrada = False
        self.semente_usada_var.set(f"Semente usada: {partida.semente}")
        self._escrever(self.txt_rel, "Nenhuma rodada jogada ainda.")
        self._escrever(self.txt_hist, "")
        self._mensagem(f"Largada! Você é o robô {partida.jogador}. Responda ao desafio (opcional), "
                       "compre benefícios e avance a rodada.")
        self.atualizar()

    def avancar(self):
        try:
            rel = self.partida.avancar()
        except RuntimeError as erro:
            messagebox.showwarning("Ação bloqueada", str(erro))
            return
        self._escrever(self.txt_rel, rel.texto())
        self._escrever(self.txt_hist, rel.texto() + "\n" + "-" * 40 + "\n", anexar=True)
        self.abas.select(0)
        if self.partida.finalizada:
            self._mensagem("Fim da corrida! " + self.partida.resumo_final())
        else:
            self._mensagem(f"Rodada {rel.rodada} concluída. Prepare a próxima: desafio e compras.")
        self.atualizar()

    def nova_partida(self):
        p = self.partida
        if p is not None and not p.finalizada:
            if not messagebox.askyesno("Nova partida", "A corrida está em andamento. Abandonar e recomeçar?"):
                return
        self.partida = None
        self.jogador_var.set("")
        self.semente_var.set("")
        self.semente_usada_var.set("")
        self._escrever(self.txt_rel, "")
        self._escrever(self.txt_hist, "")
        self._mensagem("Nova partida: escolha seu robô e clique em “Iniciar corrida”.")
        self.atualizar()

    def comprar(self, nome: str):
        try:
            custo = self.partida.comprar(nome)
        except (ValueError, RuntimeError) as erro:
            messagebox.showwarning("Compra não realizada", str(erro))
            return
        self._mensagem(f"Compra feita: {custo} crédito(s) gastos em {nome} para o robô "
                       f"{self.partida.jogador}. Saldo: {self.partida.desafios.creditos}. "
                       "Será aplicado na próxima rodada.")
        self.atualizar()

    def zerar_estatisticas(self):
        if messagebox.askyesno("Zerar estatísticas", "Apagar as estatísticas de todas as partidas?"):
            self.estat.zerar()
            self._atualizar_estatisticas()

    def exportar(self, tipo: str):
        if self.partida is None or not self.partida.relatorios:
            messagebox.showinfo("Exportar", "Jogue pelo menos uma rodada antes de exportar.")
            return
        ext = ".txt" if tipo == "txt" else ".csv"
        caminho = filedialog.asksaveasfilename(
            defaultextension=ext, initialfile=f"roborace_{tipo}{ext}",
            filetypes=[("Arquivo " + ext.upper(), "*" + ext)])
        if not caminho:
            return
        try:
            (exportar_txt if tipo == "txt" else exportar_csv)(self.partida, caminho)
        except OSError as erro:
            messagebox.showerror("Erro ao salvar", str(erro))
            return
        self._mensagem(f"Arquivo salvo em: {caminho}")

    # ----------------------------------------------------------------- diálogo
    def abrir_desafio(self):
        p = self.partida
        pergunta = p.desafios.pergunta
        dlg = tk.Toplevel(self.root)
        dlg.title("Desafio de programação")
        dlg.transient(self.root)
        corpo = ttk.Frame(dlg, padding=14)
        corpo.pack(fill="both", expand=True)
        ttk.Label(corpo, text=pergunta.enunciado, wraplength=460, font=self.fonte_destaque).pack(anchor="w", pady=(0, 8))
        escolha = tk.IntVar(value=-1)
        radios = []
        for i, alt in enumerate(pergunta.alternativas):
            rb = ttk.Radiobutton(corpo, text=f"{'ABC'[i]}) {alt}", value=i, variable=escolha)
            rb.pack(anchor="w", pady=2)
            radios.append(rb)
        retorno = tk.StringVar()
        ttk.Label(corpo, textvariable=retorno, wraplength=460, justify="left").pack(anchor="w", pady=8)
        botoes = ttk.Frame(corpo)
        botoes.pack(fill="x")

        def fechar(_e=None):
            self.dialogo_aberto = False
            dlg.destroy()

        def confirmar():
            if escolha.get() < 0:
                messagebox.showwarning("Desafio", "Escolha uma alternativa.", parent=dlg)
                return
            acertou, explicacao = p.responder(escolha.get())
            certa = pergunta.alternativas[pergunta.correta]
            if acertou:
                retorno.set(f"✔ Correto! +{regras.CREDITOS_POR_ACERTO} crédito.\n{explicacao}")
            else:
                retorno.set(f"✘ Incorreto. Resposta certa: {certa}\n{explicacao}")
            for rb in radios:
                rb.configure(state="disabled")
            btn_ok.configure(state="disabled")
            btn_fechar.configure(text="Fechar")

        btn_ok = ttk.Button(botoes, text="Confirmar resposta", command=confirmar)
        btn_ok.pack(side="left")
        btn_fechar = ttk.Button(botoes, text="Fechar sem responder", command=fechar)
        btn_fechar.pack(side="right")
        dlg.protocol("WM_DELETE_WINDOW", fechar)
        dlg.bind("<Escape>", fechar)

        self.dialogo_aberto = True          # a corrida não avança com o diálogo aberto
        dlg.grab_set()
        self.root.wait_window(dlg)
        self.dialogo_aberto = False
        self._mensagem("Desafio respondido." if p.desafios.respondida else "Desafio adiado (ainda disponível nesta rodada).")
        self.atualizar()
