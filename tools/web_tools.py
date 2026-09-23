import urllib.parse
import urllib.request
import re
import subprocess

def web_search(query: str) -> str:
    """Pesquisa no YouTube ou Google abrindo no navegador. Para vídeos do YouTube, reproduz o vídeo diretamente."""
    try:
        query_stripped = query.strip()
        if query_stripped.startswith("http://") or query_stripped.startswith("https://"):
            url = query_stripped
        elif query_stripped.lower() in ["youtube", "youtube.com", "abrir youtube"]:
            url = "https://www.youtube.com"
        elif any(k in query.lower() for k in ["youtube", "video", "vídeo", "assistir"]):
            query_limpa = query.lower()
            for w in ["youtube", "video", "vídeo", "assistir", "abrir", "procure"]:
                query_limpa = query_limpa.replace(w, "")
            query_limpa = query_limpa.strip()
            
            if not query_limpa:
                url = "https://www.youtube.com"
            else:
                # Faz o web scraping ultra-rápido para capturar o ID direto do primeiro vídeo
                try:
                    search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query_limpa)}"
                    req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'})
                    with urllib.request.urlopen(req, timeout=3) as resp:
                        html = resp.read().decode('utf-8', errors='ignore')
                    video_ids = re.findall(r"watch\?v=([a-zA-Z0-9_-]{11})", html)
                    if video_ids:
                        # Abre diretamente o vídeo em execução (player)
                        url = f"https://www.youtube.com/watch?v={video_ids[0]}"
                    else:
                        url = search_url
                except Exception:
                    url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query_limpa)}"
        else:
            url = f"https://www.google.com/search?q={urllib.parse.quote(query)}"
            
        subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
        return f"Navegador aberto com sucesso em: {url}"
    except Exception as e:
        return f"Erro ao pesquisar na web: {e}"
