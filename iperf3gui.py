import customtkinter as ctk
import subprocess
import threading
import sys
import os
import re
from PIL import Image
import PIL._tkinter_finder  

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(os.path.dirname(__file__))
    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class IperfApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("iPerf3 - Teste Ponto a Ponto")
        self.geometry("850x880") # Janela ligeiramente mais alta para respirar melhor
        self.minsize(780, 700)
        self.configure(fg_color="#1e1e2e")
        
        self.process = None
        self.protocol_var = ctk.StringVar(value="TCP")
        self.direction_var = ctk.StringVar(value="Upload")
        self.bandwidth_var = ctk.StringVar(value="100M")
        
        self.protocol_var.trace_add("write", self.atualizar_controles_udp)
        self.protocol_var.trace_add("write", lambda *args: self.limpar_grafico_total())
        self.direction_var.trace_add("write", lambda *args: self.limpar_grafico_total())

        self.cores_grafico = ['#50fa7b', '#8be9fd', '#ff79c6', '#f1fa8c', '#ffb86c', '#bd93f9']
        self.cor_atual_idx = 0
        self.current_x = []
        self.current_y = []
        self.current_line = None

        self.criar_interface()
        self._carregar_logo()
        self.atualizar_controles_udp()
        
        self.bind('<Return>', self._atalho_enter)
        self.bind('<KP_Enter>', self._atalho_enter)

    def criar_interface(self):
        self.main_frame = ctk.CTkFrame(self, fg_color="#282a36", corner_radius=10)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Define 2 colunas principais simétricas para o topo
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        # --- Dados do Servidor ---
        label_server = ctk.CTkLabel(self.main_frame, text="Dados do Servidor:", font=ctk.CTkFont(size=14, weight="bold"))
        label_server.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))

        server_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        server_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(server_frame, text="IP/Host:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.entry_ip = ctk.CTkEntry(server_frame, placeholder_text="Ex: 192.168.1.100", width=220, border_color="#44475a")
        self.entry_ip.grid(row=0, column=1, sticky="w")
        self.entry_ip.insert(0, "200.152.98.6")

        ctk.CTkLabel(server_frame, text="Porta:").grid(row=0, column=2, sticky="w", padx=(30, 8))
        self.entry_port = ctk.CTkEntry(server_frame, width=80, border_color="#44475a")
        self.entry_port.grid(row=0, column=3, sticky="w")
        self.entry_port.insert(0, "5201")

        # --- Separador ---
        ctk.CTkFrame(self.main_frame, height=1, fg_color="#44475a").grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=12)

        # --- Configurações do Teste ---
        label_config = ctk.CTkLabel(self.main_frame, text="Configurações do Teste:", font=ctk.CTkFont(size=14, weight="bold"))
        label_config.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 5))

        config_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        config_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))
        
        # Proporção simétrica perfeita para as 3 colunas de configuração
        config_frame.columnconfigure(0, weight=1)
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(2, weight=1)
        
        # Col 0: Protocolo
        ctk.CTkLabel(config_frame, text="Protocolo:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#bd93f9").grid(row=0, column=0, sticky="w", pady=(0, 6))
        ctk.CTkRadioButton(config_frame, text="TCP", variable=self.protocol_var, value="TCP").grid(row=1, column=0, sticky="w", pady=6)
        ctk.CTkRadioButton(config_frame, text="UDP", variable=self.protocol_var, value="UDP").grid(row=2, column=0, sticky="w", pady=6)

        # Col 1: Direção
        ctk.CTkLabel(config_frame, text="Direção:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#bd93f9").grid(row=0, column=1, sticky="w", pady=(0, 6))
        ctk.CTkRadioButton(config_frame, text="Upload", variable=self.direction_var, value="Upload").grid(row=1, column=1, sticky="w", pady=6)
        ctk.CTkRadioButton(config_frame, text="Download", variable=self.direction_var, value="Download").grid(row=2, column=1, sticky="w", pady=6)
        ctk.CTkRadioButton(config_frame, text="Ambos", variable=self.direction_var, value="Ambos").grid(row=3, column=1, sticky="w", pady=6)

        # Col 2: Parâmetros
        params_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        params_frame.grid(row=0, column=2, rowspan=4, sticky="nw")
        ctk.CTkLabel(params_frame, text="Parâmetros:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#bd93f9").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        
        ctk.CTkLabel(params_frame, text="Threads (-P):").grid(row=1, column=0, sticky="w", pady=6, padx=(0, 8))
        self.entry_threads = ctk.CTkEntry(params_frame, width=65, border_color="#44475a")
        self.entry_threads.grid(row=1, column=1, sticky="w", pady=6)
        self.entry_threads.insert(0, "1")

        ctk.CTkLabel(params_frame, text="Tempo (seg):").grid(row=2, column=0, sticky="w", pady=6, padx=(0, 8))
        self.entry_time = ctk.CTkEntry(params_frame, width=65, border_color="#44475a")
        self.entry_time.grid(row=2, column=1, sticky="w", pady=6)
        self.entry_time.insert(0, "10")

        ctk.CTkLabel(params_frame, text="Banda UDP:").grid(row=3, column=0, sticky="w", pady=6, padx=(0, 8))
        self.combo_bandwidth = ctk.CTkComboBox(
            params_frame,
            width=100,
            variable=self.bandwidth_var,
            state="disabled",
            values=["10M","50M","100M","200M","300M","400M","500M","600M","700M","800M","900M","1000M"]
        )
        self.combo_bandwidth.grid(row=3, column=1, sticky="w", pady=6)

        # --- Separador e Status ---
        ctk.CTkFrame(self.main_frame, height=1, fg_color="#44475a").grid(row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=12)
        self.status_label = ctk.CTkLabel(self.main_frame, text="Pressione ENTER para iniciar.", text_color="#f8f8f2")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=(0, 10))

        # --- Botões de Ação ---
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 15))
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)
        btn_frame.columnconfigure(2, weight=1)
        
        self.btn_start = ctk.CTkButton(btn_frame, text="▶ INICIAR (ENTER)", fg_color="#1b8f36", hover_color="#146c29", height=42, command=self.iniciar_teste_thread)
        self.btn_start.grid(row=0, column=0, sticky="ew", padx=(0, 5))
        
        self.btn_stop = ctk.CTkButton(btn_frame, text="■ PARAR", fg_color="#ff5555", hover_color="#cc2222", height=42, state="disabled", command=self.parar_teste)
        self.btn_stop.grid(row=0, column=1, sticky="ew", padx=5)
        
        self.btn_clear = ctk.CTkButton(btn_frame, text="🧹 LIMPAR GRÁFICO", fg_color="#44475a", hover_color="#6272a4", height=42, command=self.limpar_grafico_total)
        self.btn_clear.grid(row=0, column=2, sticky="ew", padx=(5, 0))

        # --- Gráfico Vetorial ---
        self.fig, self.ax = plt.subplots(figsize=(6, 2.5), dpi=100)
        self.fig.patch.set_facecolor('#282a36')
        self.ax.set_facecolor('#191a21')
        self.ax.tick_params(colors='#f8f8f2', labelsize=9)
        self.ax.set_title("Comparativo de Largura de Banda (Mbps)", color='#f8f8f2', weight='bold', fontsize=11)
        self.ax.set_xlabel("Tempo (segundos)", color='#f8f8f2', fontsize=9)
        self.ax.set_ylabel("Velocidade (Mbps)", color='#f8f8f2', fontsize=9)
        self.ax.grid(True, color='#44475a', linestyle='--', alpha=0.3)
        for spine in self.ax.spines.values():
            spine.set_color('#44475a')

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.main_frame)
        self.canvas.get_tk_widget().grid(row=8, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 10))

        # --- Console ---
        self.console = ctk.CTkTextbox(self.main_frame, fg_color="#191a21", text_color="#f8f8f2", wrap="none")
        self.console.grid(row=9, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 20))
        
        # PESOS DINÂMICOS: Garante que o Gráfico e a Consola expandem de forma equilibrada
        # Gráfico recebe peso 3 (ligeiramente maior), Consola recebe peso 2
        self.main_frame.rowconfigure(8, weight=3)
        self.main_frame.rowconfigure(9, weight=2)



    def atualizar_controles_udp(self, *args):
        if self.protocol_var.get() == "UDP":
            self.combo_bandwidth.configure(state="normal")
        else:
            self.combo_bandwidth.configure(state="disabled")

    def _carregar_logo(self):
        try:
            caminho = resource_path("logo.jpg")
            img = Image.open(caminho).convert("RGBA")
            dados = img.getdata()
            novos = []
            for pixel in dados:
                r, g, b, a = pixel
                if r > 200 and g > 200 and b > 200:
                    novos.append((r, g, b, 0))
                else:
                    novos.append(pixel)
            img.putdata(novos)
            img.thumbnail((130, 50), Image.LANCZOS)
            self._logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(img.width, img.height))
            logo_label = ctk.CTkLabel(self.main_frame, image=self._logo_img, text="", fg_color="transparent")
            logo_label.grid(row=0, column=1, sticky="e", padx=20, pady=(20, 5))
        except Exception:
            pass

    def _atalho_enter(self, event):
        if self.btn_start.cget("state") == "normal":
            self.iniciar_teste_thread()

    def limpar_grafico_total(self):
        self.cor_atual_idx = 0
        self.current_x = []
        self.current_y = []
        self.current_line = None
        self.ax.clear()
        self.ax.set_facecolor('#191a21')
        self.ax.tick_params(colors='#f8f8f2', labelsize=9)
        self.ax.set_title("Comparativo de Largura de Banda (Mbps)", color='#f8f8f2', weight='bold', fontsize=11)
        self.ax.set_xlabel("Tempo (segundos)", color='#f8f8f2', fontsize=9)
        self.ax.set_ylabel("Velocidade (Mbps)", color='#f8f8f2', fontsize=9)
        self.ax.grid(True, color='#44475a', linestyle='--', alpha=0.3)
        self.canvas.draw()
        
    def update_chart(self, value):
        self.after(0, self._safe_update_chart, value)

    def _safe_update_chart(self, value):
        tempo_atual = len(self.current_x) + 1
        self.current_x.append(tempo_atual)
        self.current_y.append(value)
        if self.current_line:
            self.current_line.set_data(self.current_x, self.current_y)
        self.ax.relim()
        self.ax.autoscale_view()
        self.canvas.draw()

    def log(self, msg):
        self.after(0, lambda: self._escrever_log(msg))

    def _escrever_log(self, msg):
        self.console.configure(state="normal")
        self.console.insert("end", msg + "\n")
        self.console.see("end")
        self.console.configure(state="disabled")

    def iniciar_teste_thread(self):
        ip = self.entry_ip.get().strip()
        if not ip:
            self.log("[ERRO] O campo IP do Servidor não pode estar vazio.")
            return

        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.status_label.configure(text="Teste em execução...", text_color="#50fa7b")
        
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

        self.current_x = []
        self.current_y = []
        
        cor_da_vez = self.cores_grafico[self.cor_atual_idx % len(self.cores_grafico)]
        self.cor_atual_idx += 1
        
        self.current_line, = self.ax.plot(
            [], [], color=cor_da_vez, linewidth=2.5, marker='o', markersize=4, label=f"Execução #{self.cor_atual_idx}"
        )
        
        legenda = self.ax.legend(facecolor='#191a21', edgecolor='#44475a', loc='upper left', fontsize=8)
        if legenda:
            for texto_legenda in legenda.get_texts():
                texto_legenda.set_color('#f8f8f2')
        self.canvas.draw()

        threading.Thread(target=self.executar_iperf, daemon=True).start()

    def executar_iperf(self):
        ip = self.entry_ip.get()
        porta = self.entry_port.get()
        tempo = self.entry_time.get()
        threads = self.entry_threads.get()

        cmd = ["iperf3", "-c", ip, "-p", porta, "-t", tempo, "-P", threads, "--forceflush"]
        
        if self.protocol_var.get() == "UDP":
            cmd.extend(["-u", "-b", self.bandwidth_var.get()])
        direcao = self.direction_var.get()
        if direcao == "Download":
            cmd.append("-R")
        elif direcao == "Ambos":
            cmd.append("--bidir")

        self.log(f"> Comando: {' '.join(cmd)}\n" + "=" * 56)
        num_threads = int(threads) if threads.isdigit() else 1

        try:
            kwargs = {"stdout": subprocess.PIPE, "stderr": subprocess.PIPE, "text": True, "bufsize": 1}
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
                
            self.process = subprocess.Popen(cmd, **kwargs)
            
            for linha in iter(self.process.stdout.readline, ''):
                if linha:
                    linha_str = linha.strip()
                    self.log(linha_str)
                    
                    if "sender" in linha_str or "receiver" in linha_str:
                        continue
                    
                    val = None
                    if num_threads > 1:
                        if "[SUM]" in linha_str:
                            match = re.search(r'(\d+(?:\.\d+)?)\s+Mbits/sec', linha_str)
                            if match: val = float(match.group(1))
                    else:
                        if "sec" in linha_str:
                            match = re.search(r'(\d+(?:\.\d+)?)\s+Mbits/sec', linha_str)
                            if match: val = float(match.group(1))
                    
                    if val is not None:
                        self.update_chart(val)
                        
            erro = self.process.stderr.read()
            if erro:
                self.log(f"[ERRO iPerf3]: {erro.strip()}")
            self.process.wait()
            
        except FileNotFoundError:
            self.log("[ERRO FATAL] O executável 'iperf3' não foi encontrado.")
        except Exception as e:
            self.log(f"[ERRO SUBPROCESSO]: {str(e)}")
        finally:
            self.log("=" * 56 + "\n> Teste Concluído.")
            self.resetar_botoes()

    def parar_teste(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.log("\n[AVISO] Teste interrompido pelo utilizador.")
            self.resetar_botoes()

    def resetar_botoes(self):
        self.after(0, lambda: self.btn_start.configure(state="normal"))
        self.after(0, lambda: self.btn_stop.configure(state="disabled"))
        self.after(0, lambda: self.status_label.configure(text="Pressione ENTER para iniciar.", text_color="#f8f8f2"))

if __name__ == "__main__":
    app = IperfApp()
    app.mainloop()