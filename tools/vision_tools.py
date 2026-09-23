import os
from mss import mss
import google.generativeai as genai
from PIL import Image
from dotenv import load_dotenv

# Garante o carregamento das chaves de API
load_dotenv()

def analyze_screen(question: str) -> str:
    """Captura a tela inteira do computador em tempo real para ler código aberto, analisar erros de terminal, inspecionar imagens/designs visíveis, identificar elementos visuais ou obter coordenadas para cliques."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            return "Erro: GEMINI_API_KEY não configurada. Visão indisponível."
            
        screenshot_path = os.path.join("storage", "screenshots", "temp_screen.jpg")
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        with mss() as sct:
            monitor = sct.monitors[1]
            sct_img = sct.grab(monitor)
            img = Image.frombytes("RGB", sct_img.size, sct_img.bgra, "raw", "BGRX")
            orig_w, orig_h = img.size
            
            # Mantém nitidez nativa para leitura de código (até 1920px), comprimindo em JPEG leve
            if orig_w > 1920:
                scale = 1920.0 / orig_w
                new_w = int(orig_w * scale)
                new_h = int(orig_h * scale)
                img_to_save = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
            else:
                img_to_save = img

            img_to_save.save(screenshot_path, format="JPEG", quality=85)
            
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("models/gemini-flash-lite-latest")
        
        img_obj = Image.open(screenshot_path)
        prompt = (
            f"Você é o módulo de visão e análise técnica do assistente ARES. "
            f"A resolução da tela física do usuário é {orig_w}x{orig_h}.\n"
            f"Pergunta ou tarefa do usuário: {question}\n\n"
            "DIRETRIZES DE ANÁLISE:\n"
            "1. CÓDIGO E TERMINAL: Se a tarefa envolver ler código, debugar, corrigir erros ou inspecionar scripts:\n"
            "   - Transcreva com precisão cirúrgica os trechos de código, comandos, tracebacks e mensagens de erro visíveis.\n"
            "   - Indique o nome do arquivo (se visível no título da aba ou janela) e a linguagem.\n"
            "2. IMAGENS E INTERFACE (UI): Se a tarefa for baseada em uma imagem, design, mockup ou layout na tela:\n"
            "   - Descreva a estrutura detalhada, componentes visuais, cores, disposição e regras necessárias para codificar a solução.\n"
            "3. CLIQUE OU NAVEGAÇÃO: Se a tarefa for clicar em botões, links ou vídeos:\n"
            "   - Forneça as coordenadas exatas: 'Coordenadas: X=<numero>, Y=<numero>'.\n"
            "   - Se for vídeo ou link: 'Título: <nome exato>'.\n"
            "4. Seja direto, fornecendo todo o contexto textual e técnico necessário para a IA de programação agir."
        )
        
        response = model.generate_content([prompt, img_obj])
        return f"Análise Visual da Tela:\n{response.text}"
    except Exception as e:
        return f"Erro ao analisar a tela: {str(e)}"

def click_on_screen(x: float, y: float) -> str:
    """Move o mouse e clica em uma coordenada específica da tela."""
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        target_x = int(round(float(x)))
        target_y = int(round(float(y)))
        pyautogui.click(target_x, target_y)
        return f"Clique realizado com sucesso na coordenada ({target_x}, {target_y})."
    except Exception as e:
        return f"Erro ao tentar clicar na tela: {str(e)}"

def type_on_screen(text: str, press_enter: bool = True) -> str:
    """Digita um texto na tela (como se fosse o teclado) e opcionalmente aperta Enter."""
    try:
        import pyautogui
        pyautogui.FAILSAFE = False
        pyautogui.write(text, interval=0.05)
        if press_enter:
            pyautogui.press('enter')
        return f"Texto '{text}' digitado com sucesso."
    except Exception as e:
        return f"Erro ao tentar digitar na tela: {str(e)}"
