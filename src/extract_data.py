import requests
import json
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_weather_data(url:str) -> list:
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        print(f'Error: {response.status_code} - {data.get("message", "Unknown error")}')
        return []

    if not data:
        print('Error: Nenhum dado retornado da API.')
        return []
    
    output_path = 'data/weather_data.json'
    output_dir = Path(output_path).parent
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(data, f, indent=4)

    logging.info(f'Arquivo salvo em: {output_path}')
    return data
