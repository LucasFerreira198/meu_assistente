import os
import subprocess
from core.os_adapter import SystemAdapter

sys_adapter = SystemAdapter()

def media_control(action: str) -> str:
    """Usa o playerctl para controlar mídia."""
    try:
        if action == "play-pause":
            os.system("playerctl play-pause")
            return "Mídia alternada (play/pause)."
        elif action == "next":
            os.system("playerctl next")
            return "Próxima mídia."
        elif action == "prev":
            os.system("playerctl previous")
            return "Mídia anterior."
        return "Comando de mídia inválido."
    except Exception as e:
        return f"Erro ao controlar mídia: {e}"

def play_music(query: str) -> str:
    """Abre o spotify pesquisando por uma música específica."""
    try:
        sys_adapter.launch_app("spotify")
        subprocess.Popen(["xdg-open", f"spotify:search:{query}"])
        return f"Procurando e tocando '{query}' no Spotify."
    except Exception as e:
        return f"Erro ao buscar música: {e}"

