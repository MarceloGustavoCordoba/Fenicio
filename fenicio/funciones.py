import requests

def fenicio_ordenes(dia):
    
    url = "https://hudsoncocina.com.uy/API_V1/ordenes?fDesde=" + dia + "&fHasta=" + dia

    try:
        response = requests.get(url)
        return response
    except requests.exceptions.RequestException as e:
        return e