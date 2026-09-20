import subprocess
import os
import platform

def speak(text: str):
    os_name = platform.system().lower()
    piper_bin = "./piper/piper" if os_name != "windows" else "piper\\piper.exe"
    model_path = "piper/pt_BR-faber-medium.onnx"

    if not os.path.exists(piper_bin):
        print("⚠️ Piper TTS não encontrado. Pulei a fala.")
        return

    play_cmd = "aplay" if os_name == "linux" else ("afplay" if os_name == "darwin" else "ffplay -nodisp -autoexit -")

    command = f'echo "{text}" | {piper_bin} -m {model_path} --output_raw | {play_cmd}'
    subprocess.Popen(command, shell=True, stderr=subprocess.DEVNULL)