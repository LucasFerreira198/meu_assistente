import subprocess
import os
import platform
import signal

current_tts_process = None

def stop_speaking():
    global current_tts_process
    if current_tts_process is not None:
        try:
            # Mata o grupo de processos (o shell e o aplay)
            os.killpg(os.getpgid(current_tts_process.pid), signal.SIGTERM)
        except Exception:
            pass
        current_tts_process = None
    # No linux, garantir que o aplay parou
    os.system("pkill -9 aplay > /dev/null 2>&1")

def speak(text: str):
    if not text:
        return

    os_name = platform.system().lower()
    
    # O executável real está dentro da subpasta piper/piper/piper
    piper_bin = os.path.join("piper", "piper", "piper") if os_name != "windows" else os.path.join("piper", "piper", "piper.exe")
    model_path = os.path.join("piper", "pt_BR-faber-medium.onnx")

    if not os.path.isfile(piper_bin):
        print("⚠️ Piper TTS não encontrado (executável).")
        return

    if not os.path.isfile(model_path):
        print("⚠️ Modelo de voz do Piper não encontrado.")
        return

    # aplay precisa dos parâmetros exatos (raw, 16-bit, 22050Hz) para não distorcer o áudio do Piper
    # O 2>/dev/null no final esconde os erros do Jack server e ALSA no terminal
    play_cmd = "aplay -r 22050 -f S16_LE -t raw -q 2>/dev/null" if os_name == "linux" else ("afplay" if os_name == "darwin" else "ffplay -nodisp -autoexit -")

    global current_tts_process
    stop_speaking() # Garante que para a fala anterior antes de começar uma nova

    # Passa o texto para o piper e redireciona o áudio bruto direto para o aplay
    piper_lib_path = os.path.dirname(piper_bin)
    command = f'echo "{text}" | LD_LIBRARY_PATH={piper_lib_path} {piper_bin} -m {model_path} --output_raw | {play_cmd}'
    
    try:
        # Usa Popen para não bloquear o script inteiramente, mas damos wait() para que
        # ele possa ser interrompido externamente (via kill).
        current_tts_process = subprocess.Popen(command, shell=True, stderr=subprocess.DEVNULL, preexec_fn=os.setsid if os_name == "linux" else None)
        current_tts_process.wait()
    except Exception as e:
        print(f"⚠️ Erro ao tentar rodar o Piper TTS: {e}")
    finally:
        current_tts_process = None