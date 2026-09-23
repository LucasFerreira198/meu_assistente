import os
os.environ["GRPC_ENABLE_FORK_SUPPORT"] = "false"
from dotenv import load_dotenv
import ollama

# Carrega variáveis de ambiente (Chaves de API)
load_dotenv()

def classify_intent(user_text: str) -> str:
    """Sempre utiliza Antigravity (Gemini) como cérebro principal."""
    return "antigravity"

def route_to_qwen(messages, tools):
    """Rota direta para o Ollama (Qwen) como fallback offline."""
    try:
        response = ollama.chat(model='qwen2.5:3b', messages=messages, tools=tools)
        return response
    except Exception as e:
        print(f"\n⚠️ Falha no Qwen: {e}")
        return None

def get_action_announcement(name: str, args: dict) -> str:
    """Gera um feedback verbal dinâmico, elegante e natural em português para cada ação executada."""
    if name == "analyze_screen":
        question = args.get("question", "").lower()
        if any(w in question for w in ["código", "codigo", "script", "erro", "traceback", "terminal"]):
            return "Analisando o código e as mensagens na sua tela agora..."
        elif any(w in question for w in ["imagem", "design", "layout", "interface", "foto"]):
            return "Analisando a imagem e os componentes visuais na tela agora..."
        elif any(w in question for w in ["vídeo", "video", "youtube", "botão", "botao", "clique", "clicar"]):
            return "Localizando o elemento na sua tela agora..."
        return "Olhando para a sua tela agora..."
        
    elif name == "write_file":
        filepath = args.get("filepath", "")
        basename = os.path.basename(filepath)
        if basename == "gui.py":
            return "Atualizando e recriando a minha interface agora..."
        elif basename.endswith(".py"):
            return f"Escrevendo o código Python no arquivo {basename}..."
        elif basename.endswith(".sh"):
            return f"Criando o script de terminal {basename}..."
        elif basename.endswith((".html", ".css", ".js")):
            return f"Gerando os arquivos de interface web em {basename}..."
        elif basename:
            return f"Escrevendo o arquivo {basename} agora..."
        return "Criando o arquivo de código agora..."

    elif name == "read_file":
        filepath = args.get("filepath", "")
        basename = os.path.basename(filepath)
        return f"Lendo o código do arquivo {basename}..." if basename else "Lendo o arquivo..."

    elif name == "view_file_lines":
        filepath = args.get("filepath", "")
        basename = os.path.basename(filepath)
        return f"Inspecionando as linhas do arquivo {basename}..." if basename else "Inspecionando o código..."

    elif name == "replace_file_content":
        filepath = args.get("filepath", "")
        basename = os.path.basename(filepath)
        return f"Aplicando alteração cirúrgica no código de {basename}..." if basename else "Aplicando alteração cirúrgica no código..."

    elif name == "verify_code_syntax":
        filepath = args.get("filepath", "")
        basename = os.path.basename(filepath)
        return f"Validando a integridade e sintaxe de {basename}..." if basename else "Verificando sintaxe do código..."

    elif name == "run_terminal_command":
        cmd = args.get("command", "")
        if "python" in cmd:
            return "Executando o script Python no terminal..."
        elif "git" in cmd:
            return "Executando comando no repositório Git..."
        elif any(w in cmd for w in ["mkdir", "touch", "mv", "cp"]):
            return "Organizando os arquivos no sistema..."
        return "Executando comando no terminal agora..."

    elif name == "open_terminal_window":
        return "Abrindo a janela do terminal na tela..."

    elif name == "web_search":
        query = args.get("query", "")
        if "youtube" in query.lower():
            return "Buscando e abrindo o vídeo no YouTube..."
        return "Abrindo o navegador para pesquisar..."

    elif name == "click_on_screen":
        return "Clicando no elemento indicado na tela..."

    elif name == "type_on_screen":
        return "Digitando o texto na tela..."

    elif name == "create_background_agent":
        agent_name = args.get("name", "autônomo")
        return f"Iniciando o sub-agente '{agent_name}' em segundo plano..."

    elif name == "stop_background_agent":
        return "Interrompendo a execução do sub-agente..."

    elif name == "memorize_fact":
        return "Guardando essa informação na minha memória permanente..."

    elif name == "open_aplication":
        app = args.get("app_name", "aplicativo")
        return f"Abrindo o aplicativo {app}..."

    elif name == "close_aplication":
        app = args.get("app_name", "aplicativo")
        return f"Fechando o aplicativo {app}..."

    elif name == "get_system_health":
        return "Verificando o consumo de CPU e memória do sistema..."

    elif name == "get_weather":
        return "Consultando a previsão do tempo..."

    elif name == "get_news":
        return "Buscando as notícias mais recentes..."

    elif name == "set_volume":
        return "Ajustando o volume do sistema..."

    return None

