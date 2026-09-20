import platform
import subprocess
import shutil
import os

class SystemAdapter:
    def __init__(self):
        self.os = platform.system().lower()

    def launch_app(self, app_name: str) -> str:
        try:
            if self.os == "windows":
                os.system(f"start {app_name}")
            elif self.os == "darwin":
                subprocess.Popen(["open", "-a", app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif self.os == "linux":
                if shutil.which(app_name):
                    subprocess.Popen([app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                    return f"Aplicativo '{app_name}' aberto (via terminal)."

                exit_code = os.system(f"gtk-launch {app_name} > /dev/null 2>&1")
                if exit_code == 0:
                    return f"Aplicativo '{app_name}' aberto (via atalho da interface)."
                
                if shutil.which("flatpak"):
                    # Busca o nome de registro do app (ex: com.spotify.Client)
                    flatpak_search = os.popen(f"flatpak list --app --columns=application | grep -i {app_name}").read().strip()
                    if flatpak_search:
                        app_id = flatpak_search.split('\n')[0] # Pega o primeiro da lista
                        subprocess.Popen(["flatpak", "run", app_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                        return f"Aplicativo '{app_name}' aberto via Flatpak."
                return f"Erro: O aplicativo '{app_name}' não foi encontrado no sistema."
            return f"sucesso: Aplicativo '{app_name}' aberto no sistema {self.os}."
        except Exception as e:
            return f"Erro ao abrir {app_name}: {str(e)}"
            