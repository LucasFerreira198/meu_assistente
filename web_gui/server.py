import asyncio
import threading
import os
import json
import time
import subprocess
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI()

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
app.mount("/static", StaticFiles(directory=CURRENT_DIR), name="static")

active_websockets = []
server_loop = None

@app.get("/")
def get_index():
    return FileResponse(os.path.join(CURRENT_DIR, "index.html"))

@app.get("/style.css")
def get_css():
    return FileResponse(os.path.join(CURRENT_DIR, "style.css"))

@app.get("/app.js")
def get_js():
    return FileResponse(os.path.join(CURRENT_DIR, "app.js"))

import base64
import signal
import gc
import psutil
import math
import tkinter as tk

class DesktopMiniEyes:
    def __init__(self):
        self.root = None
        self.canvas = None
        self.state = "listening"
        self.time_step = 0
        self.visible = False
        self._drag_data = {"x": 0, "y": 0}
        self.ready_event = threading.Event()
        self.started = False

    def start(self):
        if self.started: return
        self.started = True
        threading.Thread(target=self._run, daemon=True).start()
        self.ready_event.wait(timeout=2)

    def _run(self):
        try:
            self.root = tk.Tk()
            self.root.title("ARES Mini Eyes")
            self.root.overrideredirect(True)
            self.root.attributes("-topmost", True)
            self.root.configure(bg="#030712")

            sw = self.root.winfo_screenwidth()
            sh = self.root.winfo_screenheight()
            w, h = 150, 95
            x = sw - w - 24
            y = sh - h - 50
            self.root.geometry(f"{w}x{h}+{x}+{y}")

            self.canvas = tk.Canvas(self.root, width=w, height=h, bg="#030712", highlightthickness=1, highlightbackground="#00F0FF")
            self.canvas.pack(fill="both", expand=True)

            self.canvas.bind("<ButtonPress-1>", self._start_drag)
            self.canvas.bind("<B1-Motion>", self._do_drag)
            self.canvas.bind("<Double-Button-1>", self._restore_main)

            self.root.withdraw()
            self.ready_event.set()

            self._animate()
            self.root.mainloop()
        except Exception as e:
            print("DesktopMiniEyes error:", e)

    def _start_drag(self, event):
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

    def _do_drag(self, event):
        x = self.root.winfo_x() + (event.x - self._drag_data["x"])
        y = self.root.winfo_y() + (event.y - self._drag_data["y"])
        self.root.geometry(f"+{x}+{y}")

    def _restore_main(self, event=None):
        import subprocess
        subprocess.Popen("flatpak run com.google.Chrome || wmctrl -a 'A.R.E.S.' || true", shell=True)
        self.hide()

    def show(self):
        if not self.started:
            self.start()
        if self.root:
            self.root.after(0, lambda: self.root.deiconify())
            self.visible = True

    def hide(self):
        if self.root:
            self.root.after(0, lambda: self.root.withdraw())
            self.visible = False

    def toggle(self):
        if self.visible: self.hide()
        else: self.show()

    def set_state(self, state):
        self.state = state

    def _animate(self):
        if not self.root or not self.canvas:
            return
        self.time_step += 1
        
        color = "#00F0FF" # Listening
        h = 40
        offset_x = 0
        offset_y = 0
        
        if self.state == "thinking":
            color = "#F59E0B" # Âmbar
            h = 20 + int(math.sin(self.time_step * 0.4) * 8)
            offset_x = int(math.cos(self.time_step * 0.25) * 6)
        elif self.state == "speaking":
            color = "#38BDF8" # Azul neon
            h = 42 + int(math.sin(self.time_step * 0.6) * 10)
            offset_y = int(math.sin(self.time_step * 0.3) * 3)
        else:
            if self.time_step % 60 < 3:
                h = 4 # Pisca
            else:
                offset_y = int(math.sin(self.time_step * 0.08) * 3)
                
        self.canvas.delete("eye")
        # Olho esquerdo
        x1 = 25 + offset_x
        y1 = 44 - h // 2 + offset_y
        self.canvas.create_rectangle(x1, y1, x1 + 34, y1 + h, fill=color, outline=color, tags="eye")
        # Olho direito
        x2 = 91 + offset_x
        y2 = 44 - h // 2 + offset_y
        self.canvas.create_rectangle(x2, y2, x2 + 34, y2 + h, fill=color, outline=color, tags="eye")
        
        status_text = "ESCUTANDO..." if self.state == "listening" else ("PENSANDO..." if self.state == "thinking" else "FALANDO...")
        self.canvas.create_text(75, 80, text=status_text, fill=color, font=("monospace", 7, "bold"), tags="eye")
        
        self.root.after(40, self._animate)

