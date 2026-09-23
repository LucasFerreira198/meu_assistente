import json
import os

MEMORY_FILE = os.path.join("storage", "memories", "memory.json")

def load_memory() -> dict:
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    return data
        except Exception:
            pass
    return {"profiles": {"Lucas": []}, "system": {}}

def _save_memory(mem_dict: dict):
    try:
        os.makedirs(os.path.dirname(MEMORY_FILE), exist_ok=True)
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(mem_dict, f, indent=4, ensure_ascii=False)
    except Exception:
        pass

def memorize_fact(fact: str, profile: str = "Lucas") -> str:
    """Armazena permanentemente uma preferência ou fato sobre o usuário (ou outras pessoas)."""
    mem = load_memory()
    if "profiles" not in mem:
        mem["profiles"] = {}
    if profile not in mem["profiles"]:
        mem["profiles"][profile] = []
        
    mem["profiles"][profile].append(fact)
    _save_memory(mem)
    return f"Fato memorizado com sucesso no perfil de {profile}: '{fact}'"

def get_system_knowledge(key: str) -> str:
    mem = load_memory()
    return mem.get("system", {}).get(key)

def save_system_knowledge(key: str, value: str):
    mem = load_memory()
    if "system" not in mem:
        mem["system"] = {}
    mem["system"][key] = value
    _save_memory(mem)

