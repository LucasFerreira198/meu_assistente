import ollama
from core.os_adapter import SystemAdapter

sys_adapter = SystemAdapter()

AVAILABLE_TOOLS = {"open_aplication": sys_adapter.launch_app}
TOOLS_SCHEMA = [{
    "type": "fuction",
    "function": {
        "name": "open_aplication",
        "description": "Abre um aplicativo no computador do usuário.",
        "parameters": {
            "type": "object",
            "properties": {"app_name": {"type": "string", "description": "Comando do app (ex: firefox, calcualtor, spotify)"}},
            "required": ["app_name"],
        }
    }
}]

def process_intent(user_text: str) -> str:
    messages = [
        {"role": "system", "content": "Você é um assistente rápido e direto, Se acionar uma ferramenta, confirme com uma frase curta."},
        {"role": "user", "content": user_text}
    ]

    response = ollama.chat(model='qwen2.5:7b', messages=messages, tools=TOOLS_SCHEMA)
    tool_calls = response.get("message", {}).get("tool_calls")

    if tool_calls:
        for tool in tool_calls:
            fucn_name = tool["function"]["name"]
            args = tool["function"]["arguments"]

            if fucn_name in AVAILABLE_TOOLS:
                result = AVAILABLE_TOOLS[fucn_name](**args)
                print(f"⚙️ [SISTEMA]: {result}")

                messages.append(response["message"])
                messages.append({"role": "tool", "content": result})
                final_responde = ollama.chat(model="qwen2.5:7b", messages=messages)
                return final_responde["message"]["content"]

    return response["message"]["content"]