desktop_mini_eyes = DesktopMiniEyes()

def get_running_apps_list():
    """Retorna lista de aplicativos do usuário em execução com PID para gerenciamento no HUD."""
    apps = []
    ignored = {
        "systemd", "dbus-daemon", "pipewire", "wireplumber", "pulseaudio", "gnome-shell", 
        "xorg", "wayland", "python3", "python", "bash", "sh", "sleep", "sshd", "cat", 
        "grep", "ps", "uvicorn", "flatpak-session-helper", "systemd-resolved"
    }
    
    # Lista de padrões reconhecidos de aplicativos comuns
    app_patterns = [
        ("chrome", "Google Chrome"),
        ("firefox", "Mozilla Firefox"),
        ("code", "Visual Studio Code"),
        ("spotify", "Spotify"),
        ("discord", "Discord"),
        ("slack", "Slack"),
        ("steam", "Steam"),
        ("gnome-terminal", "Terminal Linux"),
        ("terminal", "Terminal"),
        ("nautilus", "Gerenciador de Arquivos"),
        ("gedit", "Editor de Texto"),
        ("calc", "Calculadora"),
        ("vlc", "VLC Media Player"),
        ("obs", "OBS Studio"),
        ("telegram", "Telegram Desktop"),
        ("cursor", "Cursor AI"),
        ("blender", "Blender"),
        ("gimp", "GIMP"),
        ("inkscape", "Inkscape")
    ]
    
    seen = set()
    for p in psutil.process_iter(["pid", "name", "cmdline"]):
        try:
            name = p.info["name"] or ""
            if name.lower() in ignored:
                continue
            cmdline = " ".join(p.info.get("cmdline") or []).lower()
            
            for key, display in app_patterns:
                if (key in name.lower() or key in cmdline) and display not in seen:
                    apps.append({
                        "pid": p.info["pid"],
                        "name": display,
                        "raw_name": name
                    })
                    seen.add(display)
                    break
        except Exception:
            pass
            
    return apps

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    active_websockets.append(websocket)
    
    # Envia lista de apps e status inicial imediatamente ao conectar
    try:
        await websocket.send_text(json.dumps({
            "type": "apps_list",
            "apps": get_running_apps_list()
        }))
    except Exception:
        pass
        
    try:
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                mtype = msg.get("type")
                
                if mtype == "command":
                    cmd_text = msg.get("text", "")
                    img_data = msg.get("image")
                    
                    def execute_command():
                        from core.tts import speak
                        broadcast_sync({"type": "state", "state": "thinking"})
                        
                        spoken_messages = []
                        def web_feedback(text, brain):
                            spoken_messages.append(text)
                            if brain == "TERMINAL_LOG":
                                broadcast_sync({"type": "terminal", "message": text})
                            else:
                                broadcast_sync({"type": "state", "state": "speaking"})
                                broadcast_sync({"type": "chat", "speaker": f"ARES ({brain})", "message": text})
                                speak(text)
                                
                        try:
                            if img_data:
                                web_feedback("Processando imagem anexada no terminal...", "antigravity")
                                img_bytes = base64.b64decode(img_data.split(",")[-1])
                                img_dir = os.path.abspath("storage/screenshots")
                                os.makedirs(img_dir, exist_ok=True)
                                img_path = os.path.join(img_dir, "terminal_upload.png")
                                with open(img_path, "wb") as f:
                                    f.write(img_bytes)
                                    
                                import google.generativeai as genai
                                from PIL import Image
                                api_key = os.getenv("GEMINI_API_KEY")
                                genai.configure(api_key=api_key)
                                model = genai.GenerativeModel("gemini-3.6-flash")
                                pil_img = Image.open(img_path)
                                
                                query = cmd_text or "Analise detalhadamente esta imagem enviada pelo usuário e responda como ARES."
                                resp = model.generate_content([query, pil_img])
                                out_text = resp.text
                                web_feedback(out_text, "ARES")
                            else:
                                from core.llm import process_intent
                                ans = process_intent(cmd_text, feedback_callback=web_feedback)
                                if ans and ans.strip() and ans not in spoken_messages:
                                    broadcast_sync({"type": "state", "state": "speaking"})
                                    broadcast_sync({"type": "chat", "speaker": "ARES", "message": ans})
                                    speak(ans)
                        except Exception as ex:
                            broadcast_sync({"type": "terminal", "message": f"❌ Erro ao executar: {ex}"})
                        finally:
                            broadcast_sync({"type": "state", "state": "listening"})
                            
                    threading.Thread(target=execute_command, daemon=True).start()

                elif mtype == "window_state":
                    state = msg.get("state")
                    if state == "hidden":
                        desktop_mini_eyes.show()
                    elif state == "visible":
                        desktop_mini_eyes.hide()

                elif mtype == "toggle_mini":
                    desktop_mini_eyes.toggle()
                            
                elif mtype == "get_apps":
                    await websocket.send_text(json.dumps({
                        "type": "apps_list",
                        "apps": get_running_apps_list()
                    }))
                    
                elif mtype == "kill_process":
                    pid = msg.get("pid")
                    pname = msg.get("name", "Processo")
                    try:
                        p = psutil.Process(pid)
                        p.terminate()
                        p.wait(timeout=2)
                        broadcast_sync({
                            "type": "terminal",
                            "message": f"🛑 [SISTEMA] Processo '{pname}' (PID: {pid}) encerrado com sucesso."
                        })
                    except Exception as pe:
                        # Fallback SIGKILL
                        try:
                            os.kill(pid, signal.SIGKILL)
                            broadcast_sync({
                                "type": "terminal",
                                "message": f"🛑 [SISTEMA] Processo '{pname}' (PID: {pid}) forçado a encerrar (SIGKILL)."
                            })
                        except Exception:
                            broadcast_sync({
                                "type": "terminal",
                                "message": f"⚠️ Não foi possível encerrar PID {pid}: {pe}"
                            })
                    broadcast_sync({
                        "type": "apps_list",
                        "apps": get_running_apps_list()
                    })
                    
                elif mtype == "system_boost":
                    def run_boost():
                        # Limpa screenshots temporários e arquivos de áudio
                        cleaned = 0
                        for folder in ["storage/audio", "storage/screenshots"]:
                            if os.path.exists(folder):
                                for f in os.listdir(folder):
                                    fp = os.path.join(folder, f)
                                    try:
                                        if os.path.isfile(fp):
                                            os.remove(fp)
                                            cleaned += 1
                                    except Exception:
                                        pass
                        gc.collect()
                        broadcast_sync({
                            "type": "terminal",
                            "message": f"⚡ [SISTEMA BOOST] Otimização concluída! {cleaned} arquivos temporários limpos e memória liberada."
                        })
                    threading.Thread(target=run_boost, daemon=True).start()
                    
                elif mtype == "screen_snap":
                    from tools.vision_tools import analyze_screen
                    from ares import ares_instance
                    feedback_cb = ares_instance.feedback_callback if ares_instance else None
                    def run_snap():
                        if feedback_cb: feedback_cb("Capturando e analisando a tela atual...", "antigravity")
                        res = analyze_screen("Descreva de forma clara e resumida o que está visível na tela do usuário agora.")
                        if feedback_cb: feedback_cb(res, "ARES")
                    threading.Thread(target=run_snap, daemon=True).start()
                    
                elif mtype == "interrupt":
                    from core.tts import stop_speaking
                    stop_speaking()
                    
                elif mtype == "stop_agent":
                    from core.agent_manager import agent_manager
                    agent_manager.stop_agent(msg.get("id"))
            except Exception as e:
                print("Erro ao processar mensagem do websocket:", e)
    except WebSocketDisconnect:
        if websocket in active_websockets:
            active_websockets.remove(websocket)

