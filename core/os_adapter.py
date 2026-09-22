import platform
import subprocess
import shutil
import os
import psutil
import json
import time

STATE_FILE = "state.json"

class SystemAdapter:
    def __init__(self):
        self.os = platform.system().lower()
        self.tracked_apps = self._load_state()

    def _load_state(self):
        if os.path.exists(STATE_FILE):
            try:
                with open(STATE_FILE, "r") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def _save_state(self):
        try:
            with open(STATE_FILE, "w") as f:
                json.dump(self.tracked_apps, f)
        except Exception:
            pass

    def launch_app(self, app_name: str) -> str:
        try:
            # Garante que não foi passado argumentos maliciosos pro grep
            safe_app_name = app_name.replace("-", "").strip()
            
            if self.os == "windows":
                os.system(f"start {safe_app_name}")
            elif self.os == "darwin":
                subprocess.Popen(["open", "-a", safe_app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            elif self.os == "linux":
                if shutil.which(safe_app_name):
                    process = subprocess.Popen([safe_app_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                    self.tracked_apps[safe_app_name] = {"pid": process.pid, "type": "native", "time": time.time()}
                    self._save_state()
                    return f"Aplicativo '{safe_app_name}' aberto (via terminal)."

                exit_code = os.system(f"gtk-launch {safe_app_name} > /dev/null 2>&1")
                if exit_code == 0:
                    self.tracked_apps[safe_app_name] = {"pid": None, "type": "gtk-launch", "time": time.time()}
                    self._save_state()
                    return f"Aplicativo '{safe_app_name}' aberto (via atalho da interface)."
                
                if shutil.which("flatpak"):
                    flatpak_search = os.popen(f"flatpak list --app --columns=application | grep -i {safe_app_name}").read().strip()
                    if flatpak_search:
                        app_id = flatpak_search.split('\n')[0]
                        process = subprocess.Popen(["flatpak", "run", app_id], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                        self.tracked_apps[safe_app_name] = {"pid": process.pid, "type": "flatpak", "time": time.time()}
                        self._save_state()
                        return f"Aplicativo '{safe_app_name}' aberto via Flatpak."
                return f"Erro: O aplicativo '{safe_app_name}' não foi encontrado no sistema."
            return f"sucesso: Aplicativo '{safe_app_name}' aberto no sistema {self.os}."
        except Exception as e:
            return f"Erro ao abrir {app_name}: {str(e)}"

    def close_app(self, app_name: str) -> str:
        """Tenta fechar um aplicativo, pelo PID se monitorado ou pkill como fallback."""
        app_name = app_name.lower().strip()
        closed = False
        
        # 1. Tenta matar pelo PID se rastreado
        if app_name in self.tracked_apps:
            pid = self.tracked_apps[app_name]["pid"]
            if pid is not None:
                try:
                    p = psutil.Process(pid)
                    p.terminate()
                    p.wait(timeout=3)
                    closed = True
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    pass
            del self.tracked_apps[app_name]
            self._save_state()
            
        # 2. Tenta pkill/killall como fallback genérico (muito comum no Linux)
        if not closed:
            exit_code = os.system(f"pkill -f -i {app_name}")
            if exit_code == 0:
                closed = True
            elif shutil.which("flatpak"):
                # flatpak kill
                f_search = os.popen(f"flatpak list --app --columns=application | grep -i {app_name}").read().strip()
                if f_search:
                    f_id = f_search.split('\n')[0]
                    if os.system(f"flatpak kill {f_id}") == 0:
                        closed = True

        if closed:
            return f"Aplicativo '{app_name}' fechado com sucesso."
        else:
            return f"Não foi possível encontrar ou fechar o aplicativo '{app_name}'."
            
    def get_active_apps(self) -> str:
        """Returns a string describing which monitored apps are still open."""
        open_apps = []
        changed = False
        
        try:
            # Lista de processos normais
            ps_out = subprocess.run(["ps", "-A", "-o", "comm="], stdout=subprocess.PIPE, text=True).stdout.lower()
            # Lista de flatpaks rodando (se existir)
            flatpak_out = ""
            if shutil.which("flatpak"):
                flatpak_out = subprocess.run(["flatpak", "ps", "--columns=application"], stdout=subprocess.PIPE, text=True).stdout.lower()
        except Exception:
            ps_out = ""
            flatpak_out = ""
            
        for name, info in list(self.tracked_apps.items()):
            pid = info.get("pid") if isinstance(info, dict) else info
            
            # Grace period de 10 segundos para aplicativos que acabaram de ser abertos
            launch_time = info.get("time", 0) if isinstance(info, dict) else 0
            if time.time() - launch_time < 10:
                open_apps.append(name)
                continue
                
            pid_alive = False
            if pid is not None:
                try:
                    pid_alive = psutil.pid_exists(pid)
                except Exception:
                    pass
            
            # Se o nome aparecer nos processos ou no flatpak ps, assumimos que está vivo
            name_lower = name.lower()
            name_alive = (name_lower in ps_out) or (name_lower in flatpak_out)

            if pid_alive or name_alive:
                open_apps.append(name)
            else:
                del self.tracked_apps[name]
                changed = True
                
        if changed:
            self._save_state()
            
        open_apps = list(set(open_apps))
        return "\n".join([f"> {app}" for app in open_apps]) if open_apps else "> Nenhum app."

    def get_active_apps_context(self) -> str:
        return self.get_active_apps().replace("\n> ", ", ").replace("> ", "")