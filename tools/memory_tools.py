import json
import os

MEMORY_FILE = "memory.json"

def load_memory() -> list:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return []

def _save_memory(mem_list):
    try:
        with open(MEMORY_FILE, "w") as f:
            json.dump(mem_list, f)
    except Exception:
        pass

def memorize_fact(fact: str) -> str:
    """Armazena permanentemente uma preferência ou fato sobre o usuário."""
    mem_list = load_memory()
    mem_list.append(fact)
    _save_memory(mem_list)
    return f"Fato memorizado com sucesso: '{fact}'"