def broadcast_sync(message_dict):
    """Envia uma mensagem JSON para todas as telas Web conectadas de forma thread-safe."""
    global server_loop
    if message_dict.get("type") == "state":
        try:
            desktop_mini_eyes.set_state(message_dict.get("state", "listening"))
        except Exception:
            pass
    if not server_loop or not active_websockets:
        return
    text = json.dumps(message_dict)
    for ws in list(active_websockets):
        try:
            asyncio.run_coroutine_threadsafe(ws.send_text(text), server_loop)
        except Exception:
            pass


class DummyWidget:
    def __init__(self, key_name=None):
        self.key_name = key_name

    def configure(self, **kwargs):
        text = kwargs.get("text")
        if text is not None:
            if self.key_name == "cpu":
                val = text.replace("CPU Usage: ", "").replace("%", "").strip()
                broadcast_sync({"type": "stats", "cpu": val})
            elif self.key_name == "ram":
                val = text.replace("RAM Usage: ", "").strip()
                broadcast_sync({"type": "stats", "ram": val})
            elif self.key_name == "temp":
                broadcast_sync({"type": "stats", "weather": text})
            elif self.key_name == "weather_desc":
                broadcast_sync({"type": "stats", "weather": text})
            elif self.key_name == "apps":
                lines = [l for l in text.split("\n") if l.strip() and not l.startswith("[")]
                broadcast_sync({"type": "stats", "apps": f"{len(lines)} ATIVOS"})

    def set(self, val):
        pass

    def insert(self, pos, text):
        pass

    def see(self, pos):
        pass


