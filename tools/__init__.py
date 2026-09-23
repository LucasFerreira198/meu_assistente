from .os_tools import open_aplication, close_aplication, get_active_apps_context
from .media_tools import media_control, play_music
from .web_tools import web_search
from .memory_tools import memorize_fact, load_memory
from .system_tools import get_system_health, set_volume
from .weather_tools import get_weather
from .news_tools import get_news
from .alarm_tools import set_timer
from .coding_tools import (
    run_terminal_command, read_file, write_file, save_reusable_script,
    open_terminal_window, view_file_lines, replace_file_content, verify_code_syntax
)
from .vision_tools import analyze_screen, click_on_screen, type_on_screen
from .project_tools import log_project_progress, get_project_summary, list_projects
from .agent_tools import create_background_agent, list_active_agents, stop_background_agent

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
    "set_timer": set_timer,
    "run_terminal_command": run_terminal_command,
    "open_terminal_window": open_terminal_window,
    "read_file": read_file,
    "write_file": write_file,
    "view_file_lines": view_file_lines,
    "replace_file_content": replace_file_content,
    "verify_code_syntax": verify_code_syntax,
    "save_reusable_script": save_reusable_script,
    "analyze_screen": analyze_screen,
    "click_on_screen": click_on_screen,
    "type_on_screen": type_on_screen,
    "log_project_progress": log_project_progress,
    "get_project_summary": get_project_summary,
    "list_projects": list_projects,
    "create_background_agent": create_background_agent,
    "list_active_agents": list_active_agents,
    "stop_background_agent": stop_background_agent
}

TOOLS_SCHEMA = [
    {
        "type": "function",
        "function": {
            "name": "memorize_fact",
            "description": "Salva uma memória permanente sobre o usuário ou sobre outra pessoa.",
            "parameters": {
                "type": "object",
                "properties": {
                    "fact": {"type": "string", "description": "Fato claro e direto. Ex: 'Gosta de rock', 'A esposa se chama Maria'."},
                    "profile": {"type": "string", "description": "Nome da pessoa a qual este fato pertence. Padrão é 'Lucas'."}
                },
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

TOOLS_SCHEMA.extend([
    {
        "type": "function",
        "function": {
            "name": "run_terminal_command",
            "description": "Executa comandos bash no terminal Linux do usuário (ex: curl, python, ls, grep) e retorna stdout/stderr. Pode ser usado para testar códigos, baixar arquivos, etc.",
            "parameters": {
                "type": "object",
                "properties": {"command": {"type": "string", "description": "O comando bash exato a executar."}},
                "required": ["command"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Cria ou edita um arquivo no disco rígido do usuário. Útil para escrever scripts Python, HTML, etc.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Caminho absoluto ou relativo do arquivo a ser criado."},
                    "content": {"type": "string", "description": "Código fonte completo ou texto do arquivo."}
                },
                "required": ["filepath", "content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Lê o conteúdo de um arquivo existente no computador.",
            "parameters": {
                "type": "object",
                "properties": {"filepath": {"type": "string", "description": "Caminho do arquivo."}},
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "view_file_lines",
            "description": "Lê um intervalo específico e numerado de linhas de um arquivo (1-indexado). Use para inspecionar código com precisão cirúrgica antes de editar.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Caminho do arquivo a ser inspecionado."},
                    "start_line": {"type": "integer", "description": "Linha inicial (padrão: 1)."},
                    "end_line": {"type": "integer", "description": "Linha final (padrão: 100)."}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "replace_file_content",
            "description": "Substitui cirurgicamente um trecho exato de código por outro sem sobrescrever nem corromper o restante do arquivo. É a forma segura e recomendada de alterar código existente (estilo Antigravity).",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Caminho do arquivo a ser modificado."},
                    "target_content": {"type": "string", "description": "Trecho de código exato que deve ser substituído (incluindo indentação)."},
                    "replacement_content": {"type": "string", "description": "Novo trecho de código que entrará no lugar."}
                },
                "required": ["filepath", "target_content", "replacement_content"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "verify_code_syntax",
            "description": "Compila e verifica a sintaxe e integridade de um arquivo de código (.py, .sh, .js, .json). Sempre chame após editar código para garantir que não há erros.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filepath": {"type": "string", "description": "Caminho do arquivo a ser verificado."}
                },
                "required": ["filepath"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "save_reusable_script",
            "description": "Salva um código fonte útil e testado na pasta interna 'ares_scripts/' para não precisar ser escrito novamente no futuro. Também registra esse atalho no banco de dados de Conhecimento do Sistema.",
            "parameters": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Nome do arquivo (ex: teste_api.py, buscar_site.sh)"},
                    "content": {"type": "string", "description": "Código completo."},
                    "description": {"type": "string", "description": "Para que serve este script?"}
                },
                "required": ["name", "content", "description"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_screen",
            "description": "Tira um print invisível da tela atual do usuário e envia para a IA de Visão. Útil para: descobrir qual é o 'primeiro link', 'o que está escrito no erro', ou 'onde está o botão x'.",
            "parameters": {
                "type": "object",
                "properties": {"question": {"type": "string", "description": "O que você quer procurar ou saber sobre a tela do usuário?"}},
                "required": ["question"]
            }
        }
    }
])
TOOLS_SCHEMA.extend([
    {
        "type": "function",
        "function": {
            "name": "click_on_screen",
            "description": "Move o mouse e clica (botão esquerdo) em uma coordenada (X, Y) exata da tela. Use 'analyze_screen' antes para descobrir a coordenada correta de um botão ou link.",
            "parameters": {
                "type": "object",
                "properties": {
                    "x": {"type": "integer", "description": "Coordenada X na tela (horizontal)."},
                    "y": {"type": "integer", "description": "Coordenada Y na tela (vertical)."}
                },
                "required": ["x", "y"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "type_on_screen",
            "description": "Usa o teclado para digitar um texto onde o cursor de texto estiver focado. Muito útil para preencher barras de pesquisa após clicar nelas.",
            "parameters": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Texto a ser digitado."},
                    "press_enter": {"type": "boolean", "description": "Se deve apertar ENTER após digitar (Padrão: True)."}
                },
                "required": ["text"]
            }
        }
    }
])
