import customtkinter as ctk
import subprocess
import threading
import sys
import os
import re
import socket
import queue
import json
import ast
from tkinter import messagebox
import tempfile
from pathlib import Path
import base64
from io import BytesIO
import ipaddress
import urllib.request
import urllib.error
from PIL import Image
import PIL._tkinter_finder  

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Aumente esta versão ao publicar uma nova atualização do script na branch main.
APP_VERSION = (1, 1, 2)
UPDATE_URL = "https://raw.githubusercontent.com/fernandoalvesbr/IperfGui/main/iperf3gui.py"


def versao_do_script(conteudo):
    tree = ast.parse(conteudo)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(
                isinstance(target, ast.Name) and target.id == "APP_VERSION"
                for target in node.targets):
            version = ast.literal_eval(node.value)
            if (isinstance(version, tuple) and len(version) == 3
                    and all(type(part) is int and part >= 0 for part in version)):
                return version
    return (0, 0, 0)


def gravar_script_atomico(caminho, conteudo, modo):
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(dir=caminho.parent, delete=False) as arquivo:
            temporario = Path(arquivo.name)
            arquivo.write(conteudo)
            arquivo.flush()
            os.fsync(arquivo.fileno())
        temporario.chmod(modo)
        temporario.replace(caminho)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)


