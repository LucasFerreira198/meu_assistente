import customtkinter as ctk
import tkinter as tk
import math

class FloatingAssistant(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("C.Y.B.E.R - Assistant")
        self.geometry("950x550+100+100")
        self.minsize(800, 450) # Impede de esmagar a tela
        
        # Cores baseadas na Imagem 1 (Cyber Dashboard)
        self.bg_color = "#0B0F19"
        self.panel_color = "#111827"
        self.accent_color = "#00E5FF"
        self.text_main = "#E2E8F0"
        self.text_dim = "#94A3B8"
        
        self.configure(fg_color=self.bg_color)
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=2)
        self.grid_columnconfigure(2, weight=2)
        self.grid_rowconfigure(0, weight=1)
        
        # ================= ESQUERDA: SYSTEM STATS E APPS =================
        self.left_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.left_panel.grid(row=0, column=0, sticky="nsew", padx=15, pady=15)
        self.left_panel.grid_rowconfigure(0, weight=0)
        self.left_panel.grid_rowconfigure(1, weight=0)
        self.left_panel.grid_rowconfigure(2, weight=1) # Permite o painel de apps crescer
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        # Card 1: Saúde do Sistema
        self.sys_card = ctk.CTkFrame(self.left_panel, fg_color=self.panel_color, corner_radius=8, border_width=1, border_color="#1E293B")
        self.sys_card.grid(row=0, column=0, sticky="nsew", pady=(0, 15))
        
        ctk.CTkLabel(self.sys_card, text="⚙️ System Stats", font=("Helvetica", 14, "bold"), text_color=self.accent_color).pack(anchor="w", padx=15, pady=(15, 10))
        
        self.lbl_cpu = ctk.CTkLabel(self.sys_card, text="CPU Usage: 0%", font=("Helvetica", 12), text_color=self.text_main)
        self.lbl_cpu.pack(anchor="w", padx=15)
        self.progress_cpu = ctk.CTkProgressBar(self.sys_card, height=4, progress_color=self.accent_color, fg_color="#1E293B")
        self.progress_cpu.pack(fill="x", padx=15, pady=(2, 10))
        self.progress_cpu.set(0)
        
        self.lbl_ram = ctk.CTkLabel(self.sys_card, text="RAM Usage: 0 GB", font=("Helvetica", 12), text_color=self.text_main)
        self.lbl_ram.pack(anchor="w", padx=15)
        self.progress_ram = ctk.CTkProgressBar(self.sys_card, height=4, progress_color=self.accent_color, fg_color="#1E293B")
        self.progress_ram.pack(fill="x", padx=15, pady=(2, 15))
        self.progress_ram.set(0)
        
        # Card 2: Clima / Tempo
        self.weather_card = ctk.CTkFrame(self.left_panel, fg_color=self.panel_color, corner_radius=8, border_width=1, border_color="#1E293B")
        self.weather_card.grid(row=1, column=0, sticky="nsew", pady=(0, 15))
        
        ctk.CTkLabel(self.weather_card, text="☁️ Weather", font=("Helvetica", 14, "bold"), text_color=self.accent_color).pack(anchor="w", padx=15, pady=(15, 10))
        self.lbl_temp = ctk.CTkLabel(self.weather_card, text="--°C", font=("Helvetica", 28, "bold"), text_color=self.text_main)
        self.lbl_temp.pack(anchor="w", padx=15)
        self.lbl_weather_desc = ctk.CTkLabel(self.weather_card, text="--", font=("Helvetica", 12), text_color=self.text_dim)
        self.lbl_weather_desc.pack(anchor="w", padx=15, pady=(0, 15))

        # Card 3: Apps Abertos movido para a Esquerda
        self.apps_card = ctk.CTkFrame(self.left_panel, fg_color=self.panel_color, corner_radius=8, border_width=1, border_color="#1E293B")
        self.apps_card.grid(row=2, column=0, sticky="nsew")
        ctk.CTkLabel(self.apps_card, text="🟢 Apps Abertos", font=("Helvetica", 14, "bold"), text_color=self.accent_color).pack(anchor="w", padx=15, pady=(15, 5))
        self.apps_label = ctk.CTkLabel(self.apps_card, text="--", font=("Courier", 11), justify="left", text_color="#34D399")
        self.apps_label.pack(anchor="nw", padx=15, pady=5)

        # ================= CENTRO: RADAR ANIMADO =================
        self.center_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.center_panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=15)
        self.center_panel.grid_rowconfigure(1, weight=1)
        self.center_panel.grid_columnconfigure(0, weight=1)
        
        self.title_label = ctk.CTkLabel(self.center_panel, text="A. R. E. S.", font=("Helvetica", 22, "bold"), text_color=self.text_main)
        self.title_label.grid(row=0, column=0, pady=(0, 5))
        
        self.canvas = tk.Canvas(self.center_panel, bg=self.bg_color, highlightthickness=0)
        self.canvas.grid(row=1, column=0, sticky="nsew")
        
        self.status_badge = ctk.CTkFrame(self.center_panel, fg_color="#064E3B", corner_radius=15, height=30)
        self.status_badge.grid(row=2, column=0, pady=(15, 0))
        self.status_label = ctk.CTkLabel(self.status_badge, text="● Online - Escutando", font=("Helvetica", 12, "bold"), text_color="#34D399")
        self.status_label.pack(padx=15, pady=2)
        
        self.time_step = 0
        self.ai_state = "listening"
        
        # ================= DIREITA: TERMINAL DE CONVERSA =================
        self.right_panel = ctk.CTkFrame(self, fg_color=self.panel_color, corner_radius=8, border_width=1, border_color="#1E293B")
        self.right_panel.grid(row=0, column=2, sticky="nsew", padx=15, pady=15)
        
        ctk.CTkLabel(self.right_panel, text="Conversation Log", font=("Helvetica", 14, "bold"), text_color=self.text_main).pack(anchor="w", padx=15, pady=(15, 10))
        
        self.chat_box = ctk.CTkTextbox(self.right_panel, fg_color="#0F172A", text_color=self.text_dim, font=("Helvetica", 12), wrap="word")
        self.chat_box.pack(expand=True, fill="both", padx=15, pady=(0, 15))
        self.chat_box.configure(state="disabled")

        self.btn_interrupt = ctk.CTkButton(self.right_panel, text="🛑 Interromper e Ouvir", font=("Helvetica", 12, "bold"), fg_color="#7F1D1D", hover_color="#991B1B", command=self.on_interrupt)
        self.btn_interrupt.pack(fill="x", padx=15, pady=(0, 15))

        # Inicia a tela e garante update nas dimensões
        self.update()
        self.animate()

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
        
        if cx > 50 and cy > 50:
            color_main = "#06b6d4" # Cyan / Blue for eyes
            
            eye_w = 80
            eye_h = 100
            eye_gap = 60
            offset_y = 0
            
            if self.ai_state == "thinking":
                color_main = "#FBBF24"
                eye_h = 40 + math.sin(self.time_step * 0.2) * 10
                # Move slightly to simulate looking around
                offset_x = math.cos(self.time_step * 0.1) * 20
                cx += offset_x
            elif self.ai_state == "speaking":
                color_main = "#60A5FA"
                # Pulsa conforme fala
                eye_h = 90 + math.sin(self.time_step * 0.8) * 15
            else:
                # Blink natural de vez em quando (estado listening)
                if self.time_step % 60 < 2:
                    eye_h = 10 # Pisca
                else:
                    # Leve movimento orgânico
                    offset_y = math.sin(self.time_step * 0.05) * 5

            # Olho Esquerdo
            self.draw_eye(cx - (eye_w/2 + eye_gap/2), cy + offset_y, eye_w, eye_h, 20, color_main)
            # Olho Direito
            self.draw_eye(cx + (eye_w/2 + eye_gap/2), cy + offset_y, eye_w, eye_h, 20, color_main)
                    
        self.after(50, self.animate)

if __name__ == "__main__":
    app = FloatingAssistant()
    app.mainloop()
