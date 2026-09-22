from .os_tools import open_aplication, close_aplication, get_active_apps_context
from .media_tools import media_control, play_music
from .web_tools import web_search
from .memory_tools import memorize_fact, load_memory
from .system_tools import get_system_health, set_volume
from .weather_tools import get_weather
from .news_tools import get_news
from .alarm_tools import set_timer

AVAILABLE_TOOLS = {
    "open_aplication": open_aplication,
    "close_aplication": close_aplication,
    "media_control": media_control,
    "play_music": play_music,
    "web_search": web_search,
    "memorize_fact": memorize_fact,
    "get_system_health": get_system_health,
    "set_volume": set_volume,
    "get_weather": get_weather,
    "get_news": get_news,
    "set_timer": set_timer
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "memorize_fact",
            "description": "Salva uma memória permanente sobre o usuário (seu nome, suas preferências, coisas que ele gosta).",
            "parameters": {
                "type": "object",
                "properties": {"fact": {"type": "string", "description": "Fato claro e direto. Ex: 'O usuário se chama Lucas', 'O usuário gosta de rock'."}},
                "required": ["fact"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "open_aplication",
            "description": "Abre um aplicativo de sistema local (NÃO USE para sites como YouTube ou Google. Apenas apps instalados ex: spotify, firefox, calculator).",
            "parameters": {
                "type": "object",
                "properties": {"app_name": {"type": "string", "description": "Nome EXATO e correto do app"}},
                "required": ["app_name"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "close_aplication",
            "description": "Fecha ou encerra um aplicativo que está aberto no sistema (ex: spotify, firefox, calculator).",
            "parameters": {
                "type": "object",
                "properties": {"app_name": {"type": "string", "description": "Nome EXATO e correto do app a ser fechado."}},
                "required": ["app_name"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "media_control",
            "description": "Controla a reprodução de mídia atual (pausar, proxima música, voltar).",
            "parameters": {
                "type": "object",
                "properties": {"action": {"type": "string", "description": "Ação a ser realizada: 'play-pause', 'next', ou 'prev'."}},
                "required": ["action"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "play_music",
            "description": "Toca ou pesquisa uma música específica (ex: toque uma musica calma, toque rock).",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "O nome da música, artista ou estilo a ser buscado."}},
                "required": ["query"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Abre o navegador de internet padrão e faz uma pesquisa no Google ou YouTube.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string", "description": "O que pesquisar. Pode incluir 'youtube' no termo se for vídeo."}},
                "required": ["query"],
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_system_health",
            "description": "Verifica a saúde atual do PC (uso de CPU, uso de RAM, disco ocupado).",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_volume",
            "description": "Altera o volume do computador ou silencia (mute).",
            "parameters": {
                "type": "object",
                "properties": {
                    "level": {"type": "integer", "description": "Nível do volume em porcentagem (0 a 100)."},
                    "action": {"type": "string", "description": "Ação alternativa: 'mute' ou 'unmute'"}
                },
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Busca a previsão do tempo e clima de uma cidade.",
            "parameters": {
                "type": "object",
                "properties": {"location": {"type": "string", "description": "Nome da cidade para ver o clima. Deixe vazio para usar a localização atual."}},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_news",
            "description": "Lê as principais e últimas notícias do momento no Brasil.",
            "parameters": {
                "type": "object",
                "properties": {},
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_timer",
            "description": "Cria um alarme/lembrete. O LLM deve converter o tempo que o usuário pediu para segundos e passar para a ferramenta.",
            "parameters": {
                "type": "object",
                "properties": {
                    "seconds": {"type": "integer", "description": "Quantos SEGUNDOS faltam para o alarme tocar (Ex: se pedir 5 minutos, envie 300)."},
                    "message": {"type": "string", "description": "Qual o motivo do alarme."}
                },
                "required": ["seconds"]
            }
        }
    }
]

