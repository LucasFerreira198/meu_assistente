from core.agent_manager import agent_manager

def create_background_agent(name: str, task_prompt: str) -> str:
    """Cria e inicia um Sub-Agente autônomo em segundo plano para programar, rodar testes ou executar tarefas demoradas enquanto o usuário conversa com o ARES."""
    agent_id = agent_manager.spawn_agent(name=name, task_prompt=task_prompt)
    return f"Sub-Agente '{name}' (ID: {agent_id}) iniciado com sucesso em segundo plano! Ele já está trabalhando na tarefa: {task_prompt}"

def list_active_agents() -> str:
    """Lista todos os Sub-Agentes criados, seu status atual e o último log de atividade."""
    agents = agent_manager.get_agents_info()
    if not agents:
        return "Nenhum sub-agente ativo no momento."
        
    lines = ["=== SUB-AGENTES EM SEGUNDO PLANO ==="]
    for a in agents:
        lines.append(
            f"- [{a['status'].upper()}] {a['name']} (ID: {a['id']}):\n"
            f"  Tarefa: {a['task']}\n"
            f"  Início: {a['start']} | Fim: {a['end'] or 'Em andamento'}\n"
            f"  Último log: {a['last_log']}"
        )
    return "\n".join(lines)

def stop_background_agent(agent_id: str) -> str:
    """Interrompe a execução de um sub-agente específico."""
    ok = agent_manager.stop_agent(agent_id)
    if ok:
        return f"Sub-Agente '{agent_id}' foi interrompido com sucesso."
    return f"Sub-Agente '{agent_id}' não encontrado."

