import threading
import time
import os

def set_timer(seconds: int, message: str = "Alarme!") -> str:
    """Define um timer para disparar após X segundos."""
    def timer_thread():
        time.sleep(seconds)
        # Toca um bipe no linux e cria um arquivo de log ou notificação
        os.system('notify-send "ARES ALARME" "' + message + '"')
        os.system('spd-say "Alarme ARES, ' + message + '"')
        
    t = threading.Thread(target=timer_thread, daemon=True)
    t.start()
    return f"Alarme definido para daqui a {seconds} segundos. Motivo: {message}"

