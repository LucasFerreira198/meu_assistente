import sounddevice as sd
import numpy as np
import scipy.io.wavfile as wav

def record_audio(duration = 5, fs = 48000, filename="temp.wav"):
    print(f"🎤 Escutando por {duration} segundos...")
    recording = sd.rec(int(duration * fs), samplerate=fs, channels=2, dtype='int16', device=0)
    sd.wait()
    wav.write(filename, fs, recording)
    return filename