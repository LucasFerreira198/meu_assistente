import urllib.parse
import subprocess

def web_search(query: str) -> str:
    """Pesquisa no YouTube ou Google abrindo no navegador."""
    try:
        if "youtube" in query.lower():
            query_limpa = query.lower().replace("youtube", "").strip()
            url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query_limpa)}" if query_limpa else "https://www.youtube.com"
        else:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            
        subprocess.Popen(["xdg-open", url])
        return f"Navegador aberto pesquisando por: {query}"
    except Exception as e:
        return f"Erro ao pesquisar na web: {e}"

