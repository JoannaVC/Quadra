# conexion y personalizacion para geoapify
import requests

# Función para obtener dirección a partir de coordenadas usando Geoapify
def get_address_from_coords(lat, lng, api_key):
    url = f"https://api.geoapify.com/v1/geocode/reverse?lat={lat}&lon={lng}&apiKey={api_key}"
    resp = requests.get(url)
    if resp.status_code == 200:
        data = resp.json()
        if data['features']:
            props = data['features'][0]['properties']
            # Puedes ajustar el formato según lo que quieras mostrar
            return f"{props.get('street', '')} {props.get('housenumber', '')}, {props.get('city', '')}"
    return "Dirección no disponible"