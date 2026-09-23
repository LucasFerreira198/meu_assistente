import os
import json
import time

PROJECTS_DIR = os.path.join("storage", "projects")

def _ensure_dir():
    os.makedirs(PROJECTS_DIR, exist_ok=True)

def _get_project_path(project_name: str) -> str:
    _ensure_dir()
    safe_name = "".join(c for c in project_name if c.isalnum() or c in ("-", "_")).lower()
    return os.path.join(PROJECTS_DIR, f"{safe_name}.json")

def log_project_progress(project_name: str, summary: str, files_summary: str = "", pending_tasks: str = "") -> str:
    """Registra o progresso e estado de um projeto de programação no disco para que o ARES se lembre de tudo no futuro sem gastar tokens extras."""
    filepath = _get_project_path(project_name)
    
    project_data = {
        "project_name": project_name,
        "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "summary": summary,
        "files_summary": files_summary,
        "pending_tasks": pending_tasks
    }
    
    if os.path.exists(filepath):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                old_data = json.load(f)
                history = old_data.get("history", [])
                history.append({
                    "date": old_data.get("last_updated"),
                    "summary": old_data.get("summary")
                })
                project_data["history"] = history[-5:] # Mantém os últimos 5 checkpoints
        except Exception:
            pass
            
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(project_data, f, indent=4, ensure_ascii=False)
        return f"Progresso do projeto '{project_name}' gravado com sucesso no diário de bordo."
    except Exception as e:
        return f"Erro ao gravar diário de projeto: {e}"

def get_project_summary(project_name: str) -> str:
    """Lê o diário de bordo e resumo do projeto para continuar o desenvolvimento sem precisar re-analisar arquivos do zero."""
    filepath = _get_project_path(project_name)
    if not os.path.exists(filepath):
        return f"Nenhum diário de bordo encontrado para o projeto '{project_name}'. Você pode iniciar registrando com `log_project_progress`."
        
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        summary = (
            f"=== DIÁRIO DO PROJETO: {data.get('project_name')} ===\n"
            f"Última Atualização: {data.get('last_updated')}\n"
            f"Resumo do que foi feito: {data.get('summary')}\n"
            f"Arquivos envolvidos: {data.get('files_summary')}\n"
            f"Tarefas Pendentes: {data.get('pending_tasks')}\n"
        )
        return summary
    except Exception as e:
        return f"Erro ao carregar resumo do projeto: {e}"

def list_projects() -> str:
    """Lista todos os projetos com diários de bordo registrados na memória do ARES."""
    _ensure_dir()
    files = [f for f in os.listdir(PROJECTS_DIR) if f.endswith(".json")]
    if not files:
        return "Nenhum projeto registrado no momento."
        
    projects = []
    for f in files:
        try:
            with open(os.path.join(PROJECTS_DIR, f), "r", encoding="utf-8") as jf:
                d = json.load(jf)
                projects.append(f"- {d.get('project_name')} (Atualizado em: {d.get('last_updated')}): {d.get('summary')[:80]}...")
        except Exception:
            pass
    return "Projetos em Andamento:\n" + "\n".join(projects)