# Logo MLS em PNG transparente, incorporado para dispensar arquivos externos.
MLS_LOGO_BASE64 = (
    "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"
    "OJqpRwaItmr7JAqWroOIiqFZFugYGuZlBVTNBod67+381EuTz2WA9QpyLtw7u7b12OeRA+tyui/VSgvbQiwEPomHkBoC4Chwkgiq"
    "bgKInqpwcFLjK0d1GrHourp2Xa8gdeVcfbufnQObZjz0BomV9eSsEHgwFAwcAdM08eBOQRAVPLgLUBqlihyXMgTq+NQrSB0ZV9/s"
    "l8GBdZM7rnaiRYvBjIFfkfEy0awKBduMgWY6YEteACVhUF0vEn/xCvLIqIUdema/vq/PrII9/Z/Zumfg7I17+s9AmPbmngEz3t3T"
    "Z+rWPYNmbdszcPrre4Zg+WN5G/cMnLb68wf/OGfwhVrC9KcWPtU3N3/vw9hfr9ztnyF8+vCM1z99JHfd7r7T83f3n7Z+d5/pmz99"
    "OLdgT9/Zb+7pN3vHngGT1+55ZPTsrieOqc2w+VKrrGVyq77H4NYRc5VbR6xTOgxa5EnHfOtRs3CFT2z1y3h/BMeWnvWCzw2pugLY"
    "IXuRx4V0HP+J4JafCVx6Lrh41e3d/L2DZgRPN2MKR0ZKoGlapBJkPKzzlANwrCpLYhIBbMHD6R7+wdPROFXdL01ByIkDdQKpvTW5"
    "cfNy2rRlCWvUspSktKygSS0ruMSWFSS+pSqmtCx3/C01TMM02LLM9LQ0xOQWYlyTTifSOh/vXUYu+oOYdOkcQ069KkwTWxpCg2s0"
    "Lum6KEJMSLxe45Ouj9CE66Mk/josbxmBQEvV8bWMUaElk3zf1BxDxtiXR6Y0uUZL9jSPJVzTPBZ/7RWxtEZ3qA3Tmkc9zX+lSmk3"
    "RFMDaYfbDRkbX7Pdxcp3yV6Zkj5x483dJm0c8uDUgpcemrH9Xz1m7irvOfsdlj79PWYk3x5h3t+E/SlXR2IIoudGVUJw0i6JMoSa"
    "qVteXV+d8v6bVdv/O5X5f63KvmtVJ/nWiJN8W8TjuUm1Gl0d1RtfHeU8N6gpl91UlJWVdUpZzc8ZGnEiFcM9eAaheFB3DB0UWQIb"
    "D+wOSpSFX4RXekAdnlN2WgdadW7S5cl5LQZkLnu9/xMz004kQpTE9hYfBJ34IAZeBPQtiRdMzoM3qApEwQMxGoAKWwQN8WwpBWJc"
    "ECKO0srd1U6kdy7v6WMWBYOpV72qi3FQqgvAFOzLwXEg6Dg2nfirxmlQP1icH2wEjSlgUgE83gB7dcpju6HG409u9qAGPrzg8iDI"
    "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"
)

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
        scale = self._get_window_scaling()
        width = min(850, int((self.winfo_screenwidth() - 60) / scale))
        height = min(880, int((self.winfo_screenheight() - 120) / scale))
        self.minsize(min(480, width), min(360, height))
        self.geometry(f"{width}x{height}")
        self.resizable(True, True)
        self.configure(fg_color="#1e1e2e")
        
        self.update_events = queue.Queue()
        self.update_busy = False
        self.pending_update = None
        self.script_path = Path(__file__).resolve()
        self.server_process = None
        self.server_events = queue.Queue()
        self.server_stop = threading.Event()
        self.server_running = False
        self.server_samples = {}
        self.server_series = {}
        self.server_session = 0
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

        self.historico_ips = self._carregar_historico_ips()
        self.criar_interface()
        self.criar_interface_servidor()
        self.after(100, self._processar_eventos_servidor)
        self.protocol("WM_DELETE_WINDOW", self._fechar)
        self._carregar_logo()
        self.atualizar_controles_udp()
        self._compact_layout = None
        self.bind("<Configure>", self._adaptar_layout, add="+")
        
        self.bind('<Return>', self._atalho_enter)
        self.bind('<KP_Enter>', self._atalho_enter)
        self.after(100, self._processar_atualizacoes)
        self.after(1500, lambda: self.verificar_atualizacoes(automatico=True))

    def _adaptar_layout(self, event):
        if event.widget is not self:
            return
        compact = event.width / self._get_window_scaling() < 760
        if compact == self._compact_layout:
            return
        self._compact_layout = compact
        address = self.client_address_frame
        # Mantém o IP editável e leva a porta para outra linha em janelas estreitas.
        if not hasattr(self, "client_port_label"):
            self.client_port_label = address.grid_slaves(row=0, column=2)[0]
        self.entry_ip.grid_configure(sticky="ew")
        address.columnconfigure(1, weight=1)
        self.client_port_label.grid_configure(
            row=1 if compact else 0, column=0 if compact else 2,
            padx=(0, 8) if compact else (20, 8), pady=(8, 0) if compact else 0)
        self.entry_port.grid_configure(
            row=1 if compact else 0, column=1 if compact else 3,
            pady=(8, 0) if compact else 0)
        self.client_params_frame.grid_configure(
            row=4 if compact else 0, column=0 if compact else 2,
            columnspan=2 if compact else 1, rowspan=1 if compact else 4,
            pady=(12, 0) if compact else 0)
        self.client_config_frame.columnconfigure(2, weight=0 if compact else 1)
        for index, button in enumerate((self.btn_start, self.btn_stop, self.btn_clear)):
            button.grid_configure(row=index if compact else 0,
                                  column=0 if compact else index,
                                  columnspan=3 if compact else 1,
                                  padx=0 if compact else 5, pady=3 if compact else 0)
        self.server_button.grid_configure(row=1 if compact else 0,
                                          column=0 if compact else 2,
                                          columnspan=4 if compact else 1,
                                          padx=0 if compact else (20, 0),
                                          pady=(10, 0) if compact else 0)
        self.server_clear_button.grid_configure(row=2 if compact else 0,
                                                column=0 if compact else 3,
                                                columnspan=4 if compact else 1,
                                                padx=0 if compact else (10, 0),
                                                pady=(8, 0) if compact else 0)
        self.ax.set_title("Largura de banda (Mbps)" if compact else
                          "Comparativo de Largura de Banda (Mbps)",
                          color="#f8f8f2", weight="bold", fontsize=11)
        self.server_ax.set_title("Servidor — Banda (Mbps)" if compact else
                                 "Largura de Banda do Servidor (Mbps)",
                                 color="#f8f8f2", weight="bold", fontsize=11)
        self.canvas.draw_idle()
        self.server_canvas.draw_idle()

    def verificar_atualizacoes(self, automatico=False):
        if self.update_busy:
            return
        if self.pending_update is not None:
            self._oferecer_atualizacao()
            return
        self.update_busy = True
        self.update_button.configure(state="disabled")
        self.update_status.configure(text="Verificando atualizações...")
        threading.Thread(target=self._baixar_atualizacao, args=(automatico,), daemon=True).start()

    def _baixar_atualizacao(self, automatico):
        try:
            original = self.script_path.read_bytes()
            request = urllib.request.Request(UPDATE_URL, headers={
                "User-Agent": "IperfGui", "Cache-Control": "no-cache"})
            with urllib.request.urlopen(request, timeout=10) as response:
                content = response.read(2 * 1024 * 1024 + 1)
            if len(content) > 2 * 1024 * 1024:
                raise ValueError("O arquivo de atualização excede o tamanho permitido.")
            version = versao_do_script(content)
            if version <= APP_VERSION:
                self.update_events.put(("current", automatico))
                return
            compile(content, str(self.script_path), "exec")
            self.update_events.put(("available", (version, content, original)))
        except Exception as exc:
            self.update_events.put(("error", (automatico, str(exc))))

    def _processar_atualizacoes(self):
        try:
            kind, value = self.update_events.get_nowait()
        except queue.Empty:
            pass
        else:
            self.update_busy = False
            self.update_button.configure(state="normal")
            if kind == "available":
                self.pending_update = value
                self.update_button.configure(text="Atualizar e reiniciar")
                self.update_status.configure(text="Nova versão: " + ".".join(map(str, value[0])))
                if not self._teste_ativo():
                    self._oferecer_atualizacao()
            elif kind == "current":
                self.update_status.configure(text="Versão " + ".".join(map(str, APP_VERSION)) + " — atualizada")
                if not value:
                    messagebox.showinfo("Atualizações", "Você já está na versão mais recente.", parent=self)
            else:
                automatico, error = value
                self.update_status.configure(text="Não foi possível verificar atualizações.")
                if not automatico:
                    messagebox.showerror("Atualizações", error, parent=self)
        self.after(100, self._processar_atualizacoes)

    def _teste_ativo(self):
        return (self.server_running or self.btn_start.cget("state") == "disabled"
                or (self.process is not None and self.process.poll() is None))

    def _oferecer_atualizacao(self):
        if self._teste_ativo():
            messagebox.showinfo("Atualizações", "Pare o teste e o servidor antes de atualizar.", parent=self)
            return
        version, content, original = self.pending_update
        version_text = ".".join(map(str, version))
        if not messagebox.askyesno(
                "Atualização disponível",
                f"Instalar a versão {version_text} do GitHub e reiniciar?\n\n"
                "O script atual será guardado em iperf3gui.py.bak.\n"
                "Seu histórico de IPs será preservado.", parent=self):
            return
        # A caixa de diálogo processa eventos; confirme novamente antes da troca.
        if self._teste_ativo():
            messagebox.showinfo("Atualizações", "Pare o teste e o servidor antes de atualizar.", parent=self)
            return
        installed = False
        try:
            if self.script_path.read_bytes() != original:
                self.pending_update = None
                self.update_button.configure(text="Verificar atualizações")
                raise RuntimeError("O script foi alterado desde a consulta. Verifique as atualizações novamente.")
            mode = self.script_path.stat().st_mode & 0o777
            backup = self.script_path.with_suffix(self.script_path.suffix + ".bak")
            gravar_script_atomico(backup, original, mode)
            gravar_script_atomico(self.script_path, content, mode)
            installed = True
            os.execv(sys.executable, [sys.executable, str(self.script_path), *sys.argv[1:]])
        except Exception as exc:
            error = str(exc)
            if installed:
                try:
                    gravar_script_atomico(self.script_path, original, mode)
                except OSError as rollback_error:
                    error += f"\nRestaure o arquivo .bak manualmente: {rollback_error}"
            messagebox.showerror("Não foi possível atualizar", error, parent=self)

    def _caminho_historico_ips(self):
        if sys.platform == "win32":
            base = Path(os.environ.get("APPDATA") or Path.home() / "AppData" / "Roaming")
        else:
            base = Path(os.environ.get("XDG_CONFIG_HOME") or Path.home() / ".config")
        return base / "IperfGui" / "historico_ips.json"

    def _carregar_historico_ips(self):
        try:
            dados = json.loads(self._caminho_historico_ips().read_text(encoding="utf-8"))
            if not isinstance(dados, list):
                return []
            return list(dict.fromkeys(ip.strip() for ip in dados
                                      if isinstance(ip, str) and ip.strip()))[:30]
        except (OSError, ValueError):
            return []

    def _opcoes_ip(self):
        return ["200.152.98.6"] + [ip for ip in self.historico_ips if ip != "200.152.98.6"]

    def _memorizar_ip(self, ip):
        self.historico_ips = [ip] + [host for host in self.historico_ips if host != ip]
        self.historico_ips = self.historico_ips[:30]
        self.entry_ip.configure(values=self._opcoes_ip())
        self.entry_ip.set(ip)
        caminho = self._caminho_historico_ips()
        temporario = None
        try:
            caminho.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=caminho.parent,
                                             delete=False) as arquivo:
                temporario = Path(arquivo.name)
                json.dump(self.historico_ips, arquivo, ensure_ascii=False, indent=2)
            temporario.replace(caminho)
        except OSError:
            self.log("[AVISO] Não foi possível salvar o histórico de IPs neste computador.")
        finally:
            if temporario is not None:
                try:
                    temporario.unlink(missing_ok=True)
                except OSError:
                    pass

    def criar_interface(self):
        update_bar = ctk.CTkFrame(self, fg_color="transparent")
        update_bar.pack(fill="x", padx=20, pady=(10, 0))
        self.update_status = ctk.CTkLabel(
            update_bar, text="Versão " + ".".join(map(str, APP_VERSION)), wraplength=210)
        self.update_status.pack(side="left")
        self.update_button = ctk.CTkButton(
            update_bar, text="Verificar atualizações", command=self.verificar_atualizacoes)
        self.update_button.pack(side="right")
        self.tabs = ctk.CTkTabview(self, fg_color="#282a36", anchor="nw")
        self.tabs.pack(fill="both", expand=True, padx=16, pady=(8, 16))
        client_tab = self.tabs.add("Modo cliente")
        server_tab = self.tabs.add("Modo servidor")
        # A rolagem preserva a altura dos controles em telas pequenas ou com escala alta.
        self.main_frame = ctk.CTkScrollableFrame(client_tab, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True)
        self.server_frame = ctk.CTkScrollableFrame(server_tab, fg_color="transparent")
        self.server_frame.pack(fill="both", expand=True)
        
        # Define 2 colunas principais simétricas para o topo
        self.main_frame.columnconfigure(0, weight=1)
        self.main_frame.columnconfigure(1, weight=1)

        # --- Dados do Servidor ---
        label_server = ctk.CTkLabel(self.main_frame, text="Dados do Servidor:", font=ctk.CTkFont(size=14, weight="bold"))
        label_server.grid(row=0, column=0, sticky="w", padx=20, pady=(8, 5))

        server_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.client_address_frame = server_frame
        server_frame.grid(row=1, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))

        ctk.CTkLabel(server_frame, text="IP/Host:").grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.entry_ip = ctk.CTkComboBox(server_frame, values=self._opcoes_ip(),
                                             state="normal", width=220, border_color="#44475a")
        self.entry_ip.grid(row=0, column=1, sticky="w")
        self.entry_ip.set(self.historico_ips[0] if self.historico_ips else "200.152.98.6")

        ctk.CTkLabel(server_frame, text="Porta:").grid(row=0, column=2, sticky="w", padx=(30, 8))
        self.entry_port = ctk.CTkEntry(server_frame, width=80, border_color="#44475a")
        self.entry_port.grid(row=0, column=3, sticky="w")
        self.entry_port.insert(0, "5201")

        # --- Separador ---
        ctk.CTkFrame(self.main_frame, height=1, fg_color="#44475a").grid(row=2, column=0, columnspan=2, sticky="ew", padx=20, pady=4)

        # --- Configurações do Teste ---
        label_config = ctk.CTkLabel(self.main_frame, text="Configurações do Teste:", font=ctk.CTkFont(size=14, weight="bold"))
        label_config.grid(row=3, column=0, columnspan=2, sticky="w", padx=20, pady=(0, 5))

        config_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.client_config_frame = config_frame
        config_frame.grid(row=4, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 10))
        
        # Proporção simétrica perfeita para as 3 colunas de configuração
        config_frame.columnconfigure(0, weight=1)
        config_frame.columnconfigure(1, weight=1)
        config_frame.columnconfigure(2, weight=1)
        
        # Col 0: Protocolo
        ctk.CTkLabel(config_frame, text="Protocolo:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#bd93f9").grid(row=0, column=0, sticky="w", pady=(0, 6))
        ctk.CTkRadioButton(config_frame, text="TCP", variable=self.protocol_var, value="TCP").grid(row=1, column=0, sticky="w", pady=4)
        ctk.CTkRadioButton(config_frame, text="UDP", variable=self.protocol_var, value="UDP").grid(row=2, column=0, sticky="w", pady=4)

        # Col 1: Direção
        ctk.CTkLabel(config_frame, text="Direção:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#bd93f9").grid(row=0, column=1, sticky="w", pady=(0, 6))
        ctk.CTkRadioButton(config_frame, text="Upload", variable=self.direction_var, value="Upload").grid(row=1, column=1, sticky="w", pady=4)
        ctk.CTkRadioButton(config_frame, text="Download", variable=self.direction_var, value="Download").grid(row=2, column=1, sticky="w", pady=4)
        ctk.CTkRadioButton(config_frame, text="Ambos", variable=self.direction_var, value="Ambos").grid(row=3, column=1, sticky="w", pady=4)

        # Col 2: Parâmetros
        params_frame = ctk.CTkFrame(config_frame, fg_color="transparent")
        self.client_params_frame = params_frame
        params_frame.grid(row=0, column=2, rowspan=4, sticky="nw")
        ctk.CTkLabel(params_frame, text="Parâmetros:", font=ctk.CTkFont(size=12, weight="bold"), text_color="#bd93f9").grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 6))
        
        ctk.CTkLabel(params_frame, text="Threads (-P):").grid(row=1, column=0, sticky="w", pady=6, padx=(0, 8))
        self.entry_threads = ctk.CTkEntry(params_frame, width=65, border_color="#44475a")
        self.entry_threads.grid(row=1, column=1, sticky="w", pady=4)
        self.entry_threads.insert(0, "1")

        ctk.CTkLabel(params_frame, text="Tempo (seg):").grid(row=2, column=0, sticky="w", pady=6, padx=(0, 8))
        self.entry_time = ctk.CTkEntry(params_frame, width=65, border_color="#44475a")
        self.entry_time.grid(row=2, column=1, sticky="w", pady=4)
        self.entry_time.insert(0, "10")

        ctk.CTkLabel(params_frame, text="Banda UDP:").grid(row=3, column=0, sticky="w", pady=6, padx=(0, 8))
        self.combo_bandwidth = ctk.CTkComboBox(
            params_frame,
            width=100,
            variable=self.bandwidth_var,
            state="disabled",
            values=["10M","50M","100M","200M","300M","400M","500M","600M","700M","800M","900M","1000M"]
        )
        self.combo_bandwidth.grid(row=3, column=1, sticky="w", pady=4)

        # --- Separador e Status ---
        ctk.CTkFrame(self.main_frame, height=1, fg_color="#44475a").grid(row=5, column=0, columnspan=2, sticky="ew", padx=20, pady=4)
        self.status_label = ctk.CTkLabel(self.main_frame, text="Pressione ENTER para iniciar.", text_color="#f8f8f2")
        self.status_label.grid(row=6, column=0, columnspan=2, pady=(0, 10))

        # --- Botões de Ação ---
        btn_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        btn_frame.grid(row=7, column=0, columnspan=2, sticky="ew", padx=20, pady=(0, 8))
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
        self.fig, self.ax = plt.subplots(figsize=(6, 2.6), dpi=100, constrained_layout=True)
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
        self.canvas.get_tk_widget().configure(height=260, width=1)
        self.canvas.get_tk_widget().grid(row=8, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 10))

        # --- Console ---
        self.console = ctk.CTkTextbox(self.main_frame, height=150, fg_color="#191a21", text_color="#f8f8f2", wrap="none")
        self.console.grid(row=9, column=0, columnspan=2, sticky="nsew", padx=20, pady=(0, 20))
        
        # PESOS DINÂMICOS: Garante que o Gráfico e a Consola expandem de forma equilibrada
        # Gráfico recebe peso 3 (ligeiramente maior), Consola recebe peso 2
        self.main_frame.rowconfigure(8, weight=3, minsize=270)
        self.main_frame.rowconfigure(9, weight=2, minsize=170)



    def criar_interface_servidor(self):
        frame = self.server_frame
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(3, weight=3, minsize=320)
        frame.rowconfigure(4, weight=2, minsize=220)
        ctk.CTkLabel(frame, text="Servidor iPerf3", font=ctk.CTkFont(size=16, weight="bold")).grid(
            row=0, column=0, sticky="w", padx=20, pady=(8, 10))
        controls = ctk.CTkFrame(frame, fg_color="transparent")
        self.server_controls = controls
        controls.grid(row=1, column=0, sticky="ew", padx=20, pady=10)
        controls.columnconfigure(2, weight=1)
        ctk.CTkLabel(controls, text="Porta:").grid(row=0, column=0, padx=(0, 8))
        self.server_port = ctk.CTkEntry(controls, width=80, border_color="#44475a")
        self.server_port.grid(row=0, column=1)
        self.server_port.insert(0, "5201")
        self.server_button = ctk.CTkButton(
            controls, text="▶ INICIAR SERVIDOR", height=42,
            fg_color="#1b8f36", hover_color="#146c29", command=self.alternar_servidor)
        self.server_button.grid(row=0, column=2, sticky="ew", padx=(20, 0))
        self.server_clear_button = ctk.CTkButton(
            controls, text="🧹 LIMPAR GRÁFICO", height=42,
            fg_color="#44475a", hover_color="#6272a4", command=self.limpar_grafico_servidor)
        self.server_clear_button.grid(row=0, column=3, sticky="ew", padx=(10, 0))
        self.server_status = ctk.CTkLabel(frame, text="Servidor parado.")
        self.server_status.grid(row=2, column=0, pady=10)
        self.server_fig, self.server_ax = plt.subplots(figsize=(6, 2.6), dpi=100, constrained_layout=True)
        self.server_fig.patch.set_facecolor("#282a36")
        self.server_ax.set_facecolor("#191a21")
        self.server_ax.tick_params(colors="#f8f8f2", labelsize=9)
        self.server_ax.set_title("Largura de Banda do Servidor (Mbps)", color="#f8f8f2", weight="bold")
        self.server_ax.set_xlabel("Tempo do teste (segundos)", color="#f8f8f2")
        self.server_ax.set_ylabel("Velocidade (Mbps)", color="#f8f8f2")
        self.server_ax.grid(True, color="#44475a", linestyle="--", alpha=0.3)
        for spine in self.server_ax.spines.values():
            spine.set_color("#44475a")
        self.server_canvas = FigureCanvasTkAgg(self.server_fig, master=frame)
        self.server_canvas.get_tk_widget().configure(height=300, width=1)
        self.server_canvas.get_tk_widget().grid(row=3, column=0, sticky="nsew", padx=20, pady=10)
        self.server_console = ctk.CTkTextbox(frame, height=200, fg_color="#191a21", text_color="#f8f8f2", wrap="none")
        self.server_console.grid(row=4, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self._log_servidor("> Seu IP local: identificando...")
        self._log_servidor("> Seu IP público: consultando...")
        threading.Thread(target=self._identificar_ip, daemon=True).start()
        threading.Thread(target=self._identificar_ip_publico, daemon=True).start()

    def limpar_grafico_servidor(self):
        self.server_samples = {}
        self.server_series = {}
        for line in list(self.server_ax.lines):
            line.remove()
        legend = self.server_ax.get_legend()
        if legend is not None:
            legend.remove()
        self.server_ax.relim()
        self.server_ax.set_xlim(0, 1)
        self.server_ax.set_ylim(0, 1)
        self.server_ax.set_autoscale_on(True)
        self.server_canvas.draw_idle()

    def _identificar_ip(self):
        addresses = set()
        try:
            # UDP connect seleciona a interface de saída sem enviar pacotes.
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("192.0.2.1", 80))
                addresses.add(sock.getsockname()[0])
        except OSError:
            pass
        try:
            addresses.update(socket.gethostbyname_ex(socket.gethostname())[2])
        except OSError:
            pass
        addresses = sorted(ip for ip in addresses if not ip.startswith("127."))
        self.server_events.put(("ip", ", ".join(addresses) or "127.0.0.1 (somente acesso local)"))

    def _identificar_ip_publico(self):
        try:
            with urllib.request.urlopen("https://api.ipify.org", timeout=5) as response:
                address = str(ipaddress.ip_address(response.read(128).decode("ascii").strip()))
        except (OSError, ValueError, UnicodeError, urllib.error.URLError):
            address = "indisponível (verifique a conexão com a internet)"
        self.server_events.put(("public_ip", address))

    def _log_servidor(self, message):
        self.server_console.configure(state="normal")
        self.server_console.insert("end", message + "\n")
        self.server_console.see("end")
        self.server_console.configure(state="disabled")

    def alternar_servidor(self):
        if self.server_running:
            self.server_stop.set()
            self.server_button.configure(state="disabled")
            self.server_status.configure(text="Parando servidor...")
            threading.Thread(target=self._parar_processo_servidor, daemon=True).start()
            return
        port = self.server_port.get().strip()
        if not port.isascii() or not port.isdigit() or not 1 <= int(port) <= 65535:
            self._log_servidor("[ERRO] Informe uma porta entre 1 e 65535.")
            return
        self.server_running = True
        self.server_stop.clear()
        self.server_port.configure(state="disabled")
        self.server_button.configure(text="■ PARAR SERVIDOR", fg_color="#ff5555", hover_color="#cc2222")
        self.server_status.configure(text=f"Iniciando servidor na porta {port}...")
        threading.Thread(target=self._executar_servidor, args=(port,), daemon=True).start()

    def _executar_servidor(self, port):
        cmd = ["iperf3", "-s", "-p", port, "-i", "1", "--forceflush"]
        self.server_events.put(("log", "> Comando: " + " ".join(cmd)))
        try:
            kwargs = dict(stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                          text=True, bufsize=1, errors="replace")
            if sys.platform == "win32":
                kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
            process = subprocess.Popen(cmd, **kwargs)
            self.server_process = process
            if self.server_stop.is_set():
                self._parar_processo_servidor()
            with process.stdout:
                for line in process.stdout:
                    self.server_events.put(("line", line.strip()))
            code = process.wait()
            if code and not self.server_stop.is_set():
                self.server_events.put(("log", f"[ERRO] Servidor encerrado com código {code}."))
        except FileNotFoundError:
            self.server_events.put(("log", "[ERRO] O executável 'iperf3' não foi encontrado."))
        except Exception as exc:
            self.server_events.put(("log", f"[ERRO] {exc}"))
        finally:
            self.server_process = None
            self.server_events.put(("done", None))

    def _parar_processo_servidor(self):
        process = self.server_process
        if process and process.poll() is None:
            try:
                process.terminate()
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            except OSError:
                pass

    def _processar_eventos_servidor(self):
        for _ in range(300):
            try:
                kind, value = self.server_events.get_nowait()
            except queue.Empty:
                break
            if kind in ("ip", "public_ip"):
                row, label = (1, "local") if kind == "ip" else (2, "público")
                self.server_console.configure(state="normal")
                self.server_console.delete(f"{row}.0", f"{row + 1}.0")
                self.server_console.insert(f"{row}.0", f"> Seu IP {label}: {value}\n")
                self.server_console.configure(state="disabled")
            elif kind == "done":
                self.server_running = False
                self.server_port.configure(state="normal")
                self.server_button.configure(state="normal", text="▶ INICIAR SERVIDOR",
                                             fg_color="#1b8f36", hover_color="#146c29")
                self.server_status.configure(text="Servidor parado.")
                self._log_servidor("> Servidor parado.")
            else:
                self._log_servidor(value)
                if kind == "line":
                    if "Server listening on" in value:
                        self.server_status.configure(text=value)
                    if "Accepted connection" in value:
                        self.server_session += 1
                        self.server_samples = {}
                        self.server_series = {}
                        self.server_status.configure(text="Cliente conectado. Teste em execução.")
                    self._atualizar_grafico_servidor(value)
        self.after(100, self._processar_eventos_servidor)

    def _atualizar_grafico_servidor(self, line):
        if "sender" in line or "receiver" in line:
            return
        match = re.search(
            r"\[\s*(\d+|SUM)\]\s*(?:\[(TX|RX)[^\]]*\])?\s*"
            r"(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)\s+sec\s+"
            r"[\d.]+\s+\S+\s+([\d.]+)\s+([KMGT]?)bits/sec", line)
        if not match:
            return
        stream, direction, start, end, rate, unit = match.groups()
        start, end = float(start), float(end)
        if end <= start:
            return
        direction = direction or "Total"
        samples = self.server_samples.setdefault(direction, {})
        # Totais finais sem rótulo não devem sobrescrever os intervalos.
        if start == 0 and any(t < end for t in samples):
            return
        interval = samples.setdefault(end, {})
        interval[stream] = float(rate) * {"": 0.000001, "K": 0.001, "M": 1, "G": 1000, "T": 1000000}[unit]
        if direction not in self.server_series:
            color = self.cores_grafico[len(self.server_ax.lines) % len(self.cores_grafico)]
            curve, = self.server_ax.plot([], [], color=color, linewidth=2,
                                        label=f"Teste #{self.server_session} ({direction})")
            self.server_series[direction] = curve
            legend = self.server_ax.legend(facecolor="#191a21", edgecolor="#44475a", fontsize=8)
            for label in legend.get_texts():
                label.set_color("#f8f8f2")
        times = sorted(samples)
        rates = [samples[t].get("SUM", sum(v for k, v in samples[t].items() if k != "SUM")) for t in times]
        self.server_series[direction].set_data(times, rates)
        self.server_ax.relim()
        self.server_ax.autoscale_view()
        self.server_canvas.draw_idle()

    def _fechar(self):
        self.server_stop.set()
        self._parar_processo_servidor()
        if self.process and self.process.poll() is None:
            self.process.terminate()
        plt.close(self.fig)
        plt.close(self.server_fig)
        self.destroy()

    def atualizar_controles_udp(self, *args):
        if self.protocol_var.get() == "UDP":
            self.combo_bandwidth.configure(state="normal")
        else:
            self.combo_bandwidth.configure(state="disabled")

    def _carregar_logo(self):
        with Image.open(BytesIO(base64.b64decode(MLS_LOGO_BASE64))) as source:
            img = source.convert("RGBA")
        self._logo_img = ctk.CTkImage(
            light_image=img, dark_image=img, size=(130, 50))
        self.client_logo = ctk.CTkLabel(
            self.main_frame, image=self._logo_img, text="", fg_color="transparent")
        self.client_logo.grid(row=0, column=1, sticky="e", padx=20, pady=(8, 5))
        self.server_logo = ctk.CTkLabel(
            self.server_frame, image=self._logo_img, text="", fg_color="transparent")
        self.server_logo.grid(row=0, column=0, sticky="e", padx=20, pady=(8, 10))

    def _atalho_enter(self, event):
        if self.tabs.get() == "Modo servidor":
            self.alternar_servidor()
            return
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
        self.ax.set_title("Largura de banda (Mbps)" if self._compact_layout else "Comparativo de Largura de Banda (Mbps)", color='#f8f8f2', weight='bold', fontsize=11)
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

        self._memorizar_ip(ip)
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
