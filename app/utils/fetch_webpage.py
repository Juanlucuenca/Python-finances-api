from fastapi import HTTPException
import requests


def fetch_webpage(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Error fetching {url}: {str(e)}")
