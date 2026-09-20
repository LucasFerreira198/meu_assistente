import asyncio
from core.audio_capture import record_audio
from core.stt import transcribe
from core.llm import process_intent
from core.tts import speak
import os


async def assistant_loop():
    print("🚀 Assistente Local Iniciado! (Ctrl+C para sair)")

    while True:
        input("Pressione [ENTER] para falar...")

        # 1. Gravando áudio
        audio_file = record_audio(duration=4)

        # 2. transcreve (STT)
        text_input = transcribe(audio_file)
        print(f"👤 Você disse: {text_input}")

        if not text_input:
            continue

        # 3. Processa intenção e ferramentas (LLM)
        response = process_intent(text_input)
        print(f"🤖 Assistente: {response}")
        
        # 4. Fala (TTS)
        speak(response)
        
        # Limpeza
        # if os.path.exists(audio_file):
        #     os.remove(audio_file)

        await asyncio.sleep(1)

if __name__ == "__main__":
    try:
        asyncio.run(assistant_loop())
    except KeyboardInterrupt:
        print("\nDesligando...")
        