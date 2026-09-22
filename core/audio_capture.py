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
# Desabilita o ajuste dinâmico para que ele não fique "sensível demais" quando a sala estiver quieta (evita pegar o teclado)
recognizer.dynamic_energy_threshold = False
# Aumenta a força necessária para ativar (Padrão era 300~400. 1500 exige que você fale claro)
recognizer.energy_threshold = 1500
# Tempo máximo de silêncio antes dele entender que você terminou a frase. Aumentado para 1.2 segundos para não cortar sua fala.
recognizer.pause_threshold = 1.2

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
        # print("🎤 Ajustando para o ruído ambiente inicial...")
        recognizer.adjust_for_ambient_noise(source, duration=1)
finally:
    os.dup2(old_stderr_init, 2)
    os.close(devnull_init)
    os.close(old_stderr_init)

def record_audio(filename="temp.wav", timeout=None, phrase_time_limit=10) -> str:
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
                
            with open(filename, "wb") as f:
                f.write(audio_data.get_wav_data())
                
            return filename
    finally:
        os.dup2(old_stderr, 2)
        os.close(devnull)
        os.close(old_stderr)