import speech_recognition as sr

def transcribe(audio_path: str) -> str:
    """Lê o arquivo de áudio WAV e envia para a API rápida do Google."""
    r = sr.Recognizer()
    try:
        with sr.AudioFile(audio_path) as source:
            audio = r.record(source)
            # A API pública do Google é absurdamente rápida e muito mais leve que o Whisper local
            text = r.recognize_google(audio, language="pt-BR")
            return text
    except sr.UnknownValueError:
        # Quando o Google ouve apenas ruído/silêncio e não entende nada
        return ""
    except sr.RequestError:
        # Sem internet ou erro nos servidores do Google
        return "Desculpe, estou sem conexão com a internet."
    except Exception:
        return ""