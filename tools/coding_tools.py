import os
import subprocess
import json

def run_terminal_command(command: str) -> str:
    """Executa um comando de terminal na máquina host e retorna a saída."""
    try:
        # A timeout prevents the assistant from hanging indefinitely on commands that wait for input
        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
        output = result.stdout + result.stderr
        return output if output else "Comando executado com sucesso sem saída visível."
    except subprocess.TimeoutExpired:
        return "Erro: O comando excedeu o tempo limite de 30 segundos e foi abortado."
    except Exception as e:
        return f"Erro ao executar o comando: {str(e)}"

def read_file(filepath: str) -> str:
    """Lê o conteúdo de um arquivo no disco."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"Erro ao ler arquivo: {str(e)}"

def write_file(filepath: str, content: str) -> str:
    """Cria ou edita um arquivo com o conteúdo fornecido."""
    try:
        # Cria as pastas pai caso não existam
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return f"Arquivo '{filepath}' salvo com sucesso."
    except Exception as e:
        return f"Erro ao escrever no arquivo: {str(e)}"

def save_reusable_script(name: str, content: str, description: str) -> str:
    """Salva um script útil na pasta 'ares_scripts/' e registra o conhecimento no banco de dados para reuso."""
    try:
        scripts_dir = os.path.abspath("ares_scripts")
        os.makedirs(scripts_dir, exist_ok=True)
        
        filepath = os.path.join(scripts_dir, name)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
        # Torna executável se for shell/bash
        if name.endswith(".sh"):
            os.chmod(filepath, 0o755)
            
        # Salva o registro na memória do sistema (System Knowledge)
        from .memory_tools import save_system_knowledge
        cache_key = f"script_{name.split('.')[0]}"
        save_system_knowledge(cache_key, {"path": filepath, "description": description})
        
        return f"Script '{name}' salvo em {filepath} e registrado na Memória de Sistema para reuso futuro."
    except Exception as e:
        return f"Erro ao salvar script reutilizável: {str(e)}"

def open_terminal_window(command: str = "") -> str:
    """Abre uma janela física visível do terminal do Linux (GNOME Terminal) na tela do usuário. Se for fornecido um comando, executa o comando dentro do terminal e mantém a janela aberta para o usuário ver."""
    try:
        if command and command.strip():
            cmd = f'gnome-terminal -- bash -c "{command}; echo; echo Pressione qualquer tecla para sair...; read -n 1; exec bash"'
        else:
            cmd = 'gnome-terminal'
        subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return "Janela do terminal aberta com sucesso na tela do usuário."
    except Exception as e:
        return f"Erro ao abrir janela do terminal: {e}"

def view_file_lines(filepath: str, start_line: int = 1, end_line: int = 100) -> str:
    """Visualiza um trecho numerado de linhas de um arquivo existente (1-indexado).
    Essencial para inspecionar código com precisão antes de fazer edições cirúrgicas."""
    try:
        if not os.path.exists(filepath):
            return f"Erro: O arquivo '{filepath}' não existe."
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        
        total_lines = len(lines)
        if total_lines == 0:
            return f"O arquivo '{filepath}' está vazio."
            
        start_line = max(1, int(start_line))
        end_line = min(total_lines, int(end_line))
        
        if start_line > end_line:
            return f"Erro: start_line ({start_line}) é maior que end_line ({end_line})."
            
        result_lines = []
        for idx in range(start_line - 1, end_line):
            result_lines.append(f"{idx + 1}: {lines[idx].rstrip('\\r\\n')}")
            
        header = f"--- [{filepath}] (Linhas {start_line} a {end_line} de {total_lines}) ---"
        return header + "\n" + "\n".join(result_lines)
    except Exception as e:
        return f"Erro ao ler linhas do arquivo: {str(e)}"

def replace_file_content(filepath: str, target_content: str, replacement_content: str) -> str:
    """Substitui cirurgicamente um trecho exato de código por outro sem sobrescrever ou corromper o arquivo inteiro.
    Esta é a ferramenta recomendada para editar código com segurança, no estilo Antigravity."""
    try:
        if not os.path.exists(filepath):
            return f"Erro: O arquivo '{filepath}' não existe."
            
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        if target_content not in content:
            return f"Erro: O trecho 'target_content' não foi encontrado exatamente como especificado dentro de '{filepath}'. Verifique quebras de linha e indentação usando view_file_lines."
            
        occurrences = content.count(target_content)
        if occurrences > 1:
            # Substitui a primeira ocorrência
            new_content = content.replace(target_content, replacement_content, 1)
            extra_msg = f" (Aviso: foram encontradas {occurrences} ocorrências idênticas; a primeira foi substituída)"
        else:
            new_content = content.replace(target_content, replacement_content)
            extra_msg = ""
            
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(new_content)
            
        return f"Sucesso: Trecho substituído cirurgicamente em '{filepath}'{extra_msg}."
    except Exception as e:
        return f"Erro ao substituir conteúdo em '{filepath}': {str(e)}"

def verify_code_syntax(filepath: str) -> str:
    """Verifica e valida a sintaxe e integridade do arquivo de código (Python, Bash, JS, JSON).
    Permite ao assistente identificar erros de sintaxe e corrigi-los autonomamente antes de declarar a tarefa pronta."""
    try:
        if not os.path.exists(filepath):
            return f"Erro: O arquivo '{filepath}' não foi encontrado."
            
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == ".py":
            cmd = f'python3 -m py_compile "{filepath}"'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                return f"✅ [Sintaxe Python Válida]: O arquivo '{filepath}' compilou perfeitamente sem erros de sintaxe."
            else:
                return f"❌ [Erro de Sintaxe Python]: Falha na compilação de '{filepath}':\n{res.stderr}"
                
        elif ext in [".sh", ".bash"]:
            cmd = f'bash -n "{filepath}"'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                return f"✅ [Sintaxe Bash Válida]: O script '{filepath}' passou na verificação de sintaxe."
            else:
                return f"❌ [Erro de Sintaxe Bash] em '{filepath}':\n{res.stderr}"
                
        elif ext == ".json":
            with open(filepath, "r", encoding="utf-8") as f:
                json.load(f)
            return f"✅ [JSON Válido]: O arquivo '{filepath}' é um JSON bem formatado."
            
        elif ext == ".js":
            cmd = f'node --check "{filepath}"'
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if res.returncode == 0:
                return f"✅ [Sintaxe JavaScript Válida]: O script '{filepath}' é sintaticamente correto."
            else:
                return f"❌ [Erro de Sintaxe JS] em '{filepath}':\n{res.stderr}"
                
        else:
            return f"Aviso: Tipo de arquivo '{ext}' não possui linter automatizado configurado, mas o arquivo existe."
    except json.JSONDecodeError as je:
        return f"❌ [Erro de Formato JSON] em '{filepath}': {str(je)}"
    except Exception as e:
        return f"Erro ao verificar sintaxe de '{filepath}': {str(e)}"

