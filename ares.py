import os
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "false"
import threading
import time
import queue
from core.audio_capture import record_audio
from core.stt import transcribe
from core.llm import process_intent
from core.tts import speak
from tools.system_tools import get_system_health
from core.os_adapter import SystemAdapter
from gui import FloatingAssistant
from core.agent_manager import agent_manager
import re

sys_adapter = SystemAdapter()

ui_queue = queue.Queue()

class ARES_System:
    def __init__(self, gui: FloatingAssistant):
        global ares_instance
        ares_instance = self
        self.gui = gui
        self.prev_agent_count = 0
        agent_manager.set_ui_callback(lambda info: ui_queue.put((info, None, "AGENTS_UPDATE")))
        self.update_stats()
        threading.Thread(target=self.fetch_weather, daemon=True).start()
        threading.Thread(target=self.brain_loop, daemon=True).start()
        self.process_queue()

    def fetch_weather(self):
        from tools.weather_tools import get_weather
        try:
            weather_str = get_weather()
            # Retorno ex: "Tempo em Sao Paulo: 25°C. Condição: Clear"
            temp_match = re.search(r'([-+]?\d+°C)', weather_str)
            desc_match = re.search(r'Condição:\s*(.+)', weather_str)
            
            if temp_match:
                self.gui.lbl_temp.configure(text=temp_match.group(1))
            if desc_match:
                self.gui.lbl_weather_desc.configure(text=desc_match.group(1))
        except Exception:
            pass

    def update_stats(self):
        try:
            health_str = get_system_health()
            # Parse simple values: CPU: 12% | RAM: 45%
            cpu_match = re.search(r'CPU:\s*([\d\.]+)%', health_str)
            ram_match = re.search(r'RAM:\s*([\d\.]+)%', health_str)
            
            if cpu_match:
                cpu_val = float(cpu_match.group(1))
                self.gui.lbl_cpu.configure(text=f"CPU Usage: {cpu_val}%")
                self.gui.progress_cpu.set(cpu_val / 100.0)
                
            if ram_match:
                ram_val = float(ram_match.group(1))
                self.gui.lbl_ram.configure(text=f"RAM Usage: {ram_val}%")
                self.gui.progress_ram.set(ram_val / 100.0)
            
            apps = sys_adapter.get_active_apps()
            self.gui.apps_label.configure(text=f"[PROCESSOS ATIVOS]\n{apps}")
        except Exception as e:
            pass
        self.gui.after(3000, self.update_stats)

    def process_queue(self):
        while not ui_queue.empty():
            msg, state, speaker = ui_queue.get()
            
            if speaker == "AGENTS_UPDATE":
                agents_info = msg
                self.gui.update_agents_list(agents_info)
                if len(agents_info) > self.prev_agent_count:
                    self.prev_agent_count = len(agents_info)
                    if self.gui.current_view != "Sub-Agentes":
                        self.gui.switch_view("Sub-Agentes")
                continue

            if speaker == "TERMINAL_LOG":
                if hasattr(self.gui, "add_terminal_log"):
                    self.gui.add_terminal_log(msg)
                else:
                    if self.gui.current_view != "Terminal":
                        self.gui.switch_view("Terminal")
                    self.gui.terminal_box.configure(state="normal")
                    self.gui.terminal_box.insert("end", msg)
                    self.gui.terminal_box.see("end")
                    self.gui.terminal_box.configure(state="disabled")
                continue

            if state:
                self.gui.ai_state = state
                self.gui.change_state(None) # atualiza cor do status
                
            if msg:
                if hasattr(self.gui, "add_chat_message"):
                    self.gui.add_chat_message(speaker, msg)
                else:
                    self.gui.chat_box.configure(state="normal")
                    self.gui.chat_box.insert("end", f"\n[{speaker}] {msg}\n")
                    self.gui.chat_box.see("end")
                    self.gui.chat_box.configure(state="disabled")
                
        self.gui.after(100, self.process_queue)

    def feedback_callback(self, msg: str, brain: str):
        if brain == "TERMINAL_LOG":
            ui_queue.put((msg, None, "TERMINAL_LOG"))
        else:
            ui_queue.put((msg, "speaking", f"ARES ({brain})"))
            # Envia para o motor TTS sequencial (não bloqueia e não corta frases anteriores)
            speak(msg)

    def brain_loop(self):
        ui_queue.put(("ARES ONLINE. Módulos iniciados.", "listening", "SISTEMA"))
        while True:
            ui_queue.put((None, "listening", None))
            audio_path = record_audio()
            if not audio_path:
                continue
                
            ui_queue.put((None, "thinking", None))
            
            text = transcribe(audio_path)
            if not text:
                continue
                
            ui_queue.put((text, None, "VOCÊ"))
            
            # Passa o callback para receber updates enquanto a IA trabalha (Autonomous Loop)
            # Todo texto (intermediário ou final) será roteado pelo feedback_callback
            process_intent(text, feedback_callback=self.feedback_callback)
            
            # Aguarda o áudio terminar de tocar nos alto-falantes antes de abrir o microfone
            from core.tts import wait_until_done
            wait_until_done()
            
            time.sleep(0.3) # Pausa curta após falar

ares_instance = None

# Escolha da interface: 'web' para o HUD Stark idêntico em HTML/CSS com olhos OLED, ou 'tk' para CustomTkinter
UI_MODE = os.getenv("ARES_UI_MODE", "web").lower()

if UI_MODE == "web":
    from web_gui.server import WebHUDApp as AssistantApp
else:
    from gui import FloatingAssistant as AssistantApp

if __name__ == "__main__":
    app = AssistantApp()
    ares = ARES_System(app)
    ares_instance = ares
    app.mainloop()

