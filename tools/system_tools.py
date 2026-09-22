import psutil
import os
import subprocess

# Call once to initialize
psutil.cpu_percent(interval=None)

def get_system_health() -> str:
    """Retorna o status atual do processador, memória RAM e armazenamento."""
    try:
        cpu_usage = psutil.cpu_percent(interval=None)
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        status = (
            f"CPU: {cpu_usage}% de uso.\n"
            f"RAM: {ram.percent}% (Usando {ram.used // (1024**3)}GB de {ram.total // (1024**3)}GB).\n"
            f"Disco Principal: {disk.percent}% ocupado."
        )
        return status
    except Exception as e:
        return f"Erro ao verificar saúde do PC: {e}"

def set_volume(level: int = None, action: str = None) -> str:
    """Controla o volume tentando vários métodos (PipeWire, PulseAudio, ALSA puro)."""
    try:
        if action == "mute":
            if os.system("wpctl set-mute @DEFAULT_AUDIO_SINK@ 1 > /dev/null 2>&1") != 0:
                if os.system("amixer -D pulse sset Master mute > /dev/null 2>&1") != 0:
                    os.system("amixer sset Master mute > /dev/null 2>&1")
            return "Sistema mutado."
        elif action == "unmute":
            if os.system("wpctl set-mute @DEFAULT_AUDIO_SINK@ 0 > /dev/null 2>&1") != 0:
                if os.system("amixer -D pulse sset Master unmute > /dev/null 2>&1") != 0:
                    os.system("amixer sset Master unmute > /dev/null 2>&1")
            return "Sistema desmutado."
        elif level is not None:
            level = max(0, min(100, level))
            float_level = level / 100.0
            
            # Tenta Pipewire (wpctl)
            if os.system(f"wpctl set-volume @DEFAULT_AUDIO_SINK@ {float_level} > /dev/null 2>&1") != 0:
                # Se falhar, tenta PulseAudio/ALSA padrão
                if os.system(f"amixer -D pulse sset Master {level}% > /dev/null 2>&1") != 0:
                    # Se falhar, tenta ALSA Puro (sem pulse)
                    if os.system(f"amixer sset Master {level}% > /dev/null 2>&1") != 0:
                        # Última tentativa (PulseAudio puro)
                        os.system(f"pactl set-sink-volume @DEFAULT_SINK@ {level}% > /dev/null 2>&1")
                        
            return f"Volume ajustado para {level}%."
        return "Nenhuma ação de volume especificada."
    except Exception as e:
        return f"Erro ao ajustar volume: {e}"
