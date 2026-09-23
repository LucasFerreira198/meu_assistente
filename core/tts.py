import subprocess
import os
import platform
import signal
import queue
import threading
import re

current_tts_process = None
tts_queue = queue.Queue()
is_worker_started = False
queue_lock = threading.Lock()

def stop_speaking():
    """Para imediatamente a fala atual e descarta frases pendentes na fila."""
    global current_tts_process
    with queue_lock:
        while not tts_queue.empty():
            try:
                tts_queue.get_nowait()
                tts_queue.task_done()
            except Exception:
                break
                
    if current_tts_process is not None:
        try:
            os.killpg(os.getpgid(current_tts_process.pid), signal.SIGTERM)
        except Exception:
            pass
        current_tts_process = None
    os.system("pkill -9 aplay > /dev/null 2>&1")

def _play_raw(text: str):
    global current_tts_process
    if not text or not text.strip():
        return

    os_name = platform.system().lower()
    piper_bin = os.path.join("piper", "piper", "piper") if os_name != "windows" else os.path.join("piper", "piper", "piper.exe")
    model_path = os.path.join("piper", "pt_BR-faber-medium.onnx")

    if not os.path.isfile(piper_bin) or not os.path.isfile(model_path):
        return

    # Limpa markdown e caracteres especiais que possam confundir o sintetizador
    clean_text = re.sub(r'[`*_#>]', '', text).strip()
    if not clean_text:
        return

    piper_lib_path = os.path.dirname(piper_bin)
    env = dict(os.environ, LD_LIBRARY_PATH=piper_lib_path)

    try:
        # Inicia o Piper TTS recebendo texto via STDIN direto (sem passar por shell bash)
        p_piper = subprocess.Popen(
            [piper_bin, "-m", model_path, "--output_raw"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            env=env,
            preexec_fn=os.setsid if os_name == "linux" else None
        )
        
        # Conecta a saída de áudio do Piper diretamente ao reprodutor do sistema
        play_cmd = ["aplay", "-r", "22050", "-f", "S16_LE", "-t", "raw", "-q"] if os_name == "linux" else (["afplay"] if os_name == "darwin" else ["ffplay", "-nodisp", "-autoexit", "-"])
        
        p_play = subprocess.Popen(
            play_cmd,
            stdin=p_piper.stdout,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid if os_name == "linux" else None
        )
        p_piper.stdout.close()
        
        current_tts_process = p_play
        
        # Envia o texto seguro em UTF-8 direto pelo pipe
        p_piper.stdin.write(clean_text.encode('utf-8'))
        p_piper.stdin.close()
        
        p_play.wait()
        p_piper.wait()
    except Exception as e:
        print(f"⚠️ Erro no Piper TTS: {e}")
    finally:
        current_tts_process = None

def _tts_worker():
    while True:
        text = tts_queue.get()
        if text is None:
            break
        try:
            _play_raw(text)
        except Exception as e:
            print(f"⚠️ Erro ao reproduzir fala: {e}")
        finally:
            tts_queue.task_done()

def ensure_worker():
    global is_worker_started
    if not is_worker_started:
        t = threading.Thread(target=_tts_worker, daemon=True)
        t.start()
        is_worker_started = True

def speak(text: str):
    """Enfileira o texto para ser falado sequencialmente, sem cortar frases anteriores."""
    if not text or not text.strip():
        return
    ensure_worker()
    tts_queue.put(text)

def is_speaking() -> bool:
    """Retorna True se houver áudio sendo reproduzido ou na fila."""
    return not tts_queue.empty() or current_tts_process is not None

def wait_until_done():
    """Bloqueia até que toda a fala tenha terminado nos alto-falantes antes de abrir o microfone."""
    import time
    tts_queue.join()
    while current_tts_process is not None:
        time.sleep(0.05)