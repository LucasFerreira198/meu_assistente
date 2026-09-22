import urllib.request
import xml.etree.ElementTree as ET

def get_news() -> str:
    """Busca as últimas 5 manchetes do Brasil no Google News."""
    try:
        url = "https://news.google.com/rss?hl=pt-BR&gl=BR&ceid=BR:pt-419"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            xml_data = response.read()
        
        root = ET.fromstring(xml_data)
        items = root.findall('.//item')
        
        headlines = []
        for i, item in enumerate(items[:5]):
            title = item.find('title').text
            headlines.append(f"- {title}")
            
        return "Aqui estão as manchetes atuais:\n" + "\n".join(headlines)
    except Exception as e:
        return f"Erro ao buscar notícias: {e}"