class WebHUDApp:
    """Implementa a mesma interface pública de FloatingAssistant para compatibilidade total com o ARES."""
    def __init__(self):
        self.ai_state = "listening"
        
        # Mapeamento para que ares.py continue chamando widgets sem erro
        self.lbl_cpu = DummyWidget("cpu")
        self.progress_cpu = DummyWidget("progress_cpu")
        self.lbl_ram = DummyWidget("ram")
        self.progress_ram = DummyWidget("progress_ram")
        self.lbl_temp = DummyWidget("temp")
        self.lbl_weather_desc = DummyWidget("weather_desc")
        self.apps_label = DummyWidget("apps")
        
        self.chat_box = DummyWidget("chat")
        self.terminal_box = DummyWidget("terminal")
        self.status_badge = DummyWidget("badge")
        self.status_label = DummyWidget("status")
        
        self.current_view = "Conversa"

        # Inicia o servidor Web FastAPI em segundo plano
        self.server_thread = threading.Thread(target=self._run_server, daemon=True)
        self.server_thread.start()
        time.sleep(0.8)

        # Broadcast periódico de apps do usuário em segundo plano
        def _apps_poller():
            while True:
                time.sleep(4)
                try:
                    if active_websockets:
                        apps = get_running_apps_list()
                        broadcast_sync({"type": "apps_list", "apps": apps})
                except Exception:
                    pass
        threading.Thread(target=_apps_poller, daemon=True).start()

        # Abre o Google Chrome no modo App
        self._open_browser_app()

    def _run_server(self):
        global server_loop
        server_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(server_loop)
        config = uvicorn.Config(app, host="127.0.0.1", port=8765, log_level="warning", loop="asyncio")
        server = uvicorn.Server(config)
        server_loop.run_until_complete(server.serve())

    def _open_browser_app(self):
        url = "http://127.0.0.1:8765"
        cmd = None
        # Tenta Chrome Flatpak
        try:
            res = subprocess.run(["flatpak", "info", "com.google.Chrome"], capture_output=True)
            if res.returncode == 0:
                cmd = f'flatpak run com.google.Chrome --app="{url}" --window-size=1300,760'
        except Exception:
            pass

        if not cmd:
            cmd = f'xdg-open "{url}"'

        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)

    def change_state(self, event=None):
        broadcast_sync({"type": "state", "state": self.ai_state})

    def switch_view(self, view_name: str):
        self.current_view = view_name

    def toggle_view(self):
        pass

    def add_chat_message(self, speaker, message):
        broadcast_sync({"type": "chat", "speaker": speaker, "message": message})

    def add_terminal_log(self, text):
        broadcast_sync({"type": "terminal", "message": text})

    def update_agents_list(self, agents_info: list):
        broadcast_sync({"type": "agents", "agents": agents_info})

    def after(self, ms, func):
        threading.Timer(ms / 1000.0, func).start()

    def mainloop(self):
        """Mantém o processo vivo."""
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

