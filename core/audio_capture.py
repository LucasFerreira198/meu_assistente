import speech_recognition as sr
import os
import ctypes

# Oculta mensagens de erro do ALSA (C-level) 
# Isso resolve o problema de poluição visual do PyAudio no Linux
ERROR_HANDLER_FUNC = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)
def py_error_handler(filename, line, function, err, fmt):
    pass
c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)
try:
    asound = ctypes.cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
except OSError:
    pass

# Inicializa o reconhecedor e o microfone apenas uma vez para evitar spam de logs do ALSA/PyAudio no Linux
recognizer = sr.Recognizer()
# Habilita ajuste com piso fixo acima do ruído da sala (ruído medido em ~100-149, voz humana em 400-1500)
recognizer.dynamic_energy_threshold = False
recognizer.energy_threshold = 380
# Pausa de 0.8s de silêncio para encerrar a frase com agilidade
recognizer.pause_threshold = 0.8

# Redireciona stderr temporariamente para esconder erros adicionais do JACK/PyAudio durante a criação
devnull = os.open(os.devnull, os.O_WRONLY)
old_stderr = os.dup(2)
os.dup2(devnull, 2)
try:
    microphone = sr.Microphone()
finally:
    os.dup2(old_stderr, 2)
    os.close(devnull)
    os.close(old_stderr)

devnull_init = os.open(os.devnull, os.O_WRONLY)
old_stderr_init = os.dup(2)
os.dup2(devnull_init, 2)
try:
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.6)
        if recognizer.energy_threshold < 350:
            recognizer.energy_threshold = 350
finally:
    os.dup2(old_stderr_init, 2)
    os.close(devnull_init)
    os.close(old_stderr_init)

DEFAULT_AUDIO_PATH = os.path.join("storage", "audio", "temp.wav")

def record_audio(filename=DEFAULT_AUDIO_PATH, timeout=5, phrase_time_limit=10) -> str:
    """Escuta o microfone aguardando fala, e salva em um arquivo WAV."""
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    os.dup2(devnull, 2)
    
    try:
        with microphone as source:
            # Restaurar stderr temporariamente se quiser que outros erros apareçam,
            # mas vamos manter silenciado enquanto ele escuta para evitar spans do ALSA.
            try:
                audio_data = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                return None
            except Exception as e:
                # Retorna silenciosamente e lida no main
                return None
                
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, "wb") as f:
                f.write(audio_data.get_wav_data())
                
            return filename
    finally:
        os.dup2(old_stderr, 2)
        os.close(devnull)
        os.close(old_stderr)