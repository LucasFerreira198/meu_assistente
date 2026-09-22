import requests

def get_weather(location: str = "") -> str:
    """Busca a previsão do tempo atual para a localização especificada. Se vazio, pega a localização por IP."""
    try:
        # wttr.in retorna o clima em texto puro
        url = f"https://pt.wttr.in/{location}?format=Em+%l+está+%C+com+%t.+Sensação+de+%f,+umidade+%h."
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text
        return f"Não foi possível obter o clima (Status: {response.status_code})."
    except Exception as e:
        return f"Erro ao buscar clima: {e}"

