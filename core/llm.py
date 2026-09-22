import ollama
from tools import AVAILABLE_TOOLS, TOOLS_SCHEMA, get_active_apps_context, load_memory

conversation_history = []

def process_intent(user_text: str) -> str:
    global conversation_history
    
    active_apps_context = get_active_apps_context()
    user_memory = load_memory()
    memory_context = "Memórias do usuário:\n" + "\n".join(user_memory) if user_memory else "O usuário ainda não compartilhou fatos pessoais."
    
    sys_prompt = (
        "Você é ARES, um assistente virtual ultra-avançado de inteligência artificial criado para controlar o computador do usuário (Lucas).\n"
        f"{memory_context}\n"
        f"Contexto do Sistema atual:\nApps em execução: {active_apps_context}\n\n"
        "REGRAS OBRIGATÓRIAS:\n"
        "1. Se o usuário pedir para tocar uma música ou artista pelo nome (ex: 'Toque Nirvana', 'Toque Nirvana no Spotify'), VOCÊ DEVE USAR A FERRAMENTA play_music. (ISSO TEM PRIORIDADE SOBRE ABRIR APP).\n"
        "2. Se o usuário pedir para abrir um APLICATIVO DO COMPUTADOR, use open_aplication. MAS se ele pedir para abrir um SITE (como YouTube, Google, Netflix, etc), VOCÊ DEVE USAR A FERRAMENTA web_search (ex: web_search(query='youtube')).\n"
        "3. Se o usuário pedir para fechar um app, VOCÊ DEVE USAR A FERRAMENTA close_aplication.\n"
        "4. Se o usuário der uma ordem genérica como 'dê play', 'pause', 'pule a música' ou 'volte a música', VOCÊ DEVE USAR A FERRAMENTA `media_control`.\n"
        "5. Se o usuário pedir para pesquisar no YouTube ou Google, use web_search.\n"
        "6. Se o usuário falar sobre si mesmo ou pedir para você lembrar de algo, VOCÊ DEVE EXECUTAR A FERRAMENTA memorize_fact (ex: memorize_fact(fact='O usuário gosta de Naruto')).\n"
        "7. Se pedir para verificar a saúde do sistema ou RAM/CPU, use get_system_health.\n"
        "8. Se perguntar do tempo ou clima, use get_weather.\n"
        "9. Se pedir para alterar o volume, use set_volume.\n"
        "10. Se pedir notícias do dia, use get_news.\n"
        "11. Se pedir para criar um alarme/lembrete/timer, use set_timer.\n"
        "12. NUNCA diga que executou uma ação (como memorizar, ligar, abrir, tocar) sem antes DE FATO ter disparado a ferramenta correspondente. É proibido mentir que fez algo.\n"
        "13. Confirme as ações com frases curtas."
    )

    messages = [{"role": "system", "content": sys_prompt}] + conversation_history + [{"role": "user", "content": user_text}]

    response = ollama.chat(model='qwen2.5:3b', messages=messages, tools=TOOLS_SCHEMA)
    tool_calls = response.get("message", {}).get("tool_calls")

    if tool_calls:
        for tool in tool_calls:
            fucn_name = tool["function"]["name"]
            args = tool["function"]["arguments"]

            if fucn_name in AVAILABLE_TOOLS:
                result = AVAILABLE_TOOLS[fucn_name](**args)
                print(f"\033[90m⚙️ [SISTEMA]: {result}\033[0m")

                messages.append(response["message"])
                messages.append({"role": "tool", "content": result})
                
                # Resposta final em stream após usar ferramenta
                print("\033[96m🤖 Assistente: \033[0m", end="", flush=True)
                final_response_stream = ollama.chat(model="qwen2.5:3b", messages=messages, stream=True)
                full_text = ""
                for chunk in final_response_stream:
                    part = chunk.get("message", {}).get("content", "")
                    print(part, end="", flush=True)
                    full_text += part
                print("\n")
                
                conversation_history.append({"role": "user", "content": user_text})
                conversation_history.append({"role": "assistant", "content": full_text})
                if len(conversation_history) > 10:
                    conversation_history = conversation_history[-10:]
                return full_text

    # Resposta direta em stream sem ferramenta
    print("\033[96m🤖 Assistente: \033[0m", end="", flush=True)
    response_stream = ollama.chat(model='qwen2.5:3b', messages=messages, stream=True)
    full_text = ""
    for chunk in response_stream:
        part = chunk.get("message", {}).get("content", "")
        print(part, end="", flush=True)
        full_text += part
    print("\n")
    
    conversation_history.append({"role": "user", "content": user_text})
    conversation_history.append({"role": "assistant", "content": full_text})
    if len(conversation_history) > 10:
        conversation_history = conversation_history[-10:]
        
    return full_text