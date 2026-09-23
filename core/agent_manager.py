import threading
import time
import os
import uuid
from dotenv import load_dotenv

load_dotenv()

class SubAgent:
    def __init__(self, agent_id: str, name: str, task_prompt: str, on_update_callback=None):
        self.agent_id = agent_id
        self.name = name
        self.task_prompt = task_prompt
        self.status = "running" # "running", "completed", "error", "stopped"
        self.start_time = time.strftime("%H:%M:%S")
        self.end_time = None
        self.logs = []
        self.on_update_callback = on_update_callback
        self._stop_event = threading.Event()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)

    def log(self, text: str):
        msg = f"[{time.strftime('%H:%M:%S')}] {text}"
        self.logs.append(msg)
        if self.on_update_callback:
            try:
                self.on_update_callback(self)
            except Exception:
                pass

    def stop(self):
        self.status = "stopped"
        self.end_time = time.strftime("%H:%M:%S")
        self._stop_event.set()
        self.log("⚠️ Agente interrompido pelo usuário.")

    def _run_loop(self):
        import google.generativeai as genai
        from tools.coding_tools import (
            run_terminal_command, read_file, write_file, save_reusable_script,
            view_file_lines, replace_file_content, verify_code_syntax
        )
        from tools.project_tools import log_project_progress, get_project_summary
        from tools.vision_tools import analyze_screen
        
        self.log(f"Iniciando sub-agente '{self.name}'...")
        
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            self.status = "error"
            self.log("Erro: GEMINI_API_KEY ausente.")
            return

        genai.configure(api_key=api_key)
        
        agent_tools = {
            "run_terminal_command": run_terminal_command,
            "read_file": read_file,
            "write_file": write_file,
            "view_file_lines": view_file_lines,
            "replace_file_content": replace_file_content,
            "verify_code_syntax": verify_code_syntax,
            "save_reusable_script": save_reusable_script,
            "log_project_progress": log_project_progress,
            "get_project_summary": get_project_summary,
            "analyze_screen": analyze_screen
        }
        
        system_instruction = (
            f"Você é o Sub-Agente '{self.name}', um Engenheiro de Software Autônomo e Trabalhador em Segundo Plano do sistema ARES (padrão Antigravity).\n"
            "Sua missão é executar e resolver a tarefa atribuída de forma 100% independente, com rigor cirúrgico e auto-correção:\n"
            f"TAREFA: {self.task_prompt}\n\n"
            "DIRETRIZES DE ENGENHARIA CIRÚRGICA (ESTILO ANTIGRAVITY):\n"
            "1. INSPECIONE ANTES DE MODIFICAR: Use `view_file_lines` ou `read_file` para analisar o arquivo antes de alterá-lo.\n"
            "2. EDIÇÃO CIRÚRGICA: Para alterar código existente, use SEMPRE `replace_file_content`. NUNCA sobrescreva arquivos inteiros com `write_file` a menos que seja um arquivo novo.\n"
            "3. VERIFICAÇÃO AUTOMÁTICA OBRIGATÓRIA: Após qualquer modificação ou criação de arquivo, chame SEMPRE `verify_code_syntax` para garantir que o código compila sem erros de sintaxe.\n"
            "4. LOOP DE AUTO-CORREÇÃO: Se `verify_code_syntax` ou `run_terminal_command` acusar erro ou traceback, leia a mensagem de erro com atenção, use `replace_file_content` para corrigir a falha pontual e teste novamente. Repita até o código estar 100% funcional e verificado.\n"
            "5. VISÃO DA TELA: Se necessário inspecionar erros ou código abertos na tela do usuário, use `analyze_screen`.\n"
            "6. CONCLUSÃO: Ao concluir, apresente um resumo claro e conciso do que foi alterado, verificado e validado com sucesso."
        )
        
        try:
            # Prioriza gemini-3.6-flash para raciocínio avançado de programação; fallback para gemini-flash-latest
            chosen_model = "gemini-3.6-flash"
            try:
                model = genai.GenerativeModel(
                    model_name=chosen_model,
                    system_instruction=system_instruction,
                    tools=list(agent_tools.values())
                )
                chat = model.start_chat()
                resp = chat.send_message("Comece a executar a tarefa atribuída agora.")
            except Exception as me:
                self.log(f"Fallback de modelo para gemini-flash-latest devido a: {me}")
                chosen_model = "gemini-flash-latest"
                model = genai.GenerativeModel(
                    model_name=chosen_model,
                    system_instruction=system_instruction,
                    tools=list(agent_tools.values())
                )
                chat = model.start_chat()
                resp = chat.send_message("Comece a executar a tarefa atribuída agora.")
                
            max_steps = 15
            step = 0
            
            while step < max_steps and not self._stop_event.is_set():
                step += 1
                function_calls = []
                text_content = ""
                
                if resp.candidates and resp.candidates[0].content.parts:
                    for part in resp.candidates[0].content.parts:
                        if part.function_call:
                            function_calls.append(part.function_call)
                        elif part.text:
                            text_content += part.text
                            
                if text_content:
                    self.log(f"IA: {text_content[:150]}")
                    
                if not function_calls or self._stop_event.is_set():
                    break
                    
                tool_responses = []
                for fc in function_calls:
                    if self._stop_event.is_set():
                        break
                    fn_name = fc.name
                    args = type(fc).to_dict(fc).get("args", {})
                    self.log(f"> Executando {fn_name}({str(args)[:80]})")
                    
                    if fn_name in agent_tools:
                        result = agent_tools[fn_name](**args)
                    else:
                        result = f"Ferramenta '{fn_name}' indisponível."
                        
                    self.log(f"< Resultado: {str(result)[:100]}")
                    
                    tool_responses.append(
                        genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=fn_name,
                                response={"result": str(result)}
                            )
                        )
                    )
                    
                if self._stop_event.is_set():
                    break
                    
                resp = chat.send_message(
                    genai.protos.Content(parts=tool_responses)
                )

            if not self._stop_event.is_set():
                self.status = "completed"
                self.end_time = time.strftime("%H:%M:%S")
                self.log(f"✅ Agente '{self.name}' concluiu a tarefa com sucesso!")
        except Exception as e:
            self.status = "error"
            self.end_time = time.strftime("%H:%M:%S")
            self.log(f"❌ Erro na execução do agente: {str(e)}")

    def start(self):
        self.thread.start()


