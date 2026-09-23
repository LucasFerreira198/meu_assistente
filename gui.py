import customtkinter as ctk
import tkinter as tk
import math
import time
import os

# Configuração do Tema Global (Estilo HUD / JARVIS / Cyber)
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class FloatingAssistant(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("A.R.E.S. // J.A.R.V.I.S. HUD Interface")
        self.geometry("1100x650+50+50")
        self.minsize(950, 550)

        # Paleta de Cores Estilo Stark HUD / JARVIS
        self.bg_color = "#05080F"         # Preto / Azul ultra profundo
        self.panel_color = "#0B0F19"      # Painel fosco com contraste
        self.border_color = "#00D2FF"     # Neon Ciano brilhante
        self.accent_color = "#00F0FF"     # Ciano elétrico
        self.text_main = "#E2E8F0"        # Branco gelo
        self.text_dim = "#94A3B8"         # Cinza azulado

        self.configure(fg_color=self.bg_color)

        self.ai_state = "listening"
        self.hud_mode = "arc_reactor"
        self.time_step = 0
        self.cached_agents_info = []

        # ================= TOP HEADER (BARRA SUPERIOR JARVIS) =================
        self.setup_top_header()

        # ================= CONTAINER PRINCIPAL (3 COLUNAS) =================
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=12, pady=(0, 10))

        self.main_container.grid_columnconfigure(0, weight=1) # Esquerda (Stats)
        self.main_container.grid_columnconfigure(1, weight=2) # Centro (Arc Reactor)
        self.main_container.grid_columnconfigure(2, weight=2) # Direita (Conversa/Terminal/Agentes)
        self.main_container.grid_rowconfigure(0, weight=1)

        # ================= COLUNA 1: ESQUERDA (SYSTEM STATS, WEATHER, APPS) =================
        self.setup_left_panel()

        # ================= COLUNA 2: CENTRO (ARC-REACTOR HOLOGRAPHIC CORE) =================
        self.setup_center_panel()

        # ================= COLUNA 3: DIREITA (CHAT / TERMINAL / SUB-AGENTES) =================
        self.setup_right_panel()

        # Inicializa lista de agentes vazia
        self.update_agents_list([])

        # Inicia loop de animação contínua do Reator Arc
        self.update()
        self.animate()

    def setup_top_header(self):
        """Cabeçalho superior com título, status da IA, relógio e alternador de HUD."""
        self.header_frame = ctk.CTkFrame(self, fg_color=self.panel_color, corner_radius=6, height=50, border_width=1, border_color=self.border_color)
        self.header_frame.pack(fill="x", padx=12, pady=10)

        # Título
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="A.R.E.S. // J.A.R.V.I.S.", 
            font=("Consolas", 18, "bold"), 
            text_color=self.accent_color
        )
        self.title_label.pack(side="left", padx=15, pady=8)

        # Badge de Estado da IA
        self.status_badge = ctk.CTkFrame(self.header_frame, fg_color="#064E3B", corner_radius=12, height=28)
        self.status_badge.pack(side="left", padx=10, pady=8)
        self.status_label = ctk.CTkLabel(self.status_badge, text="● Online - Escutando", font=("Helvetica", 11, "bold"), text_color="#34D399")
        self.status_label.pack(padx=12, pady=2)

        # Botão seletor de modo HUD
        self.btn_hud_mode = ctk.CTkButton(
            self.header_frame,
            text="⚡ HUD Arc",
            width=90,
            height=26,
            font=("Consolas", 10, "bold"),
            fg_color="#1E293B",
            hover_color="#334155",
            border_width=1,
            border_color="#38BDF8",
            command=self.toggle_hud_mode
        )
        self.btn_hud_mode.pack(side="right", padx=15, pady=8)

        # Relógio HUD
        self.clock_label = ctk.CTkLabel(
            self.header_frame, 
            text="", 
            font=("Consolas", 13, "bold"), 
            text_color=self.border_color
        )
        self.clock_label.pack(side="right", padx=15, pady=8)
        self.update_clock()

    def update_clock(self):
        current_time = time.strftime("%H:%M:%S")
        self.clock_label.configure(text=f"TIME: {current_time}")
        self.after(1000, self.update_clock)

    def setup_left_panel(self):
        self.left_panel = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=6, pady=5)
        self.left_panel.grid_rowconfigure(0, weight=0)
        self.left_panel.grid_rowconfigure(1, weight=0)
        self.left_panel.grid_rowconfigure(2, weight=1)
        self.left_panel.grid_columnconfigure(0, weight=1)

        # Card 1: System Stats
        self.sys_card = ctk.CTkFrame(self.left_panel, fg_color=self.panel_color, corner_radius=6, border_width=1, border_color=self.border_color)
        self.sys_card.grid(row=0, column=0, sticky="nsew", pady=(0, 10))

        ctk.CTkLabel(self.sys_card, text="SYSTEM // RT-MONITOR", font=("Consolas", 12, "bold"), text_color=self.accent_color).pack(anchor="w", padx=15, pady=(12, 6))

        self.lbl_cpu = ctk.CTkLabel(self.sys_card, text="CPU Usage: 0%", font=("Consolas", 11), text_color=self.text_main)
        self.lbl_cpu.pack(anchor="w", padx=15)
        self.progress_cpu = ctk.CTkProgressBar(self.sys_card, height=4, progress_color=self.border_color, fg_color="#1E293B")
        self.progress_cpu.pack(fill="x", padx=15, pady=(2, 8))
        self.progress_cpu.set(0)

        self.lbl_ram = ctk.CTkLabel(self.sys_card, text="RAM Usage: 0 GB", font=("Consolas", 11), text_color=self.text_main)
        self.lbl_ram.pack(anchor="w", padx=15)
        self.progress_ram = ctk.CTkProgressBar(self.sys_card, height=4, progress_color=self.border_color, fg_color="#1E293B")
        self.progress_ram.pack(fill="x", padx=15, pady=(2, 12))
        self.progress_ram.set(0)

        # Card 2: Clima / Weather
        self.weather_card = ctk.CTkFrame(self.left_panel, fg_color=self.panel_color, corner_radius=6, border_width=1, border_color=self.border_color)
        self.weather_card.grid(row=1, column=0, sticky="nsew", pady=(0, 10))

        ctk.CTkLabel(self.weather_card, text="SYSTEM // ATMOSPHERE", font=("Consolas", 12, "bold"), text_color=self.accent_color).pack(anchor="w", padx=15, pady=(12, 4))
        self.lbl_temp = ctk.CTkLabel(self.weather_card, text="--°C", font=("Helvetica", 24, "bold"), text_color=self.text_main)
        self.lbl_temp.pack(anchor="w", padx=15)
        self.lbl_weather_desc = ctk.CTkLabel(self.weather_card, text="--", font=("Helvetica", 11), text_color=self.text_dim)
        self.lbl_weather_desc.pack(anchor="w", padx=15, pady=(0, 12))

        # Card 3: Apps Abertos
        self.apps_card = ctk.CTkFrame(self.left_panel, fg_color=self.panel_color, corner_radius=6, border_width=1, border_color=self.border_color)
        self.apps_card.grid(row=2, column=0, sticky="nsew")

        ctk.CTkLabel(self.apps_card, text="SYSTEM // ACTIVE APPS", font=("Consolas", 12, "bold"), text_color=self.accent_color).pack(anchor="w", padx=15, pady=(12, 4))
        self.apps_label = ctk.CTkLabel(self.apps_card, text="--", font=("Courier", 10), justify="left", text_color="#34D399")
        self.apps_label.pack(anchor="nw", padx=15, pady=4)

    def setup_center_panel(self):
        self.center_panel = ctk.CTkFrame(self.main_container, fg_color=self.panel_color, corner_radius=6, border_width=1, border_color=self.border_color)
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=6, pady=5)
        self.center_panel.grid_rowconfigure(1, weight=1)
        self.center_panel.grid_columnconfigure(0, weight=1)

        self.center_title = ctk.CTkLabel(self.center_panel, text="CORE // ARC-REACTOR HUD", font=("Consolas", 13, "bold"), text_color=self.accent_color)
        self.center_title.grid(row=0, column=0, pady=(12, 4))

        self.canvas = tk.Canvas(self.center_panel, bg=self.panel_color, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

    def setup_right_panel(self):
        self.right_panel = ctk.CTkFrame(self.main_container, fg_color=self.panel_color, corner_radius=6, border_width=1, border_color=self.border_color)
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=6, pady=5)

        self.right_header = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.right_header.pack(fill="x", padx=15, pady=(12, 8))

        self.lbl_right_title = ctk.CTkLabel(self.right_header, text="Log de Conversa", font=("Consolas", 13, "bold"), text_color=self.text_main)
        self.lbl_right_title.pack(anchor="w")

        # 3 Abas Modernas (SegmentedButton)
        self.view_selector = ctk.CTkSegmentedButton(
            self.right_header,
            values=["Conversa", "Terminal", "Sub-Agentes"],
            command=self.switch_view,
            selected_color="#0284C7",
            selected_hover_color="#0369A1",
            unselected_color="#1E293B",
            unselected_hover_color="#334155",
            font=("Helvetica", 10, "bold")
        )
        self.view_selector.set("Conversa")
        self.view_selector.pack(fill="x", pady=(8, 0))

        # View 1: Chat Box (Padrão)
        self.chat_box = ctk.CTkTextbox(self.right_panel, fg_color="#05080F", text_color=self.text_main, font=("Consolas", 11), wrap="word", border_width=1, border_color="#1E293B")
        self.chat_box.pack(expand=True, fill="both", padx=15, pady=(0, 10))
        self.chat_box.configure(state="disabled")

        # View 2: Terminal Box (Oculta por padrão)
        self.terminal_box = ctk.CTkTextbox(self.right_panel, fg_color="#000000", text_color="#22C55E", font=("Courier", 11), wrap="word", border_width=1, border_color="#1E293B")
        self.terminal_box.configure(state="disabled")

        # View 3: Sub-Agentes Frame (Oculta por padrão)
        self.agents_frame = ctk.CTkScrollableFrame(self.right_panel, fg_color="#05080F", border_width=1, border_color="#1E293B")

        # Botão de Interromper Fala
        self.btn_interrupt = ctk.CTkButton(self.right_panel, text="🛑 Interromper e Ouvir", font=("Helvetica", 11, "bold"), fg_color="#7F1D1D", hover_color="#991B1B", command=self.on_interrupt)
        self.btn_interrupt.pack(fill="x", padx=15, pady=(0, 12))

        self.current_view = "Conversa"

    def switch_view(self, view_name: str):
        self.current_view = view_name
        self.view_selector.set(view_name)

        self.chat_box.pack_forget()
        self.terminal_box.pack_forget()
        self.agents_frame.pack_forget()
        self.btn_interrupt.pack_forget()

        if view_name == "Conversa":
            self.lbl_right_title.configure(text="Log de Conversa")
            self.chat_box.pack(expand=True, fill="both", padx=15, pady=(0, 10))
            self.btn_interrupt.pack(fill="x", padx=15, pady=(0, 12))
        elif view_name == "Terminal":
            self.lbl_right_title.configure(text="Terminal Hacker")
            self.terminal_box.pack(expand=True, fill="both", padx=15, pady=(0, 10))
            self.btn_interrupt.pack(fill="x", padx=15, pady=(0, 12))
        elif view_name == "Sub-Agentes":
            self.lbl_right_title.configure(text="Sub-Agentes Autônomos")
            self.agents_frame.pack(expand=True, fill="both", padx=15, pady=(0, 10))
            self.btn_interrupt.pack(fill="x", padx=15, pady=(0, 12))

    def toggle_view(self):
        if self.current_view == "Conversa":
            self.switch_view("Terminal")
        else:
            self.switch_view("Conversa")

    def update_agents_list(self, agents_info: list):
        self.cached_agents_info = agents_info
        for widget in self.agents_frame.winfo_children():
            widget.destroy()

        if not agents_info:
            empty_lbl = ctk.CTkLabel(
                self.agents_frame,
                text="Nenhum sub-agente ativo no momento.\n\nPeça ao ARES por voz:\n\"ARES, crie um sub-agente para [tarefa]\"",
                font=("Consolas", 11),
                text_color=self.text_dim,
                justify="center"
            )
            empty_lbl.pack(expand=True, pady=40)
            return

        for agent in agents_info:
            card = ctk.CTkFrame(self.agents_frame, fg_color="#0B0F19", corner_radius=6, border_width=1, border_color="#1E293B")
            card.pack(fill="x", padx=5, pady=6)

            hdr = ctk.CTkFrame(card, fg_color="transparent")
            hdr.pack(fill="x", padx=10, pady=(8, 4))

            lbl_name = ctk.CTkLabel(hdr, text=f"🤖 {agent.get('name', 'Agente')} ({agent.get('id', '')})", font=("Consolas", 11, "bold"), text_color=self.accent_color)
            lbl_name.pack(side="left")

            status = agent.get("status", "running")
            badge_colors = {
                "running": ("#064E3B", "#34D399", "● Rodando"),
                "completed": ("#1E3A8A", "#60A5FA", "✔ Concluído"),
                "error": ("#7F1D1D", "#F87171", "✖ Erro"),
                "stopped": ("#374151", "#9CA3AF", "■ Parado")
            }
            bg_col, text_col, status_text = badge_colors.get(status, ("#374151", "#9CA3AF", status))

            badge = ctk.CTkLabel(hdr, text=status_text, font=("Consolas", 9, "bold"), text_color=text_col, fg_color=bg_col, corner_radius=6, padx=8, pady=2)
            badge.pack(side="right")

            lbl_task = ctk.CTkLabel(card, text=f"Tarefa: {agent.get('task', '')}", font=("Helvetica", 10), text_color=self.text_main, wraplength=280, justify="left")
            lbl_task.pack(anchor="w", padx=10, pady=(2, 4))

            last_log = agent.get("last_log", "")
            if last_log:
                lbl_log = ctk.CTkLabel(card, text=last_log, font=("Courier", 9), text_color="#38BDF8", wraplength=280, justify="left")
                lbl_log.pack(anchor="w", padx=10, pady=(0, 6))

            footer = ctk.CTkFrame(card, fg_color="transparent")
            footer.pack(fill="x", padx=10, pady=(0, 8))

            time_str = f"Início: {agent.get('start', '')}"
            if agent.get('end'):
                time_str += f" | Fim: {agent.get('end')}"
            lbl_time = ctk.CTkLabel(footer, text=time_str, font=("Consolas", 9), text_color=self.text_dim)
            lbl_time.pack(side="left")

            if status == "running":
                btn_stop = ctk.CTkButton(
                    footer,
                    text="Parar",
                    width=55,
                    height=20,
                    font=("Helvetica", 9, "bold"),
                    fg_color="#7F1D1D",
                    hover_color="#991B1B",
                    command=lambda aid=agent.get('id'): self.on_stop_agent(aid)
                )
                btn_stop.pack(side="right")

    def on_stop_agent(self, agent_id: str):
        try:
            from core.agent_manager import agent_manager
            agent_manager.stop_agent(agent_id)
        except Exception as e:
            print(f"Erro ao parar agente {agent_id}: {e}")

    def on_interrupt(self):
        try:
            from core.tts import stop_speaking
            stop_speaking()
        except Exception:
            pass

    def change_state(self, event=None):
        if self.ai_state == "listening":
            self.status_badge.configure(fg_color="#064E3B")
            self.status_label.configure(text="● Online - Escutando", text_color="#34D399")
        elif self.ai_state == "thinking":
            self.status_badge.configure(fg_color="#78350F")
            self.status_label.configure(text="● Processando", text_color="#FBBF24")
        elif self.ai_state == "speaking":
            self.status_badge.configure(fg_color="#1E3A8A")
            self.status_label.configure(text="● Falando", text_color="#60A5FA")

    def toggle_hud_mode(self):
        if self.hud_mode == "arc_reactor":
            self.hud_mode = "robot_eyes"
            self.btn_hud_mode.configure(text="👁️ Olhos OLED")
        else:
            self.hud_mode = "arc_reactor"
            self.btn_hud_mode.configure(text="⚡ HUD Arc")

    def draw_arc_reactor(self, cx, cy, color_main, color_dim):
        r = min(cx, cy) - 22
        if r < 40:
            return

        angle_rot = (self.time_step * 2.5) % 360
        angle_counter = (360 - (self.time_step * 3.5) % 360)

        if self.ai_state == "thinking":
            angle_rot = (self.time_step * 7) % 360
            angle_counter = (360 - (self.time_step * 9) % 360)

        # 1. Anel externo com marcadores e ticks de bússola/radar
        self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline="#1E293B", width=1.5)
        
        num_ticks = 36
        for i in range(num_ticks):
            theta = math.radians(i * (360 / num_ticks))
            is_major = (i % 9 == 0)
            is_mid = (i % 3 == 0)
            tick_len = 10 if is_major else (6 if is_mid else 3)
            tx1 = cx + r * math.cos(theta)
            ty1 = cy + r * math.sin(theta)
            tx2 = cx + (r - tick_len) * math.cos(theta)
            ty2 = cy + (r - tick_len) * math.sin(theta)
            t_col = color_main if is_major else (color_dim if is_mid else "#1E293B")
            self.canvas.create_line(tx1, ty1, tx2, ty2, fill=t_col, width=2 if is_major else 1)

        # 2. Retículos e Mira Holográfica (Crosshairs)
        ch_len = r + 8
        self.canvas.create_line(cx - ch_len, cy, cx - r + 16, cy, fill="#334155", width=1)
        self.canvas.create_line(cx + r - 16, cy, cx + ch_len, cy, fill="#334155", width=1)
        self.canvas.create_line(cx, cy - ch_len, cx, cy - r + 16, fill="#334155", width=1)
        self.canvas.create_line(cx, cy + r - 16, cx, cy + ch_len, fill="#334155", width=1)

        # 3. Anel Primário - 3 Arcos grossos de energia giratórios
        r_mid = r * 0.76
        for i in range(3):
            arc_start = (angle_rot + i * 120) % 360
            self.canvas.create_arc(
                cx - r_mid, cy - r_mid, cx + r_mid, cy + r_mid,
                start=arc_start, extent=65, outline=color_main, width=3.5, style="arc"
            )

        # 4. Anel Secundário - 4 Arcos em contra-rotação
        r_inner_ring = r * 0.54
        for i in range(4):
            arc_start = (angle_counter + i * 90) % 360
            self.canvas.create_arc(
                cx - r_inner_ring, cy - r_inner_ring, cx + r_inner_ring, cy + r_inner_ring,
                start=arc_start, extent=45, outline=color_dim, width=2, style="arc"
            )

        # 5. Efeito sonoro / Shockwave quando falando
        if self.ai_state == "speaking":
            shock_r = (self.time_step * 4) % int(r_mid)
            if shock_r > 15:
                self.canvas.create_oval(
                    cx - shock_r, cy - shock_r, cx + shock_r, cy + shock_r,
                    outline=color_main, width=1.5
                )

        # 6. Núcleo de Energia (Arc Core) com Pulso
        pulse = math.sin(self.time_step * (0.35 if self.ai_state == "thinking" else 0.15)) * 4
        if self.ai_state == "speaking":
            pulse = math.sin(self.time_step * 0.8) * 7

        r_core = max(18, r * 0.28 + pulse)
        self.canvas.create_oval(cx - r_core, cy - r_core, cx + r_core, cy + r_core, outline=color_main, width=2)
        
        # Centro brilhante do reator
        r_center = max(8, r_core * 0.45)
        self.canvas.create_oval(cx - r_center, cy - r_center, cx + r_center, cy + r_center, fill=color_main, outline="")

        # 7. Telemetria Digital no HUD
        status_txt = "SYSTEM READY"
        if self.ai_state == "thinking":
            status_txt = "PROCESSING"
        elif self.ai_state == "speaking":
            status_txt = "AUDIO OUT"

        self.canvas.create_text(cx, cy + r * 0.42, text=status_txt, fill=color_main, font=("Consolas", 9, "bold"))
        self.canvas.create_text(cx, cy - r * 0.42, text="A.R.E.S. // ARC-II", fill="#64748B", font=("Courier", 8))

    def draw_eye(self, cx, cy, width, height, corner_radius, color):
        x1 = cx - width/2
        y1 = cy - height/2
        x2 = cx + width/2
        y2 = cy + height/2
        r = corner_radius
        
        self.canvas.create_oval(x1, y1, x1+2*r, y1+2*r, fill=color, outline="")
        self.canvas.create_oval(x2-2*r, y1, x2, y1+2*r, fill=color, outline="")
        self.canvas.create_oval(x1, y2-2*r, x1+2*r, y2, fill=color, outline="")
        self.canvas.create_oval(x2-2*r, y2-2*r, x2, y2, fill=color, outline="")
        
        self.canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=color, outline="")
        self.canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=color, outline="")

    def animate(self):
        self.canvas.delete("all")
        self.time_step += 1
        
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        cx, cy = w // 2, h // 2
        
        if cx > 40 and cy > 40:
            if self.ai_state == "thinking":
                color_main = "#F59E0B"
                color_dim = "#78350F"
            elif self.ai_state == "speaking":
                color_main = "#38BDF8"
                color_dim = "#818CF8"
            else:
                color_main = "#00F0FF"
                color_dim = "#0284C7"

            if self.hud_mode == "arc_reactor":
                self.draw_arc_reactor(cx, cy, color_main, color_dim)
            else:
                eye_w = 80
                eye_h = 100
                eye_gap = 60
                offset_y = 0
                
                if self.ai_state == "thinking":
                    eye_h = 40 + math.sin(self.time_step * 0.2) * 10
                    offset_x = math.cos(self.time_step * 0.1) * 20
                    cx += offset_x
                elif self.ai_state == "speaking":
                    eye_h = 90 + math.sin(self.time_step * 0.8) * 15
                else:
                    if self.time_step % 60 < 2:
                        eye_h = 10
                    else:
                        offset_y = math.sin(self.time_step * 0.05) * 5

                self.draw_eye(cx - (eye_w/2 + eye_gap/2), cy + offset_y, eye_w, eye_h, 20, color_main)
                self.draw_eye(cx + (eye_w/2 + eye_gap/2), cy + offset_y, eye_w, eye_h, 20, color_main)
                        
        self.after(50, self.animate)

# Alias para compatibilidade total com qualquer import
JarvisDashboard = FloatingAssistant

if __name__ == "__main__":
    app = FloatingAssistant()
    app.mainloop()
