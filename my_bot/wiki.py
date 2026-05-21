import requests

def get_wiki_summary(query: str) -> str:
    try:
        url = "https://ru.wikipedia.org/api/rest_v1/page/summary/" + query.replace(" ", "_")
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("extract", "")[:500]
        else:
            return ""
    except Exception:
        return ""