class AgentManager:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(AgentManager, cls).__new__(cls)
            cls._instance.agents = {}
            cls._instance.ui_callback = None
            cls._instance.lock = threading.Lock()
        return cls._instance

    def set_ui_callback(self, callback):
        self.ui_callback = callback

    def spawn_agent(self, name: str, task_prompt: str) -> str:
        agent_id = f"agent-{len(self.agents) + 1}"
        agent = SubAgent(agent_id, name, task_prompt, on_update_callback=self._on_agent_update)
        with self.lock:
            self.agents[agent_id] = agent
        agent.start()
        self._notify_ui()
        return agent_id

    def _on_agent_update(self, agent):
        self._notify_ui()

    def _notify_ui(self):
        if self.ui_callback:
            try:
                self.ui_callback(self.get_agents_info())
            except Exception:
                pass

    def stop_agent(self, agent_id: str) -> bool:
        with self.lock:
            if agent_id in self.agents:
                self.agents[agent_id].stop()
                self._notify_ui()
                return True
        return False

    def get_agents_info(self) -> list:
        info_list = []
        with self.lock:
            for aid, a in self.agents.items():
                info_list.append({
                    "id": a.agent_id,
                    "name": a.name,
                    "task": a.task_prompt,
                    "status": a.status,
                    "start": a.start_time,
                    "end": a.end_time,
                    "last_log": a.logs[-1] if a.logs else "Aguardando..."
                })
        return info_list

agent_manager = AgentManager()