def run_antigravity_loop(sys_prompt: str, conversation_history: list, user_text: str, feedback_callback=None) -> str:
    """Executa o loop autônomo completo do ARES usando o chat nativo do Gemini (Antigravity)."""
    import google.generativeai as genai
    from tools import AVAILABLE_TOOLS
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Chave GEMINI_API_KEY ausente no arquivo .env")
        
    genai.configure(api_key=api_key)
    
    # Prepara o histórico anterior simples (somente user e model)
    history = []
    for msg in conversation_history:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg.get("content", "")]})
        
    tools_list = list(AVAILABLE_TOOLS.values())
    
    coding_triggers = ["código", "codigo", "script", "programa", "interface", "recria", "função", "bug", "erro", "terminal", "arquivo", "modificar", "consertar", "editar"]
    is_coding_task = any(w in user_text.lower() for w in coding_triggers)
    
    # Para tarefas de programação ou edição de código, utiliza gemini-3.6-flash (alta capacidade de raciocínio)
    if is_coding_task:
        preferred_models = ["gemini-3.6-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]
        max_steps = 10
    else:
        preferred_models = ["gemini-flash-lite-latest", "gemini-3.6-flash", "gemini-flash-latest"]
        max_steps = 6
        
    chat = None
    resp = None
    for m_name in preferred_models:
        try:
            model = genai.GenerativeModel(
                model_name=m_name,
                system_instruction=sys_prompt,
                tools=tools_list
            )
            chat = model.start_chat(history=history)
            resp = chat.send_message(user_text)
            break
        except Exception as e:
            print(f"Tentando próximo modelo após: {e}")
            continue
            
    if resp is None:
        raise RuntimeError("Falha ao inicializar o modelo Gemini com as ferramentas.")
        
    step = 0
    final_spoken = ""
    
    while step < max_steps:
        step += 1
        function_calls = []
        text_content = ""
        
        if resp.candidates and resp.candidates[0].content.parts:
            for part in resp.candidates[0].content.parts:
                if part.function_call:
                    function_calls.append(part.function_call)
                elif part.text:
                    text_content += part.text
                    
        # Se o modelo gerou uma fala intermediária ou final
        if text_content and feedback_callback:
            feedback_callback(text_content, "antigravity")
            final_spoken += text_content + " "
            
        if not function_calls:
            # Se a IA anunciou que está criando/modificando arquivos mas não incluiu a tool call no mesmo turno
            action_triggers = ["criando os arquivos", "vou criar", "gerando os arquivos", "escrevendo o arquivo", "modificando o arquivo", "vou recriar", "criando o arquivo", "criando a nova interface"]
            if step < 4 and any(trig in text_content.lower() for trig in action_triggers):
                resp = chat.send_message("Execute agora chamando a ferramenta apropriada (como write_file) para concluir a ação prometida.")
                continue
            break
            
        # Executa as chamadas de ferramentas geradas pelo Gemini
        tool_responses = []
        for fc in function_calls:
            name = fc.name
            args = type(fc).to_dict(fc).get("args", {})
            
            # Anúncio verbal contextual e inteligente antes de executar a ação
            announcement = get_action_announcement(name, args)
            if announcement and feedback_callback:
                feedback_callback(announcement, "antigravity")
                
            if name in AVAILABLE_TOOLS:
                tool_res = AVAILABLE_TOOLS[name](**args)
            else:
                tool_res = f"Ferramenta '{name}' não encontrada."
                
            # Log em tempo real no terminal da UI
            if feedback_callback:
                feedback_callback(f"> {name}({args})\n{tool_res}\n", "TERMINAL_LOG")
            else:
                print(f"\033[90m⚙️ [SISTEMA]: {name} -> {str(tool_res)[:200]}...\033[0m")
                
            tool_responses.append(
                genai.protos.Part(
                    function_response=genai.protos.FunctionResponse(
                        name=name,
                        response={"result": str(tool_res)}
                    )
                )
            )
            
        # Envia as respostas das ferramentas de volta ao chat do Gemini
        resp = chat.send_message(
            genai.protos.Content(parts=tool_responses)
        )
        
    return final_spoken.strip() or (resp.text if hasattr(resp, "text") and resp.text else "Ação concluída com sucesso.")
