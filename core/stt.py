from faster_whisper import WhisperModel

model = WhisperModel("tiny", device='cpu', compute_type="int8")

def transcribe(audio_path: str) -> str:
    segments, _ = model.transcribe(audio_path, language="pt", beam_size=1)
    text = "".join([segment.text for segment in segments])
    return text.strip()