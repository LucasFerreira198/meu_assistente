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
import re

sys_adapter = SystemAdapter()

ui_queue = queue.Queue()

class ARES_System:
    def __init__(self, gui: FloatingAssistant):
        self.gui = gui
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
            
            if state:
                # Dispara clique direito fake para mudar animacao
                self.gui.ai_state = state
                self.gui.change_state(None) # atualiza cor da bolinha
                
            if msg:
                self.gui.chat_box.configure(state="normal")
                self.gui.chat_box.insert("end", f"\n[{speaker}] {msg}\n")
                self.gui.chat_box.see("end")
                self.gui.chat_box.configure(state="disabled")
                
        self.gui.after(100, self.process_queue)

    def brain_loop(self):
        ui_queue.put(("ARES ONLINE. Módulos iniciados.", "listening", "SISTEMA"))
        while True:
            ui_queue.put((None, "listening", None))
            audio_path = record_audio(filename="temp.wav")
            if not audio_path:
                continue
                
            ui_queue.put(("Processando áudio...", "thinking", "SISTEMA"))
            
            text = transcribe(audio_path)
            if not text:
                continue
                
            ui_queue.put((text, None, "VOCÊ"))
            
            response = process_intent(text)
            
            ui_queue.put((response, "speaking", "ARES"))
            speak(response)
            
            time.sleep(1) # Pausa pequena após falar

if __name__ == "__main__":
    app = FloatingAssistant()
    ares = ARES_System(app)
    app.mainloop()

